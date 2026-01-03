'''
Docstring for backend.api.pvt

| Feature             | Status         |
| ------------------- | -------------- |
| Core PVT stats      | Implemented    |
| WPA-primary scoring | Implemented    |
| Sample quality      | Implemented    |
| Phase split         | Needs new SQL  |
| Style split         | Needs new SQL  |
| Key dismissals      | Needs new SQL  |
| Venue home/away     | Needs metadata |

'''

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.db import get_connection
from end_applications.pvt_util import (
    get_player_vs_team_batting,
    get_player_vs_team_bowling,
)

router = APIRouter(prefix="/api/pvt", tags=["Player vs Team"])

def _confidence_from_sample(sample: str) -> str:
    if sample == "STRONG":
        return "HIGH"
    if sample == "MODERATE":
        return "MEDIUM"
    if sample == "WEAK":
        return "LOW"
    return "INSUFFICIENT"


def _rating_map(rating: str) -> str:
    mapping = {
        "EXCELLENT": "EXCELLENT",
        "ABOVE_AVERAGE": "GOOD",
        "AVERAGE": "AVERAGE",
        "BELOW_AVERAGE": "POOR",
    }
    return mapping.get(rating, "UNKNOWN")


class PVTBatterRequest(BaseModel):
    batter: str
    team: str
    venue: Optional[str] = None
    phase: Optional[str] = "all"  # accepted but not used yet

@router.post("/batter")
def batter_vs_team(req: PVTBatterRequest):
    conn = None
    try:
        conn = get_connection()

        stats = get_player_vs_team_batting(
            conn=conn,
            player=req.batter,
            opponent_team=req.team,
            venue=req.venue,
        )

        if stats["balls_faced"] == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Insufficient data",
                    "batter": req.batter,
                    "team": req.team,
                },
            )

        return {
            "batter": req.batter,
            "team": req.team,
            "venue": req.venue or "ALL",
            "performance": {
                "innings_played": stats["innings"],
                "runs_scored": stats["runs_scored"],
                "balls_faced": stats["balls_faced"],
                "dismissals": stats["dismissals"],
                "average": stats["average"],
                "strike_rate": stats["strike_rate"],
                "boundary_percentage": stats["boundary_pct"],
                "avg_rpa": stats["strike_rate"] / 100,
                "avg_wpa": stats["wpa_per_ball"],
                "performance_rating": _rating_map(stats["performance_rating"]),
            },
            "confidence": _confidence_from_sample(stats["sample_quality"]),
        }

    finally:
        if conn:
            conn.close()


class PVTBowlerRequest(BaseModel):
    bowler: str
    team: str
    venue: Optional[str] = None
    phase: Optional[str] = "all"  # accepted but not used yet

@router.post("/bowler")
def bowler_vs_team(req: PVTBowlerRequest):
    conn = None
    try:
        conn = get_connection()

        stats = get_player_vs_team_bowling(
            conn=conn,
            player=req.bowler,
            opponent_team=req.team,
            venue=req.venue,
        )

        if stats["balls_bowled"] == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Insufficient data",
                    "bowler": req.bowler,
                    "team": req.team,
                },
            )

        return {
            "bowler": req.bowler,
            "team": req.team,
            "venue": req.venue or "ALL",
            "performance": {
                "innings_bowled": stats["matches"],
                "balls_bowled": stats["balls_bowled"],
                "runs_conceded": stats["runs_conceded"],
                "wickets": stats["wickets"],
                "economy": stats["economy"],
                "strike_rate": stats["strike_rate"],
                "average": stats["average"],
                "dot_ball_percentage": stats["dot_pct"],
                "avg_rpa": -stats["economy"] / 6,
                "avg_wpa": stats["wpa_per_ball"],
                "performance_rating": _rating_map(stats["performance_rating"]),
            },
            "confidence": _confidence_from_sample(stats["sample_quality"]),
        }

    finally:
        if conn:
            conn.close()
