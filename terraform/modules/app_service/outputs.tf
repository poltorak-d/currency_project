output "backend_name" {
  value = azurerm_linux_web_app.backend.name
}

output "frontend_name" {
  value = azurerm_linux_web_app.frontend.name
}

output "backend_hostname" {
  value = azurerm_linux_web_app.backend.default_hostname
}

output "frontend_hostname" {
  value = azurerm_linux_web_app.frontend.default_hostname
}

output "backend_principal_id" {
  description = "Managed identity principal ID for backend - used to grant Key Vault access"
  value       = azurerm_linux_web_app.backend.identity[0].principal_id
}

output "frontend_principal_id" {
  description = "Managed identity principal ID for frontend"
  value       = azurerm_linux_web_app.frontend.identity[0].principal_id
}
