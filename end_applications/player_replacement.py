# end_applications/player_replacement.py

import numpy as np
from end_applications.analytics_adjustment.confidence import exposure_confidence

VECTOR_COLS = [
    "career_bat_rpa_z",
    "career_bowl_rpa_z",
    "career_bat_wpa_z",
    "career_bowl_wpa_z",
]

# -----------------------
# Math
# -----------------------
def cosine_similarity(a, b) -> float:
    return float(
        np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    )


# -----------------------
# Data loaders
# -----------------------
def load_player_vectors(conn):
    rows = conn.execute(
        f"""
        SELECT
            player,
            {", ".join(VECTOR_COLS)},
            total_value_z,
            role,
            inferred_nationality,
            days_since_last_match,
            balls_faced,
            balls_bowled
        FROM player_vectors
        """
    ).fetchall()

    data = {}
    dim = len(VECTOR_COLS)

    for r in rows:
        data[r[0]] = {
            "vector": np.array(r[1:1 + dim], dtype=float),
            "total_value_z": float(r[1 + dim]),
            "role": r[2 + dim],
            "nationality": r[3 + dim],
            "days_since_last_match": r[4 + dim],
            "balls_faced": r[5 + dim] or 0,
            "balls_bowled": r[6 + dim] or 0,
        }
    return data


def load_player_form(conn):
    rows = conn.execute(
        """
        SELECT player, form_total_z, form_confidence
        FROM player_form
        """
    ).fetchall()

    return {
        r[0]: {
            "form_z": float(r[1]),
            "confidence": float(r[2]),
        }
        for r in rows
    }


# -----------------------
# Production replacement engine
# -----------------------
def get_player_replacements(
    conn,
    target_player: str,
    top_k: int = 10,
    allowed_nationalities: list[str] | None = None,
    exclude_retired: bool = True,
    max_days_since_last_match: int = 365,
    form_cap: float = 0.3,
    exposure_cap: int = 3000,
) -> list[dict]:

    vectors = load_player_vectors(conn)
    forms = load_player_form(conn)

    if target_player not in vectors:
        raise ValueError(f"Target player '{target_player}' not found")

    target = vectors[target_player]
    target_vec = target["vector"]
    target_value = target["total_value_z"]
    target_role = target["role"]

    results = []

    for player, info in vectors.items():
        if player == target_player:
            continue

        # ---- Role constraint
        if info["role"] != target_role:
            continue

        # ---- Retired / inactive constraint
        if exclude_retired and info["days_since_last_match"] > max_days_since_last_match:
            continue

        # ---- Nationality constraint
        if allowed_nationalities is not None:
            if info["nationality"] not in allowed_nationalities:
                continue

        # ---- Similarity
        sim = cosine_similarity(target_vec, info["vector"])

        # ---- Form adjustment (capped)
        form = forms.get(player, {"form_z": 0.0, "confidence": 0.0})
        raw_form = form["form_z"] * form["confidence"]
        form_adj = 1 + max(-form_cap, min(form_cap, raw_form))

        # ---- Exposure-based confidence (CENTRALIZED)
        confidence = exposure_confidence(
            info["balls_faced"],
            info["balls_bowled"],
            cap=exposure_cap
        )

        final_score = sim * form_adj * confidence
        delta = info["total_value_z"] - target_value

        results.append({
            "player": player,
            "role": info["role"],
            "nationality": info["nationality"],
            "days_since_last_match": info["days_since_last_match"],
            "exposure": info["balls_faced"] + info["balls_bowled"],
            "similarity": round(sim, 4),
            "form_adjustment": round(form_adj, 4),
            "confidence": round(confidence, 4),
            "expected_value_delta": round(delta, 4),
            "final_score": round(final_score, 4),
        })

    return sorted(results, key=lambda x: x["final_score"], reverse=True)[:top_k]
