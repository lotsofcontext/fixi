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

  validation {
    condition     = can(regex("^[a-z0-9]+$", var.location))
    error_message = "location must be a valid Azure region short name (lowercase alphanumeric, no dashes or spaces)."
  }
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
  description = "Container image tag Fixi should run. Expected format: <repo>:<tag>. The ACR login server is prepended automatically — do NOT include it here."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9._/-]+:[a-zA-Z0-9._-]+$", var.container_image))
    error_message = "container_image must be in format 'repo:tag' (e.g. fixi:1.4.2). Do NOT include the registry server."
  }
}

variable "container_cpu" {
  description = "vCPU allocated to the Fixi container. ACI minimum 0.5."
  type        = number
  default     = 1.0

  validation {
    condition     = var.container_cpu >= 0.5
    error_message = "container_cpu must be at least 0.5 (ACI minimum)."
  }
}

variable "container_memory_gb" {
  description = "Memory (in GiB) allocated to the Fixi container."
  type        = number
  default     = 2.0

  validation {
    condition     = var.container_memory_gb >= 0.5
    error_message = "container_memory_gb must be at least 0.5 (ACI minimum)."
  }
}

# -----------------------------------------------------------------------------
# Secrets
#
# Secret VALUES are never passed through Terraform variables. They are:
#   1. Created as "REPLACE_ME" placeholders by the key_vault module
#   2. Populated out-of-band via `az keyvault secret set`
#   3. Read at apply time by the container_instance module's data sources
#
# The secret names are fixed: anthropic-api-key, ado-pat, github-pat.
# The key_vault_id is passed directly between modules (no URI parsing).
# -----------------------------------------------------------------------------

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
