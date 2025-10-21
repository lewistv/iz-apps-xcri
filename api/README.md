# XCRI Rankings API

REST API for NCAA Cross Country Rankings (XCRI). Provides fast, filtered access to athlete rankings, team rankings, and calculation metadata.

**API Version:** 1.0.0
**Status:** Production Ready

---

## Features

- **Fast Queries**: <100ms response times for list endpoints
- **Comprehensive Filters**: Division, gender, search, pagination
- **Auto-Generated Docs**: Swagger UI and ReDoc
- **CORS Enabled**: Ready for frontend integration
- **Type-Safe**: Full Pydantic validation
- **Database-Backed**: Direct access to 24,000+ athlete rankings

---

## Quick Start

### Installation

```bash
# Navigate to API directory
cd webapp/api

# Install dependencies
pip3 install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your database credentials (or use existing .mysql/web4.ini)
```

### Running the Server

```bash
# From project root
cd /Users/lewistv/code/ustfccca/izzypy_xcri
python3 -m uvicorn webapp.api.main:app --host 0.0.0.0 --port 8000 --reload

# Or for production (no reload)
python3 -m uvicorn webapp.api.main:app --host 0.0.0.0 --port 8000
```

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## API Endpoints

### System

#### `GET /`
Health check and API info
```bash
curl http://localhost:8000/
```

#### `GET /health`
Detailed health check with database status
```bash
curl http://localhost:8000/health
```

---

### Athletes

#### `GET /athletes/`
List athlete rankings with filters and pagination

**Query Parameters:**
- `season_year` (int): Season year (default: 2024)
- `division` (int): Division code (2030=D1, 2031=D2, 2032=D3, 2028=NAIA)
- `gender` (str): Gender code (M or F)
- `scoring_group` (str): Scoring scope (default: "division")
- `checkpoint_date` (str): Rankings as of date (YYYY-MM-DD)
- `algorithm_type` (str): Algorithm (default: "light")
- `limit` (int): Results per page (default: 25, max: 500)
- `offset` (int): Pagination offset (default: 0)
- `search` (str): Search by name or school
- `min_races` (int): Minimum race count filter

**Examples:**
```bash
# Top 25 D1 Men
curl "http://localhost:8000/athletes/?division=2030&gender=M&limit=25"

# Search for athletes named "Smith"
curl "http://localhost:8000/athletes/?search=Smith"

# Pagination - get results 26-50
curl "http://localhost:8000/athletes/?division=2030&gender=M&limit=25&offset=25"

# Filter by minimum races
curl "http://localhost:8000/athletes/?division=2030&gender=M&min_races=5"
```

**Response:**
```json
{
  "total": 3981,
  "limit": 25,
  "offset": 0,
  "results": [
    {
      "athlete_rank": 1,
      "anet_athlete_hnd": 19019918,
      "athlete_name_first": "Graham",
      "athlete_name_last": "Blanks",
      "team_name": "Harvard",
      "division_code": 2030,
      "gender_code": "M",
      "xcri_score": 999.0,
      "races_count": 4,
      "season_average": 168.19,
      "h2h_wins": 621,
      "h2h_losses": 1,
      "h2h_win_rate": 0.9984,
      ...
    }
  ]
}
```

#### `GET /athletes/{athlete_hnd}`
Get single athlete by AthleticNet athlete handle

**Example:**
```bash
curl "http://localhost:8000/athletes/19019918?season_year=2024"
```

#### `GET /athletes/team/{team_hnd}/roster`
Get all athletes on a team roster

**Example:**
```bash
curl "http://localhost:8000/athletes/team/20937/roster?season_year=2024"
```

---

### Teams

#### `GET /teams/`
List team rankings with filters and pagination

**Query Parameters:**
- `season_year` (int): Season year (default: 2024)
- `division` (int): Division code
- `gender` (str): Gender code (M or F)
- `scoring_group` (str): Scoring scope (default: "division")
- `checkpoint_date` (str): Rankings as of date (YYYY-MM-DD)
- `algorithm_type` (str): Algorithm (default: "light")
- `limit` (int): Results per page (default: 25, max: 500)
- `offset` (int): Pagination offset (default: 0)
- `search` (str): Search by school name

**Examples:**
```bash
# Top 25 D1 Men teams
curl "http://localhost:8000/teams/?division=2030&gender=M&limit=25"

# Search for teams
curl "http://localhost:8000/teams/?search=Harvard"
```

**Response:**
```json
{
  "total": 328,
  "limit": 25,
  "offset": 0,
  "results": [
    {
      "team_rank": 1,
      "anet_team_hnd": 20690,
      "team_name": "BYU",
      "division_code": 2030,
      "gender_code": "M",
      "team_xcri_score": 102.0,
      "athletes_count": 15,
      "top7_average": 979.6,
      "top5_average": 979.6,
      "squad_depth_score": 0.3333,
      "top_athlete_1_hnd": 12363122,
      ...
    }
  ]
}
```

#### `GET /teams/{team_hnd}`
Get single team by AthleticNet team handle

**Example:**
```bash
curl "http://localhost:8000/teams/20690?season_year=2024"
```

---

### Metadata

#### `GET /metadata/`
List calculation metadata records

**Query Parameters:**
- `season_year` (int): Season year (required)
- `division` (int): Division code (optional)
- `gender` (str): Gender code (optional)
- `scoring_group` (str): Scoring scope (optional)
- `checkpoint_date` (str): Checkpoint date (optional)
- `algorithm_type` (str): Algorithm type (optional)

