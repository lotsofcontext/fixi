###############################################################################
# main.tf
#
# Root module that wires together all child modules into the full Fixi
# runtime environment on Azure.
#
# High-level flow:
#
#   1. Configure azurerm provider
#   2. Read current subscription/tenant context (for RBAC assignments)
#   3. Create the resource group
#   4. Deploy networking (VNet + subnet + NSG)
#   5. Deploy Container Registry (ACR)
#   6. Deploy managed identity + role assignments (ACR pull, KV secrets user)
#   7. Deploy Key Vault and pre-create secret placeholders
#   8. Deploy Log Analytics workspace
#   9. Deploy Azure Container Instance running the Fixi image
#
# Each block below is documented with the reason it exists, not just what
# it does. The "why" is what makes this readable IaC.
###############################################################################

# -----------------------------------------------------------------------------
# Provider configuration
#
# The `features {}` block is mandatory for azurerm 3.x. We explicitly set
# behaviour for resources that have safety switches so the defaults are
# explicit and reviewable:
#
#   - key_vault: purge_soft_delete_on_destroy=false protects us from
#     accidentally wiping a vault on `terraform destroy`. To genuinely
#     delete it, operators must purge manually via `az keyvault purge`.
#   - resource_group: prevent_deletion_if_contains_resources=true stops
#     `terraform destroy` from nuking a whole RG if some drift has
#     introduced resources Terraform doesn't know about.
# -----------------------------------------------------------------------------

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }

    resource_group {
      prevent_deletion_if_contains_resources = true
    }
  }
}

# -----------------------------------------------------------------------------
# Context data sources
#
# We look up the current subscription and client config to:
#   - Tag resources with subscription ID (useful in multi-sub orgs)
#   - Grant the Terraform runner temporary KV access so we can pre-create
#     secret placeholders during `apply` (removed after first run in prod)
# -----------------------------------------------------------------------------

data "azurerm_client_config" "current" {}

data "azurerm_subscription" "current" {}

# -----------------------------------------------------------------------------
# Resource Group
#
# Single RG per environment keeps RBAC simple: one "Contributor" grant on
# the RG lets an operator manage everything Fixi owns without leaking
# permissions to unrelated workloads.
# -----------------------------------------------------------------------------

resource "azurerm_resource_group" "this" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.common_tags
}

# -----------------------------------------------------------------------------
# Networking module
#
# Creates the VNet, the ACI delegated subnet, and the NSG that closes off
# all inbound traffic. Fixi is invoked by pushing work items to its queue;
# it does not expose an HTTP ingress.
# -----------------------------------------------------------------------------

module "networking" {
  source = "./modules/networking"

  resource_group_name = azurerm_resource_group.this.name
  location            = var.location

  vnet_name          = local.vnet_name
  vnet_address_space = var.vnet_address_space

  aci_subnet_name   = local.aci_subnet_name
  aci_subnet_prefix = var.aci_subnet_prefix

  nsg_name = local.nsg_name

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Container Registry module
#
# Basic SKU is sufficient for a single-image workload. If we start shipping
# multi-arch builds or need geo-replication for regional disaster recovery,
# bump the sku to "Premium" in the module inputs.
# -----------------------------------------------------------------------------

module "container_registry" {
  source = "./modules/container_registry"

  resource_group_name = azurerm_resource_group.this.name
  location            = var.location

  acr_name = local.acr_name
  sku      = "Basic"

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Managed Identity module
#
# User-assigned (not system-assigned) so that we can pre-grant RBAC BEFORE
# the ACI exists. System-assigned identities don't materialise until the
# parent resource is created, which causes a chicken-and-egg for AcrPull.
# -----------------------------------------------------------------------------

module "managed_identity" {
  source = "./modules/managed_identity"

  resource_group_name = azurerm_resource_group.this.name
  location            = var.location

  name = local.managed_identity_name

  # Role assignments are done INSIDE the module so that destroying the
  # module cleanly removes the bindings.
  acr_id                          = module.container_registry.acr_id
  key_vault_id                    = module.key_vault.key_vault_id
  additional_kv_reader_object_ids = var.additional_kv_reader_object_ids

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Key Vault module
#
# Uses RBAC authorization (not the legacy access-policy model). The
# Terraform runner is granted "Key Vault Secrets Officer" so that this
# module can stand up secret placeholders; production operators should
# revoke this after first apply.
# -----------------------------------------------------------------------------

module "key_vault" {
  source = "./modules/key_vault"

  resource_group_name = azurerm_resource_group.this.name
  location            = var.location

  key_vault_name = local.key_vault_name
  tenant_id      = data.azurerm_client_config.current.tenant_id

  # The current principal (CI/CD SP or human running terraform) needs to be
  # able to write placeholder secrets.
  terraform_principal_object_id = data.azurerm_client_config.current.object_id

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Log Analytics workspace
#
# Kept inline (not in a module) because it's a single resource with no
# downstream fan-out. If we add App Insights or Sentinel in the future,
# refactor this into its own module.
# -----------------------------------------------------------------------------

resource "azurerm_log_analytics_workspace" "this" {
  name                = local.log_analytics_name
  location            = var.location
  resource_group_name = azurerm_resource_group.this.name

  sku               = "PerGB2018"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Container Instance module (Fixi runtime)
#
# Depends on the full chain: ACR (image), KV (secrets), MI (pull + read),
# networking (subnet), and Log Analytics (diagnostics). The explicit
# depends_on keeps Terraform from racing creation order on first apply.
# -----------------------------------------------------------------------------

module "container_instance" {
  source = "./modules/container_instance"

  resource_group_name = azurerm_resource_group.this.name
  location            = var.location

  aci_name = local.aci_name

  # Compute sizing
  cpu_cores = var.container_cpu
  memory_gb = var.container_memory_gb

  # Image
  acr_login_server = module.container_registry.acr_login_server
  container_image  = var.container_image

  # Identity
  managed_identity_id = module.managed_identity.identity_id

  # Networking
  subnet_id = module.networking.aci_subnet_id

  # Secret references (injected as env vars via Key Vault lookups)
  anthropic_api_key_secret_id = var.anthropic_api_key_secret_id
  ado_pat_secret_id           = var.ado_pat_secret_id
  github_pat_secret_id        = var.github_pat_secret_id

  # Observability
  log_analytics_workspace_id  = azurerm_log_analytics_workspace.this.workspace_id
  log_analytics_workspace_key = azurerm_log_analytics_workspace.this.primary_shared_key

  tags = local.common_tags

  depends_on = [
    module.networking,
    module.container_registry,
    module.managed_identity,
    module.key_vault,
    azurerm_log_analytics_workspace.this,
  ]
}
