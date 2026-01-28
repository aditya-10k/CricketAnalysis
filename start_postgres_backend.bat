@echo off
echo Starting PostgreSQL Migration and Backend...

REM Set DB_TYPE to postgres to use the new db.session logic
set DB_TYPE=postgres

REM Set Database Credentials (NEON DB)
set DATABASE_URL=postgresql://neondb_owner:npg_KutZiQrHpy73@ep-ancient-band-a1dzkai8-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

REM 1. Build the Database (Run Migration)
echo Running DB Migration...
python db/build_analytics_db_pg.py
IF %ERRORLEVEL% NEQ 0 (
    echo DB Migration Failed!
    exit /b %ERRORLEVEL%
)

REM 2. Start the Backend
echo Starting Backend...
python -m uvicorn backend.main_pg:app --reload --port 8000
