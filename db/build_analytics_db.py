# db/build_analytics_db.py

import sqlite3
import pandas as pd

DB_PATH = "analytics.db"


# =====================================================
# PLAYER-LEVEL TABLES
# =====================================================
def load_player_vectors(conn):
    vectors_df = pd.read_csv("outputs/player_vectors_base.csv")
    nationality_df = pd.read_csv(
        "outputs/player_total_value_master_enriched_final.csv",
        usecols=["player", "inferred_nationality"]
    )

    vectors_df = vectors_df.merge(
        nationality_df,
        on="player",
        how="left"
    )

    required_cols = {
        "player",
        "career_bat_rpa_z",
        "career_bowl_rpa_z",
        "career_bat_wpa_z",
        "career_bowl_wpa_z",
        "total_value_z",
        "role",
        "days_since_last_match",
        "inferred_nationality"
    }

    missing = required_cols - set(vectors_df.columns)
    if missing:
        raise ValueError(f"Missing columns in player_vectors table: {missing}")

    vectors_df.to_sql("player_vectors", conn, if_exists="replace", index=False)



def load_player_form(conn):
    df = pd.read_csv("outputs/player_form_overlay.csv")

    required_cols = {
        "player",
        "form_total_z",
        "form_confidence"
    }

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in player_form_overlay.csv: {missing}")

    df.to_sql("player_form", conn, if_exists="replace", index=False)

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_player_form_player ON player_form(player)"
    )


# =====================================================
# TEAM-LEVEL TABLES (future use)
# =====================================================
def load_team_elo(conn):
    df = pd.read_csv("outputs/team_elo_history.csv")

    df.to_sql("team_elo", conn, if_exists="replace", index=False)

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_team_elo_team_date ON team_elo(team, date)"
    )


# =====================================================
# BUILD DATABASE
# =====================================================
def build_db():
    conn = sqlite3.connect(DB_PATH)

    print("Loading player vectors...")
    load_player_vectors(conn)

    print("Loading player form...")
    load_player_form(conn)

    print("Loading team elo...")
    load_team_elo(conn)

    conn.commit()
    conn.close()

    print("\nanalytics.db built successfully")


if __name__ == "__main__":
    build_db()
