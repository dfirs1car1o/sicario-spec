terraform {
  required_version = ">= 1.6.0"
  required_providers {
  }
}

# SicarioSpec starter: add providers and resources intentionally.
# Required before merge:
# - least privilege IAM
# - no public exposure unless justified
# - encryption enabled
# - logging enabled
# - tags/labels applied from var.tags per docs/governance/tagging-taxonomy.md
# - policy-as-code scan clean or exception approved
