# end_applications/synergy_util.py
"""
SYNERGY - Partnership Analysis Engine
Analyzes how players perform together vs separately.

FIXES APPLIED:
- Correct partnership calculation (innings-level, not ball-level)
- Safe None handling throughout
- Proper strike rate calculation
- Complete bowling combination logic
"""

import db.session as db
import numpy as np
from typing import Optional, Dict, List, Tuple
from collections import defaultdict


# Sample quality thresholds
PARTNERSHIP_STRONG = 50   # 50+ balls together
PARTNERSHIP_MODERATE = 25
PARTNERSHIP_WEAK = 10

BOWLING_COMBO_STRONG = 60  # 10+ overs together
BOWLING_COMBO_MODERATE = 30
BOWLING_COMBO_WEAK = 12


# =====================================================
# BATTING PARTNERSHIPS
# =====================================================

def get_batting_partnership(
    conn: db.Connection,
    player_a: str,
    player_b: str,
    venue: Optional[str] = None
) -> Dict:
    """
    Get detailed batting partnership stats between two players.
    
    Args:
        player_a: First batter name
        player_b: Second batter name
        venue: Optional venue filter
        
    Returns:
        Complete partnership statistics
    """
    
    venue_filter = "AND venue = ?" if venue else ""
    params = [player_a, player_b]
    if venue:
        params.append(venue)
    
    # ✅ FIXED: Count innings where both played, aggregate their individual contributions
    query = f"""
        WITH innings_together AS (
            SELECT match_id, innings, venue
            FROM ball_by_ball
            WHERE striker IN (?, ?)
            {venue_filter}
            GROUP BY match_id, innings
            HAVING COUNT(DISTINCT striker) = 2
        ),
        player_contributions AS (
            SELECT 
                b.match_id,
                b.innings,
                COUNT(*) as balls_faced,
                SUM(b.runs_off_bat) as runs_scored,
                SUM(b.wpa) as wpa,
                SUM(CASE WHEN b.runs_off_bat >= 4 THEN 1 ELSE 0 END) as boundaries
            FROM ball_by_ball b
            INNER JOIN innings_together it
                ON b.match_id = it.match_id
                AND b.innings = it.innings
            WHERE b.striker IN (?, ?)
            {venue_filter}
            GROUP BY b.match_id, b.innings
        )
        SELECT 
            COUNT(DISTINCT match_id) as matches,
            COUNT(*) as innings,
            SUM(balls_faced) as total_balls,
            SUM(runs_scored) as total_runs,
            SUM(wpa) as total_wpa,
            SUM(boundaries) as total_boundaries,
            AVG(runs_scored) as avg_partnership,
            MAX(runs_scored) as best_partnership
        FROM player_contributions
    """
    
    query_params = params + params
    if venue:
        query_params.append(venue)
    
    row = conn.execute(query, query_params).fetchone()
    
    # ✅ FIXED: Safe None handling
    if not row or row[2] is None or row[2] == 0:  # total_balls
        return {
            "player_a": player_a,
            "player_b": player_b,
            "venue": venue or "ALL",
            "matches_together": 0,
            "innings_together": 0,
            "balls_together": 0,
            "runs_together": 0,
            "partnership_sr": 0.0,
            "total_wpa": 0.0,
            "wpa_per_ball": 0.0,
            "boundaries_together": 0,
            "avg_partnership": 0.0,
            "best_partnership": 0,
            "player_a_solo_sr": 0,
            "player_b_solo_sr": 0,
            "synergy_boost": 0.0,
            "synergy_score": 0.0,
            "synergy_rating": "NO_DATA",
            "hand_combination": "UNKNOWN",
            "sample_quality": "INSUFFICIENT"
        }
    
    matches = row[0] or 0
    innings = row[1] or 0
    balls = row[2] or 0
    runs = row[3] or 0
    total_wpa = row[4] or 0.0
    boundaries = row[5] or 0
    avg_partnership = row[6] or 0.0
    best_partnership = row[7] or 0
    
    partnership_sr = (runs * 100.0 / balls) if balls > 0 else 0.0
    wpa_per_ball = (total_wpa / balls) if balls > 0 else 0.0
    
    # Get solo performance for comparison
    player_a_solo = _get_solo_batting_stats(conn, player_a, venue)
    player_b_solo = _get_solo_batting_stats(conn, player_b, venue)
    
    # Calculate synergy boost
    if player_a_solo and player_b_solo and player_a_solo['strike_rate'] > 0 and player_b_solo['strike_rate'] > 0:
        expected_sr = (player_a_solo['strike_rate'] + player_b_solo['strike_rate']) / 2
        synergy_boost = (partnership_sr - expected_sr) / expected_sr if expected_sr > 0 else 0.0
        
        expected_wpa = (player_a_solo['wpa_per_ball'] + player_b_solo['wpa_per_ball']) / 2
        wpa_boost = (wpa_per_ball - expected_wpa) / abs(expected_wpa) if expected_wpa != 0 else 0.0
        
        # Combined synergy score (60% WPA, 40% SR)
        synergy_score = (wpa_boost * 0.6 + synergy_boost * 0.4)
    else:
        synergy_boost = 0.0
        synergy_score = 0.0
    
    # Sample quality
    if balls >= PARTNERSHIP_STRONG:
        sample = "STRONG"
    elif balls >= PARTNERSHIP_MODERATE:
        sample = "MODERATE"
    elif balls >= PARTNERSHIP_WEAK:
        sample = "WEAK"
    else:
        sample = "INSUFFICIENT"
    
    # Synergy rating
    if synergy_score > 0.15:
        rating = "EXCELLENT"
    elif synergy_score > 0.05:
        rating = "GOOD"
    elif synergy_score > -0.05:
        rating = "NEUTRAL"
    else:
        rating = "POOR"
    
    # Get hand combination
    hand_combo = _get_hand_combination(conn, player_a, player_b)
    
    return {
        "player_a": player_a,
        "player_b": player_b,
        "venue": venue or "ALL",
        "matches_together": int(matches),
        "innings_together": int(innings),
        "balls_together": int(balls),
        "runs_together": int(runs),
        "partnership_sr": round(partnership_sr, 2),
        "total_wpa": round(total_wpa, 4),
        "wpa_per_ball": round(wpa_per_ball, 4),
        "boundaries_together": int(boundaries),
        "avg_partnership": round(avg_partnership, 2),
        "best_partnership": int(best_partnership),
        "player_a_solo_sr": player_a_solo['strike_rate'] if player_a_solo else 0,
        "player_b_solo_sr": player_b_solo['strike_rate'] if player_b_solo else 0,
        "synergy_boost": round(synergy_boost, 3),
        "synergy_score": round(synergy_score, 3),
        "synergy_rating": rating,
        "hand_combination": hand_combo,
        "sample_quality": sample
    }


