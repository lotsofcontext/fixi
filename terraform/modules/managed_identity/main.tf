###############################################################################
# modules/managed_identity/main.tf
#
# User-assigned Managed Identity (UAMI) + role assignments.
#
# Why user-assigned instead of system-assigned:
#   1. We can grant RBAC BEFORE the ACI exists, avoiding chicken-and-egg.
#   2. Rebuilding the ACI (e.g. to change image) does not rotate the
#      identity — so external RBAC grants (Azure DevOps permissions,
#      custom GitHub OAuth app bindings) survive container restarts.
#   3. The same identity can be reused if we later split Fixi into
#      multiple container groups.
#
# Roles granted here:
#   - AcrPull on the target ACR
#   - Key Vault Secrets User on the target Key Vault
#   - (optional) same KV Secrets User grant for a list of developer
#     object IDs for live debugging
###############################################################################

# -----------------------------------------------------------------------------
# The identity itself
# -----------------------------------------------------------------------------

resource "azurerm_user_assigned_identity" "this" {
  name                = var.name
  resource_group_name = var.resource_group_name
  location            = var.location

  tags = var.tags
}

# -----------------------------------------------------------------------------
# AcrPull on the container registry
#
# Scoping the assignment to acr_id (not the resource group) follows the
# principle of least privilege — Fixi cannot enumerate or pull from any
# other registry in the subscription.
# -----------------------------------------------------------------------------

resource "azurerm_role_assignment" "acr_pull" {
  scope                = var.acr_id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.this.principal_id

  # Helpful annotation that shows up in Azure Activity Log
  description = "AcrPull for the Fixi ACI managed identity"
}

# -----------------------------------------------------------------------------
# Key Vault Secrets User on the target vault
#
# This role allows `get` and `list` on secrets but NOT `set`, `delete`,
# or `purge`. It's the minimum needed for Fixi to read its runtime
# secrets at startup.
# -----------------------------------------------------------------------------

resource "azurerm_role_assignment" "kv_secrets_user" {
  scope                = var.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.this.principal_id

  description = "Key Vault Secrets User for the Fixi ACI managed identity"
}

# -----------------------------------------------------------------------------
# Additional (optional) human readers for debugging
#
# `for_each` over a set keeps assignments idempotent even if the list is
# reordered in tfvars.
# -----------------------------------------------------------------------------

resource "azurerm_role_assignment" "kv_secrets_user_additional" {
  for_each = toset(var.additional_kv_reader_object_ids)

  scope                = var.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = each.value

  description = "Extra Key Vault Secrets User grant for human debugger"
}
