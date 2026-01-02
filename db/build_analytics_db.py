# db/build_analytics_db.py
"""
ONE-TIME DATABASE BUILDER
Converts all CSV outputs to SQLite for production API use.
Run once after analytics pipeline completes.
"""

import sqlite3
import pandas as pd

DB_PATH = "analytics.db"

# =====================================================
# PLAYER-LEVEL TABLES
# =====================================================

def load_player_batting_positions(conn):
    """Load pre-calculated batting positions"""
    print("  → Loading player batting positions...")
    
    try:
        df = pd.read_csv("C:/Desktop/crickanal/outputs/player_batting_positions.csv")
        
        required_cols = {"player", "avg_position", "median_position", "innings_count"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        
        df.to_sql("player_batting_positions", conn, if_exists="replace", index=False)
        
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pbp_player ON player_batting_positions(player)")
        
        print(f"    ✓ Loaded {len(df)} player positions")
        
        # Show sample
        sample = df[df['innings_count'] > 50].nlargest(5, 'innings_count')
        print(f"    Sample positions: {list(zip(sample['player'], sample['avg_position']))}")
        
    except FileNotFoundError:
        print("    ⚠ player_batting_positions.csv not found - run calculate_positions.py first")


def load_player_vectors(conn):
    """Load 4D vectors + metadata for similarity matching"""
    print("  → Loading player vectors...")

    vectors_df = pd.read_csv("C:/Desktop/crickanal/outputs/player_vectors_base.csv")

    # Check if metadata columns already exist
    metadata_cols = {"inferred_nationality", "batting_style", "bowling_style"}
    missing_metadata = metadata_cols - set(vectors_df.columns)

    # If metadata missing, merge from player_final_values.csv
    if missing_metadata:
        print(f"    ⚠ Metadata columns missing: {missing_metadata}")
        print("    → Merging from player_final_values.csv...")

        final_values_df = pd.read_csv("C:/Desktop/crickanal/outputs/player_final_values.csv")

        # Check what metadata columns are available
        available_metadata = metadata_cols & set(final_values_df.columns)

        if available_metadata:
            merge_cols = ["player"] + list(available_metadata)
            vectors_df = vectors_df.merge(
                final_values_df[merge_cols],
                on="player",
                how="left"
            )
            print(f"    ✓ Merged columns: {available_metadata}")
        else:
            print("    ⚠ No metadata found in player_final_values.csv either")
            # Add placeholder columns
            for col in missing_metadata:
                vectors_df[col] = None

    # Validate required columns (exclude metadata for now if not available)
    core_required = {
        "player", "role", "exposure",
        "career_bat_rpa_z", "career_bowl_rpa_z",
        "career_bat_wpa_z", "career_bowl_wpa_z",
        "balls_faced", "balls_bowled"
    }

    missing_core = core_required - set(vectors_df.columns)
    if missing_core:
        raise ValueError(f"Missing CORE columns: {missing_core}")

    # Add metadata columns if still missing (with NULL values)
    for col in metadata_cols:
        if col not in vectors_df.columns:
            vectors_df[col] = None
            print(f"    ⚠ Added placeholder column: {col}")

    vectors_df.to_sql("player_vectors", conn, if_exists="replace", index=False)

    # Indexes for fast lookups
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pv_player ON player_vectors(player)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pv_role ON player_vectors(role)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pv_nationality ON player_vectors(inferred_nationality)")

    print(f"    ✓ Loaded {len(vectors_df)} players")


def load_player_final_values(conn):
    """Load final rankings with confidence scores"""
    print("  → Loading player final values...")

    df = pd.read_csv("C:/Desktop/crickanal/outputs/player_final_values.csv")

    required_cols = {
        "player", "role", "total_value_z", "confidence",
        "final_value", "exposure"
    }

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Calculate days since last match if column exists
    if "last_match_played" in df.columns:
        df['last_match_played'] = pd.to_datetime(df['last_match_played'], errors='coerce')
        df['days_since_last_match'] = (pd.Timestamp.now() - df['last_match_played']).dt.days
    else:
        df['days_since_last_match'] = None
        print("    ⚠ last_match_played column not found - set to NULL")

    df.to_sql("player_final_values", conn, if_exists="replace", index=False)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_pfv_player ON player_final_values(player)")

    print(f"    ✓ Loaded {len(df)} players")


def load_player_form(conn):
    """Load rolling 10-inning form overlay"""
    print("  → Loading player form...")

    df = pd.read_csv("C:/Desktop/crickanal/outputs/player_form_overlay.csv")

    required_cols = {"player", "form_total_z", "form_confidence"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df.to_sql("player_form", conn, if_exists="replace", index=False)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_pf_player ON player_form(player)")

    print(f"    ✓ Loaded {len(df)} players")


def load_player_daily_innings(conn):
    """Load player-innings aggregation for PVP/PVT modules"""
    print("  → Loading player daily innings...")

    df = pd.read_csv("C:/Desktop/crickanal/outputs/player_daily_innings_impact.csv")

    df.to_sql("player_daily_innings", conn, if_exists="replace", index=False)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_pdi_player ON player_daily_innings(player)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pdi_match ON player_daily_innings(match_id)")

    print(f"    ✓ Loaded {len(df)} innings")


# =====================================================
# TEAM-LEVEL TABLES
# =====================================================
def load_team_elo(conn):
    """Load team strength ratings for PVT module"""
    print("  → Loading team ELO history...")

    try:
        df = pd.read_csv("C:/Desktop/crickanal/outputs/team_elo_history.csv")
        df.to_sql("team_elo", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_te_team_date ON team_elo(team, date)")
        print(f"    ✓ Loaded {len(df)} ELO records")
    except FileNotFoundError:
        print("    ⚠ team_elo_history.csv not found - skipping (will create in future modules)")


# =====================================================
# BALL-LEVEL DATA (for deep analysis)
# =====================================================
def load_ball_by_ball_combined(conn):
    """Load full ball-by-ball data with RPA+WPA"""
    print("  → Loading ball-by-ball combined data...")

    df = pd.read_csv("C:/Desktop/crickanal/outputs/ball_by_ball_rpa_wpa_combined.csv")

    # ✅ FIX 1: Rename 'batter' to 'striker' for consistency
    if 'batter' in df.columns:
        df.rename(columns={'batter': 'striker'}, inplace=True)
        print("    → Renamed 'batter' to 'striker'")

    # ✅ FIX 2: Create 'player_dismissed' from 'is_wicket' + 'striker'
    # When is_wicket=1, the dismissed player is the striker
    if 'player_dismissed' not in df.columns:
        df['player_dismissed'] = df.apply(
            lambda row: row['striker'] if row.get('is_wicket') == 1 else None,
            axis=1
        )
        print("    → Created 'player_dismissed' column from is_wicket")

    # Validate critical columns
    required = ['striker', 'bowler', 'runs_off_bat', 'venue', 'match_id', 'rpa', 'wpa']
    missing = [col for col in required if col not in df.columns]
    
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df.to_sql("ball_by_ball", conn, if_exists="replace", index=False)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_bbb_match ON ball_by_ball(match_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bbb_striker ON ball_by_ball(striker)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bbb_bowler ON ball_by_ball(bowler)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bbb_venue ON ball_by_ball(venue)")

    print(f"    ✓ Loaded {len(df)} balls")


# =====================================================
# APPLICATION-SPECIFIC VIEWS
# =====================================================
def create_replacement_view(conn):
    """Denormalized view for player replacement engine"""
    print("  → Creating player_replacement_view...")

    conn.execute("DROP VIEW IF EXISTS player_replacement_view")

    conn.execute("""
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
    """)

    print("    ✓ Created replacement view")


def create_bestxi_view(conn):
    """Base view for Best XI optimization"""
    print("  → Creating player_bestxi_base view...")

    conn.execute("DROP VIEW IF EXISTS player_bestxi_base")

    conn.execute("""
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
    """)

    print("    ✓ Created Best XI view")


# =====================================================
# BUILD PIPELINE
# =====================================================
def build_db():
    """Main build pipeline - run once after analytics complete"""
    print("\n" + "="*60)
    print("BUILDING ANALYTICS DATABASE")
    print("="*60 + "\n")

    conn = sqlite3.connect(DB_PATH)

    try:
        # Core player tables
        load_player_vectors(conn)
        load_player_final_values(conn)
        load_player_form(conn)
        load_player_daily_innings(conn)
        load_player_batting_positions(conn)  # ✅ ADD THIS LINE

        # Team tables (optional - may not exist yet)
        load_team_elo(conn)

        # Ball-level data
        load_ball_by_ball_combined(conn)

        # Application views
        create_replacement_view(conn)
        create_bestxi_view(conn)

        conn.commit()

        print("\n" + "="*60)
        print("✅ analytics.db BUILT SUCCESSFULLY")
        print("="*60)

    except Exception as e:
        conn.rollback()
        print(f"\n❌ BUILD FAILED: {e}")
        raise
    finally:
        conn.close()



if __name__ == "__main__":
    build_db()