def get_best_batting_partners(
    conn: db.Connection,
    player: str,
    min_balls: int = 25,
    top_k: int = 10
) -> List[Dict]:
    """
    Find best batting partners for a player.
    
    Args:
        player: Player name
        min_balls: Minimum balls together
        top_k: Number of results to return
        
    Returns:
        List of partners sorted by synergy score
    """
    
    # Find all partners (innings where both played)
    query = """
        WITH innings_together AS (
            SELECT match_id, innings
            FROM ball_by_ball
            WHERE striker IN (
                SELECT DISTINCT b2.striker
                FROM ball_by_ball b1
                INNER JOIN ball_by_ball b2
                    ON b1.match_id = b2.match_id
                    AND b1.innings = b2.innings
                WHERE b1.striker = ?
                AND b2.striker != ?
            )
            GROUP BY match_id, innings
            HAVING COUNT(DISTINCT striker) >= 2
        ),
        partner_stats AS (
            SELECT 
                b.striker as partner,
                COUNT(DISTINCT b.match_id) as matches,
                COUNT(*) as balls
            FROM ball_by_ball b
            INNER JOIN innings_together it
                ON b.match_id = it.match_id
                AND b.innings = it.innings
            WHERE b.striker != ?
            GROUP BY partner
            HAVING balls >= ?
        )
        SELECT partner, matches, balls
        FROM partner_stats
        ORDER BY balls DESC
        LIMIT 50
    """
    
    partners = conn.execute(query, (player, player, player, min_balls)).fetchall()
    
    results = []
    for partner, matches, balls in partners:
        stats = get_batting_partnership(conn, player, partner)
        
        if stats['sample_quality'] != "INSUFFICIENT":
            results.append({
                "partner": partner,
                "matches": stats['matches_together'],
                "balls_together": stats['balls_together'],
                "partnership_sr": stats['partnership_sr'],
                "synergy_boost": stats['synergy_boost'],
                "synergy_score": stats['synergy_score'],
                "rating": stats['synergy_rating'],
                "hand_combo": stats['hand_combination']
            })
    
    # Sort by synergy score
    results.sort(key=lambda x: x['synergy_score'], reverse=True)
    
    return results[:top_k]


