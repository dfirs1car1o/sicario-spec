terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "region" {
  type        = string
  description = "GCP region."
}

variable "labels" {
  type        = map(string)
  description = "Required SicarioSpec labels: owner, system, environment, data-classification, retention, compliance-scope, cost-center, source-repo, managed-by, and expires-on for temporary resources."
  default     = {}
}
