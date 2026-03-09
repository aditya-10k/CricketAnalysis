from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.db import get_connection
from end_applications.pvp_util import (
    get_head_to_head,
    predict_matchup,
)

router = APIRouter(prefix="/api/pvp", tags=["Player vs Player"])


class PVPPredictRequest(BaseModel):
    batter: str
    bowler: str
    venue: Optional[str] = None
    recent_matches_only: bool = False


def _confidence_from_sample(sample_size: str) -> str:
    if sample_size == "STRONG":
        return "HIGH"
    if sample_size == "MODERATE":
        return "MEDIUM"
    if sample_size == "WEAK":
        return "LOW"
    return "INSUFFICIENT"


@router.post("/predict")
def predict_pvp(req: PVPPredictRequest):
    conn = None

    try:
        conn = get_connection()

        # Head-to-head stats
        h2h = get_head_to_head(
            conn=conn,
            striker=req.batter,
            bowler=req.bowler,
            venue=req.venue,
        )

        # Insufficient data check
        if h2h["balls_faced"] < 10:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Insufficient data for matchup prediction",
                    "batter": req.batter,
                    "bowler": req.bowler,
                    "balls_faced": h2h["balls_faced"],
                    "minimum_required": 10,
                    "suggestion": "Not enough historical data between these players",
                }
            )

        # Predict matchup
        prediction = predict_matchup(
            conn=conn,
            striker=req.batter,
            bowler=req.bowler,
            venue=req.venue,
        )

        pred = prediction["prediction"]
        sample_quality = _confidence_from_sample(pred["confidence"])

        # Winner logic
        winner = "batter" if pred["matchup_advantage"] > 0 else "bowler"

        return {
            "batter": req.batter,
            "bowler": req.bowler,
            "venue": req.venue or "NEUTRAL",
            "prediction": {
                "expected_runs_per_ball": round(pred["expected_strike_rate"] / 100, 2),
                "expected_dismissal_rate": round(pred["dismissal_probability_pct"] / 100, 3),
                "matchup_advantage": pred["matchup_advantage"],
                "confidence": sample_quality,
                "winner": winner,
            },
            "historical_data": {
                "balls_faced": h2h["balls_faced"],
                "runs_scored": h2h["runs_scored"],
                "dismissals": h2h["dismissals"],
                "strike_rate": h2h["strike_rate"],
                "average": round(
                    (h2h["runs_scored"] / max(h2h["dismissals"], 1)), 2
                ),
                "boundary_percentage": h2h["boundary_pct"],
            },
            "context": {
                "batter_career_avg_rpa": prediction["striker_baseline"]["avg_strike_rate"] / 100,
                "bowler_career_avg_rpa": prediction["bowler_baseline"]["avg_runs_per_ball"],
                "venue_factor": 0.0 if not req.venue else 0.08,
                "style_matchup": (
                    prediction["style_context"]["notes"]
                    if prediction.get("style_context")
                    else None
                ),
            },
            "sample_quality": sample_quality,
        }

    finally:
        if conn:
            conn.close()
