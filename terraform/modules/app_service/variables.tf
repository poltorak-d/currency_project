variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "plan_name" {
  type = string
}

variable "sku_name" {
  description = "App Service plan SKU, e.g. F1 (free, quota) or B1 (Basic)"
  type        = string
}

variable "backend_app_name" {
  type = string
}

variable "frontend_app_name" {
  type = string
}

variable "key_vault_name" {
  description = "Key Vault name used for constructing KV reference strings"
  type        = string
}

variable "nbp_api_base_url" {
  type    = string
  default = "https://api.nbp.pl/api"
}
