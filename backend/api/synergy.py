from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.db import get_connection
from end_applications.synergy_util import (
    get_batting_partnership,
    get_bowling_combination
)

router = APIRouter(prefix="/api/synergy", tags=["Synergy"])


def sample_to_confidence(sample: str) -> float:
    return {
        "STRONG": 0.9,
        "MODERATE": 0.7,
        "WEAK": 0.5,
        "INSUFFICIENT": 0.2
    }.get(sample, 0.2)


def sample_to_label(sample: str) -> str:
    return {
        "STRONG": "HIGH",
        "MODERATE": "MEDIUM",
        "WEAK": "LOW",
        "INSUFFICIENT": "INSUFFICIENT"
    }.get(sample, "INSUFFICIENT")


class BattingSynergyRequest(BaseModel):
    batter1: str
    batter2: str
    venue: Optional[str] = None

@router.post("/batting")
def batting_synergy(req: BattingSynergyRequest):
    conn = None
    try:
        conn = get_connection()

        stats = get_batting_partnership(
            conn=conn,
            player_a=req.batter1,
            player_b=req.batter2,
            venue=req.venue
        )

        if stats["balls_together"] == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Insufficient partnership data",
                    "batter1": req.batter1,
                    "batter2": req.batter2
                }
            )

        return {
            "batter1": req.batter1,
            "batter2": req.batter2,
            "partnership": {
                "innings_together": stats["innings_together"],
                "partnership_runs": stats["runs_together"],
                "balls_together": stats["balls_together"],
                "partnership_rate": round(stats["partnership_sr"] / 6, 2),
                "avg_partnership": stats["avg_partnership"],
                "highest_partnership": stats["best_partnership"],
            },
            "synergy_analysis": {
                "synergy_score": stats["synergy_score"],
                "rating": stats["synergy_rating"],
                "compatibility": (
                    "High complementary batting styles"
                    if stats["synergy_score"] > 0.15 else
                    "Moderate compatibility"
                    if stats["synergy_score"] > 0.05 else
                    "Low partnership impact"
                )
            },
            "individual_when_together": {
                "batter1": {
                    "strike_rate": stats["player_a_solo_sr"]
                },
                "batter2": {
                    "strike_rate": stats["player_b_solo_sr"]
                }
            },
            "sample_quality": sample_to_label(stats["sample_quality"]),
            "confidence": sample_to_confidence(stats["sample_quality"])
        }

    finally:
        if conn:
            conn.close()


class BowlingSynergyRequest(BaseModel):
    bowler1: str
    bowler2: str
    venue: Optional[str] = None
    phase: Optional[str] = None

@router.post("/bowling")
def bowling_synergy(req: BowlingSynergyRequest):
    conn = None
    try:
        conn = get_connection()

        stats = get_bowling_combination(
            conn=conn,
            bowler_a=req.bowler1,
            bowler_b=req.bowler2,
            phase=req.phase,
            venue=req.venue
        )

        if stats["balls_together"] == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Insufficient bowling combination data",
                    "bowler1": req.bowler1,
                    "bowler2": req.bowler2
                }
            )

        return {
            "bowler1": req.bowler1,
            "bowler2": req.bowler2,
            "combination": {
                "matches_together": stats["matches_together"],
                "balls_together": stats["balls_together"],
                "combined_wickets": stats["wickets"],
                "combined_economy": stats["combined_economy"],
                "partnership_strike_rate": stats["combined_strike_rate"],
                "dot_ball_percentage": stats["dot_pct"]
            },
            "synergy_analysis": {
                "synergy_score": stats["synergy_score"],
                "rating": stats["synergy_rating"],
                "explanation": (
                    "Strong complementary bowling styles"
                    if stats["synergy_score"] > 0.15 else
                    "Decent control and pressure"
                    if stats["synergy_score"] > 0.05 else
                    "Limited combined impact"
                )
            },
            "wicket_partnership": {
                "wicket_clustering": stats["wicket_clustering"]
            },
            "sample_quality": sample_to_label(stats["sample_quality"]),
            "confidence": sample_to_confidence(stats["sample_quality"])
        }

    finally:
        if conn:
            conn.close()
