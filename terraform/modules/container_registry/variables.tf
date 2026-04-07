###############################################################################
# modules/container_registry/variables.tf
###############################################################################

variable "resource_group_name" {
  description = "Resource group that will hold the ACR."
  type        = string
}

variable "location" {
  description = "Azure region for the ACR."
  type        = string
}

variable "acr_name" {
  description = "Globally-unique ACR name (lowercase alphanumeric, 5-50 chars)."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{5,50}$", var.acr_name))
    error_message = "acr_name must be 5-50 lowercase alphanumeric characters."
  }
}

variable "sku" {
  description = "ACR SKU. One of: Basic, Standard, Premium."
  type        = string
  default     = "Basic"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.sku)
    error_message = "sku must be Basic, Standard, or Premium."
  }
}

variable "tags" {
  description = "Tags applied to the ACR."
  type        = map(string)
  default     = {}
}
