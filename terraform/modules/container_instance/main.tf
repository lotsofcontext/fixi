###############################################################################
# modules/container_instance/main.tf
#
# Azure Container Instance (ACI) running the Fixi agent.
#
# Architectural notes:
#   - We use a single-container group. Fixi is one process; no sidecars.
#   - `os_type = "Linux"` is mandatory for VNet-integrated ACI today.
#   - `restart_policy = "OnFailure"` — Fixi is a long-running worker
#     that polls a queue. If it crashes, we want ACI to restart it.
#     Use "Never" for true one-shot jobs; "Always" will cause restart
#     loops on configuration errors.
#   - We attach the user-assigned managed identity so Fixi can pull
#     secrets from Key Vault using DefaultAzureCredential inside the
#     container.
#   - Diagnostic logs stream to the Log Analytics workspace provided
#     by the root module.
#
# Secret injection:
#   We fetch the secret values at plan time via `data` sources on Key
#   Vault and pass them as `secure_environment_variables`. This means:
#     - The values are encrypted at rest in ACI state.
#     - They never appear in `terraform show` (secure envs are
#       redacted).
#     - Rotating a secret requires re-running terraform apply to push
#       the new value into the ACI (documented trade-off).
###############################################################################

# -----------------------------------------------------------------------------
# Data sources: read secret values from Key Vault at apply time.
#
# These resolve because the root module has already granted the
# Terraform runner "Key Vault Secrets Officer" via the key_vault module.
# If that role is revoked post-bootstrap, an operator must pass the
# secret values via a different mechanism (e.g. external var from a
# bootstrap script).
# -----------------------------------------------------------------------------

data "azurerm_key_vault_secret" "anthropic_api_key" {
  name         = "anthropic-api-key"
  key_vault_id = local.key_vault_id_from_secret_uri
}

data "azurerm_key_vault_secret" "ado_pat" {
  name         = "ado-pat"
  key_vault_id = local.key_vault_id_from_secret_uri
}

data "azurerm_key_vault_secret" "github_pat" {
  name         = "github-pat"
  key_vault_id = local.key_vault_id_from_secret_uri
}

# -----------------------------------------------------------------------------
# Helper: derive the Key Vault resource ID from the secret URI.
#
# The root module passes secret URIs (e.g.
#   https://kv-fixi-dev-abc123.vault.azure.net/secrets/anthropic-api-key)
# but `data.azurerm_key_vault_secret` requires a key_vault_id. We parse
# the vault name out of the URI and then look up the vault by name.
# This keeps the module contract clean (caller only deals with URIs)
# without adding a redundant variable.
# -----------------------------------------------------------------------------

locals {
  # Pull "kv-fixi-dev-abc123" out of "https://kv-fixi-dev-abc123.vault.azure.net/secrets/..."
  vault_name_from_uri = regex("https://([^.]+)\\.vault\\.azure\\.net", var.anthropic_api_key_secret_id)[0]
}

data "azurerm_key_vault" "target" {
  name                = local.vault_name_from_uri
  resource_group_name = var.resource_group_name
}

locals {
  key_vault_id_from_secret_uri = data.azurerm_key_vault.target.id
}

# -----------------------------------------------------------------------------
# Container group
# -----------------------------------------------------------------------------

resource "azurerm_container_group" "this" {
  name                = var.aci_name
  resource_group_name = var.resource_group_name
  location            = var.location

  os_type        = "Linux"
  restart_policy = "OnFailure"

  # VNet integration. Once `subnet_ids` is set, ACI is NOT publicly
  # addressable and `ip_address_type` must be "Private".
  ip_address_type = "Private"
  subnet_ids      = [var.subnet_id]

  # Bind the user-assigned managed identity. This is what lets the
  # container call Azure AD via IMDS and fetch tokens for Key Vault,
  # Storage, Azure DevOps, etc.
  identity {
    type         = "UserAssigned"
    identity_ids = [var.managed_identity_id]
  }

  # Pull images from our own ACR using the managed identity.
  image_registry_credential {
    server                    = var.acr_login_server
    user_assigned_identity_id = var.managed_identity_id
  }

  # -------------------------------------------------------------------------
  # Diagnostics: stream stdout/stderr to Log Analytics.
  # -------------------------------------------------------------------------
  diagnostics {
    log_analytics {
      workspace_id  = var.log_analytics_workspace_id
      workspace_key = var.log_analytics_workspace_key
    }
  }

  # -------------------------------------------------------------------------
  # The one and only container
  # -------------------------------------------------------------------------
  container {
    name   = "fixi"
    image  = "${var.acr_login_server}/${var.container_image}"
    cpu    = var.cpu_cores
    memory = var.memory_gb

    # ACI requires at least one port definition even for private groups.
    # Fixi doesn't listen on anything — we declare a single unused port
    # so the API accepts the spec.
    ports {
      port     = 8080
      protocol = "TCP"
    }

    # Non-sensitive configuration — visible in `terraform show`.
    environment_variables = {
      FIXI_ENV                 = var.aci_name
      FIXI_LOG_LEVEL           = "info"
      AZURE_CLIENT_ID          = "" # Injected by ACI when using UAMI; placeholder so reviewers know to expect it
      ANTHROPIC_API_KEY_SECRET = var.anthropic_api_key_secret_id
      ADO_PAT_SECRET           = var.ado_pat_secret_id
      GITHUB_PAT_SECRET        = var.github_pat_secret_id
    }

    # Secret values — encrypted at rest, redacted in state.
    secure_environment_variables = {
      ANTHROPIC_API_KEY = data.azurerm_key_vault_secret.anthropic_api_key.value
      ADO_PAT           = data.azurerm_key_vault_secret.ado_pat.value
      GITHUB_PAT        = data.azurerm_key_vault_secret.github_pat.value
    }
  }

  tags = var.tags
}
