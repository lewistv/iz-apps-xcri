# XCRI Production Deployment Log

## Deployment Date
October 21, 2025 - Deployment Session 001

## Deployment Status
⚠️ **PARTIAL SUCCESS** - Frontend deployed, API proxy needs configuration

## Production URLs
- **Frontend**: https://web4.ustfccca.org/iz/xcri/ ✅ WORKING
- **API** (local): http://127.0.0.1:8001 ✅ WORKING
- **API** (proxied): https://web4.ustfccca.org/iz/xcri/api/ ⚠️ NOT WORKING
- **API Docs**: http://127.0.0.1:8001/docs (local only)
- **Health**: http://127.0.0.1:8001/health ✅ WORKING (local)

## Service Status
- **Backend**: systemd service `xcri-api` - Active (running) with 2 workers
- **Frontend**: Apache serving static files from `/public_html/iz/xcri/`
- **Database**: MySQL `web4ustfccca_iz` - Connected (read-only)

## Deployment Summary

### Phase 1: Server Setup ✅
- Files copied via rsync to `/home/web4ustfccca/public_html/iz/xcri/`
- .env file created with correct variable names (XCRI_DB_*, API_*)
- Permissions set to 600 for security

### Phase 2: Backend Setup ✅
- Python 3.9.16 virtual environment created
- All dependencies installed (FastAPI, uvicorn, pymysql, pandas)
- Import fixes applied (removed `webapp.api.` prefixes)
- Standalone database.py created (PyMySQL-based)
- Manual API startup tested successfully

### Phase 3: Systemd Service ✅
- Logs directory created: `/public_html/iz/xcri/logs/`
- Service file updated with correct paths
- User systemd service installed and enabled
- Service running with 2 workers (PIDs: 3782880, 3782886, 3782887)

### Phase 4: Frontend Build ✅
- Vite config updated with `base: '/iz/xcri/'`
- Production build completed (457KB JS, 33KB CSS)
- Files deployed to server root directory
- DirectoryIndex added to .htaccess

### Phase 5: Apache Configuration ⚠️
- Root .htaccess updated with XCRI passthrough rule
- Subdirectory .htaccess configured for SPA routing
- Frontend serving correctly at https://web4.ustfccca.org/iz/xcri/
- **ISSUE**: API proxy not working (mod_proxy may need enabling)

## Known Issues

### 1. API Proxy Not Working (CRITICAL)
**Problem**: Requests to `/iz/xcri/api/*` return WordPress 404 instead of proxying to port 8001

**Root Cause**: Apache mod_proxy may not be enabled, or [P] flag not working

**Rewrite Rule** (in `/public_html/iz/xcri/.htaccess`):
```apache
RewriteCond %{REQUEST_URI} ^/iz/xcri/api/
RewriteRule ^api/(.*)$ http://127.0.0.1:8001/$1 [P,L]
```

**Temporary Workaround**: API accessible locally at http://127.0.0.1:8001

**Fix Needed**:
1. Verify mod_proxy and mod_proxy_http are enabled
2. Consider using ProxyPass directive if available
3. Alternative: Use different port/subdomain for API

### 2. Empty Table Data
**Problem**: Health check shows 0 rows in XCRI tables

**Tables Checked**:
- `iz_rankings_xcri_athlete_rankings`: 0 rows
- `iz_rankings_xcri_team_rankings`: 0 rows  
- `iz_rankings_xcri_metadata`: 0 rows

**Possible Causes**:
- Tables exist but haven't been populated with data
- Data population scripts haven't been run
- Different database environment than expected

**Fix Needed**: Run data population scripts from izzypy_xcri repository

### 3. Snapshot Directory Missing
**Problem**: `/home/web4ustfccca/izzypy_xcri/data/exports` does not exist

**Impact**: Historical snapshot endpoints will not work

**Current Config**: `SNAPSHOT_DIR` points to non-existent path

**Fix Needed**:
- Copy snapshot files from development to server
- Or update path to correct location
- Or create placeholder directory

## Files Modified on Server

### Created:
- `/home/web4ustfccca/public_html/iz/xcri/` (entire directory)
- `/home/web4ustfccca/public_html/iz/xcri/api/.env`
- `/home/web4ustfccca/public_html/iz/xcri/api/database.py` (standalone version)
- `/home/web4ustfccca/public_html/iz/xcri/logs/`
- `~/.config/systemd/user/xcri-api.service`

