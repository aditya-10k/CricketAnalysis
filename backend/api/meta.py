from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from backend.services.db import get_connection

router = APIRouter(prefix="/api/meta", tags=["Metadata"])


@router.get("/players")
def list_players(
    role: Optional[str] = Query(None),
    nationality: Optional[str] = Query(None),
    active_only: bool = Query(False)
):
    """
    List all players with optional filters.
    """
    conn = get_connection()

    where = []
    params = []

    if role:
        where.append("role = ?")
        params.append(role)

    if nationality:
        where.append("inferred_nationality = ?")
        params.append(nationality)

    if active_only:
        where.append("days_since_last_match <= 365")

    where_clause = f"WHERE {' AND '.join(where)}" if where else ""

    query = f"""
        SELECT
            player,
            role,
            inferred_nationality,
            batting_style,
            bowling_style,
            total_value_z,
            confidence,
            days_since_last_match
        FROM player_final_values
        {where_clause}
        ORDER BY total_value_z DESC
    """

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return {
        "count": len(rows),
        "players": [
            {
                "player": r[0],
                "role": r[1],
                "nationality": r[2],
                "batting_style": r[3],
                "bowling_style": r[4],
                "total_value_z": round(r[5], 3),
                "confidence": round(r[6], 3),
                "days_since_last_match": r[7]
            }
            for r in rows
        ]
    }


@router.get("/teams")
def list_teams():
    """
    List all teams appearing in the database.
    """
    conn = get_connection()

    query = """
        SELECT DISTINCT team FROM (
            SELECT batting_team AS team FROM ball_by_ball
            UNION
            SELECT bowling_team AS team FROM ball_by_ball
            UNION
            SELECT team FROM team_elo
            UNION
            SELECT opponent FROM team_elo
        )
        WHERE team IS NOT NULL
        ORDER BY team
    """

    rows = conn.execute(query).fetchall()
    conn.close()

    return {
        "count": len(rows),
        "teams": [r[0] for r in rows]
    }


@router.get("/player/{player_name}")
def get_player_profile(player_name: str):
    """
    Get complete analytics profile for a player.
    """
    conn = get_connection()

    player = conn.execute("""
        SELECT
            pf.player,
            pf.role,
            pf.inferred_nationality,
            pf.batting_style,
            pf.bowling_style,
            pf.total_value_z,
            pf.final_value,
            pf.confidence,
            pf.days_since_last_match,
            pf.balls_faced,
            pf.balls_bowled,
            pf.runs_scored,
            pf.wickets_taken
        FROM player_final_values pf
        WHERE pf.player = ?
    """, (player_name,)).fetchone()

    if not player:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Player '{player_name}' not found"
        )

    form = conn.execute("""
        SELECT
            form_total_z,
            form_confidence,
            form_as_of_date
        FROM player_form
        WHERE player = ?
    """, (player_name,)).fetchone()

    position = conn.execute("""
        SELECT
            avg_position,
            median_position,
            innings_count
        FROM player_batting_positions
        WHERE player = ?
    """, (player_name,)).fetchone()

    conn.close()

    return {
        "player": player[0],
        "role": player[1],
        "nationality": player[2],
        "styles": {
            "batting": player[3],
            "bowling": player[4]
        },
        "career": {
            "total_value_z": round(player[5], 3),
            "final_value": round(player[6], 3),
            "confidence": round(player[7], 3),
            "days_since_last_match": player[8]
        },
        "exposure": {
            "balls_faced": player[9],
            "balls_bowled": player[10],
            "runs_scored": player[11],
            "wickets_taken": player[12]
        },
        "batting_position": {
            "avg": round(position[0], 2) if position else None,
            "median": round(position[1], 2) if position else None,
            "innings": position[2] if position else 0
        },
        "recent_form": {
            "form_z": round(form[0], 3) if form else 0.0,
            "confidence": round(form[1], 3) if form else 0.0,
            "as_of": form[2] if form else None
        }
    }


@router.get("/teams/{team}")
def team_details(team: str):
    conn = get_connection()

    # Latest ELO
    elo = conn.execute("""
        SELECT 
            AVG(effective_elo) AS elo,
            COUNT(*) AS matches
        FROM team_elo
        WHERE team = ?
    """, (team,)).fetchone()

    if not elo or elo[1] == 0:
        raise HTTPException(status_code=404, detail="Team not found")

    # Venues played
    venues = conn.execute("""
        SELECT DISTINCT venue
        FROM ball_by_ball
        WHERE batting_team = ? OR bowling_team = ?
    """, (team, team)).fetchall()

    conn.close()

    return {
        "team": team,
        "avg_elo": round(elo[0], 1),
        "matches_played": elo[1],
        "venues_played": [v[0] for v in venues]
    }



@router.get("/teams/{team}/elo")
def team_elo_history(team: str):
    conn = get_connection()

    rows = conn.execute("""
        SELECT date, effective_elo
        FROM team_elo
        WHERE team = ?
        ORDER BY date
    """, (team,)).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="Team not found")

    conn.close()

    return {
        "team": team,
        "elo_history": [
            {"date": r[0], "elo": round(r[1], 1)}
            for r in rows
        ]
    }



@router.get("/teams/{team}/players")
def team_players(
    team: str,
    status: str = Query(
        "all",
        description="Filter by player status: all | active | retired"
    ),
    max_days_inactive: int = Query(
        730,
        description="Days since last match to consider retired"
    )
):
    """
    List players of a team with optional retired/active filtering.
    """

    if status not in {"all", "active", "retired"}:
        raise HTTPException(
            status_code=400,
            detail="status must be one of: all, active, retired"
        )

    conn = get_connection()

    # Base query
    query = """
        SELECT
            p.player,
            pv.role,
            pv.batting_style,
            pv.bowling_style,
            COUNT(DISTINCT p.match_id) AS matches_played,
            pf.days_since_last_match
        FROM player_daily_innings p
        JOIN player_vectors pv ON p.player = pv.player
        LEFT JOIN player_final_values pf ON p.player = pf.player
        WHERE p.team = ?
    """

    params = [team]

    # Status filtering
    if status == "active":
        query += " AND pf.days_since_last_match <= ?"
        params.append(max_days_inactive)
    elif status == "retired":
        query += " AND pf.days_since_last_match > ?"
        params.append(max_days_inactive)

    query += """
        GROUP BY p.player
        ORDER BY matches_played DESC
    """

    try:
        rows = conn.execute(query, params).fetchall()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

    conn.close()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Team not found or no players match filter"
        )

    return {
        "team": team,
        "status_filter": status,
        "retirement_threshold_days": max_days_inactive,
        "count": len(rows),
        "players": [
            {
                "player": r[0],
                "role": r[1],
                "batting_style": r[2],
                "bowling_style": r[3],
                "matches_played": r[4],
                "days_since_last_match": r[5],
                "status": (
                    "RETIRED"
                    if r[5] is not None and r[5] > max_days_inactive
                    else "ACTIVE"
                )
            }
            for r in rows
        ]
    }