**Example:**
```bash
curl "http://localhost:8000/metadata/?season_year=2024"
```

#### `GET /metadata/latest`
Get most recent calculation for each division/gender

**Example:**
```bash
curl "http://localhost:8000/metadata/latest"
```

**Response:**
```json
{
  "total": 6,
  "results": [
    {
      "metadata_id": 9,
      "season_year": 2024,
      "division_code": 2030,
      "gender_code": "F",
      "algorithm_type": "light",
      "total_athletes": 4657,
      "total_teams": 360,
      "processing_time_seconds": 17720.19,
      "cache_hit_rate": 1.0,
      "calculated_at": "2025-10-12T22:18:20",
      ...
    }
  ]
}
```

#### `GET /metadata/{metadata_id}`
Get single metadata record by ID

**Example:**
```bash
curl "http://localhost:8000/metadata/9"
```

#### `GET /metadata/summary/processing`
Get aggregate processing statistics

**Example:**
```bash
curl "http://localhost:8000/metadata/summary/processing"
```

---

## Division Codes

| Code | Division |
|------|----------|
| 2030 | NCAA Division I |
| 2031 | NCAA Division II |
| 2032 | NCAA Division III |
| 2028 | NAIA |
| 19781 | NJCAA Division I |
| 19782 | NJCAA Division II |
| 2034 | NJCAA Division III |

---

## Response Format

All list endpoints return:
```json
{
  "total": 3981,        // Total matching records
  "limit": 25,          // Results per page
  "offset": 0,          // Pagination offset
  "results": [...]      // Array of results
}
```

All timestamps are in ISO 8601 format: `2025-10-12T22:18:20`

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Success
- `307 Temporary Redirect`: Trailing slash redirect (use -L with curl)
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Invalid query parameters
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "error": "NotFoundError",
  "message": "Athlete 12345 not found for season 2024",
  "detail": "Additional error details"
}
```

---

## Configuration

### Environment Variables

Create `.env` file in `webapp/api/`:

```env
# Database (Option 1: Config file path)
XCRI_DB_CONFIG_PATH=/Users/username/.mysql/web4.ini

# Database (Option 2: Individual credentials)
XCRI_DB_HOST=web4.ustfccca.org
XCRI_DB_PORT=3306
XCRI_DB_USER=your_username
XCRI_DB_PASSWORD=your_password
XCRI_DB_NAME=ustfccca_v3

# API
API_HOST=0.0.0.0
API_PORT=8000
API_TITLE=XCRI Rankings API
API_VERSION=1.0.0

# CORS
API_CORS_ORIGINS=*  # or comma-separated list
```

### Database Tables

- `iz_rankings_xcri_athlete_rankings` - 24,334 athletes (6 divisions)
- `iz_rankings_xcri_team_rankings` - 1,961 teams (6 divisions)
- `iz_rankings_xcri_calculation_metadata` - 6 metadata records

---

## Performance

- **Query Speed**: <100ms for list endpoints (validated Session 032)
- **Database**: MySQL with indexed columns
- **Throughput**: ~1,345 records/second export (Session 033)
- **Records**: 24,334 athletes + 1,961 teams across 6 divisions

---

## Development

### Project Structure

```
webapp/api/
├── main.py              # FastAPI app entry point
├── config.py            # Settings management
├── database.py          # Database connection wrapper
├── models.py            # Pydantic request/response models
├── routes/
│   ├── athletes.py      # Athlete endpoints
│   ├── teams.py         # Team endpoints
│   └── metadata.py      # Metadata endpoints
├── services/
│   ├── athlete_service.py   # Athlete business logic
│   ├── team_service.py      # Team business logic
│   └── metadata_service.py  # Metadata business logic
├── requirements.txt     # Dependencies
└── README.md           # This file
```

### Running Tests

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test athlete endpoint
curl "http://localhost:8000/athletes/?division=2030&gender=M&limit=5"

# Test team endpoint
curl "http://localhost:8000/teams/?division=2030&gender=M&limit=5"

# Test metadata
curl "http://localhost:8000/metadata/latest"
```

### Dependencies

- fastapi==0.104.1 - Web framework
- uvicorn[standard]==0.24.0 - ASGI server
- pydantic==2.5.0 - Data validation
- pydantic-settings==2.1.0 - Settings management
- python-dotenv==1.0.0 - Environment variables
- pymysql>=1.1.0 - MySQL driver (from main requirements.txt)

---

## Deployment

### Production Deployment

```bash
# Run with gunicorn + uvicorn workers
gunicorn webapp.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker Deployment (Future)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "webapp.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment-Specific Settings

- **Development**: Set `API_CORS_ORIGINS=*` for all origins
- **Production**: Set specific allowed origins: `API_CORS_ORIGINS=https://xcri.ustfccca.org,https://www.ustfccca.org`

---

## Support

- **Documentation**: http://localhost:8000/docs (Swagger UI)
- **Project**: XCRI Research Project (Sessions 1-34)
- **Database**: web4.ustfccca.org (read-only access)

---

## Version History

- **v1.0.0** (2025-10-12, Session 034): Initial release
  - 11 REST endpoints
  - Full athlete/team/metadata access
  - Pagination and search
  - Auto-generated OpenAPI docs
  - CORS enabled
  - Production-ready performance

---

**Generated**: Session 034 - October 12, 2025
**Status**: Production Ready ✅