### Modified:
- `/home/web4ustfccca/public_html/.htaccess` (added XCRI rule)
- `/home/web4ustfccca/public_html/iz/xcri/.htaccess` (added DirectoryIndex)
- `/home/web4ustfccca/public_html/iz/xcri/deployment/xcri-api.service` (path fixes)
- All `/public_html/iz/xcri/api/**/*.py` files (import fixes)

### Backups:
- `/home/web4ustfccca/public_html/.htaccess.backup-xcri`
- `/home/web4ustfccca/public_html/iz/xcri/api/*.bak` (sed backups)

## Testing Results

### ✅ Working:
- Frontend loads at https://web4.ustfccca.org/iz/xcri/
- React SPA assets load correctly (/iz/xcri/assets/*)
- Backend API responds locally (127.0.0.1:8001)
- Health check endpoint works (locally)
- Database connection validated
- Systemd service auto-restarts
- Python imports working
- All dependencies installed

### ⚠️ Not Working:
- API proxy through Apache (404 from WordPress)
- Historical snapshots (directory missing)
- Table data empty (needs population)

### 🚫 Not Tested:
- Frontend functionality (requires working API proxy)
- All 15 API endpoints
- SCS components modal
- Search and filtering
- Pagination
- Cross-browser compatibility
- Mobile responsive design
- Performance benchmarks

## Next Steps

### Immediate (Before Production Use):
1. **Enable mod_proxy** on Apache or configure alternative API access method
2. **Populate database tables** with XCRI ranking data
3. **Test API endpoints** once proxy is working
4. **Copy snapshot files** to server or configure correct path

### Short Term:
1. Complete frontend testing (all features)
2. Performance validation (API <100ms, page <2s)
3. Cross-browser testing (Chrome, Safari, Firefox)
4. Mobile responsive testing
5. Error handling verification

### Long Term:
1. Monitor service uptime and logs
2. Set up automated data updates (coordinate with izzypy_xcri)
3. Implement snapshot file management
4. Consider caching strategy for API responses

## Deployment Configuration

### Server Environment:
- **Server**: web4.ustfccca.org (100-29-47-255.cprapid.com)
- **User**: web4ustfccca
- **Path**: `/home/web4ustfccca/public_html/iz/xcri/`
- **Python**: 3.9.16
- **Node.js**: Not installed on server (built locally)
- **Apache**: Version unknown (running)

### Database Configuration:
- **Host**: localhost
- **Port**: 3306
- **Database**: web4ustfccca_iz
- **User**: web4ustfccca_public (read-only)
- **Tables**: 12 XCRI tables present

### API Configuration:
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Workers**: 2
- **Port**: 8001 (localhost only)
- **Logs**: `/public_html/iz/xcri/logs/api-*.log`

### Frontend Configuration:
- **Framework**: React 19
- **Build Tool**: Vite 7.1.11
- **Base Path**: /iz/xcri/
- **Bundle Size**: 490KB total (457KB JS, 33KB CSS)

## Deployed By
Claude Code - Deployment Session 001  
Date: October 21, 2025

## Notes

### Import Fixes Applied:
All Python files had `from webapp.api.` imports changed to relative imports without the prefix. This was necessary because the code structure changed from the development environment.

### Database Module Rewrite:
Created standalone `database.py` using PyMySQL directly instead of relying on external `algorithms.shared.database_connection` module that doesn't exist in production.

### Frontend Base Path:
Added `base: '/iz/xcri/'` to vite.config.js to ensure asset paths work correctly in the `/iz/xcri/` subdirectory.

### Systemd User Service:
Removed `User=` directive from service file since user services run as the user who started them.

## Lessons Learned

1. **Import paths matter**: Development structure (webapp.api.*) differed from deployment structure
2. **Vite base path required**: SPAs in subdirectories need explicit base configuration
3. **Apache modules**: Proxy functionality requires mod_proxy - verify before deployment
4. **Environment validation**: Check all paths (.env variables) exist on target server
5. **Data vs code**: Separate concerns - code deployed, data needs separate process

