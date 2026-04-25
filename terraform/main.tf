data "azurerm_client_config" "current" {}

# Random 4-byte suffix to keep resource names globally unique
resource "random_id" "suffix" {
  byte_length = 4
}

# Random password for SQL Server admin - stored in Key Vault, never exposed
resource "random_password" "sql_admin" {
  length           = 20
  special          = true
  override_special = "!#*()-_=+[]{}:"
  min_lower        = 2
  min_upper        = 2
  min_numeric      = 2
  min_special      = 2
}

locals {
  suffix          = lower(random_id.suffix.hex)
  sql_server_name = "sql-${var.app_name_prefix}-${local.suffix}"
  sql_db_name     = "${var.app_name_prefix}-db"
  kv_name         = "kv-${var.app_name_prefix}-${local.suffix}"
  backend_name    = "app-${var.app_name_prefix}-backend-${local.suffix}"
  frontend_name   = "app-${var.app_name_prefix}-frontend-${local.suffix}"
  plan_name       = "asp-${var.app_name_prefix}-${local.suffix}"
}

# ── Resource Group ────────────────────────────────────────────────────────────
module "resource_group" {
  source   = "./modules/resource_group"
  name     = var.resource_group_name
  location = var.location
}

# ── Azure SQL (free serverless tier) ─────────────────────────────────────────
module "sql_database" {
  source              = "./modules/sql_database"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  server_name         = local.sql_server_name
  database_name       = local.sql_db_name
  admin_username      = var.sql_admin_username
  admin_password      = random_password.sql_admin.result
}

# ── Key Vault (holds all secrets) ─────────────────────────────────────────────
module "key_vault" {
  source              = "./modules/key_vault"
  name                = local.kv_name
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  terraform_object_id = data.azurerm_client_config.current.object_id
  db_admin_password   = random_password.sql_admin.result
  # Async SQLAlchemy on App Service (aioodbc). Oryx image includes ODBC Driver 18.
  db_connection_string = join("", [
    "mssql+aioodbc://",
    var.sql_admin_username,
    ":",
    urlencode(random_password.sql_admin.result),
    "@",
    module.sql_database.server_fqdn,
    ":1433/",
    local.sql_db_name,
    "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes",
  ])
}

# ── App Services (shared Linux plan; SKU from var.app_service_sku) ───────────
module "app_service" {
  source              = "./modules/app_service"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  plan_name           = local.plan_name
  sku_name            = var.app_service_sku
  backend_app_name    = local.backend_name
  frontend_app_name   = local.frontend_name
  key_vault_name      = module.key_vault.vault_name
  nbp_api_base_url    = "https://api.nbp.pl/api"
}

# ── Grant App Service managed identities read access to Key Vault ─────────────
resource "azurerm_key_vault_access_policy" "backend" {
  key_vault_id = module.key_vault.vault_id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = module.app_service.backend_principal_id

  secret_permissions = ["Get", "List"]
}

resource "azurerm_key_vault_access_policy" "frontend" {
  key_vault_id = module.key_vault.vault_id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = module.app_service.frontend_principal_id

  secret_permissions = ["Get", "List"]
}
