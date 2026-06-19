variable "environment" {
  type        = string
  description = "Deployment environment."
}

variable "location" {
  type        = string
  description = "Azure region."
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name."
}

variable "storage_account_name" {
  type        = string
  description = "Globally unique storage account name."
}

variable "tags" {
  type        = map(string)
  description = "Additional resource tags."
  default     = {}
}

