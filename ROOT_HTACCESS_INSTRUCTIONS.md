# Root .htaccess Configuration for XCRI

## Location
`/home/web4ustfccca/public_html/.htaccess` (on web4.ustfccca.org server)

## Required Change

Add the following line **AFTER** the existing IZ app routing rules (around line 9):

```apache
# XCRI API - Route to CGI proxy
RewriteRule ^iz/xcri/api(/.*)?$ /iz/xcri/api-proxy.cgi$1 [QSA,L]
```

## Context

This rule should be placed in the "IZ Flask App Routing" section, which begins around line 1-2:

```apache
# IZ Flask App Routing - Must be BEFORE WordPress rules
RewriteEngine On
RewriteBase /

# Redirect /iz/xc-scoreboard to Flask CGI (preserve query parameters)
RewriteRule ^iz/xc-scoreboard(/.*)?$ /iz/xc-scoreboard/app-iz-xc-scoreboard.cgi [QSA,L]

RewriteRule ^iz/season-resume(/.*)?$ /iz/season-resume/app-iz-sr.cgi [QSA,L]

# XCRI API - Route to CGI proxy
RewriteRule ^iz/xcri/api(/.*)?$ /iz/xcri/api-proxy.cgi$1 [QSA,L]

# Redirect other /iz/ paths to main IZ app  
RewriteRule ^iz/?$ /iz/app-iz-main.cgi [QSA,L]
```

## Why This Is Needed

1. **WordPress Interference**: Without this rule, WordPress catches `/iz/xcri/api/*` requests and returns 404 errors
2. **API-Only Routing**: This rule ONLY routes API requests (`/iz/xcri/api/*`) to the CGI proxy, allowing static frontend files to be served normally
3. **Path Preservation**: The `$1` captures and preserves the path after `/api/` (e.g., `/health`, `/athletes/`, etc.)

## What This Fixes

- ✅ Bypasses WordPress for XCRI API requests
- ✅ Routes API calls to the CGI proxy with correct PATH_INFO
- ✅ Allows React SPA frontend to load from `/iz/xcri/` without interference
- ✅ Maintains compatibility with other IZ applications

## Testing

After adding this rule, test with:

```bash
curl https://web4.ustfccca.org/iz/xcri/api/health
# Should return: {"status":"healthy",...}

curl https://web4.ustfccca.org/iz/xcri/
# Should return: HTML for React SPA
```

## Notes

- This rule must be placed BEFORE the WordPress block (around line 91)
- The existing WordPress XCRI exclusion rules can remain but are not sufficient alone
- Do NOT route all `/iz/xcri/*` requests - only `/iz/xcri/api/*`
