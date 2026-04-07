###############################################################################
# modules/networking/main.tf
#
# VNet + delegated ACI subnet + lockdown NSG.
#
# Delegation detail:
#   Azure Container Instances deployed into a VNet require the subnet to
#   be delegated to "Microsoft.ContainerInstance/containerGroups". Without
#   that delegation the apply fails with a cryptic "subnet not delegated"
#   error that has confused many engineers before us.
###############################################################################

# -----------------------------------------------------------------------------
# Virtual Network
# -----------------------------------------------------------------------------

resource "azurerm_virtual_network" "this" {
  name                = var.vnet_name
  resource_group_name = var.resource_group_name
  location            = var.location
  address_space       = var.vnet_address_space

  tags = var.tags
}

# -----------------------------------------------------------------------------
# ACI delegated subnet
#
# `delegation` is what tells Azure that ACI is allowed to inject a NIC
# into this subnet. Without it, the container group will fail to create.
# -----------------------------------------------------------------------------

resource "azurerm_subnet" "aci" {
  name                 = var.aci_subnet_name
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = [var.aci_subnet_prefix]

  delegation {
    name = "aci-delegation"

    service_delegation {
      name = "Microsoft.ContainerInstance/containerGroups"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/action",
      ]
    }
  }
}

# -----------------------------------------------------------------------------
# Network Security Group
#
# Default posture: deny everything inbound from anywhere.
# ACI needs egress to:
#   - Azure DevOps (dev.azure.com, *.vsassets.io)    — fetch work items, push commits
#   - GitHub (api.github.com, github.com)            — non-ADO repos
#   - Anthropic API (api.anthropic.com)              — Claude inference
#   - Azure Management (management.azure.com)        — managed identity, Key Vault
#
# We rely on the default "AllowInternetOutBound" rule (priority 65001) for
# egress because the destination set is too broad to whitelist reliably
# and ACI does not support an egress web-firewall without AKS. In a
# tighter deployment, front this with an Azure Firewall and set the
# default egress rule to Deny.
# -----------------------------------------------------------------------------

resource "azurerm_network_security_group" "this" {
  name                = var.nsg_name
  resource_group_name = var.resource_group_name
  location            = var.location

  # Explicit inbound deny (priority 4096 — after any future allow rules).
  # The default AzureLoadBalancer rule stays intact so health probes work
  # if we ever front this with an internal LB.
  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = var.tags
}

# -----------------------------------------------------------------------------
# Associate NSG with the ACI subnet
# -----------------------------------------------------------------------------

resource "azurerm_subnet_network_security_group_association" "aci" {
  subnet_id                 = azurerm_subnet.aci.id
  network_security_group_id = azurerm_network_security_group.this.id
}
