# end_applications/player_replacement_util.py
"""
PLAYER REPLACEMENT ENGINE
Uses Euclidean distance in 4D z-score space with constraint matching.
"""

import db.session as db
import numpy as np
from typing import Optional

# Global constants (match handover spec)
MIN_CONFIDENCE = 0.6        
MAX_VALUE_DROP = 0.2        
FORM_WEIGHT = 0.15          
MAX_DAYS_INACTIVE = 365     

VECTOR_COLS = [
    "career_bat_rpa_z",
    "career_bowl_rpa_z",
    "career_bat_wpa_z",
    "career_bowl_wpa_z"
]


def get_player_replacements(
    conn: db.Connection,
    target_player: str,
    top_k: int = 10,
    allowed_nationalities: Optional[list[str]] = None,
    exclude_inactive: bool = True,
    match_batting_style: bool = False,
    match_bowling_style: bool = False,
    min_confidence: float = MIN_CONFIDENCE,
    max_value_drop: float = MAX_VALUE_DROP,
) -> list[dict]:
    """Find top-k similar players as replacements"""
    
    target = _load_target_player(conn, target_player)
    if target is None:
        raise ValueError(f"Target player '{target_player}' not found in database")
    
    candidates = _load_candidate_pool(
        conn=conn,
        target_role=target["role"],
        target_player=target_player,
        allowed_nationalities=allowed_nationalities,
        exclude_inactive=exclude_inactive,
        min_confidence=min_confidence
    )
    
    results = []
    
    for candidate in candidates:
        value_delta = candidate["total_value_z"] - target["total_value_z"]
        if value_delta < -max_value_drop:
            continue
        
        distance = np.linalg.norm(target["vector"] - candidate["vector"])
        similarity_score = 1 / (1 + distance)
        
        form_boost = candidate["form_total_z"] * candidate["form_confidence"] * FORM_WEIGHT
        form_boost = max(-0.15, min(0.15, form_boost))
        
        style_bonus = 0.0
        if match_batting_style and candidate["batting_style"] == target["batting_style"]:
            if candidate["batting_style"] is not None:
                style_bonus += 0.05
        if match_bowling_style and candidate["bowling_style"] == target["bowling_style"]:
            if candidate["bowling_style"] is not None:
                style_bonus += 0.05
        
        final_score = similarity_score * (1 + form_boost + style_bonus)
        
        results.append({
            "player": candidate["player"],
            "role": candidate["role"],
            "nationality": candidate["nationality"],
            "batting_style": candidate["batting_style"],
            "bowling_style": candidate["bowling_style"],
            "exposure": candidate["exposure"],
            "days_since_last_match": candidate["days_since_last_match"],
            "confidence": round(candidate["confidence"], 3),
            "distance": round(distance, 4),
            "similarity_score": round(similarity_score, 4),
            "form_adjustment": round(form_boost, 4),
            "style_bonus": round(style_bonus, 4),
            "value_delta": round(value_delta, 4),
            "final_score": round(final_score, 4),
            "current_value_z": round(candidate["total_value_z"], 4),
            "target_value_z": round(target["total_value_z"], 4),
        })
    
    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results[:top_k]


def _load_target_player(conn: db.Connection, player_name: str) -> Optional[dict]:
    """Load target player's vector and metadata"""
    
    query = f"""
        SELECT 
            player, role, inferred_nationality, batting_style, bowling_style,
            {', '.join(VECTOR_COLS)},
            total_value_z, confidence, exposure, days_since_last_match
        FROM player_replacement_view
        WHERE player = ?
    """
    
    row = conn.execute(query, (player_name,)).fetchone()
    if row is None:
        return None
    
    return {
        "player": row[0],
        "role": row[1],
        "nationality": row[2],
        "batting_style": row[3],
        "bowling_style": row[4],
        "vector": np.array(row[5:9], dtype=float),
        "total_value_z": float(row[9]),
        "confidence": float(row[10]),
        "exposure": int(row[11] or 0),
        "days_since_last_match": int(row[12] or 999),
    }


