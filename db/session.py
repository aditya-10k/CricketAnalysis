import os
import sys

# Default to Postgres for cloud readiness if not specified, or if explicit
DB_TYPE = os.getenv("DB_TYPE", "postgres")

# Generic Error Types (aliased later)
OperationalError = None
IntegrityError = None
Connection = None

if DB_TYPE == "sqlite":
    import sqlite3
    
    OperationalError = sqlite3.OperationalError
    IntegrityError = sqlite3.IntegrityError
    Connection = sqlite3.Connection

    from pathlib import Path
    # Determine DB path relative to this file
    # db/session.py -> parent is db/, parent is project root
    BASE_DIR = Path(__file__).resolve().parents[1]
    SQLITE_DB_PATH = BASE_DIR / "analytics.db"

    def get_connection():
        """Get standard SQLite connection."""
        return sqlite3.connect(SQLITE_DB_PATH)

else:
    # PostgreSQL Mode
    import psycopg2
    from psycopg2 import OperationalError as PgOperationalError
    from psycopg2 import IntegrityError as PgIntegrityError
    
    OperationalError = PgOperationalError
    IntegrityError = PgIntegrityError
    # We define a dummy type for type hinting if needed, or alias standard connection
    Connection = object 

    # Adapter Classes
    class SQLiteCompatibleCursor:
        def __init__(self, pg_cursor):
            self.cursor = pg_cursor

        def execute(self, sql, params=None):
            # Convert SQLite ? placeholders to Psycopg2 %s
            if sql:
                sql = sql.replace('?', '%s')
            
            # Handle None params
            if params is None:
                self.cursor.execute(sql)
            else:
                self.cursor.execute(sql, params)
            return self

        def fetchone(self):
            return self.cursor.fetchone()

        def fetchall(self):
            return self.cursor.fetchall()
            
        def close(self):
            self.cursor.close()
            
        def __getattr__(self, name):
            return getattr(self.cursor, name)
        
        def __iter__(self):
            return iter(self.cursor)

    class SQLiteCompatibleConnection:
        def __init__(self, pg_conn):
            self.conn = pg_conn

        def cursor(self):
            return SQLiteCompatibleCursor(self.conn.cursor())

        def execute(self, sql, params=None):
            """Emulate sqlite3 connection.execute shortcut"""
            cursor = self.cursor()
            cursor.execute(sql, params)
            return cursor

        def commit(self):
            self.conn.commit()

        def rollback(self):
            self.conn.rollback()

        def close(self):
            self.conn.close()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                self.rollback()
            else:
                self.commit()
            self.close()

    def get_connection():
        """Get PostgreSQL connection wrapped in SQLite adapter."""
        # Use DATABASE_URL if available (standard for Render/Heroku)
        dsn = os.getenv("DATABASE_URL")
        
        if not dsn:
            # Fallback to individual credentials
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASS", "password")
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            dbname = os.getenv("DB_NAME", "crickanal")
            
            raw_conn = psycopg2.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                dbname=dbname
            )
        else:
            raw_conn = psycopg2.connect(dsn)
            
        return SQLiteCompatibleConnection(raw_conn)
