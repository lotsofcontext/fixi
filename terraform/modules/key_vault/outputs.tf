###############################################################################
# modules/key_vault/outputs.tf
###############################################################################

output "key_vault_id" {
  description = "Full resource ID of the Key Vault."
  value       = azurerm_key_vault.this.id
}

output "key_vault_name" {
  description = "Name of the Key Vault."
  value       = azurerm_key_vault.this.name
}

output "key_vault_uri" {
  description = "Base URI of the Key Vault (https://<name>.vault.azure.net/)."
  value       = azurerm_key_vault.this.vault_uri
}

output "placeholder_secret_names" {
  description = "Names of the pre-created secret placeholders that Fixi expects to find populated before startup."
  value       = [for s in azurerm_key_vault_secret.placeholders : s.name]
}
