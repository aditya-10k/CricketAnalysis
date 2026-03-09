from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.db import get_connection
from end_applications.bestxi_optimizer import optimize_best_xi

router = APIRouter(prefix="/api/bestxi", tags=["Best XI Optimizer"])


class BestXIConstraints(BaseModel):
    max_overseas: Optional[int] = Field(
        default=None,
        description="Maximum overseas players (null = no limit)"
    )
    min_bowlers: int = Field(default=4, ge=1, le=6)
    min_batters: int = Field(default=5, ge=1, le=8)
    min_confidence: float = Field(default=0.3, ge=0.0, le=1.0)

class BestXIRequest(BaseModel):
    home_squad: List[str] = Field(..., min_items=11)
    away_squad: List[str] = Field(..., min_items=11)
    venue: Optional[str] = None
    constraints: Optional[BestXIConstraints] = None

def error_response(
    message: str,
    details: Optional[str] = None,
    suggestion: Optional[str] = None,
    missing_roles: Optional[List[str]] = None
) -> Dict[str, Any]:
    return {
        "error": message,
        "details": details,
        "missing_roles": missing_roles,
        "suggestion": suggestion
    }

@router.post("/optimize")
def optimize_best_xi_api(req: BestXIRequest):
    conn = None
    try:
        conn = get_connection()

        constraints_dict = (
            req.constraints.dict()
            if req.constraints
            else {}
        )

        result = optimize_best_xi(
            conn=conn,
            home_squad=req.home_squad,
            away_squad=req.away_squad,
            venue=req.venue,
            constraints=constraints_dict
        )

        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=error_response(
                    message=result["error"],
                    details=f"Need 11 players, got {len(req.home_squad)}",
                    suggestion="Ensure squad has enough eligible batters and bowlers"
                )
            )

        return result

    finally:
        if conn:
            conn.close()
