# Fixi Terraform Tests

Two test suites for the Fixi infrastructure:

## 1. Native Terraform Tests (no Go required)

```bash
cd terraform/
terraform init
terraform test
```

Runs `tests/naming.tftest.hcl` — validates naming conventions and variable constraints via `terraform plan`.

**Requires:** Terraform >= 1.6.0, Azure credentials (for plan).

## 2. Terratest (Go, no Azure required)

```bash
cd terraform/test/
go mod tidy          # First time only — downloads dependencies
go test -v -timeout 10m
```

Validates without Azure credentials:
- Module file structure (all 5 modules have main/variables/outputs)
- No hardcoded secrets in .tf/.tfvars files
- No real Key Vault URIs in tfvars (secrets managed internally)
- No `timestamp()` in tags (causes drift)
- No unused providers in versions.tf
- `terraform init` succeeds (provider download)
- `terraform validate` passes (syntax + consistency)
- `terraform fmt -check` passes (formatting)

**Requires:** Go >= 1.22, Terraform >= 1.6.0. No Azure credentials needed.

## Quick start (CI/CD)

```yaml
# GitHub Actions example
- name: Terraform Validate
  run: |
    cd terraform/test
    go mod tidy
    go test -v -timeout 10m -run "TestTerraformInit|TestTerraformValidate|TestTerraformFmt"

- name: Security Checks
  run: |
    cd terraform/test
    go test -v -run "TestNoHardcodedSecrets|TestTfvarsNoRealSecretURIs"
```