def predict_batting_synergy(
    conn: db.Connection,
    player_a: str,
    player_b: str
) -> Dict:
    """
    Predict synergy for players who haven't played together.
    Uses similarity-based approach.
    
    Args:
        player_a: First player name
        player_b: Second player name
        
    Returns:
        Predicted synergy with confidence
    """
    
    # Check if they've played together
    existing = get_batting_partnership(conn, player_a, player_b)
    
    if existing['balls_together'] > 0:
        return {
            "player_a": player_a,
            "player_b": player_b,
            "prediction_method": "HISTORICAL",
            "predicted_synergy": existing['synergy_score'],
            "confidence": "HIGH" if existing['sample_quality'] == "STRONG" else "MODERATE",
            "historical_data": existing
        }
    
    # Get player profiles
    profile_a = _get_batting_profile(conn, player_a)
    profile_b = _get_batting_profile(conn, player_b)
    
    # ✅ IMPROVED: Better error messages
    if not profile_a and not profile_b:
        return {
            "player_a": player_a,
            "player_b": player_b,
            "error": f"Both players not found in player_vectors table. They may be tail-enders or have insufficient career data."
        }
    elif not profile_a:
        return {
            "player_a": player_a,
            "player_b": player_b,
            "error": f"Player '{player_a}' not found in player_vectors table. Insufficient career data."
        }
    elif not profile_b:
        return {
            "player_a": player_a,
            "player_b": player_b,
            "error": f"Player '{player_b}' not found in player_vectors table. Insufficient career data."
        }
    
    # Find similar partnerships
    similar_pairs = _find_similar_partnerships(conn, profile_a, profile_b)
    
    if not similar_pairs:
        return {
            "player_a": player_a,
            "player_b": player_b,
            "prediction_method": "BASELINE",
            "predicted_synergy": 0.0,
            "confidence": "LOW",
            "reasoning": ["Insufficient similar partnerships for prediction"]
        }
    
    # Average synergy from similar partnerships
    avg_synergy = np.mean([p['synergy_score'] for p in similar_pairs])
    
    # Adjustments
    hand_bonus = 0.05 if profile_a['batting_hand'] != profile_b['batting_hand'] else 0.0
    role_bonus = 0.03 if _are_complementary_roles(profile_a, profile_b) else 0.0
    
    predicted_synergy = avg_synergy + hand_bonus + role_bonus
    
    # Confidence based on number of similar pairs
    if len(similar_pairs) >= 20:
        confidence = "MODERATE"
    elif len(similar_pairs) >= 10:
        confidence = "LOW"
    else:
        confidence = "VERY_LOW"
    
    # Generate reasoning
    reasoning = []
    if hand_bonus > 0:
        reasoning.append("Left-right combination (disrupts bowler rhythm)")
    else:
        reasoning.append("Same-handed pair (reduces disruption bonus)")
    
    if role_bonus > 0:
        reasoning.append("Complementary batting styles (anchor + aggressor balance)")
    
    sr_diff = abs(profile_a['strike_rate'] - profile_b['strike_rate'])
    if sr_diff < 15:
        reasoning.append(f"Similar strike rates ({profile_a['strike_rate']:.1f} vs {profile_b['strike_rate']:.1f})")
    else:
        reasoning.append(f"Different strike rates (variety in approach)")
    
    reasoning.append(f"Prediction based on {len(similar_pairs)} similar partnerships")
    
    return {
        "player_a": player_a,
        "player_b": player_b,
        "prediction_method": "SIMILARITY_BASED",
        "predicted_synergy": round(predicted_synergy, 3),
        "confidence": confidence,
        "reasoning": reasoning,
        "similar_partnerships": [
            {"pair": f"{p['player_a']} + {p['player_b']}", "synergy": p['synergy_score']}
            for p in similar_pairs[:5]
        ],
        "predicted_rating": _score_to_rating(predicted_synergy)
    }



