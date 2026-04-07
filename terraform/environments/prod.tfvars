###############################################################################
# environments/prod.tfvars
#
# Example values for the `prod` environment. Production deploys should
# use a remote backend (see versions.tf) and should NOT be run from a
# developer laptop — use a pipeline service principal.
#
# Usage:
#   terraform workspace select prod
#   terraform plan  -var-file=environments/prod.tfvars
#   terraform apply -var-file=environments/prod.tfvars
###############################################################################

project     = "fixi"
environment = "prod"
location    = "eastus2"

tags = {
  product     = "fixi"
  owner       = "platform-engineering"
  cost_center = "production"
  managed_by  = "terraform"
  data_class  = "confidential"
  sla         = "business-hours"
}

# Production VNet — reserve 10.41.0.0/16 so dev and prod can peer later
vnet_address_space = ["10.41.0.0/16"]
aci_subnet_prefix  = "10.41.1.0/24"

# Production runtime sizing — larger so we can run the agent on several
# repos concurrently
container_image     = "fixi:1.0.0"
container_cpu       = 2.0
container_memory_gb = 4.0

# Secrets — these URIs must point at the PRODUCTION Key Vault and must
# be populated out-of-band (see README.md §Setup for the bootstrap
# procedure).
anthropic_api_key_secret_id = "https://kv-fixi-prod-EXAMPLE.vault.azure.net/secrets/anthropic-api-key"
ado_pat_secret_id           = "https://kv-fixi-prod-EXAMPLE.vault.azure.net/secrets/ado-pat"
github_pat_secret_id        = "https://kv-fixi-prod-EXAMPLE.vault.azure.net/secrets/github-pat"

# Longer retention for compliance / audit requirements
log_retention_days = 90

# On-call engineers get debug access via this list. Keep it short.
additional_kv_reader_object_ids = [
  # "00000000-0000-0000-0000-000000000000",
]
