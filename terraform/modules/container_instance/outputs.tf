###############################################################################
# modules/container_instance/outputs.tf
###############################################################################

output "aci_id" {
  description = "Full resource ID of the Azure Container Instance group."
  value       = azurerm_container_group.this.id
}

output "aci_name" {
  description = "Name of the Azure Container Instance group."
  value       = azurerm_container_group.this.name
}

output "aci_fqdn" {
  description = "Internal FQDN of the container group. Only routable from inside the VNet (or peered VNets)."
  value       = azurerm_container_group.this.fqdn
}

output "aci_ip_address" {
  description = "Private IP address assigned to the container group inside the ACI subnet."
  value       = azurerm_container_group.this.ip_address
}
