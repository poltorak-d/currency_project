#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/../terraform"
REPO_DIR="$SCRIPT_DIR/.."

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'
log()  { echo -e "${GREEN}[deploy]${NC} $1"; }
warn() { echo -e "${YELLOW}[warn]${NC} $1"; }
die()  { echo -e "${RED}[error]${NC} $1" >&2; exit 1; }
step() { echo -e "\n${BOLD}── $1 ──${NC}"; }

# ── 1. Prerequisites ──────────────────────────────────────────────────────────
step "Checking prerequisites"
command -v terraform >/dev/null 2>&1 || die "terraform not found — install it first"
command -v az        >/dev/null 2>&1 || die "Azure CLI not found — install it first"
command -v gh        >/dev/null 2>&1 || die "GitHub CLI not found — install it first"

az account show >/dev/null 2>&1 || die "Not logged into Azure. Run: az login --tenant <tenant-id>"
gh auth status  >/dev/null 2>&1 || die "Not logged into GitHub. Run: gh auth login"
log "All prerequisites met"

# ── 2. Terraform apply ────────────────────────────────────────────────────────
step "Provisioning Azure infrastructure"
cd "$TERRAFORM_DIR"
terraform apply -auto-approve
log "Infrastructure provisioned"

# ── 3. Read outputs ───────────────────────────────────────────────────────────
step "Reading Terraform outputs"
RG=$(terraform output -raw resource_group_name)
BACKEND_APP=$(terraform output -raw backend_app_name)
FRONTEND_APP=$(terraform output -raw frontend_app_name)
BACKEND_URL=$(terraform output -raw backend_url)
FRONTEND_URL=$(terraform output -raw frontend_url)
log "Resource group : $RG"
log "Backend app    : $BACKEND_APP"
log "Frontend app   : $FRONTEND_APP"

# ── 4. Fetch publish profiles (never printed to stdout) ───────────────────────
step "Fetching Azure publish profiles"
BACKEND_PROFILE=$(az webapp deployment list-publishing-profiles \
  --name "$BACKEND_APP" --resource-group "$RG" --xml)
FRONTEND_PROFILE=$(az webapp deployment list-publishing-profiles \
  --name "$FRONTEND_APP" --resource-group "$RG" --xml)
log "Publish profiles fetched"

# ── 5. Push secrets + variable to GitHub ─────────────────────────────────────
step "Configuring GitHub secrets and variables"
cd "$REPO_DIR"
gh secret set BACKEND_APP_NAME        --body "$BACKEND_APP"
gh secret set FRONTEND_APP_NAME       --body "$FRONTEND_APP"
gh secret set BACKEND_PUBLISH_PROFILE --body "$BACKEND_PROFILE"
gh secret set FRONTEND_PUBLISH_PROFILE --body "$FRONTEND_PROFILE"
gh variable set BACKEND_URL           --body "$BACKEND_URL"
log "GitHub secrets and variables set"

# ── 6. Trigger the deployment workflow ───────────────────────────────────────
step "Triggering GitHub Actions deployment"
gh workflow run deploy.yml
sleep 5  # give GitHub a moment to register the run

RUN_ID=$(gh run list --workflow=deploy.yml --limit=1 --json databaseId --jq '.[0].databaseId')
log "Watching run #$RUN_ID ..."
gh run watch "$RUN_ID" --exit-status || die "Deployment workflow failed — check: gh run view $RUN_ID --log-failed"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}Deployment complete!${NC}"
echo -e "  Frontend : ${BOLD}$FRONTEND_URL${NC}"
echo -e "  Backend  : ${BOLD}$BACKEND_URL${NC}"
echo ""
echo -e "${YELLOW}Remember to run scripts/teardown.sh when you're done to stop Azure charges.${NC}"
