###############################################################################
# outputs.tf
#
# Root-module outputs. Consumed by:
#   - CI/CD pipelines that need to know the ACR login server to docker-push
#   - Runbooks that need to know the ACI FQDN / managed identity principal
#   - Tests that verify deployment
#
# Nothing secret is emitted in plaintext. Secret URIs are marked
# `sensitive = true` so they don't land in CI console logs.
###############################################################################

# -----------------------------------------------------------------------------
# Resource group
# -----------------------------------------------------------------------------

output "resource_group_name" {
  description = "Name of the resource group holding every Fixi resource."
  value       = azurerm_resource_group.this.name
}

output "resource_group_id" {
  description = "Full resource ID of the Fixi resource group."
  value       = azurerm_resource_group.this.id
}

# -----------------------------------------------------------------------------
# Networking
# -----------------------------------------------------------------------------

output "vnet_id" {
  description = "Full resource ID of the Fixi VNet."
  value       = module.networking.vnet_id
}

output "aci_subnet_id" {
  description = "Resource ID of the delegated subnet where the ACI runs."
  value       = module.networking.aci_subnet_id
}

# -----------------------------------------------------------------------------
# Container Registry
# -----------------------------------------------------------------------------

output "acr_login_server" {
  description = "Login server URL for the ACR (e.g. acrfixidevabc123.azurecr.io). Used by `docker login` and by ACI to pull images."
  value       = module.container_registry.acr_login_server
}

output "acr_id" {
  description = "Full resource ID of the Azure Container Registry."
  value       = module.container_registry.acr_id
}

# -----------------------------------------------------------------------------
# Key Vault
# -----------------------------------------------------------------------------

output "key_vault_name" {
  description = "Name of the Key Vault holding Fixi secrets."
  value       = module.key_vault.key_vault_name
}

output "key_vault_uri" {
  description = "Base URI of the Key Vault (used to construct secret URIs)."
  value       = module.key_vault.key_vault_uri
}

# -----------------------------------------------------------------------------
# Managed Identity
# -----------------------------------------------------------------------------

output "managed_identity_id" {
  description = "Full resource ID of the user-assigned managed identity bound to the ACI."
  value       = module.managed_identity.identity_id
}

output "managed_identity_principal_id" {
  description = "AAD object ID of the managed identity. Use this when granting external RBAC (e.g. Azure DevOps)."
  value       = module.managed_identity.principal_id
}

output "managed_identity_client_id" {
  description = "Client ID of the managed identity. Use this as AZURE_CLIENT_ID inside the container."
  value       = module.managed_identity.client_id
}

# -----------------------------------------------------------------------------
# Container Instance
# -----------------------------------------------------------------------------

output "aci_id" {
  description = "Full resource ID of the Fixi container group."
  value       = module.container_instance.aci_id
}

output "aci_fqdn" {
  description = "Internal FQDN of the Fixi container group. Not publicly routable — NSG blocks all inbound."
  value       = module.container_instance.aci_fqdn
}

# -----------------------------------------------------------------------------
# Log Analytics
# -----------------------------------------------------------------------------

output "log_analytics_workspace_id" {
  description = "Workspace ID (GUID) for the Log Analytics instance. Use in Kusto queries and dashboards."
  value       = azurerm_log_analytics_workspace.this.workspace_id
}

output "log_analytics_workspace_resource_id" {
  description = "Full Azure resource ID of the Log Analytics workspace."
  value       = azurerm_log_analytics_workspace.this.id
}

# -----------------------------------------------------------------------------
# Secret references (sensitive — do not print in CI logs)
# -----------------------------------------------------------------------------

output "secret_references" {
  description = "Map of Key Vault secret URIs consumed by Fixi. Sensitive."
  value = {
    anthropic_api_key = var.anthropic_api_key_secret_id
    ado_pat           = var.ado_pat_secret_id
    github_pat        = var.github_pat_secret_id
  }
  sensitive = true
}
