# Cricket Analysis Project - AI Agent Instructions

## Architecture Overview
- **Backend**: FastAPI with PostgreSQL (Neon cloud) for production, SQLite for local testing
- **Frontend**: Flutter web app deployed to Firebase Hosting
- **Data Pipeline**: Jupyter notebooks → CSV outputs → database migration → API endpoints
- **Core Logic**: `end_applications/` contains optimization algorithms (Best XI, player replacement, etc.)
- **Database Abstraction**: `db/session.py` handles SQLite/PostgreSQL switching via `DB_TYPE` env var

## Key Patterns & Conventions

### Database Connection
- Use `from backend.services.db import get_connection()` for all DB access
- Default to PostgreSQL (`DB_TYPE=postgres`), fallback to SQLite
- PostgreSQL uses `SQLiteCompatibleConnection` wrapper for query compatibility
- Example: `conn = get_connection(); cursor = conn.cursor()`

### API Structure
- Routers in `backend/api/` with FastAPI `APIRouter`
- Pydantic models for request/response validation
- CORS enabled for all origins in development
- Example: `@router.post("/find")` with `PlayerReplacementRequest` model

### Player Data Standards
- Use ESPNcricinfo player names (e.g., "SK Yadav" for Suryakumar Yadav)
- Player roles: 'BAT', 'BOWL', 'AR' (allrounder), 'WK' (wicketkeeper)
- Include fallback players in test squads for robustness

### Testing Approach
- Tests in `test/` directory use SQLite directly
- Realistic T20 World Cup squads with ESPNcricinfo names
- Example: `conn = sqlite3.connect("analytics.db")` in test files

## Development Workflows

### Running Backend (PostgreSQL)
```bash
# Set environment variables
set DB_TYPE=postgres
set DATABASE_URL=postgresql://...

# Run migration (one-time)
python db/build_analytics_db_pg.py

# Start server
python -m uvicorn backend.main_pg:app --reload --port 8000
```

### Running Backend (SQLite)
```bash
# Build local DB (one-time)
python db/build_analytics_db.py

# Start server
python backend/main.py
```

### Data Pipeline
1. Run preprocessing notebooks in `preprocessing/` (Jupyter)
2. Generate CSV outputs to `outputs/` directory
3. Run database migration script
4. API endpoints serve processed data

## Key Files to Reference
- `backend/main.py`: API router setup and CORS
- `db/session.py`: Database abstraction layer
- `end_applications/bestxi_optimizer.py`: Core optimization logic
- `test/bestxi_test.py`: Testing patterns with realistic data
- `start_postgres_backend.bat`: Production startup script

## Cricket Analytics Concepts
- **WPA/RPA**: Win Probability Added / Run Probability Added metrics
- **Elo Ratings**: Team strength modeling
- **Player Vectors**: Multi-dimensional player performance representations
- **Matchup Adjustments**: Opponent-specific performance modifiers

## Deployment
- Frontend: Firebase Hosting (auto-deploy on merge to `WPA-RPA` branch)
- Backend: Manual deployment with Neon PostgreSQL
- CI/CD: GitHub Actions for Flutter web builds</content>
<parameter name="filePath">c:\Users\Adavith Manoj\Desktop\IPD\CricketAnalysis\.github\copilot-instructions.md