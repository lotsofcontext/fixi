###############################################################################
# versions.tf
#
# Terraform core + provider version pins.
#
# Rationale:
#   - Pin Terraform >= 1.6.0 because the root module uses features introduced
#     in 1.6 (validation blocks on locals, improved import blocks).
#   - Pin azurerm to the 3.110.x minor line: the v4 provider introduces
#     breaking changes around storage account schema and MI bindings that
#     we have not yet validated for Fixi.
#   - random is used to generate suffixes for globally-unique resources
#     (ACR, Key Vault).
#   - time is used for RBAC propagation waits (time_sleep) in the
#     key_vault module bootstrap flow.
#
# Upgrade policy:
#   - Minor-version bumps: review release notes, run `terraform plan` in dev,
#     then promote to prod.
#   - Major-version bumps: open a dedicated ticket; never bundle with
#     feature work.
###############################################################################

terraform {
  required_version = ">= 1.6.0, < 2.0.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }

    time = {
      source  = "hashicorp/time"
      version = "~> 0.12"
    }
  }

  # -------------------------------------------------------------------------
  # Remote state backend (commented intentionally).
  #
  # For production, uncomment the block below and create the storage account
  # out-of-band (chicken-and-egg problem — the state store cannot live in
  # the same state file that manages it).
  #
  # Recommended layout:
  #   - One storage account per environment (dev/staging/prod)
  #   - Container "tfstate"
  #   - Key "fixi.tfstate"
  #   - RBAC: only the CI/CD service principal has "Storage Blob Data Contributor"
  # -------------------------------------------------------------------------
  #
  # backend "azurerm" {
  #   resource_group_name  = "rg-tfstate-prod-eastus2"
  #   storage_account_name = "sttfstatefixiprod"
  #   container_name       = "tfstate"
  #   key                  = "fixi.tfstate"
  #   use_azuread_auth     = true
  # }
}
