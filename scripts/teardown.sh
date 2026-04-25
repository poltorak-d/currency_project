#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/../terraform"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'
log()  { echo -e "${GREEN}[teardown]${NC} $1"; }
die()  { echo -e "${RED}[error]${NC} $1" >&2; exit 1; }

command -v terraform >/dev/null 2>&1 || die "terraform not found"
az account show >/dev/null 2>&1 || die "Not logged into Azure. Run: az login"

echo -e "${YELLOW}${BOLD}This will destroy ALL Azure resources and stop all charges.${NC}"
read -rp "Type 'yes' to confirm: " CONFIRM
[[ "$CONFIRM" == "yes" ]] || { echo "Aborted."; exit 0; }

log "Destroying all Azure resources..."
cd "$TERRAFORM_DIR"
terraform destroy -auto-approve

echo ""
echo -e "${BOLD}${GREEN}All resources destroyed. Azure is no longer charging you.${NC}"
