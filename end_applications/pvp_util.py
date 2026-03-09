# end_applications/pvp_util.py
"""
PVP (Player vs Player) - Head-to-Head Matchup Engine
Analyzes striker vs bowler historical performance with venue/style context.
"""

import db.session as db
import numpy as np
from typing import Optional, Dict, List

# T20 priors for Bayesian smoothing
T20_PRIOR_BALLS_PER_DISMISSAL = 22.0  # 1 wicket per 22 balls = 4.5%
T20_PRIOR_STRIKE_RATE = 135.0         # T20 global average
T20_PRIOR_WICKET_RATE = 0.045         



def get_head_to_head(
    conn: db.Connection,
    striker: str,
    bowler: str,
    venue: Optional[str] = None
) -> Dict:
    """
    Get complete head-to-head stats between striker and bowler.
    """
    
    # Build query with optional venue filter
    venue_filter = "AND venue = ?" if venue else ""
    params = [striker, striker, bowler]
    if venue:
        params.append(venue)
    
    query = f"""
        SELECT 
            COUNT(*) as balls,
            SUM(runs_off_bat) as runs,
            SUM(CASE WHEN player_dismissed = ? THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN innings = 1 THEN rpa ELSE 0 END) / 
                NULLIF(SUM(CASE WHEN innings = 1 THEN 1 ELSE 0 END), 0) as avg_rpa,
            AVG(wpa) as avg_wpa,
            SUM(CASE WHEN runs_off_bat >= 4 THEN 1 ELSE 0 END) as boundaries,
            COUNT(DISTINCT match_id) as matches
        FROM ball_by_ball
        WHERE striker = ? AND bowler = ?
        {venue_filter}
    """
    
    row = conn.execute(query, params).fetchone()
    
    if not row or row[0] == 0:
        return {
            "striker": striker,
            "bowler": bowler,
            "venue": venue,
            "balls_faced": 0,
            "runs_scored": 0,
            "dismissals": 0,
            "strike_rate": 0.0,
            "avg_wpa": 0.0,
            "avg_rpa": 0.0,
            "dismissal_probability": 0.0,
            "boundaries": 0,
            "matches": 0,
            "sample_size": "INSUFFICIENT"
        }
    
    balls = row[0]
    runs = row[1] or 0
    dismissals = row[2] or 0
    avg_rpa = row[3] or 0.0
    avg_wpa = row[4] or 0.0
    boundaries = row[5] or 0
    matches = row[6] or 0
    
    strike_rate = (runs * 100.0 / balls) if balls > 0 else 0.0
    dismissal_prob = (dismissals / balls) if balls > 0 else 0.0
    
    # Sample size assessment
    if balls >= 30:
        sample = "STRONG"
    elif balls >= 12:
        sample = "MODERATE"
    elif balls >= 6:
        sample = "WEAK"
    else:
        sample = "INSUFFICIENT"
    
    return {
        "striker": striker,
        "bowler": bowler,
        "venue": venue or "ALL",
        "balls_faced": int(balls),
        "runs_scored": int(runs),
        "dismissals": int(dismissals),
        "strike_rate": round(strike_rate, 2),
        "avg_wpa": round(avg_wpa, 4),
        "avg_rpa": round(avg_rpa, 4),
        "dismissal_probability": round(dismissal_prob * 100, 2),
        "boundaries": int(boundaries),
        "boundary_pct": round((boundaries / balls * 100) if balls > 0 else 0, 2),
        "matches": int(matches),
        "sample_size": sample
    }


