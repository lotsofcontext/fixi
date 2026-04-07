###############################################################################
# modules/networking/outputs.tf
###############################################################################

output "vnet_id" {
  description = "Resource ID of the VNet."
  value       = azurerm_virtual_network.this.id
}

output "vnet_name" {
  description = "Name of the VNet."
  value       = azurerm_virtual_network.this.name
}

output "aci_subnet_id" {
  description = "Resource ID of the delegated ACI subnet."
  value       = azurerm_subnet.aci.id
}

output "nsg_id" {
  description = "Resource ID of the NSG attached to the ACI subnet."
  value       = azurerm_network_security_group.this.id
}
