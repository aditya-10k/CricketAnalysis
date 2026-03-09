# db/build_analytics_db_pg.py
"""
ONE-TIME DATABASE BUILDER (PostgreSQL)
Run once after analytics pipeline completes.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
from pathlib import Path
from sqlalchemy import text
from connections_pg import get_db_engine, get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

def ensure_database_exists():
    if os.getenv("DATABASE_URL"):
        print("DATABASE_URL found. Assuming managed database exists.")
        return

    dbname = os.getenv("DB_NAME", "crickanal")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "password")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")

    print(f"Checking if database '{dbname}' exists...")

    try:
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (dbname,))
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{dbname}' not found. Creating it...")
            cursor.execute(f'CREATE DATABASE "{dbname}"')
            print(f"Database '{dbname}' created.")
        else:
            print(f"Database '{dbname}' already exists.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Warning: Could not check/create database: {e}")
        print("Continuing, assuming database might exist or user permissions restricted.")


def drop_existing_views(engine):
    print("Dropping existing views to allow table replacement...")
    with engine.begin() as conn:
        conn.execute(text("DROP VIEW IF EXISTS player_replacement_view CASCADE"))
        conn.execute(text("DROP VIEW IF EXISTS player_bestxi_base CASCADE"))
    print("Views dropped")


def load_player_batting_positions(engine):
    print("Loading player batting positions...")

    try:
        df = pd.read_csv(OUTPUTS_DIR / "player_batting_positions.csv")

        required_cols = {"player", "avg_position", "median_position", "innings_count"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        df.to_sql("player_batting_positions", engine, if_exists="replace", index=False)

        with engine.begin() as conn:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pbp_player ON player_batting_positions(player)"))

        print(f"Loaded {len(df)} player positions")

    except FileNotFoundError:
        print("player_batting_positions.csv not found - run calculate_positions.py first")


def load_player_vectors(engine):
    print("Loading player vectors...")

    vectors_df = pd.read_csv(OUTPUTS_DIR / "player_vectors_base.csv")

    metadata_cols = {"inferred_nationality", "batting_style", "bowling_style"}
    missing_metadata = metadata_cols - set(vectors_df.columns)

    if missing_metadata:
        print(f"Metadata columns missing: {missing_metadata}")
        print("Merging from player_final_values.csv...")

        final_values_df = pd.read_csv(OUTPUTS_DIR / "player_final_values.csv")
        available_metadata = metadata_cols & set(final_values_df.columns)

        if available_metadata:
            merge_cols = ["player"] + list(available_metadata)
            vectors_df = vectors_df.merge(
                final_values_df[merge_cols],
                on="player",
                how="left"
            )
            print(f"Merged columns: {available_metadata}")
        else:
            print("No metadata found in player_final_values.csv")
            for col in missing_metadata:
                vectors_df[col] = None

    core_required = {
        "player", "role", "exposure",
        "career_bat_rpa_z", "career_bowl_rpa_z",
        "career_bat_wpa_z", "career_bowl_wpa_z",
        "balls_faced", "balls_bowled"
    }

    missing_core = core_required - set(vectors_df.columns)
    if missing_core:
        raise ValueError(f"Missing CORE columns: {missing_core}")

    for col in metadata_cols:
        if col not in vectors_df.columns:
            vectors_df[col] = None
            print(f"Added placeholder column: {col}")

    vectors_df.to_sql("player_vectors", engine, if_exists="replace", index=False)

    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pv_player ON player_vectors(player)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pv_role ON player_vectors(role)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pv_nationality ON player_vectors(inferred_nationality)"))

    print(f"Loaded {len(vectors_df)} players")


def load_player_final_values(engine):
    print("Loading player final values...")

    df = pd.read_csv(OUTPUTS_DIR / "player_final_values.csv")

    required_cols = {
        "player", "role", "total_value_z", "confidence",
        "final_value", "exposure"
    }

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if "last_match_played" in df.columns:
        df['last_match_played'] = pd.to_datetime(df['last_match_played'], errors='coerce')
        df['days_since_last_match'] = (pd.Timestamp.now() - df['last_match_played']).dt.days
    else:
        df['days_since_last_match'] = None
        print("last_match_played column not found - set to NULL")

    df.to_sql("player_final_values", engine, if_exists="replace", index=False)

    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pfv_player ON player_final_values(player)"))

    print(f"Loaded {len(df)} players")


def load_player_form(engine):
    print("Loading player form...")

    df = pd.read_csv(OUTPUTS_DIR / "player_form_overlay.csv")

    required_cols = {"player", "form_total_z", "form_confidence"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df.to_sql("player_form", engine, if_exists="replace", index=False)

    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pf_player ON player_form(player)"))

    print(f"Loaded {len(df)} players")


def load_player_daily_innings(engine):
    print("Loading player daily innings...")

    df = pd.read_csv(OUTPUTS_DIR / "player_daily_innings_impact.csv")

    df.to_sql("player_daily_innings", engine, if_exists="replace", index=False)

    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pdi_player ON player_daily_innings(player)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pdi_match ON player_daily_innings(match_id)"))

    print(f"Loaded {len(df)} innings")


def load_team_elo(engine):
    print("Loading team ELO history...")

    try:
        df = pd.read_csv(OUTPUTS_DIR / "team_elo_history.csv")
        df.to_sql("team_elo", engine, if_exists="replace", index=False)

        with engine.begin() as conn:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_te_team_date ON team_elo(team, date)"))

        print(f"Loaded {len(df)} ELO records")

    except FileNotFoundError:
        print("team_elo_history.csv not found - skipping")


def load_ball_by_ball_combined(engine):
    print("Loading ball-by-ball combined data...")

    df = pd.read_csv(OUTPUTS_DIR / "ball_by_ball_rpa_wpa_combined.csv")

    if 'batter' in df.columns:
        df.rename(columns={'batter': 'striker'}, inplace=True)
        print("Renamed 'batter' to 'striker'")

    if 'player_dismissed' not in df.columns:
        df['player_dismissed'] = df.apply(
            lambda row: row['striker'] if row.get('is_wicket') == 1 else None,
            axis=1
        )
        print("Created 'player_dismissed' column from is_wicket")

    required = ['striker', 'bowler', 'runs_off_bat', 'venue', 'match_id', 'rpa', 'wpa']
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df.to_sql("ball_by_ball", engine, if_exists="replace", index=False)

    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bbb_match ON ball_by_ball(match_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bbb_striker ON ball_by_ball(striker)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bbb_bowler ON ball_by_ball(bowler)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bbb_venue ON ball_by_ball(venue)"))

    print(f"Loaded {len(df)} balls")


def create_replacement_view(engine):
    print("Creating player_replacement_view...")

    with engine.begin() as conn:
        conn.execute(text("DROP VIEW IF EXISTS player_replacement_view"))

        conn.execute(text("""
            CREATE VIEW player_replacement_view AS
            SELECT
                v.player,
                v.role,
                v.inferred_nationality,
                v.batting_style,
                v.bowling_style,
                v.career_bat_rpa_z,
                v.career_bowl_rpa_z,
                v.career_bat_wpa_z,
                v.career_bowl_wpa_z,
                v.balls_faced,
                v.balls_bowled,
                v.exposure,
                fv.total_value_z,
                fv.confidence,
                fv.final_value,
                fv.days_since_last_match,
                COALESCE(f.form_total_z, 0.0) AS form_total_z,
                COALESCE(f.form_confidence, 0.0) AS form_confidence
            FROM player_vectors v
            LEFT JOIN player_final_values fv ON v.player = fv.player
            LEFT JOIN player_form f ON v.player = f.player
        """))

    print("Created replacement view")


def create_bestxi_view(engine):
    print("Creating player_bestxi_base view...")

    with engine.begin() as conn:
        conn.execute(text("DROP VIEW IF EXISTS player_bestxi_base"))

        conn.execute(text("""
            CREATE VIEW player_bestxi_base AS
            SELECT
                v.player,
                v.role,
                v.inferred_nationality,
                v.career_bat_rpa_z,
                v.career_bowl_rpa_z,
                v.career_bat_wpa_z,
                v.career_bowl_wpa_z,
                v.balls_faced,
                v.balls_bowled,
                v.exposure,
                fv.total_value_z,
                fv.confidence,
                fv.final_value,
                fv.days_since_last_match,
                COALESCE(f.form_total_z, 0.0) AS form_total_z,
                COALESCE(f.form_confidence, 0.0) AS form_confidence
            FROM player_vectors v
            LEFT JOIN player_final_values fv ON v.player = fv.player
            LEFT JOIN player_form f ON v.player = f.player
            WHERE fv.confidence >= 0.5
            AND fv.days_since_last_match <= 730
        """))

    print("Created Best XI view")


def build_db():
    print("\n" + "="*60)
    print("BUILDING ANALYTICS DATABASE (PostgreSQL)")
    print("="*60 + "\n")

    ensure_database_exists()
    engine = get_db_engine()

    drop_existing_views(engine)

    try:
        load_player_vectors(engine)
        load_player_final_values(engine)
        load_player_form(engine)
        load_player_daily_innings(engine)
        load_player_batting_positions(engine)

        load_team_elo(engine)

        load_ball_by_ball_combined(engine)

        create_replacement_view(engine)
        create_bestxi_view(engine)

        print("\n" + "="*60)
        print("PostgreSQL Database BUILT SUCCESSFULLY")
        print("="*60)

    except Exception as e:
        print(f"\nBUILD FAILED: {e}")
        raise


if __name__ == "__main__":
    build_db()