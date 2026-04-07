###############################################################################
# modules/managed_identity/outputs.tf
###############################################################################

output "identity_id" {
  description = "Full resource ID of the user-assigned managed identity."
  value       = azurerm_user_assigned_identity.this.id
}

output "principal_id" {
  description = "AAD object ID (principal ID) of the managed identity. Used when creating external RBAC."
  value       = azurerm_user_assigned_identity.this.principal_id
}

output "client_id" {
  description = "Client ID (application ID) of the managed identity. Injected as AZURE_CLIENT_ID env var inside the container."
  value       = azurerm_user_assigned_identity.this.client_id
}

output "tenant_id" {
  description = "Azure AD tenant ID the identity belongs to."
  value       = azurerm_user_assigned_identity.this.tenant_id
}
