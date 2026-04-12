output "resource_group_name" {
  description = "Name of the resource group"
  value       = module.resource_group.name
}

output "backend_app_name" {
  description = "Backend App Service name (use as BACKEND_APP_NAME GitHub secret)"
  value       = module.app_service.backend_name
}

output "frontend_app_name" {
  description = "Frontend App Service name (use as FRONTEND_APP_NAME GitHub secret)"
  value       = module.app_service.frontend_name
}

output "backend_url" {
  description = "Backend App Service URL (use as BACKEND_URL GitHub variable for frontend build)"
  value       = "https://${module.app_service.backend_hostname}"
}

output "frontend_url" {
  description = "Frontend App Service URL"
  value       = "https://${module.app_service.frontend_hostname}"
}

output "key_vault_name" {
  description = "Key Vault name"
  value       = module.key_vault.vault_name
}

output "sql_server_fqdn" {
  description = "SQL Server fully qualified domain name"
  value       = module.sql_database.server_fqdn
}