def predict_matchup(
    conn: db.Connection,
    striker: str,
    bowler: str,
    venue: Optional[str] = None,
    use_style_context: bool = True
) -> Dict:
    """
    Predict matchup outcome using Bayesian inference.
    Combines:
    - Historical head-to-head
    - Player baseline stats
    - Venue-specific performance (if available)
    - Style matchup context (if enabled)
    """
    
    # Get head-to-head stats (venue-specific if provided)
    h2h = get_head_to_head(conn, striker, bowler, venue)
    
    # Get player baselines
    striker_baseline = _get_player_baseline(conn, striker, is_batting=True, venue=venue)
    bowler_baseline = _get_player_baseline(conn, bowler, is_batting=False, venue=venue)
    
    if not striker_baseline or not bowler_baseline:
        return {
            "error": "Player baseline data not found",
            "striker": striker,
            "bowler": bowler
        }
    
    # Get style matchup context
    style_context = None
    if use_style_context:
        style_context = _get_style_matchup(conn, striker, bowler)
    
    # Bayesian weight based on sample size
    h2h_balls = h2h['balls_faced']
    
    if h2h_balls >= 30:
        h2h_weight = 0.7  # Strong evidence
    elif h2h_balls >= 12:
        h2h_weight = 0.5  # Moderate evidence
    elif h2h_balls >= 6:
        h2h_weight = 0.3  # Weak evidence
    else:
        h2h_weight = 0.0  # No evidence
    
    baseline_weight = 1 - h2h_weight
    
    # Predicted strike rate
    if h2h_balls > 0:
        pred_sr = (h2h['strike_rate'] * h2h_weight + 
                   striker_baseline['avg_strike_rate'] * baseline_weight)
    else:
        pred_sr = striker_baseline['avg_strike_rate']

    baseline_dismissal = (1.0 / max(striker_baseline['avg_balls_per_dismissal'], 
                                    T20_PRIOR_BALLS_PER_DISMISSAL)) * 100
    
    if h2h_balls > 0:
        pred_dismissal = (h2h['dismissal_probability'] * h2h_weight + 
                         baseline_dismissal * baseline_weight)
    else:
        pred_dismissal = baseline_dismissal
    
    # Expected WPA impact
    if h2h_balls > 0:
        pred_wpa = (h2h['avg_wpa'] * h2h_weight + 
                   striker_baseline['avg_wpa_per_ball'] * baseline_weight)
    else:
        pred_wpa = striker_baseline['avg_wpa_per_ball']

    sr_zscore = (pred_sr - 135.0) / 20.0
    
    # LOWER dismissal is BETTER for striker, so formula is (average - predicted)
    dismissal_zscore = (4.5 - pred_dismissal) / 1.5
    
    # Weighted score: SR matters more in T20 (60% weight vs 40% for safety)
    advantage_score = (sr_zscore * 0.6) + (dismissal_zscore * 0.4)
    
    # Style adjustment
    style_adjustment = 0.0
    if style_context and style_context.get('advantage_score'):
        style_adjustment = style_context['advantage_score'] * 0.15  # 15% max impact
        advantage_score += style_adjustment
    
    advantage_score = max(-1, min(1, advantage_score))
    
    return {
        "striker": striker,
        "bowler": bowler,
        "venue": venue or "NEUTRAL",
        "historical_data": h2h,
        "striker_baseline": striker_baseline,
        "bowler_baseline": bowler_baseline,
        "style_context": style_context,
        "prediction": {
            "expected_strike_rate": round(pred_sr, 2),
            "dismissal_probability_pct": round(pred_dismissal, 2),
            "expected_wpa_per_ball": round(pred_wpa, 4),
            "confidence": h2h['sample_size'],
            "h2h_weight": round(h2h_weight, 2),
            "baseline_weight": round(baseline_weight, 2),
            "style_adjustment": round(style_adjustment, 3),
            "matchup_advantage": round(advantage_score, 3),
            "advantage_interpretation": _interpret_advantage(advantage_score),
            "sr_zscore": round(sr_zscore, 3),
            "dismissal_zscore": round(dismissal_zscore, 3)
        }
    }



def get_bowler_vs_batters(
    conn: db.Connection,
    bowler: str,
    min_balls: int = 12,
    top_k: int = 10
) -> List[Dict]:
    """
    Find which batters this bowler dominates (or struggles against).
    """
    
    query = """
        SELECT 
            striker,
            COUNT(*) as balls,
            SUM(runs_off_bat) as runs,
            SUM(CASE WHEN player_dismissed = striker THEN 1 ELSE 0 END) as dismissals,
            AVG(wpa) as avg_wpa,
            COUNT(DISTINCT venue) as venues_faced
        FROM ball_by_ball
        WHERE bowler = ?
        GROUP BY striker
        HAVING balls >= ?
        ORDER BY dismissals DESC, avg_wpa ASC
        LIMIT ?
    """
    
    rows = conn.execute(query, (bowler, min_balls, top_k)).fetchall()
    
    results = []
    for row in rows:
        striker, balls, runs, dismissals, avg_wpa, venues = row
        sr = (runs * 100.0 / balls) if balls > 0 else 0
        dismissal_rate = (dismissals / balls * 100) if balls > 0 else 0
        
        results.append({
            "striker": striker,
            "balls_faced": int(balls),
            "runs_conceded": int(runs or 0),
            "dismissals": int(dismissals or 0),
            "strike_rate_allowed": round(sr, 2),
            "dismissal_rate_pct": round(dismissal_rate, 2),
            "avg_wpa": round(avg_wpa or 0, 4),
            "venues_faced_at": int(venues),
            "bowler_performance": "DOMINATES" if dismissal_rate > 4 else "COMPETITIVE"
        })
    
    return results


def get_venue_specific_h2h(
    conn: db.Connection,
    striker: str,
    bowler: str
) -> List[Dict]:
    """
    Get head-to-head stats broken down by venue.
    """

    query = """
        SELECT 
            venue,
            COUNT(*) as balls,
            SUM(runs_off_bat) as runs,
            SUM(CASE WHEN player_dismissed = ? THEN 1 ELSE 0 END) as dismissals
        FROM ball_by_ball
        WHERE striker = ? AND bowler = ?
        GROUP BY venue
        HAVING balls >= 6
        ORDER BY balls DESC
    """
    
    rows = conn.execute(query, (striker, striker, bowler)).fetchall()
    
    results = []
    for venue, balls, runs, dismissals in rows:
        sr = (runs * 100.0 / balls) if balls > 0 else 0
        dismissal_rate = (dismissals / balls * 100) if balls > 0 else 0
        
        results.append({
            "venue": venue,
            "balls": int(balls),
            "runs": int(runs or 0),
            "dismissals": int(dismissals or 0),
            "strike_rate": round(sr, 2),
            "dismissal_rate_pct": round(dismissal_rate, 2)
        })
    
    return results


