# Shared App Service Plan - F1 free tier (Linux)
resource "azurerm_service_plan" "this" {
  name                = var.plan_name
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  sku_name            = "F1"
}

# ── Backend (Python 3.11 / FastAPI) ──────────────────────────────────────────
resource "azurerm_linux_web_app" "backend" {
  name                = var.backend_app_name
  location            = var.location
  resource_group_name = var.resource_group_name
  service_plan_id     = azurerm_service_plan.this.id
  https_only          = true

  # Wymagane do wdrożeń z publish profile (GitHub Actions / OneDeploy), gdy Azure ma wyłączone domyślne basic auth.
  ftp_publish_basic_authentication_enabled     = true
  webdeploy_publish_basic_authentication_enabled = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on = false # F1 does not support always-on

    application_stack {
      python_version = "3.11"
    }

    app_command_line = "uvicorn app.main:app --host 0.0.0.0 --port 8000"
  }

  app_settings = {
    # Secret pulled from Key Vault at runtime via managed identity
    DATABASE_URL = "@Microsoft.KeyVault(VaultName=${var.key_vault_name};SecretName=db-connection-string)"

    NBP_API_BASE_URL    = var.nbp_api_base_url
    NBP_REQUEST_TIMEOUT = "10"

    # Python path so 'app' package resolves correctly
    PYTHONPATH = "/home/site/wwwroot"
    WEBSITES_PORT = "8000"

    # Tell Oryx to install requirements.txt on deploy
    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"
    ENABLE_ORYX_BUILD              = "true"
  }
}

# ── Frontend (Node.js 20 / Express serving React dist) ───────────────────────
resource "azurerm_linux_web_app" "frontend" {
  name                = var.frontend_app_name
  location            = var.location
  resource_group_name = var.resource_group_name
  service_plan_id     = azurerm_service_plan.this.id
  https_only          = true

  ftp_publish_basic_authentication_enabled     = true
  webdeploy_publish_basic_authentication_enabled = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on = false # F1 does not support always-on

    application_stack {
      node_version = "20-lts"
    }

    app_command_line = "node server.cjs"
  }

  app_settings = {
    WEBSITES_PORT                  = "3000"
    WEBSITE_NODE_DEFAULT_VERSION   = "~20"
    # Disable Oryx build - we deploy pre-built dist + node_modules
    SCM_DO_BUILD_DURING_DEPLOYMENT = "false"
  }
}
