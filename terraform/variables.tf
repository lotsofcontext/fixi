###############################################################################
# variables.tf
#
# All input variables for the Fixi root module.
#
# Conventions:
#   - Variables with no default MUST be set via a .tfvars file.
#   - Variables with a default can be overridden per-environment.
#   - Every variable has a `description` and, where it makes sense, a
#     `validation` block to fail early on typos.
###############################################################################

# -----------------------------------------------------------------------------
# Project identity
# -----------------------------------------------------------------------------

variable "project" {
  description = "Short project code used in all resource names. Keep it <=6 chars, lowercase, no dashes."
  type        = string
  default     = "fixi"

  validation {
    condition     = can(regex("^[a-z0-9]{2,6}$", var.project))
    error_message = "project must be 2-6 lowercase alphanumeric characters."
  }
}

variable "environment" {
  description = "Deployment environment. Must be one of: dev, staging, prod."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "location" {
  description = "Azure region where all resources will be deployed. Short name (e.g. eastus2)."
  type        = string
  default     = "eastus2"
}

variable "location_short" {
  description = "Short code for the region used in resource names. Defaults derived in locals if empty."
  type        = string
  default     = "eus2"
}

# -----------------------------------------------------------------------------
# Tagging
# -----------------------------------------------------------------------------

variable "tags" {
  description = "Base tags applied to every taggable resource. Merged with computed tags in locals.tf."
  type        = map(string)
  default = {
    product     = "fixi"
    owner       = "platform-engineering"
    cost_center = "r-and-d"
    managed_by  = "terraform"
  }
}

# -----------------------------------------------------------------------------
# Networking
# -----------------------------------------------------------------------------

variable "vnet_address_space" {
  description = "CIDR block for the VNet. Must not overlap with on-prem or peered networks."
  type        = list(string)
  default     = ["10.40.0.0/16"]
}

variable "aci_subnet_prefix" {
  description = "CIDR prefix for the ACI delegated subnet. Must fit inside vnet_address_space."
  type        = string
  default     = "10.40.1.0/24"
}

# -----------------------------------------------------------------------------
# Container image
# -----------------------------------------------------------------------------

variable "container_image" {
  description = "Container image tag Fixi should run. Expected format: <repo>:<tag>. The repo is prefixed with the ACR login server at runtime."
  type        = string
  # Example value injected from pipeline, not defaulted here to force explicit choice:
  # container_image = "fixi:1.4.2"
}

variable "container_cpu" {
  description = "vCPU allocated to the Fixi container. ACI minimum 0.5."
  type        = number
  default     = 1.0
}

variable "container_memory_gb" {
  description = "Memory (in GiB) allocated to the Fixi container."
  type        = number
  default     = 2.0
}

# -----------------------------------------------------------------------------
# Secrets (Key Vault secret URIs)
#
# These are NOT the secret values — they are URIs to secrets that already
# exist in the Key Vault created by this module. The actual values are
# written into Key Vault out-of-band (e.g. via `az keyvault secret set`) so
# that Terraform state never touches them.
# -----------------------------------------------------------------------------

variable "anthropic_api_key_secret_id" {
  description = "Full Key Vault secret URI for the Anthropic API key. Example: https://kv-fixi-dev-xxxx.vault.azure.net/secrets/anthropic-api-key"
  type        = string
  sensitive   = true
}

variable "ado_pat_secret_id" {
  description = "Full Key Vault secret URI for the Azure DevOps Personal Access Token."
  type        = string
  sensitive   = true
}

variable "github_pat_secret_id" {
  description = "Full Key Vault secret URI for the GitHub Personal Access Token."
  type        = string
  sensitive   = true
}

# -----------------------------------------------------------------------------
# Observability
# -----------------------------------------------------------------------------

variable "log_retention_days" {
  description = "Retention in days for the Log Analytics workspace that ingests ACI container logs."
  type        = number
  default     = 30

  validation {
    condition     = var.log_retention_days >= 30 && var.log_retention_days <= 730
    error_message = "log_retention_days must be between 30 and 730 (Azure Log Analytics limits)."
  }
}

# -----------------------------------------------------------------------------
# RBAC / identity
# -----------------------------------------------------------------------------

variable "additional_kv_reader_object_ids" {
  description = "Optional list of AAD object IDs (users, groups, or SPs) that should also receive 'Key Vault Secrets User' on the created vault. Useful for developers who need to debug the running agent."
  type        = list(string)
  default     = []
}
