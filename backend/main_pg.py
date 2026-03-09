import sys
import os

# --- 1. Monkey Patch import path ---

import backend.services.db
from db.connections_pg import get_connection as get_pg_connection

print("Monkey patching backend.services.db.get_connection to use PostgreSQL...")
backend.services.db.get_connection = get_pg_connection

# --- 2. Import the main app ---

from backend.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