# =====================================================
# BOWLING COMBINATIONS
# =====================================================

def get_bowling_combination(
    conn: db.Connection,
    bowler_a: str,
    bowler_b: str,
    phase: Optional[str] = None,
    venue: Optional[str] = None
) -> Dict:
    """
    Get bowling combination stats (how effective when operating together).
    
    Args:
        bowler_a: First bowler name
        bowler_b: Second bowler name
        phase: "powerplay" (overs 1-6), "middle" (7-15), "death" (16-20), or None
        venue: Optional venue filter
        
    Returns:
        Complete bowling combination statistics
    """
    
    # ✅ FIXED: Separate phase filters for different parts of query
    phase_filter_match = ""
    phase_filter_combo = ""
    
    if phase == "powerplay":
        phase_filter_match = "AND b1.over < 6"
        phase_filter_combo = "AND b.over < 6"
    elif phase == "middle":
        phase_filter_match = "AND b1.over BETWEEN 6 AND 15"
        phase_filter_combo = "AND b.over BETWEEN 6 AND 15"
    elif phase == "death":
        phase_filter_match = "AND b1.over >= 16"
        phase_filter_combo = "AND b.over >= 16"
    
    venue_filter = "AND venue = ?" if venue else ""
    
    params = [bowler_a, bowler_b]
    if venue:
        params.append(venue)
    
    # Find matches where both bowled
    query = f"""
        WITH match_combos AS (
            SELECT DISTINCT 
                b1.match_id,
                b1.innings
            FROM ball_by_ball b1
            INNER JOIN ball_by_ball b2 
                ON b1.match_id = b2.match_id 
                AND b1.innings = b2.innings
            WHERE b1.bowler = ? AND b2.bowler = ?
            {phase_filter_match}
            {venue_filter}
        ),
        combo_stats AS (
            SELECT 
                mc.match_id,
                COUNT(*) as balls,
                SUM(b.runs_off_bat + COALESCE(b.extras, 0)) as runs,
                SUM(CASE WHEN b.player_dismissed IS NOT NULL THEN 1 ELSE 0 END) as wickets,
                SUM(b.wpa) as total_wpa,
                SUM(CASE WHEN b.runs_off_bat = 0 AND COALESCE(b.extras, 0) = 0 THEN 1 ELSE 0 END) as dots
            FROM match_combos mc
            INNER JOIN ball_by_ball b 
                ON mc.match_id = b.match_id 
                AND mc.innings = b.innings
            WHERE b.bowler IN (?, ?)
            {phase_filter_combo}
            GROUP BY mc.match_id
        )
        SELECT 
            COUNT(*) as matches,
            SUM(balls) as total_balls,
            SUM(runs) as total_runs,
            SUM(wickets) as total_wickets,
            SUM(total_wpa) as total_wpa,
            SUM(dots) as total_dots
        FROM combo_stats
    """
    
    query_params = params + [bowler_a, bowler_b]
    if venue:
        query_params.append(venue)
    
    row = conn.execute(query, query_params).fetchone()
    
    if not row or row[1] is None or row[1] == 0:  # total_balls
        return {
            "bowler_a": bowler_a,
            "bowler_b": bowler_b,
            "phase": phase or "all",
            "venue": venue or "ALL",
            "matches_together": 0,
            "balls_together": 0,
            "overs_together": 0.0,
            "runs_conceded": 0,
            "wickets": 0,
            "combined_economy": 0.0,
            "combined_strike_rate": 999.0,
            "total_wpa": 0.0,
            "wpa_per_ball": 0.0,
            "dot_pct": 0.0,
            "bowler_a_solo_economy": 0,
            "bowler_b_solo_economy": 0,
            "synergy_boost": 0.0,
            "synergy_score": 0.0,
            "synergy_rating": "NO_DATA",
            "wicket_clustering": 0.0,
            "bowling_styles": "UNKNOWN",
            "sample_quality": "INSUFFICIENT"
        }
    
    matches = row[0] or 0
    balls = row[1] or 0
    runs = row[2] or 0
    wickets = row[3] or 0
    total_wpa = row[4] or 0.0
    dots = row[5] or 0
    
    combined_economy = (runs * 6.0 / balls) if balls > 0 else 0.0
    combined_sr = (balls / wickets) if wickets > 0 else 999.0
    wpa_per_ball = (total_wpa / balls) if balls > 0 else 0.0
    dot_pct = (dots / balls * 100) if balls > 0 else 0.0
    
    # Get solo performance
    bowler_a_solo = _get_solo_bowling_stats(conn, bowler_a, phase, venue)
    bowler_b_solo = _get_solo_bowling_stats(conn, bowler_b, phase, venue)
    
    # Calculate synergy boost
    if bowler_a_solo and bowler_b_solo and bowler_a_solo['economy'] > 0 and bowler_b_solo['economy'] > 0:
        expected_economy = (bowler_a_solo['economy'] + bowler_b_solo['economy']) / 2
        economy_boost = (expected_economy - combined_economy) / expected_economy if expected_economy > 0 else 0.0
        
        expected_wpa = (bowler_a_solo['wpa_per_ball'] + bowler_b_solo['wpa_per_ball']) / 2
        wpa_boost = (expected_wpa - wpa_per_ball) / abs(expected_wpa) if expected_wpa != 0 else 0.0
        
        # Combined synergy score (60% WPA, 40% economy)
        synergy_score = (wpa_boost * 0.6 + economy_boost * 0.4)
    else:
        economy_boost = 0.0
        synergy_score = 0.0
    
    # Sample quality
    if balls >= BOWLING_COMBO_STRONG:
        sample = "STRONG"
    elif balls >= BOWLING_COMBO_MODERATE:
        sample = "MODERATE"
    elif balls >= BOWLING_COMBO_WEAK:
        sample = "WEAK"
    else:
        sample = "INSUFFICIENT"
    
    # Synergy rating
    if synergy_score > 0.15:
        rating = "EXCELLENT"
    elif synergy_score > 0.05:
        rating = "GOOD"
    elif synergy_score > -0.05:
        rating = "NEUTRAL"
    else:
        rating = "POOR"
    
    # Wicket clustering (do wickets come in pairs?)
    wicket_clustering = _calculate_wicket_clustering(conn, bowler_a, bowler_b, phase)
    
    # Get bowling styles
    styles = _get_bowling_styles(conn, bowler_a, bowler_b)
    
    return {
        "bowler_a": bowler_a,
        "bowler_b": bowler_b,
        "phase": phase or "all",
        "venue": venue or "ALL",
        "matches_together": int(matches),
        "balls_together": int(balls),
        "overs_together": round(balls / 6, 1),
        "runs_conceded": int(runs),
        "wickets": int(wickets),
        "combined_economy": round(combined_economy, 2),
        "combined_strike_rate": round(combined_sr, 2),
        "total_wpa": round(total_wpa, 4),
        "wpa_per_ball": round(wpa_per_ball, 4),
        "dot_pct": round(dot_pct, 2),
        "bowler_a_solo_economy": bowler_a_solo['economy'] if bowler_a_solo else 0,
        "bowler_b_solo_economy": bowler_b_solo['economy'] if bowler_b_solo else 0,
        "synergy_boost": round(economy_boost, 3),
        "synergy_score": round(synergy_score, 3),
        "synergy_rating": rating,
        "wicket_clustering": round(wicket_clustering, 3),
        "bowling_styles": styles,
        "sample_quality": sample
    }



