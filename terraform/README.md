# Fixi — Azure Terraform Skeleton

Infrastructure-as-code for deploying the Fixi autonomous issue-resolution agent on Microsoft Azure.

This is a **documentation-grade skeleton**. It is designed to be read, reviewed, and analyzed. It follows Azure Cloud Adoption Framework naming, uses managed identity + Key Vault + RBAC end-to-end, and is structured as a small set of composable modules. Test in a sandbox before applying to production.

---

## Table of contents

1. [Architecture](#architecture)
2. [Module layout](#module-layout)
3. [Prerequisites](#prerequisites)
4. [Setup](#setup)
5. [Usage](#usage)
6. [Variables](#variables)
7. [Outputs](#outputs)
8. [Cost estimate](#cost-estimate)
9. [Security notes](#security-notes)
10. [Disclaimer](#disclaimer)

---

## Architecture

```
+-----------------------------------------------------------------+
|                     Resource Group                              |
|                rg-fixi-<env>-<region>                           |
|                                                                 |
|  +-------------------+         +----------------------------+   |
|  |   Log Analytics   | <-----> |   Azure Container          |   |
|  |   Workspace       |  logs   |   Instance (Fixi)          |   |
|  |  log-fixi-<env>   |         |   aci-fixi-<env>           |   |
|  +-------------------+         |                            |   |
|                                |  [user-assigned identity]  |   |
|                                |  id-fixi-<env>             |   |
|                                +-------+----------+---------+   |
|                                        |          |             |
|                          AcrPull       |          |  KV Secrets |
|                                        v          v             |
|  +------------------------+   +-------------------------+       |
|  | Azure Container        |   | Azure Key Vault         |       |
|  | Registry (ACR)         |   | kv-fixi-<env>-<suffix>  |       |
|  | acrfixi<env><suffix>   |   |  - anthropic-api-key    |       |
|  +------------------------+   |  - ado-pat              |       |
|                               |  - github-pat           |       |
|                               +-------------------------+       |
|                                                                 |
|  +---------------------------------------------------------+    |
|  | Virtual Network  vnet-fixi-<env>-<region>               |    |
|  |                                                         |    |
|  |   +-------------------------------------------------+   |    |
|  |   | Subnet  snet-fixi-aci-<env>  (delegated to ACI) |   |    |
|  |   |                                                 |   |    |
|  |   |   [NSG: deny all inbound]                       |   |    |
|  |   +-------------------------------------------------+   |    |
|  +---------------------------------------------------------+    |
+-----------------------------------------------------------------+

           Inbound: none. Fixi is invoked by pushing work
                    items to its queue, not via HTTP.

           Outbound: Azure DevOps, GitHub, Anthropic API,
                    Azure management plane (for MI / KV).
```

### Data flow

1. **Image build**: CI/CD builds a Fixi container image and pushes it to the ACR.
2. **Deploy**: Terraform applies this module. The ACI pulls the image using its managed identity.
3. **Startup**: The container boots and reads its secrets from Key Vault via the same managed identity (using `DefaultAzureCredential`).
4. **Work intake**: A ticket source (Azure DevOps board, GitHub issue, or internal queue) produces a new task. Fixi polls and picks it up.
5. **Execution**: Fixi classifies, analyses, fixes, runs tests, opens a PR. All outbound traffic goes through the default ACI egress route.
6. **Telemetry**: stdout/stderr stream to the Log Analytics workspace for Kusto queries and alerting.

---

## Module layout

| Path | Purpose |
|------|---------|
| `main.tf` | Root — provider config, resource group, module wiring |
| `variables.tf` | All input variables |
| `locals.tf` | Computed names, tag merging, random suffixes |
| `outputs.tf` | Root outputs |
| `versions.tf` | Terraform + provider version pins, backend stub |
| `modules/networking/` | VNet, ACI-delegated subnet, NSG |
| `modules/container_registry/` | Azure Container Registry (Basic SKU) |
| `modules/managed_identity/` | UAMI + AcrPull + KV Secrets User RBAC |
| `modules/key_vault/` | Key Vault (RBAC mode) + secret placeholders |
| `modules/container_instance/` | Fixi ACI — secrets, networking, diagnostics |
| `environments/dev.tfvars` | Example values for `dev` |
| `environments/prod.tfvars` | Example values for `prod` |

---

## Prerequisites

- **Azure CLI** >= 2.55 (for `az login` and manual secret writes)
- **Terraform** >= 1.6.0
- An **Azure subscription** with permissions to create:
  - Resource groups
  - Virtual networks and NSGs
  - Azure Container Registry
  - Azure Container Instances
  - Azure Key Vault (with RBAC authorization)
  - User-assigned managed identities
  - Role assignments at the subscription or resource-group scope
- Optional but recommended: an **Azure Storage Account** to hold remote state (see `versions.tf`)

---

## Setup

### 1. Authenticate

```bash
az login
az account set --subscription "<your-subscription-name-or-id>"
```

### 2. (Optional) Prepare remote state

For team use, create a storage account outside this module and uncomment the `backend "azurerm"` block in `versions.tf`. A one-liner:

```bash
az group create -n rg-tfstate-prod-eastus2 -l eastus2
az storage account create \
  -n sttfstatefixiprod \
  -g rg-tfstate-prod-eastus2 \
  -l eastus2 \
  --sku Standard_LRS \
  --encryption-services blob
az storage container create -n tfstate --account-name sttfstatefixiprod
```

### 3. Create a tfvars file

Copy `environments/dev.tfvars` to something like `dev.auto.tfvars` (or pass it via `-var-file`) and fill in:

- `container_image` — the ACR image tag you want to run
- `anthropic_api_key_secret_id`, `ado_pat_secret_id`, `github_pat_secret_id` — see step 5

### 4. First apply (bootstrap)

```bash
terraform init
terraform plan  -var-file=environments/dev.tfvars
terraform apply -var-file=environments/dev.tfvars
```

The first apply creates the Key Vault with empty secret placeholders (value `REPLACE_ME`) and all supporting infrastructure.

### 5. Populate secrets

After the first apply, write the real secret values out-of-band:

```bash
VAULT_NAME=$(terraform output -raw key_vault_name)

az keyvault secret set --vault-name "$VAULT_NAME" --name anthropic-api-key --value "<real-value>"
az keyvault secret set --vault-name "$VAULT_NAME" --name ado-pat           --value "<real-value>"
az keyvault secret set --vault-name "$VAULT_NAME" --name github-pat        --value "<real-value>"
```

Terraform's `ignore_changes` on secret values means subsequent applies will not overwrite them.

### 6. Second apply (runtime)

Re-run `terraform apply`. This time the container instance module reads the real secret values and injects them into the ACI container environment.

---

## Usage

```bash
# Plan
terraform plan -var-file=environments/dev.tfvars

# Apply
terraform apply -var-file=environments/dev.tfvars

# Inspect running Fixi logs (once ACI is running)
WORKSPACE_ID=$(terraform output -raw log_analytics_workspace_id)
az monitor log-analytics query \
  --workspace "$WORKSPACE_ID" \
  --analytics-query 'ContainerInstanceLog_CL | where ContainerName_s == "fixi" | order by TimeGenerated desc | take 100'

# Destroy (dev only — purge protection on Key Vault prevents full teardown in prod)
terraform destroy -var-file=environments/dev.tfvars
```

---

## Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `project` | string | `"fixi"` | Short project code used in every resource name |
| `environment` | string | — | One of `dev`, `staging`, `prod` |
| `location` | string | `"eastus2"` | Azure region |
| `location_short` | string | `"eus2"` | Short code used in names (reserved) |
| `tags` | map(string) | see `variables.tf` | Base tags merged with computed tags |
| `vnet_address_space` | list(string) | `["10.40.0.0/16"]` | CIDR blocks for the VNet |
| `aci_subnet_prefix` | string | `"10.40.1.0/24"` | CIDR for the ACI delegated subnet |
| `container_image` | string | — | Image and tag inside the ACR, e.g. `fixi:1.0.0` |
| `container_cpu` | number | `1.0` | vCPU allocated to the container |
| `container_memory_gb` | number | `2.0` | Memory (GiB) allocated to the container |
| `anthropic_api_key_secret_id` | string (sensitive) | — | Key Vault secret URI for the Anthropic API key |
| `ado_pat_secret_id` | string (sensitive) | — | Key Vault secret URI for the Azure DevOps PAT |
| `github_pat_secret_id` | string (sensitive) | — | Key Vault secret URI for the GitHub PAT |
| `log_retention_days` | number | `30` | Log Analytics retention, 30-730 |
| `additional_kv_reader_object_ids` | list(string) | `[]` | Extra AAD object IDs to grant KV Secrets User |

---

## Outputs

| Output | Sensitive | Description |
|--------|-----------|-------------|
| `resource_group_name` | no | Name of the RG holding Fixi |
| `resource_group_id` | no | Full resource ID of the RG |
| `vnet_id` | no | Full resource ID of the VNet |
| `aci_subnet_id` | no | Resource ID of the delegated subnet |
| `acr_login_server` | no | ACR login server FQDN |
| `acr_id` | no | Full resource ID of the ACR |
| `key_vault_name` | no | Name of the Fixi Key Vault |
| `key_vault_uri` | no | Base URI of the vault |
| `managed_identity_id` | no | Resource ID of the UAMI |
| `managed_identity_principal_id` | no | AAD object ID of the UAMI |
| `managed_identity_client_id` | no | Client ID of the UAMI (for `AZURE_CLIENT_ID`) |
| `aci_id` | no | Full resource ID of the ACI group |
| `aci_fqdn` | no | Internal FQDN of the ACI (not public) |
| `log_analytics_workspace_id` | no | Log Analytics workspace GUID |
| `log_analytics_workspace_resource_id` | no | Full resource ID of the workspace |
| `secret_references` | **yes** | Map of secret URIs consumed by Fixi |

---

## Cost estimate

Rough monthly cost for the **dev** environment (single ACI, Basic ACR, Standard KV). Prices vary by region; these figures use `eastus2` USD list prices as of Q1 2026.

| Resource | SKU / sizing | Approx. monthly USD |
|----------|--------------|---------------------|
| Resource Group | — | $0 |
| VNet + subnet + NSG | — | $0 |
| Azure Container Registry | Basic | ~$5 |
| Azure Container Instance | 0.5 vCPU, 1 GiB, always-on | ~$15 |
| Azure Key Vault | Standard, ~100 operations/day | <$1 |
| User-assigned Managed Identity | — | $0 |
| Log Analytics Workspace | Pay-as-you-go, ~1 GB/month | ~$2.50 |
| Public IP / egress | ~5 GB/month egress | ~$0.45 |
| **Total (dev)** | | **~$25-30/month** |

Production with 2 vCPU, 4 GiB, Standard ACR, 90-day log retention, and heavier Anthropic API traffic will land closer to **$150-250/month**, excluding the Anthropic API bill itself (which is usage-based and not Azure-billed).

> **Heads up**: If Fixi is restarted frequently (failed deploys, crash loops), the per-second ACI billing adds up fast. Keep an eye on the `restart_policy` and make sure your image is stable before leaving it unattended.

---

## Security notes

1. **RBAC authorization for Key Vault.** The legacy access-policy model is disabled. All access is granted via Azure AD roles (`Key Vault Secrets User`, `Key Vault Secrets Officer`). This integrates with PIM, conditional access, and audit logs natively.
2. **Secrets never logged.** Terraform outputs containing secret URIs are marked `sensitive = true`. Secret values are injected into the container via `secure_environment_variables`, which Azure encrypts at rest and redacts in `terraform show`.
3. **Minimal managed-identity scope.** The UAMI has `AcrPull` on exactly one ACR and `Key Vault Secrets User` on exactly one vault. It has **no** subscription-wide permissions.
4. **Purge protection.** Key Vault has soft-delete + purge protection enabled. A compromised operator cannot permanently wipe production secrets; they would need a 90-day window and control of a separate admin identity.
5. **Denied inbound.** The NSG attached to the ACI subnet denies all inbound traffic. Fixi has no exposed ingress — any work-item delivery is a pull, not a push.
6. **No `admin_enabled` on ACR.** The long-lived admin username/password is disabled. Only managed identities and AAD principals can pull/push.
7. **Placeholder secrets.** First apply creates `REPLACE_ME` placeholders so that operators have a self-documenting list of required secrets. `ignore_changes` ensures subsequent applies do not overwrite live values.
8. **No hardcoded identifiers.** Subscription IDs, tenant IDs, and principal IDs are discovered at plan time via `data` sources. The tfvars files do not contain any real secrets or tenant-specific data.

---

## Disclaimer

**This is a documentation-grade skeleton.** It is written to be clear and reviewable, not battle-tested in production.

Before applying to a real Azure environment:

1. Run `terraform validate` and `terraform fmt -recursive`.
2. Run `terraform plan` against a sandbox subscription and review every change.
3. Verify that the Key Vault bootstrap flow works in your tenant. The "Terraform principal writes placeholders" step assumes the principal running `terraform apply` has the ability to receive a `Key Vault Secrets Officer` role assignment — some tightly-locked tenants require this to be granted ahead of time by an AAD admin.
4. Add a remote backend (see `versions.tf`).
5. Wire this into a CI/CD pipeline so it never runs from a developer laptop in production.
6. Review the NSG rules. For a compliance-sensitive deployment, replace the permissive default egress with an explicit allowlist enforced via Azure Firewall.

Questions or issues: open a ticket against the Fixi platform team.
