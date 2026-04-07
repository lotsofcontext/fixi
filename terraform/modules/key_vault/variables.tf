###############################################################################
# modules/key_vault/variables.tf
###############################################################################

variable "resource_group_name" {
  description = "Resource group that will contain the Key Vault."
  type        = string
}

variable "location" {
  description = "Azure region for the Key Vault."
  type        = string
}

variable "key_vault_name" {
  description = "Globally-unique Key Vault name (3-24 chars, start with a letter, dashes allowed)."
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9-]{1,22}[a-zA-Z0-9]$", var.key_vault_name))
    error_message = "key_vault_name must be 3-24 chars, start with a letter, end alphanumeric, and contain only letters/digits/dashes."
  }
}

variable "tenant_id" {
  description = "Azure AD tenant ID that owns the vault."
  type        = string
}

variable "sku_name" {
  description = "Key Vault SKU. One of: standard, premium."
  type        = string
  default     = "standard"

  validation {
    condition     = contains(["standard", "premium"], var.sku_name)
    error_message = "sku_name must be standard or premium."
  }
}

variable "terraform_principal_object_id" {
  description = "AAD object ID of the principal running Terraform. Receives Key Vault Secrets Officer to create placeholder secrets."
  type        = string
}

variable "tags" {
  description = "Tags applied to the Key Vault and its secret placeholders."
  type        = map(string)
  default     = {}
}