def get_best_bowling_partners(
    conn: db.Connection,
    bowler: str,
    phase: Optional[str] = None,
    min_balls: int = 30,
    top_k: int = 10
) -> List[Dict]:
    """
    Find best bowling partners for a bowler.
    
    Args:
        bowler: Bowler name
        phase: Optional phase filter
        min_balls: Minimum balls together
        top_k: Number of results
        
    Returns:
        List of partners sorted by synergy score
    """
    
    phase_filter = ""
    if phase == "powerplay":
        phase_filter = "AND b1.over < 6"
    elif phase == "middle":
        phase_filter = "AND b1.over BETWEEN 6 AND 15"
    elif phase == "death":
        phase_filter = "AND b1.over >= 16"
    
    # Find all partners
    query = f"""
        WITH bowling_pairs AS (
            SELECT DISTINCT 
                b2.bowler as partner,
                COUNT(DISTINCT b1.match_id) as matches,
                COUNT(*) as balls
            FROM ball_by_ball b1
            INNER JOIN ball_by_ball b2 
                ON b1.match_id = b2.match_id 
                AND b1.innings = b2.innings
            WHERE b1.bowler = ?
            AND b2.bowler != ?
            {phase_filter}
            GROUP BY partner
            HAVING balls >= ?
        )
        SELECT partner, matches, balls
        FROM bowling_pairs
        ORDER BY balls DESC
        LIMIT 50
    """
    
    partners = conn.execute(query, (bowler, bowler, min_balls)).fetchall()
    
    results = []
    for partner, matches, balls in partners:
        stats = get_bowling_combination(conn, bowler, partner, phase)
        
        if stats['sample_quality'] != "INSUFFICIENT":
            results.append({
                "partner": partner,
                "matches": int(matches),
                "balls_together": int(balls),
                "combined_economy": stats['combined_economy'],
                "synergy_boost": stats['synergy_boost'],
                "synergy_score": stats['synergy_score'],
                "rating": stats['synergy_rating'],
                "styles": stats['bowling_styles']
            })
    
    # Sort by synergy score
    results.sort(key=lambda x: x['synergy_score'], reverse=True)
    
    return results[:top_k]


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _get_solo_batting_stats(conn: db.Connection, player: str, venue: Optional[str]) -> Optional[Dict]:
    """Get player's solo batting stats"""
    
    venue_filter = "AND venue = ?" if venue else ""
    params = [player]
    if venue:
        params.append(venue)
    
    row = conn.execute(f"""
        SELECT 
            COUNT(*) as balls,
            SUM(runs_off_bat) as runs,
            SUM(wpa) as total_wpa
        FROM ball_by_ball
        WHERE striker = ?
        {venue_filter}
    """, params).fetchone()
    
    if not row or not row[0] or row[0] == 0:
        return None
    
    balls = row[0] or 0
    runs = row[1] or 0
    total_wpa = row[2] or 0.0
    
    sr = (runs * 100.0 / balls) if balls > 0 else 0
    wpa_per_ball = (total_wpa / balls) if balls > 0 else 0
    
    return {
        "strike_rate": round(sr, 2),
        "wpa_per_ball": round(wpa_per_ball, 4)
    }


