###############################################################################
# modules/networking/variables.tf
###############################################################################

variable "resource_group_name" {
  description = "Name of the resource group that will contain the VNet, subnet, and NSG."
  type        = string
}

variable "location" {
  description = "Azure region for all networking resources."
  type        = string
}

variable "vnet_name" {
  description = "Name of the virtual network."
  type        = string
}

variable "vnet_address_space" {
  description = "CIDR blocks assigned to the VNet."
  type        = list(string)
}

variable "aci_subnet_name" {
  description = "Name of the subnet delegated to Azure Container Instances."
  type        = string
}

variable "aci_subnet_prefix" {
  description = "CIDR prefix for the ACI subnet. Must be inside vnet_address_space."
  type        = string
}

variable "nsg_name" {
  description = "Name of the NSG attached to the ACI subnet."
  type        = string
}

variable "tags" {
  description = "Tags applied to every resource in this module."
  type        = map(string)
  default     = {}
}
