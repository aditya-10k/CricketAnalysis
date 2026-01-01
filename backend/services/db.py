import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "analytics.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn
