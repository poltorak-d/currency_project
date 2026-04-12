variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "francecentral"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-currency-project"
}

variable "app_name_prefix" {
  description = "Short prefix used in all resource names"
  type        = string
  default     = "currency"
}

variable "sql_admin_username" {
  description = "SQL Server administrator username"
  type        = string
  default     = "dbadmin"
}
