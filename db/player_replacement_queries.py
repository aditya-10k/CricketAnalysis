"""
Database queries used by player replacement analytics.

This module contains ONLY SQL + data selection logic.
No ML, no numpy, no FastAPI code.
"""

from typing import List, Optional


# --------------------------------------------------
# Target player helpers
# --------------------------------------------------

def get_target_player_role(conn, target_player: str) -> str:
    row = conn.execute(
        """
        SELECT role
        FROM player_vectors
        WHERE player = ?
        """,
        (target_player,)
    ).fetchone()

    if row is None:
        raise ValueError(f"Target player '{target_player}' not found")

    return row[0]


# --------------------------------------------------
# Candidate selection
# --------------------------------------------------

def get_candidate_players(
    conn,
    target_player: str,
    *,
    exclude_retired: bool = True,
    max_days_since_last_match: int = 365,
    allowed_nationalities: Optional[List[str]] = None,
) -> List[str]:
    """
    Return a list of candidate player names eligible to replace the target player.
    """

    role = get_target_player_role(conn, target_player)

    query = """
        SELECT player
        FROM player_vectors
        WHERE role = ?
          AND player != ?
    """

    # 👇 IMPORTANT FIX: heterogeneous SQL params
    params: list[object] = [role, target_player]

    # Retired / inactive constraint
    if exclude_retired:
        query += " AND days_since_last_match <= ?"
        params.append(max_days_since_last_match)

    # Nationality constraint
    if allowed_nationalities:
        placeholders = ",".join("?" for _ in allowed_nationalities)
        query += f" AND inferred_nationality IN ({placeholders})"
        params.extend(allowed_nationalities)

    rows = conn.execute(query, tuple(params)).fetchall()
    return [r[0] for r in rows]


# --------------------------------------------------
# Bulk data loaders
# --------------------------------------------------

def load_player_vectors(conn):
    return conn.execute(
        """
        SELECT
            player,
            career_bat_rpa_z,
            career_bowl_rpa_z,
            career_bat_wpa_z,
            career_bowl_wpa_z,
            total_value_z,
            role,
            inferred_nationality,
            days_since_last_match,
            balls_faced,
            balls_bowled
        FROM player_vectors
        """
    ).fetchall()


def load_player_form(conn):
    return conn.execute(
        """
        SELECT
            player,
            form_total_z,
            form_confidence
        FROM player_form
        """
    ).fetchall()