def _load_candidate_pool(
    conn: db.Connection,
    target_role: str,
    target_player: str,
    allowed_nationalities: Optional[list[str]],
    exclude_inactive: bool,
    min_confidence: float
) -> list[dict]:
    """Load and filter candidate pool"""
    
    conditions = [
        "player != ?",
        "role = ?",
        f"confidence >= {min_confidence}"
    ]
    params = [target_player, target_role]
    
    if exclude_inactive:
        conditions.append(f"days_since_last_match <= {MAX_DAYS_INACTIVE}")
    
    if allowed_nationalities:
        placeholders = ','.join('?' * len(allowed_nationalities))
        conditions.append(f"inferred_nationality IN ({placeholders})")
        params.extend(allowed_nationalities)
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT 
            player, role, inferred_nationality, batting_style, bowling_style,
            {', '.join(VECTOR_COLS)},
            total_value_z, confidence, form_total_z, form_confidence,
            exposure, days_since_last_match
        FROM player_replacement_view
        WHERE {where_clause}
    """
    
    rows = conn.execute(query, params).fetchall()
    
    candidates = []
    for row in rows:
        candidates.append({
            "player": row[0],
            "role": row[1],
            "nationality": row[2],
            "batting_style": row[3],
            "bowling_style": row[4],
            "vector": np.array(row[5:9], dtype=float),
            "total_value_z": float(row[9]),
            "confidence": float(row[10]),
            "form_total_z": float(row[11] or 0.0),
            "form_confidence": float(row[12] or 0.0),
            "exposure": int(row[13] or 0),
            "days_since_last_match": int(row[14] or 999),
        })
    
    return candidates


def get_player_info(conn: db.Connection, player_name: str) -> Optional[dict]:
    """Get player summary for API responses"""
    
    query = """
        SELECT 
            player, role, inferred_nationality, batting_style, bowling_style,
            total_value_z, final_value, confidence, exposure, days_since_last_match
        FROM player_replacement_view
        WHERE player = ?
    """
    
    row = conn.execute(query, (player_name,)).fetchone()
    if row is None:
        return None
    
    return {
        "player": row[0],
        "role": row[1],
        "nationality": row[2],
        "batting_style": row[3],
        "bowling_style": row[4],
        "value_z": round(row[5], 4),
        "final_value": round(row[6], 4),
        "confidence": round(row[7], 3),
        "exposure": int(row[8]),
        "days_since_last_match": int(row[9] or 999),
    }


def list_available_nationalities(conn: db.Connection) -> list[str]:
    """Get list of all nationalities in database"""
    
    rows = conn.execute("""
        SELECT DISTINCT inferred_nationality
        FROM player_vectors
        WHERE inferred_nationality IS NOT NULL
        ORDER BY inferred_nationality
    """).fetchall()
    
    return [row[0] for row in rows]

def get_player_replacements_smart(
    conn: db.Connection,
    target_player: str,
    top_k: int = 10,
    allowed_nationalities: Optional[list[str]] = None,
    exclude_inactive: bool = True,
    match_batting_style: bool = False,
    match_bowling_style: bool = False,
) -> list[dict]:
    """
    Smart wrapper that auto-adjusts filters based on player value.
    
    Uses adaptive thresholds:
    - Elite players (z > 1.0): max_value_drop = 0.8, min_confidence = 0.5
    - Good players (z > 0.5): max_value_drop = 0.5, min_confidence = 0.6
    - Average players: max_value_drop = 0.2, min_confidence = 0.6
    """
    
    target = _load_target_player(conn, target_player)
    if target is None:
        raise ValueError(f"Target player '{target_player}' not found")
    
    target_value = target["total_value_z"]
    
    if target_value > 1.0:
        #Elite player
        max_value_drop = 0.8
        min_confidence = 0.5
        tier = "ELITE"
    elif target_value > 0.5:
        # Good player
        max_value_drop = 0.5
        min_confidence = 0.6
        tier = "GOOD"
    else:
        # Average player
        max_value_drop = 0.3
        min_confidence = 0.6
        tier = "AVERAGE"
    
    results = get_player_replacements(
        conn=conn,
        target_player=target_player,
        top_k=top_k,
        allowed_nationalities=allowed_nationalities,
        exclude_inactive=exclude_inactive,
        match_batting_style=match_batting_style,
        match_bowling_style=match_bowling_style,
        min_confidence=min_confidence,
        max_value_drop=max_value_drop
    )
    
    if len(results) == 0 and exclude_inactive:
        results = get_player_replacements(
            conn=conn,
            target_player=target_player,
            top_k=top_k,
            allowed_nationalities=allowed_nationalities,
            exclude_inactive=False,
            match_batting_style=match_batting_style,
            match_bowling_style=match_bowling_style,
            min_confidence=min_confidence,
            max_value_drop=max_value_drop
        )
    
    # Add metadata about filters used
    for r in results:
        r['_filter_tier'] = tier
        r['_max_value_drop_used'] = max_value_drop
        r['_min_confidence_used'] = min_confidence
    
    return results
