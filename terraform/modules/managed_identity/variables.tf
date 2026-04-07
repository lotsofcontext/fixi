###############################################################################
# modules/managed_identity/variables.tf
###############################################################################

variable "resource_group_name" {
  description = "Resource group that will contain the managed identity."
  type        = string
}

variable "location" {
  description = "Azure region for the managed identity."
  type        = string
}

variable "name" {
  description = "Name of the user-assigned managed identity."
  type        = string
}

variable "acr_id" {
  description = "Full resource ID of the ACR on which to grant AcrPull."
  type        = string
}

variable "key_vault_id" {
  description = "Full resource ID of the Key Vault on which to grant Key Vault Secrets User."
  type        = string
}

variable "additional_kv_reader_object_ids" {
  description = "Optional list of AAD object IDs that should also receive Key Vault Secrets User on the same vault."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags applied to the managed identity."
  type        = map(string)
  default     = {}
}