def _get_player_baseline(
    conn: db.Connection, 
    player: str, 
    is_batting: bool,
    venue: Optional[str] = None
) -> Optional[Dict]:
    """Get player's overall baseline stats (optionally venue-specific)"""
    
    venue_filter = "AND venue = ?" if venue else ""
    params = [player] if not venue else [player, venue]
    
    if is_batting:
        query = f"""
            SELECT 
                SUM(runs_off_bat) * 100.0 / COUNT(*) as avg_sr,
                AVG(wpa) as avg_wpa,
                COUNT(*) as total_balls,
                SUM(CASE WHEN player_dismissed = ? THEN 1 ELSE 0 END) as total_dismissals
            FROM ball_by_ball
            WHERE striker = ?
            {venue_filter}
        """
        
        params_dismissal = [player] + params
        row = conn.execute(query, params_dismissal).fetchone()
        
        if row and row[0]:
            total_balls = row[2]
            total_dismissals = row[3] or 0
            
            if total_dismissals > 0:
                balls_per_dismissal = total_balls / total_dismissals
                balls_per_dismissal = max(balls_per_dismissal, T20_PRIOR_BALLS_PER_DISMISSAL)
            else:
                balls_per_dismissal = T20_PRIOR_BALLS_PER_DISMISSAL
            
            return {
                "avg_strike_rate": round(row[0], 2),
                "avg_wpa_per_ball": round(row[1] or 0, 4),
                "avg_balls_per_dismissal": round(balls_per_dismissal, 2),
                "total_balls": int(total_balls)
            }
    else:
        query = f"""
            SELECT 
                SUM(runs_off_bat) * 1.0 / COUNT(*) as avg_runs_per_ball,
                AVG(wpa) as avg_wpa,
                SUM(CASE WHEN player_dismissed IS NOT NULL THEN 1 ELSE 0 END) * 1.0 / 
                    COUNT(*) as wicket_rate,
                COUNT(*) as total_balls
            FROM ball_by_ball
            WHERE bowler = ?
            {venue_filter}
        """
        
        row = conn.execute(query, params).fetchone()
        
        if row:
            raw_wicket_rate = row[2] or 0
            wicket_rate = max(raw_wicket_rate, T20_PRIOR_WICKET_RATE * 0.5) 
            
            return {
                "avg_runs_per_ball": round(row[0] or 0, 3),
                "avg_economy": round((row[0] or 0) * 6, 2),
                "avg_wpa_per_ball": round(row[1] or 0, 4),
                "wicket_rate": round(wicket_rate, 4),
                "total_balls": int(row[3])
            }
    
    return None


def _get_style_matchup(
    conn: db.Connection,
    striker: str,
    bowler: str
) -> Optional[Dict]:
    """
    Analyze batting style vs bowling style matchup.
    """
    
    # Get styles
    striker_style = conn.execute("""
        SELECT batting_style FROM player_vectors WHERE player = ?
    """, (striker,)).fetchone()
    
    bowler_style = conn.execute("""
        SELECT bowling_style FROM player_vectors WHERE player = ?
    """, (bowler,)).fetchone()
    
    if not striker_style or not bowler_style:
        return None
    
    bat_style = striker_style[0]
    bowl_style = bowler_style[0]
    
    if not bat_style or not bowl_style:
        return None
    
    # Style-based heuristics
    advantage_score = 0.0
    notes = []
    
    # Left-hand bat vs leg-spinner (advantage to batter)
    if 'left' in bat_style.lower() and 'leg' in bowl_style.lower():
        advantage_score += 0.2
        notes.append("LHB vs Leg-spinner: Batter advantage (turning away)")
    
    # Right-hand bat vs left-arm orthodox (slight batter advantage)
    if 'right' in bat_style.lower() and 'left-arm' in bowl_style.lower() and 'orthodox' in bowl_style.lower():
        advantage_score += 0.1
        notes.append("RHB vs Left-arm orthodox: Slight batter advantage")
    
    # Fast bowling vs tail-enders (check if striker is bowler-role)
    striker_role = conn.execute("""
        SELECT role FROM player_vectors WHERE player = ?
    """, (striker,)).fetchone()
    
    if striker_role and striker_role[0] == 'BOWL' and 'fast' in bowl_style.lower():
        advantage_score -= 0.15
        notes.append("Tail-ender vs Pace: Bowler advantage")
    
    return {
        "batting_style": bat_style,
        "bowling_style": bowl_style,
        "advantage_score": round(advantage_score, 3),
        "notes": notes
    }


def _interpret_advantage(score: float) -> str:
    """Interpret matchup advantage score"""
    if score > 0.5:
        return "STRONG STRIKER ADVANTAGE"
    elif score > 0.2:
        return "MODERATE STRIKER ADVANTAGE"
    elif score > -0.2:
        return "BALANCED MATCHUP"
    elif score > -0.5:
        return "MODERATE BOWLER ADVANTAGE"
    else:
        return "STRONG BOWLER ADVANTAGE"