def _get_solo_bowling_stats(conn: db.Connection, bowler: str, phase: Optional[str], venue: Optional[str]) -> Optional[Dict]:
    """Get bowler's solo stats"""
    
    # ✅ FIXED: Add table alias
    phase_filter = ""
    if phase == "powerplay":
        phase_filter = "AND b.over < 6"
    elif phase == "middle":
        phase_filter = "AND b.over BETWEEN 6 AND 15"
    elif phase == "death":
        phase_filter = "AND b.over >= 16"
    
    venue_filter = "AND b.venue = ?" if venue else ""
    params = [bowler]
    if venue:
        params.append(venue)
    
    row = conn.execute(f"""
        SELECT 
            COUNT(*) as balls,
            SUM(b.runs_off_bat + COALESCE(b.extras, 0)) as runs,
            SUM(b.wpa) as total_wpa
        FROM ball_by_ball b
        WHERE b.bowler = ?
        {phase_filter}
        {venue_filter}
    """, params).fetchone()
    
    if not row or not row[0] or row[0] == 0:
        return None
    
    balls = row[0] or 0
    runs = row[1] or 0
    total_wpa = row[2] or 0.0
    
    economy = (runs * 6.0 / balls) if balls > 0 else 0
    wpa_per_ball = (total_wpa / balls) if balls > 0 else 0
    
    return {
        "economy": round(economy, 2),
        "wpa_per_ball": round(wpa_per_ball, 4)
    }


