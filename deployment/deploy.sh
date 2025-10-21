#!/bin/bash
# XCRI Rankings Deployment Script
# Deploys XCRI webapp to web4 production server

set -e  # Exit on error

echo "=== XCRI Rankings Deployment ==="
echo ""

# Configuration
REMOTE_USER="web4ustfccca"
REMOTE_HOST="web4.ustfccca.org"
REMOTE_PATH="/home/web4ustfccca/iz/xcri"
LOCAL_PATH="/Users/lewistv/code/ustfccca/iz-apps-clean/xcri"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[1/7] Building Frontend...${NC}"
cd "$LOCAL_PATH/frontend"
npm install
npm run build
echo -e "${GREEN}✓ Frontend built${NC}"

echo ""
echo -e "${YELLOW}[2/7] Pushing to Git...${NC}"
cd "$LOCAL_PATH"
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
git push origin main
echo -e "${GREEN}✓ Pushed to Git${NC}"

echo ""
echo -e "${YELLOW}[3/7] Pulling on Server...${NC}"
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_PATH && git pull origin main"
echo -e "${GREEN}✓ Code updated on server${NC}"

echo ""
echo -e "${YELLOW}[4/7] Installing Python Dependencies...${NC}"
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_PATH/api && source venv/bin/activate && pip install -r requirements.txt"
echo -e "${GREEN}✓ Dependencies installed${NC}"

echo ""
echo -e "${YELLOW}[5/7] Installing Frontend Dependencies...${NC}"
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_PATH/frontend && npm install"
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

echo ""
echo -e "${YELLOW}[6/7] Building Frontend on Server...${NC}"
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_PATH/frontend && npm run build"
echo -e "${GREEN}✓ Frontend built on server${NC}"

echo ""
echo -e "${YELLOW}[7/7] Restarting API Service...${NC}"
ssh $REMOTE_USER@$REMOTE_HOST "systemctl --user restart xcri-api"
sleep 3
ssh $REMOTE_USER@$REMOTE_HOST "systemctl --user status xcri-api --no-pager"
echo -e "${GREEN}✓ API service restarted${NC}"

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "Production URL: https://web4.ustfccca.org/iz/xcri"
echo "API Health: https://web4.ustfccca.org/iz/xcri/api/health"
echo "API Docs: https://web4.ustfccca.org/iz/xcri/api/docs"
echo ""
