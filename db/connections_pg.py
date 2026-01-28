import os
import psycopg2
from sqlalchemy import create_engine

def get_db_url():
    dsn = os.getenv("DATABASE_URL")
    if dsn:
        if dsn.startswith("postgres://"):
            dsn = dsn.replace("postgres://", "postgresql+psycopg2://", 1)
        elif not dsn.startswith("postgresql+psycopg2://"):
             # Assuming standard postgres connection string without sqlalchemy driver
             if dsn.startswith("postgresql://"):
                 dsn = dsn.replace("postgresql://", "postgresql+psycopg2://", 1)
        return dsn

    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "password")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "crickanal")
    
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

def get_db_engine():
    """Returns a SQLAlchemy engine."""
    return create_engine(get_db_url())

def get_connection():
    """Returns a raw psycopg2 connection wrapped in SQLite adapter."""
    dsn = os.getenv("DATABASE_URL")
    if dsn:
        raw_conn = psycopg2.connect(dsn)
        return SQLiteCompatibleConnection(raw_conn)

    raw_conn = psycopg2.connect(
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "password"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "crickanal")
    )
    return SQLiteCompatibleConnection(raw_conn)

class SQLiteCompatibleCursor:
    def __init__(self, pg_cursor):
        self.cursor = pg_cursor

    def execute(self, sql, params=None):
        # Convert SQLite ? placeholders to Psycopg2 %s
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

