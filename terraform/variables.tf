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

variable "app_service_sku" {
  description = <<-EOT
    Linux App Service plan SKU for backend + frontend (shared plan).
    F1 is free but enforces a daily CPU quota; when exceeded, SCM/Kudu returns
    403 "Site Disabled" and azure/webapps-deploy fails. B1 avoids that (paid Basic tier).
  EOT
  type    = string
  default = "B1"
}
