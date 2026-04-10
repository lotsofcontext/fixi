###############################################################################
# locals.tf
#
# Computed values. Centralising naming and tagging here means every module
# call is short and consistent, and any rename only happens in one place.
#
# Naming follows the Azure Cloud Adoption Framework (CAF):
#   https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-abbreviations
#
# Pattern:  <abbr>-<project>-<env>-<region>[-<suffix>]
# Example:  rg-fixi-dev-eastus2
#
# Two resources break the pattern because Azure forbids dashes/uppercase:
#   - ACR:       acr<project><env><random>
#   - Key Vault: kv-<project>-<env>-<random>   (dashes allowed, max 24 chars)
###############################################################################

locals {
  # ---------------------------------------------------------------------------
  # Name stem reused by every resource
  # ---------------------------------------------------------------------------
  name_stem = "${var.project}-${var.environment}-${var.location}"

  # ---------------------------------------------------------------------------
  # Fully-qualified resource names
  # ---------------------------------------------------------------------------
  resource_group_name   = "rg-${local.name_stem}"
  vnet_name             = "vnet-${local.name_stem}"
  aci_subnet_name       = "snet-${var.project}-aci-${var.environment}-${var.location}"
  nsg_name              = "nsg-${local.name_stem}"
  aci_name              = "aci-${local.name_stem}"
  log_analytics_name    = "log-${local.name_stem}"
  managed_identity_name = "id-${local.name_stem}"

  # ACR has strict naming rules (alphanumeric, 5-50 chars, no dashes, globally unique)
  acr_name = "acr${var.project}${var.environment}${random_string.acr_suffix.result}"

  # Key Vault: dashes allowed, 3-24 chars, globally unique, must start with a letter
  key_vault_name = substr("kv-${var.project}-${var.environment}-${random_string.kv_suffix.result}", 0, 24)

  # ---------------------------------------------------------------------------
  # Tag merging
  #
  # We layer tags like this:
  #   1. var.tags            — base tags passed in from .tfvars
  #   2. computed defaults   — environment + location + deploy timestamp
  #
  # The computed defaults win on collision so that callers can't accidentally
  # drift the `environment` tag.
  # ---------------------------------------------------------------------------
  # Note: `last_applied` was removed because `timestamp()` changes on
  # every plan, forcing a diff on ALL tagged resources even when nothing
  # changed. If deploy tracking is needed, inject it as a variable from
  # the CI/CD pipeline (e.g. -var="deploy_timestamp=2026-04-10T12:00:00Z").
  common_tags = merge(
    var.tags,
    {
      environment = var.environment
      location    = var.location
      terraform   = "true"
    }
  )

  # ---------------------------------------------------------------------------
  # Container image FQN (ACR login server is appended at runtime in main.tf)
  # ---------------------------------------------------------------------------
  # Nothing here yet — container_image is passed through verbatim and joined
  # with the ACR login server inside the container_instance module.
}

# ---------------------------------------------------------------------------
# Random suffixes for globally-unique resources.
#
# Declared here (not in a module) so the same suffix is stable across
# terraform runs as long as state is preserved. Deleting state will
# generate new names, which is the desired failure mode for disaster
# recovery drills.
# ---------------------------------------------------------------------------

resource "random_string" "acr_suffix" {
  length  = 6
  lower   = true
  upper   = false
  numeric = true
  special = false
}

resource "random_string" "kv_suffix" {
  length  = 6
  lower   = true
  upper   = false
  numeric = true
  special = false
}
