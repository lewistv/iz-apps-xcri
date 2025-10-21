#!/bin/bash
# Safe frontend deployment script for XCRI
# Deploys frontend WITHOUT deleting server config files

set -e

echo "Building frontend..."
cd frontend
npm run build
cd ..

echo "Deploying frontend (preserving .htaccess and api-proxy.cgi)..."
rsync -av \
  --exclude='.htaccess' \
  --exclude='api-proxy.cgi' \
  --exclude='api/' \
  --exclude='logs/' \
  --exclude='deployment/' \
  --delete \
  frontend/dist/ \
  ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/

echo "✅ Frontend deployed successfully!"
echo "URL: https://web4.ustfccca.org/iz/xcri/"
