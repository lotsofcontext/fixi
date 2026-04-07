###############################################################################
# modules/container_instance/variables.tf
###############################################################################

variable "resource_group_name" {
  description = "Resource group that will contain the ACI."
  type        = string
}

variable "location" {
  description = "Azure region for the ACI."
  type        = string
}

variable "aci_name" {
  description = "Name of the Azure Container Instance group."
  type        = string
}

variable "cpu_cores" {
  description = "vCPU count allocated to the container."
  type        = number
  default     = 1.0
}

variable "memory_gb" {
  description = "Memory (GiB) allocated to the container."
  type        = number
  default     = 2.0
}

variable "acr_login_server" {
  description = "ACR login server FQDN, e.g. acrfixidevabc123.azurecr.io."
  type        = string
}

variable "container_image" {
  description = "Image and tag within the ACR, e.g. fixi:1.4.2. The ACR login server is prepended automatically."
  type        = string
}

variable "managed_identity_id" {
  description = "Full resource ID of the user-assigned managed identity to attach to the container group."
  type        = string
}

variable "subnet_id" {
  description = "Full resource ID of the ACI-delegated subnet."
  type        = string
}

variable "anthropic_api_key_secret_id" {
  description = "Key Vault secret URI for the Anthropic API key."
  type        = string
  sensitive   = true
}

variable "ado_pat_secret_id" {
  description = "Key Vault secret URI for the Azure DevOps PAT."
  type        = string
  sensitive   = true
}

variable "github_pat_secret_id" {
  description = "Key Vault secret URI for the GitHub PAT."
  type        = string
  sensitive   = true
}

variable "log_analytics_workspace_id" {
  description = "Workspace ID (GUID) of the Log Analytics workspace that will ingest container logs."
  type        = string
}

variable "log_analytics_workspace_key" {
  description = "Primary shared key for the Log Analytics workspace. Used by ACI diagnostics."
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Tags applied to the container group."
  type        = map(string)
  default     = {}
}
