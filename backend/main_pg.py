import sys
import os

# --- 1. Monkey Patch import path ---
# We want to intercept imports of 'backend.services.db' or modify the function it returns.
# Best approach: Import the target module, then overwrite the function.

import backend.services.db
from db.connections_pg import get_connection as get_pg_connection

print("Monkey patching backend.services.db.get_connection to use PostgreSQL...")
backend.services.db.get_connection = get_pg_connection

# --- 2. Import the main app ---
# Now when routers are imported by main, they will still import `get_connection` from `backend.services.db`
# but since we patched the function object IN the module, they should get the new function?
# Wait, `from module import function` binds the object currently in the module.
# If we patch it here BEFORE main imports routers (which import this function), it should work.

from backend.main import app

if __name__ == "__main__":
    import uvicorn
    # Use standard uvicorn run but point to this app
    uvicorn.run(app, host="0.0.0.0", port=8000)
