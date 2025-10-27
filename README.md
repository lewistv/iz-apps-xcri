# XCRI Rankings Web Application

Display-only web interface for USTFCCCA Cross Country Running Index (XCRI) Rankings.

## Architecture

**Frontend**:
- React 19 with Vite 7
- Client-side SPA (Single Page Application)
- Responsive design for mobile and desktop

**Backend**:
- FastAPI REST API
- Uvicorn ASGI server (2 workers)
- Read-only MySQL database access
- 15 REST endpoints for rankings data

**Database**:
- MySQL (web4ustfccca_iz)
- Read-only user: web4ustfccca_public
- 418,000+ athlete rankings
- 36,000+ team five rankings
- 14 division/gender combinations
- 13 historical snapshots (2024-2025 seasons)

## Directory Structure

```
xcri/
├── api/                    # FastAPI backend
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connection
│   ├── models.py          # Pydantic models
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   ├── .env               # Production config (not in git)
│   └── requirements.txt   # Python dependencies
├── frontend/              # React SPA
│   ├── src/              # React components
│   ├── public/           # Static assets
│   ├── dist/             # Production build (not in git)
│   ├── package.json      # Node dependencies
│   └── vite.config.js    # Vite configuration
├── deployment/           # Deployment scripts
│   ├── deploy.sh        # Main deployment script
│   └── xcri-api.service # Systemd service definition
└── .htaccess            # Apache configuration

```

## Deployment

### Initial Setup (One-time)

1. **On Server** (SSH to web4.ustfccca.org):
   ```bash
   cd /home/web4ustfccca/iz/xcri

   # Create Python virtual environment
   cd api
   python3.9 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Install systemd service
   mkdir -p ~/.config/systemd/user
   cp deployment/xcri-api.service ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable xcri-api
   systemctl --user start xcri-api

   # Create logs directory
   mkdir -p /home/web4ustfccca/iz/xcri/logs
   ```

2. **Frontend Build**:
   ```bash
   cd /home/web4ustfccca/iz/xcri/frontend
   npm install
   npm run build
   ```

### Regular Deployments

Use the deployment script:
```bash
cd /Users/lewistv/code/ustfccca/iz-apps-clean/xcri
./deployment/deploy.sh
```

Or manually via git:
```bash
# Local machine
git add .
git commit -m "Your changes"
git push origin main

# On server
ssh web4ustfccca@web4.ustfccca.org
cd /home/web4ustfccca/iz/xcri
git pull origin main
systemctl --user restart xcri-api
```

## Production URLs

- **Frontend**: https://web4.ustfccca.org/iz/xcri
- **API**: https://web4.ustfccca.org/iz/xcri/api
- **API Docs**: https://web4.ustfccca.org/iz/xcri/api/docs
- **Health Check**: https://web4.ustfccca.org/iz/xcri/api/health

## Development vs Production

**This repository** (iz-apps-clean/xcri):
- Display-only web application
- Read-only database access
- Production deployment code

**Parent repository** (izzypy_xcri):
- Algorithm development and research
- Ranking calculations
- Database writes and exports
- Weekly ranking updates

## Service Management

```bash
# Check service status
systemctl --user status xcri-api

# View logs
journalctl --user -u xcri-api -f

# Restart service
systemctl --user restart xcri-api

# Stop service
systemctl --user stop xcri-api

# Start service
systemctl --user start xcri-api
```

## Database Access

The webapp uses **read-only** database access:
- User: `web4ustfccca_public`
- Database: `web4ustfccca_iz`
- Permissions: SELECT only

All data updates are performed via the parent izzypy_xcri repository.

## Features

- **Current Rankings**: Live XCRI rankings (all divisions)
- **Historical Snapshots**: 13 weekly snapshots (2024-2025)
- **Geographic Filters**: Region and conference filtering
- **Search**: Real-time athlete/team search
- **SCS Components**: Detailed component score breakdowns
- **Team Rosters**: View team lineups and rankings
- **Performance**: <100ms API responses, <2s page loads

## Technology Stack

- **Frontend**: React 19, Vite 7, Axios, React Router
- **Backend**: FastAPI, Uvicorn, Pydantic, SQLAlchemy, PyMySQL
- **Database**: MySQL 8.0
- **Server**: Apache 2.4, User Systemd
- **Hosting**: cPanel environment (web4.ustfccca.org)

## Support

For issues or questions about this webapp, contact the development team.

For algorithm research and ranking calculations, see the parent izzypy_xcri repository.
