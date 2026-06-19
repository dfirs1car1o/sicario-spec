variable "environment" {
  type        = string
  description = "Deployment environment."
}

variable "region" {
  type        = string
  description = "Deployment region."
}

variable "tags" {
  type        = map(string)
  description = "Required SicarioSpec tags: owner, system, environment, data-classification, retention, compliance-scope, cost-center, source-repo, managed-by, and expires-on for temporary resources."
  default     = {}
}
