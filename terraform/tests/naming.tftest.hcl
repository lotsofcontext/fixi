###############################################################################
# tests/naming.tftest.hcl
#
# Basic Terraform test (TF 1.6+ native test framework) that validates
# the naming convention and variable constraints without hitting Azure.
#
# Run with:   terraform test
# From:       terraform/
###############################################################################

# --------------------------------------------------------------------------
# Test: resource names follow CAF convention
# --------------------------------------------------------------------------

run "validate_naming_conventions" {
  command = plan

  variables {
    project         = "fixi"
    environment     = "dev"
    location        = "eastus2"
    container_image = "fixi:test-latest"
  }

  assert {
    condition     = azurerm_resource_group.this.name == "rg-fixi-dev-eastus2"
    error_message = "Resource group name does not follow CAF pattern: rg-<project>-<env>-<region>"
  }

  assert {
    condition     = azurerm_log_analytics_workspace.this.name == "log-fixi-dev-eastus2"
    error_message = "Log Analytics workspace name does not follow CAF pattern."
  }
}

# --------------------------------------------------------------------------
# Test: invalid environment is rejected
# --------------------------------------------------------------------------

run "reject_invalid_environment" {
  command = plan

  variables {
    project         = "fixi"
    environment     = "qa"
    location        = "eastus2"
    container_image = "fixi:test"
  }

  expect_failures = [
    var.environment,
  ]
}

# --------------------------------------------------------------------------
# Test: invalid project name is rejected
# --------------------------------------------------------------------------

run "reject_invalid_project_name" {
  command = plan

  variables {
    project         = "FIXI-TOO-LONG"
    environment     = "dev"
    location        = "eastus2"
    container_image = "fixi:test"
  }

  expect_failures = [
    var.project,
  ]
}

# --------------------------------------------------------------------------
# Test: container_image without tag is rejected
# --------------------------------------------------------------------------

run "reject_image_without_tag" {
  command = plan

  variables {
    project         = "fixi"
    environment     = "dev"
    location        = "eastus2"
    container_image = "fixi"
  }

  expect_failures = [
    var.container_image,
  ]
}

# --------------------------------------------------------------------------
# Test: CPU below ACI minimum is rejected
# --------------------------------------------------------------------------

run "reject_cpu_below_minimum" {
  command = plan

  variables {
    project         = "fixi"
    environment     = "dev"
    location        = "eastus2"
    container_image = "fixi:test"
    container_cpu   = 0.1
  }

  expect_failures = [
    var.container_cpu,
  ]
}
