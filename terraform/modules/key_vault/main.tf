###############################################################################
# modules/key_vault/main.tf
#
# Azure Key Vault configured with RBAC authorization.
#
# Key design decisions:
#   - `enable_rbac_authorization = true`
#     Avoids the legacy access-policy model which is still enabled by
#     default in azurerm. RBAC is the modern path, integrates with
#     Azure AD natively, and is the only way to grant scoped roles like
#     "Key Vault Secrets User".
#
#   - `soft_delete_retention_days = 90` + `purge_protection_enabled = true`
#     Protects against accidental deletion. Once purge protection is on
#     it cannot be disabled — this is intentional: a compromised operator
#     should not be able to wipe production secrets.
#
#   - No secrets are written by this module. Placeholders are created so
#     that RBAC can be validated at apply time, but the actual values are
#     written out-of-band:
#       az keyvault secret set \
#         --vault-name <name> \
#         --name anthropic-api-key \
#         --value "$ANTHROPIC_API_KEY"
###############################################################################

resource "azurerm_key_vault" "this" {
  name                = var.key_vault_name
  resource_group_name = var.resource_group_name
  location            = var.location
  tenant_id           = var.tenant_id

  sku_name = var.sku_name

  # Modern auth model — use Azure RBAC instead of the built-in access
  # policy list on the vault itself.
  enable_rbac_authorization = true

  # Soft-delete is now mandatory in Azure but we pin the retention window
  # anyway so it's visible in code review.
  soft_delete_retention_days = 90
  purge_protection_enabled   = true

  # Keep the network posture explicit. For a hardened deployment, set
  # this to "Deny" and add a private endpoint + vnet rule.
  public_network_access_enabled = true

  network_acls {
    default_action = "Allow"
    bypass         = "AzureServices"
  }

  tags = var.tags
}

# -----------------------------------------------------------------------------
# Grant the Terraform runner Secrets Officer on this vault.
#
# This is what allows the `azurerm_key_vault_secret` placeholder resources
# below to be created on first apply. It is the ONLY role that the
# Terraform principal receives — after the first apply, an operator can
# safely remove this assignment if they want a zero-trust vault.
# -----------------------------------------------------------------------------

resource "azurerm_role_assignment" "terraform_secrets_officer" {
  count = var.grant_terraform_secrets_officer ? 1 : 0

  scope                = azurerm_key_vault.this.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = var.terraform_principal_object_id

  description = "Temporary Terraform grant to create secret placeholders — set grant_terraform_secrets_officer=false after bootstrap"
}

# -----------------------------------------------------------------------------
# RBAC propagation wait
#
# Azure RBAC assignments propagate eventually (5-15 minutes in practice).
# The depends_on on the role assignment above guarantees creation ORDER
# but not propagation COMPLETION. Without this wait, the secret
# placeholder creation below fails intermittently with 403 Forbidden.
# -----------------------------------------------------------------------------

resource "time_sleep" "wait_for_rbac" {
  count           = var.grant_terraform_secrets_officer ? 1 : 0
  depends_on      = [azurerm_role_assignment.terraform_secrets_officer]
  create_duration = "120s"
}

# -----------------------------------------------------------------------------
# Secret placeholders
#
# We create empty-ish placeholders so that:
#   1. Fixi's ACI definition can reference them by name without a
#      race on first deploy.
#   2. Operators can see which secrets are expected by the platform
#      (self-documenting vault).
#
# The placeholder value is literally "REPLACE_ME". Production operators
# must overwrite these via `az keyvault secret set` before Fixi starts.
# -----------------------------------------------------------------------------

locals {
  secret_names = [
    "anthropic-api-key",
    "ado-pat",
    "github-pat",
  ]
}

resource "azurerm_key_vault_secret" "placeholders" {
  for_each = toset(local.secret_names)

  name         = each.value
  value        = "REPLACE_ME"
  key_vault_id = azurerm_key_vault.this.id

  content_type = "text/plain; placeholder"

  tags = var.tags

  # Wait for RBAC to propagate before attempting to write secrets.
  # When grant_terraform_secrets_officer=false (post-bootstrap), secrets
  # are managed out-of-band and this resource is a no-op via ignore_changes.
  depends_on = [
    time_sleep.wait_for_rbac,
    azurerm_role_assignment.terraform_secrets_officer,
  ]

  lifecycle {
    # Once production operators overwrite the secret value out-of-band,
    # we don't want Terraform to reset it back to "REPLACE_ME" on the
    # next plan. `ignore_changes` pins the value to whatever's live.
    ignore_changes = [
      value,
      content_type,
    ]
  }
}