def _get_hand_combination(conn: db.Connection, player_a: str, player_b: str) -> str:
    """Get batting hand combination (RHB-LHB, RHB-RHB, etc.)"""
    
    try:
        hands = conn.execute("""
            SELECT player, batting_style 
            FROM player_vectors 
            WHERE player IN (?, ?)
        """, (player_a, player_b)).fetchall()
        
        hand_map = {}
        for player, style in hands:
            if style and 'left' in style.lower():
                hand_map[player] = 'LHB'
            else:
                hand_map[player] = 'RHB'
        
        hand_a = hand_map.get(player_a, 'RHB')
        hand_b = hand_map.get(player_b, 'RHB')
        
        return f"{hand_a}-{hand_b}"
    except:
        return "UNKNOWN"


def _get_batting_profile(conn: db.Connection, player: str) -> Optional[Dict]:
    """Get player batting profile for similarity matching"""
    
    try:
        row = conn.execute("""
            SELECT 
                batting_style,
                role,
                career_bat_rpa_z,
                career_bat_wpa_z
            FROM player_vectors
            WHERE player = ?
        """, (player,)).fetchone()
        
        if not row:
            return None
        
        style, role, rpa_z, wpa_z = row
        
        # Get strike rate
        sr_row = conn.execute("""
            SELECT SUM(runs_off_bat) * 100.0 / COUNT(*) as sr
            FROM ball_by_ball
            WHERE striker = ?
        """, (player,)).fetchone()
        
        hand = 'left' if style and 'left' in style.lower() else 'right'
        
        return {
            "player": player,
            "batting_hand": hand,
            "role": role,
            "strike_rate": sr_row[0] if sr_row and sr_row[0] else 130,
            "rpa_z": rpa_z if rpa_z else 0,
            "wpa_z": wpa_z if wpa_z else 0
        }
    except:
        return None


