from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import time

from backend.services.db import get_connection
from end_applications.player_replacement_util import (
    get_player_replacements_smart,
    get_player_info,
)

router = APIRouter(prefix="/api/replacement", tags=["Player Replacement"])

class PlayerReplacementRequest(BaseModel):
    player: str

    role_filter: Optional[str] = None
    nationality_filter: Optional[str] = None
    exclude_players: Optional[List[str]] = None

    top_n: int = 10
    consider_form: bool = True

class ReplacementResult(BaseModel):
    player: str
    role: str
    nationality: str
    similarity_score: float
    career_value: float
    final_value: float
    confidence: float
    days_since_last_match: int
    explanation: str


@router.post("/find")
def find_replacements(req: PlayerReplacementRequest):
    start_time = time.time()
    conn = None

    try:
        conn = get_connection()

        # Load target profile
        target_profile = get_player_info(conn, req.player)
        if target_profile is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Player not found",
                    "player": req.player,
                    "suggestion": "Check player name spelling (use ESPNcricinfo format)"
                }
            )

        # Run replacement engine
        results = get_player_replacements_smart(
            conn=conn,
            target_player=req.player,
            top_k=req.top_n,
            allowed_nationalities=(
                [req.nationality_filter]
                if req.nationality_filter else None
            ),
        )

        if req.exclude_players:
            results = [
                r for r in results
                if r["player"] not in req.exclude_players
            ]

        if req.role_filter:
            results = [
                r for r in results
                if r["role"] == req.role_filter
            ]

        replacements = []
        for r in results:
            replacements.append({
                "player": r["player"],
                "role": r["role"],
                "nationality": r["nationality"],
                "similarity_score": r["similarity_score"],
                "career_value": r["current_value_z"],
                "final_value": r["final_score"],
                "confidence": r["confidence"],
                "days_since_last_match": r["days_since_last_match"],
                "explanation": _build_explanation(r),
            })

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "target_player": req.player,
            "target_profile": {
                "role": target_profile["role"],
                "nationality": target_profile["nationality"],
                "career_value": target_profile["value_z"],
                "confidence": target_profile["confidence"],
                "exposure": target_profile["exposure"],
                "days_since_last_match": target_profile["days_since_last_match"],
            },
            "replacements": replacements[: req.top_n],
            "metadata": {
                "total_candidates": len(results),
                "filtered_count": len(replacements),
                "search_time_ms": elapsed_ms,
            },
        }

    finally:
        if conn:
            conn.close()


def _build_explanation(r: dict) -> str:
    if r["similarity_score"] > 0.9:
        return "Very high similarity in performance profile"
    if r["form_adjustment"] > 0:
        return "Strong recent form boosts overall value"
    if r["style_bonus"] > 0:
        return "Matching playing style provides added suitability"
    return "Balanced replacement with similar role profile"
