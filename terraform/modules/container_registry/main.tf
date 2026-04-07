###############################################################################
# modules/container_registry/main.tf
#
# Azure Container Registry (ACR).
#
# Design notes:
#   - `admin_enabled = false` on purpose. The admin user is a long-lived
#     username/password pair that bypasses RBAC. We want AcrPull via
#     managed identity, not admin creds. If CI/CD needs to push, grant
#     AcrPush to the pipeline's service principal instead.
#   - `public_network_access_enabled = true` is kept because Basic SKU
#     does not support private endpoints. For a hardened prod deployment,
#     upgrade to Premium and attach a private endpoint inside the VNet.
###############################################################################

resource "azurerm_container_registry" "this" {
  name                = var.acr_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku
  admin_enabled       = false

  # Explicit so reviewers can see the posture choice
  public_network_access_enabled = true

  tags = var.tags
}
