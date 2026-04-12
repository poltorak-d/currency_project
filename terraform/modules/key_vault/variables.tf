variable "name" {
  description = "Key Vault name (must be globally unique, 3-24 chars)"
  type        = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "tenant_id" {
  description = "Azure AD tenant ID"
  type        = string
}

variable "terraform_object_id" {
  description = "Object ID of the identity running Terraform (gets full secret access)"
  type        = string
}

variable "db_admin_password" {
  description = "SQL admin password — stored as Key Vault secret"
  type        = string
  sensitive   = true
}

variable "db_connection_string" {
  description = "Full SQLAlchemy connection string — stored as Key Vault secret"
  type        = string
  sensitive   = true
}
