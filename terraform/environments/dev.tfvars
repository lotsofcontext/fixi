###############################################################################
# environments/dev.tfvars
#
# Example values for the `dev` environment. Copy to a real dev.tfvars
# (gitignored) before apply.
#
# Usage:
#   terraform plan  -var-file=environments/dev.tfvars
#   terraform apply -var-file=environments/dev.tfvars
###############################################################################

project     = "fixi"
environment = "dev"
location    = "eastus2"

# Ownership / accounting
tags = {
  product     = "fixi"
  owner       = "platform-engineering"
  cost_center = "r-and-d"
  managed_by  = "terraform"
  confidence  = "demo"
}

# Network — keep away from prod CIDR to ease peering later
vnet_address_space = ["10.40.0.0/16"]
aci_subnet_prefix  = "10.40.1.0/24"

# Runtime sizing: small, cheap, bursty
container_image     = "fixi:dev-latest"
container_cpu       = 0.5
container_memory_gb = 1.0

# Secrets — these URIs are examples. Replace with the real Key Vault
# secret URIs after the first apply populates the vault.
# The `{vault_name}` placeholder will be resolved by whoever is running
# the deploy; do NOT commit real URIs that embed live vault names if
# the Key Vault is public.
anthropic_api_key_secret_id = "https://kv-fixi-dev-EXAMPLE.vault.azure.net/secrets/anthropic-api-key"
ado_pat_secret_id           = "https://kv-fixi-dev-EXAMPLE.vault.azure.net/secrets/ado-pat"
github_pat_secret_id        = "https://kv-fixi-dev-EXAMPLE.vault.azure.net/secrets/github-pat"

# Observability — 30 days is the cheapest tier that still allows useful debugging
log_retention_days = 30

# Optional human reviewers (paste AAD object IDs of your platform team members)
additional_kv_reader_object_ids = [
  # "00000000-0000-0000-0000-000000000000",
]