def _find_similar_partnerships(conn: db.Connection, profile_a: Dict, profile_b: Dict, limit: int = 30) -> List[Dict]:
    """Find similar partnerships for prediction"""
    
    # Simplified: find any strong partnerships as proxies
    query = """
        WITH innings_together AS (
            SELECT match_id, innings
            FROM ball_by_ball
            WHERE striker IS NOT NULL
            GROUP BY match_id, innings
            HAVING COUNT(DISTINCT striker) >= 2
        ),
        striker_pairs AS (
            SELECT DISTINCT
                b1.striker as player_a,
                b2.striker as player_b,
                COUNT(DISTINCT b1.match_id) as matches
            FROM ball_by_ball b1
            INNER JOIN ball_by_ball b2
                ON b1.match_id = b2.match_id
                AND b1.innings = b2.innings
            WHERE b1.striker < b2.striker
            AND b1.striker != ?
            AND b1.striker != ?
            AND b2.striker != ?
            AND b2.striker != ?
            GROUP BY player_a, player_b
            HAVING matches >= 3
            LIMIT ?
        )
        SELECT player_a, player_b
        FROM striker_pairs
    """
    
    pairs = conn.execute(query, (
        profile_a['player'], profile_b['player'],
        profile_a['player'], profile_b['player'],
        limit
    )).fetchall()
    
    results = []
    for p_a, p_b in pairs:
        stats = get_batting_partnership(conn, p_a, p_b)
        if stats['sample_quality'] != "INSUFFICIENT":
            results.append(stats)
    
    return results


def _are_complementary_roles(profile_a: Dict, profile_b: Dict) -> bool:
    """Check if batting roles are complementary"""
    
    sr_diff = abs(profile_a['strike_rate'] - profile_b['strike_rate'])
    return sr_diff > 20


def _calculate_wicket_clustering(conn: db.Connection, bowler_a: str, bowler_b: str, phase: Optional[str]) -> float:
    """Calculate wicket clustering coefficient"""
    
    # ✅ FIXED: Add table alias
    phase_filter = ""
    if phase == "powerplay":
        phase_filter = "AND b.over < 6"
    elif phase == "middle":
        phase_filter = "AND b.over BETWEEN 6 AND 15"
    elif phase == "death":
        phase_filter = "AND b.over >= 16"
    
    query = f"""
        SELECT 
            b.match_id,
            b.innings,
            b.over,
            b.ball,
            b.bowler,
            CASE WHEN b.player_dismissed IS NOT NULL THEN 1 ELSE 0 END as is_wicket
        FROM ball_by_ball b
        WHERE b.bowler IN (?, ?)
        AND b.match_id IN (
            SELECT DISTINCT match_id 
            FROM ball_by_ball 
            WHERE bowler = ? OR bowler = ?
        )
        {phase_filter}
        ORDER BY b.match_id, b.innings, b.over, b.ball
    """
    
    rows = conn.execute(query, (bowler_a, bowler_b, bowler_a, bowler_b)).fetchall()
    
    if len(rows) < 10:
        return 0.0
    
    wickets_paired = 0
    total_wickets = 0
    
    for i, row in enumerate(rows):
        if row[5] == 1:
            total_wickets += 1
            for j in range(i+1, min(i+13, len(rows))):
                if rows[j][0] == row[0] and rows[j][1] == row[1]:
                    if rows[j][5] == 1 and rows[j][4] != row[4]:
                        wickets_paired += 1
                        break
    
    return (wickets_paired / total_wickets) if total_wickets > 0 else 0.0

def _get_bowling_styles(conn: db.Connection, bowler_a: str, bowler_b: str) -> str:
    """Get bowling style combination"""
    
    try:
        styles = conn.execute("""
            SELECT player, bowling_style 
            FROM player_vectors 
            WHERE player IN (?, ?)
        """, (bowler_a, bowler_b)).fetchall()
        
        style_map = {player: style or 'unknown' for player, style in styles}
        style_a = style_map.get(bowler_a, 'unknown')
        style_b = style_map.get(bowler_b, 'unknown')
        
        return f"{style_a} + {style_b}"
    except:
        return "UNKNOWN"


def _score_to_rating(score: float) -> str:
    """Convert synergy score to rating"""
    if score > 0.15:
        return "EXCELLENT"
    elif score > 0.05:
        return "GOOD"
    elif score > -0.05:
        return "NEUTRAL"
    else:
        return "POOR"
