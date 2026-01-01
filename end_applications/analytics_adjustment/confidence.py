# analytics/confidence.py

import numpy as np

def exposure_confidence(
    balls_faced: int | None,
    balls_bowled: int | None,
    cap: int = 3000
) -> float:
    """
    Converts player exposure into a confidence score in [0, 1].
    Exposure = balls_faced + balls_bowled.
    Confidence saturates after `cap` balls.
    """
    bf = balls_faced or 0
    bb = balls_bowled or 0
    exposure = bf + bb

    if exposure <= 0:
        return 0.0

    return float(np.sqrt(min(exposure, cap) / cap))
