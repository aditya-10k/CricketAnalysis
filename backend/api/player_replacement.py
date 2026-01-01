from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.db import get_connection
from end_applications.player_replacement import get_player_replacements

router = APIRouter(tags=["Player Replacement"])

class PlayerReplacementRequest(BaseModel):
    target_player: str = Field(..., example="V Kohli")
    top_k: int = Field(10, ge=1, le=50)
    allowed_nationalities: Optional[List[str]] = None
    exclude_retired: bool = True
    max_days_since_last_match: int = Field(365, ge=0)
    form_cap: float = Field(0.3, ge=0.0, le=1.0)
    exposure_cap: int = Field(3000, ge=0)


@router.post("/player-replacements")
def player_replacements(req: PlayerReplacementRequest):
    conn = None
    try:
        conn = get_connection()

        results = get_player_replacements(
            conn=conn,
            target_player=req.target_player,
            top_k=req.top_k,
            allowed_nationalities=req.allowed_nationalities,
            exclude_retired=req.exclude_retired,
            max_days_since_last_match=req.max_days_since_last_match,
            form_cap=req.form_cap,
            exposure_cap=req.exposure_cap,
        )

        return {
            "target_player": req.target_player,
            "count": len(results),
            "results": results,
        }

    except ValueError as e:
        # Player not found, etc.
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        # Unexpected error
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if conn:
            conn.close()
