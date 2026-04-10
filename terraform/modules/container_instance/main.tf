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
# The key_vault_id is passed directly from the root module (via the
# key_vault module output), which eliminates the chicken-and-egg problem
# of parsing a URI for a vault that doesn't exist yet on first apply.
#
# If the Terraform runner's "Key Vault Secrets Officer" role is revoked
# post-bootstrap, an operator must pass the secret values via a different
# mechanism (e.g. external var from a bootstrap script).
# -----------------------------------------------------------------------------

data "azurerm_key_vault_secret" "anthropic_api_key" {
  name         = "anthropic-api-key"
  key_vault_id = var.key_vault_id
}

data "azurerm_key_vault_secret" "ado_pat" {
  name         = "ado-pat"
  key_vault_id = var.key_vault_id
}

data "azurerm_key_vault_secret" "github_pat" {
  name         = "github-pat"
  key_vault_id = var.key_vault_id
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
      FIXI_ENV        = var.environment
      FIXI_LOG_LEVEL  = "info"
      AZURE_CLIENT_ID = var.managed_identity_client_id
    }

    # Secret values — encrypted at rest, redacted in state.
    secure_environment_variables = {
      ANTHROPIC_API_KEY = data.azurerm_key_vault_secret.anthropic_api_key.value
      ADO_PAT           = data.azurerm_key_vault_secret.ado_pat.value
      GITHUB_PAT        = data.azurerm_key_vault_secret.github_pat.value
    }

    # -----------------------------------------------------------------
    # Liveness probe
    #
    # Detects zombie states (process alive but not functional — e.g.
    # deadlock, memory leak, exhausted connection pool). Without this,
    # restart_policy = "OnFailure" only kicks in when the process dies.
    #
    # Uses exec instead of http_get because Fixi is a queue worker,
    # not a web server. The Fixi process must touch /tmp/fixi-alive
    # on each successful poll cycle.
    # -----------------------------------------------------------------
    liveness_probe {
      exec {
        command = ["/bin/sh", "-c", "test -f /tmp/fixi-alive && find /tmp/fixi-alive -mmin -5 | grep -q ."]
      }

      initial_delay_seconds = 120
      period_seconds        = 60
      failure_threshold     = 3
      timeout_seconds       = 5
    }
  }

  tags = var.tags
}
