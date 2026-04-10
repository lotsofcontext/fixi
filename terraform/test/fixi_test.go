// Package test contains Terratest-based tests for the Fixi Terraform infrastructure.
//
// These tests validate structure, conventions, and configuration WITHOUT
// requiring an Azure subscription. They use terraform validate (which checks
// syntax and internal consistency) and static analysis of the HCL files.
//
// Run:
//   cd terraform/test
//   go test -v -timeout 10m
//
// Prerequisites:
//   - Go >= 1.22
//   - Terraform >= 1.6.0 on PATH
//   - No Azure credentials needed
package test

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/gruntwork-io/terratest/modules/files"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// rootDir returns the absolute path to the terraform/ directory.
func rootDir(t *testing.T) string {
	t.Helper()
	dir, err := filepath.Abs("../")
	require.NoError(t, err)
	return dir
}

// ---------------------------------------------------------------------------
// Structure tests — verify the expected file layout
// ---------------------------------------------------------------------------

func TestModuleStructure(t *testing.T) {
	t.Parallel()
	root := rootDir(t)

	expectedRootFiles := []string{
		"main.tf",
		"variables.tf",
		"outputs.tf",
		"locals.tf",
		"versions.tf",
	}

	for _, f := range expectedRootFiles {
		path := filepath.Join(root, f)
		assert.True(t, files.FileExists(path), "Missing root file: %s", f)
	}

	expectedModules := []string{
		"networking",
		"container_registry",
		"managed_identity",
		"key_vault",
		"container_instance",
	}

	for _, mod := range expectedModules {
		modDir := filepath.Join(root, "modules", mod)
		assert.DirExists(t, modDir, "Missing module directory: modules/%s", mod)

		// Every module must have main.tf, variables.tf, outputs.tf
		for _, f := range []string{"main.tf", "variables.tf", "outputs.tf"} {
			path := filepath.Join(modDir, f)
			assert.True(t, files.FileExists(path),
				"Module %s missing %s", mod, f)
		}
	}
}

func TestEnvironmentFiles(t *testing.T) {
	t.Parallel()
	root := rootDir(t)

	for _, env := range []string{"dev", "prod"} {
		path := filepath.Join(root, "environments", env+".tfvars")
		assert.True(t, files.FileExists(path),
			"Missing environment file: environments/%s.tfvars", env)
	}
}

// ---------------------------------------------------------------------------
// Security tests — validate no secrets or sensitive patterns in code
// ---------------------------------------------------------------------------

func TestNoHardcodedSecrets(t *testing.T) {
	t.Parallel()
	root := rootDir(t)

	// Patterns that should NEVER appear in committed .tf or .tfvars files
	dangerousPatterns := []string{
		// Private keys (hex)
		"0x" + strings.Repeat("[0-9a-fA-F]", 64), // won't match literally, see below
		// Azure subscription IDs (real ones)
		// We check for UUIDs that look like real subscription IDs
	}
	_ = dangerousPatterns

	// Walk all .tf and .tfvars files looking for suspicious patterns
	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil || info.IsDir() {
			return err
		}

		ext := filepath.Ext(path)
		if ext != ".tf" && ext != ".tfvars" {
			return nil
		}

		content, err := os.ReadFile(path)
		if err != nil {
			return err
		}

		text := string(content)

		// No real API keys (sk-ant- is Anthropic's prefix)
		assert.NotContains(t, text, "sk-ant-",
			"Possible Anthropic API key in %s", path)

		// No Azure AD secrets (ey prefix = JWT tokens)
		for _, line := range strings.Split(text, "\n") {
			trimmed := strings.TrimSpace(line)
			// Skip comments
			if strings.HasPrefix(trimmed, "#") || strings.HasPrefix(trimmed, "//") {
				continue
			}
			assert.NotContains(t, trimmed, "eyJ",
				"Possible JWT/token in %s", path)
		}

		// No GitHub PATs (ghp_ prefix)
		assert.NotContains(t, text, "ghp_",
			"Possible GitHub PAT in %s", path)

		// No passwords in plaintext
		assert.NotContains(t, text, "password =",
			"Possible plaintext password in %s", path)

		return nil
	})
	require.NoError(t, err)
}

func TestTfvarsNoRealSecretURIs(t *testing.T) {
	t.Parallel()
	root := rootDir(t)

	// After refactoring, tfvars should NOT contain any vault.azure.net URIs
	// (secrets are resolved internally via key_vault_id)
	for _, env := range []string{"dev", "prod"} {
		path := filepath.Join(root, "environments", env+".tfvars")
		content, err := os.ReadFile(path)
		require.NoError(t, err)

		text := string(content)

		// Should not have active (non-commented) secret URI references
		for _, line := range strings.Split(text, "\n") {
			trimmed := strings.TrimSpace(line)
			if strings.HasPrefix(trimmed, "#") {
				continue // comments are OK
			}
			assert.NotContains(t, trimmed, "vault.azure.net",
				"%s.tfvars has an active Key Vault URI — secrets should be managed internally", env)
		}
	}
}

// ---------------------------------------------------------------------------
// Convention tests — validate naming and tagging standards
// ---------------------------------------------------------------------------

func TestNoTimestampInTags(t *testing.T) {
	t.Parallel()
	root := rootDir(t)

	// timestamp() in tags causes drift on every plan — it was removed
	content, err := os.ReadFile(filepath.Join(root, "locals.tf"))
	require.NoError(t, err)

	assert.NotContains(t, string(content), "timestamp()",
		"locals.tf should not use timestamp() in tags — causes perpetual drift")
}

func TestNoUnusedProviders(t *testing.T) {
	t.Parallel()
	root := rootDir(t)

	content, err := os.ReadFile(filepath.Join(root, "versions.tf"))
	require.NoError(t, err)

	// azuread was removed — should not be in required_providers
	assert.NotContains(t, string(content), "hashicorp/azuread",
		"versions.tf still references azuread provider which is not used")
}

// ---------------------------------------------------------------------------
// Terraform init + validate (requires terraform binary, no Azure auth)
// ---------------------------------------------------------------------------

func TestTerraformInit(t *testing.T) {
	t.Parallel()

	tfDir := rootDir(t)

	opts := &terraform.Options{
		TerraformDir: tfDir,

		// Don't pass any vars — init doesn't need them
		NoColor: true,
	}

	// Init downloads providers and validates the lock file
	terraform.Init(t, opts)
}

func TestTerraformValidate(t *testing.T) {
	t.Parallel()

	tfDir := rootDir(t)

	opts := &terraform.Options{
		TerraformDir: tfDir,
		NoColor:      true,
	}

	// Init first (required for validate)
	terraform.Init(t, opts)

	// Validate checks syntax, internal consistency, and type correctness
	// This does NOT require Azure credentials
	terraform.Validate(t, opts)
}

func TestTerraformFmt(t *testing.T) {
	t.Parallel()

	tfDir := rootDir(t)

	// Run terraform fmt -check -recursive to verify formatting
	opts := &terraform.Options{
		TerraformDir: tfDir,
		NoColor:      true,
	}

	// Init required for fmt to work on modules
	terraform.Init(t, opts)

	// terraform fmt -check returns non-zero if files are unformatted
	output := terraform.RunTerraformCommand(t, opts, "fmt", "-check", "-recursive", "-diff")
	assert.Empty(t, output,
		"Terraform files are not properly formatted. Run: terraform fmt -recursive")
}
