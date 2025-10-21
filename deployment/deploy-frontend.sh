#!/bin/bash
# XCRI Frontend Deployment Script
# Builds and deploys frontend to production
# Preserves .htaccess and api-proxy.cgi files

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
DIST_DIR="$FRONTEND_DIR/dist"
SERVER="ustfccca-web4"
REMOTE_PATH="/home/web4ustfccca/public_html/iz/xcri"

echo "================================================"
echo "XCRI Frontend Deployment"
echo "================================================"
echo ""

# Step 1: Build frontend
echo "[1/4] Building frontend..."
cd "$FRONTEND_DIR"
npm run build
echo "✓ Build complete"
echo ""

# Step 2: Deploy frontend files (excluding .htaccess and api-proxy.cgi)
echo "[2/4] Deploying frontend files..."
rsync -avz --delete \
  --exclude='.htaccess' \
  --exclude='api-proxy.cgi' \
  --exclude='api/' \
  --exclude='logs/' \
  "$DIST_DIR/" "$SERVER:$REMOTE_PATH/"
echo "✓ Frontend files deployed"
echo ""

# Step 3: Restore .htaccess if missing
echo "[3/4] Ensuring .htaccess is present..."
if ! ssh "$SERVER" "test -f $REMOTE_PATH/.htaccess"; then
  echo "  .htaccess missing, copying from repo..."
  scp "$PROJECT_ROOT/.htaccess" "$SERVER:$REMOTE_PATH/"
  echo "  ✓ .htaccess restored"
else
  echo "  ✓ .htaccess already present"
fi
echo ""

# Step 4: Restore api-proxy.cgi if missing
echo "[4/4] Ensuring api-proxy.cgi is present..."
if ! ssh "$SERVER" "test -f $REMOTE_PATH/api-proxy.cgi"; then
  echo "  api-proxy.cgi missing, copying from repo..."
  scp "$PROJECT_ROOT/api-proxy.cgi" "$SERVER:$REMOTE_PATH/"
  ssh "$SERVER" "chmod +x $REMOTE_PATH/api-proxy.cgi"
  echo "  ✓ api-proxy.cgi restored"
else
  echo "  ✓ api-proxy.cgi already present"
fi
echo ""

# Step 5: Fix file permissions for static assets
echo "[5/5] Fixing file permissions..."
ssh "$SERVER" "chmod -R 644 $REMOTE_PATH/*.{png,jpg,jpeg,gif,svg,ico,css,js,html,json} 2>/dev/null || true"
ssh "$SERVER" "chmod 755 $REMOTE_PATH/assets 2>/dev/null || true"
ssh "$SERVER" "chmod 644 $REMOTE_PATH/assets/* 2>/dev/null || true"
echo "✓ File permissions fixed"
echo ""

echo "================================================"
echo "✓ Frontend deployment complete!"
echo "================================================"
echo ""
echo "Live URL: https://web4.ustfccca.org/iz/xcri/"
echo ""
