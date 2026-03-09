# end_applications/pvt_util.py
"""
PVT (Player vs Team) - Opposition Analysis Engine
Analyzes player performance against specific teams and team strength tiers.
"""

import db.session as db
import numpy as np
from typing import Optional, Dict, List

BATTING_SAMPLE_STRONG = 150
BATTING_SAMPLE_MODERATE = 75
BATTING_SAMPLE_WEAK = 30

BOWLING_SAMPLE_STRONG = 120
BOWLING_SAMPLE_MODERATE = 60
BOWLING_SAMPLE_WEAK = 24

# Team strength tier thresholds
TEAM_STRENGTH_TIERS = {
    "ELITE": 1800,
    "STRONG": 1650,
    "AVERAGE": 1500,
    "WEAK": 1350,
    "BOTTOM": 0
}


def get_player_vs_team_batting(
    conn: db.Connection,
    player: str,
    opponent_team: str,
    venue: Optional[str] = None
) -> Dict:
    """
    Get player's batting performance against a specific team.
    """
    
    venue_filter = "AND venue = ?" if venue else ""
    params = [player, opponent_team]
    if venue:
        params.append(venue)
    
    query = f"""
        SELECT 
            COUNT(DISTINCT match_id) as matches,
            COUNT(DISTINCT CASE WHEN striker = ? THEN match_id END) as innings,
            COUNT(*) as balls_faced,
            SUM(runs_off_bat) as runs_scored,
            SUM(CASE WHEN player_dismissed = ? THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN runs_off_bat >= 4 THEN 1 ELSE 0 END) as boundaries,
            SUM(CASE WHEN runs_off_bat = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(wpa) as total_wpa,
            COUNT(DISTINCT venue) as venues_played
        FROM ball_by_ball
        WHERE striker = ?
        AND bowling_team = ?
        {venue_filter}
    """
    
    params_query = [player, player, player, opponent_team] + ([venue] if venue else [])
    row = conn.execute(query, params_query).fetchone()
    
    if not row or row[2] == 0:  # balls_faced = 0
        return {
            "player": player,
            "opponent": opponent_team,
            "venue": venue or "ALL",
            "matches": 0,
            "innings": 0,
            "balls_faced": 0,
            "runs_scored": 0,
            "dismissals": 0,
            "strike_rate": 0.0,
            "average": 0.0,
            "total_wpa": 0.0,
            "wpa_per_ball": 0.0,
            "boundaries": 0,
            "sixes": 0,
            "boundary_pct": 0.0,
            "venues_played": 0,
            "not_out_heavy": False,
            "sample_quality": "INSUFFICIENT",
            "pvt_adjustment": 0.0
        }
    
    matches, innings, balls, runs, dismissals, boundaries, sixes, total_wpa, venues = row
    
    strike_rate = (runs * 100.0 / balls) if balls > 0 else 0.0
    
    dismissals_safe = max(dismissals, 1)
    average = runs / dismissals_safe
    not_out_heavy = (dismissals == 0 and balls >= 30)
    
    boundary_pct = (boundaries / balls * 100) if balls > 0 else 0.0
    wpa_per_ball = (total_wpa / balls) if balls > 0 else 0.0
    
    if balls >= BATTING_SAMPLE_STRONG:
        sample = "STRONG"
    elif balls >= BATTING_SAMPLE_MODERATE:
        sample = "MODERATE"
    elif balls >= BATTING_SAMPLE_WEAK:
        sample = "WEAK"
    else:
        sample = "INSUFFICIENT"
    
    # Get player's career baseline for comparison
    baseline = _get_batting_baseline(conn, player)
    
    #WPA-primary performance scoring (aligned with α=0.05)
    if baseline:
        sr_diff = strike_rate - baseline['career_sr']
        avg_diff = average - baseline['career_avg']
        wpa_diff = wpa_per_ball - baseline['career_wpa_per_ball']
        
        # WPA-dominant scoring (60% WPA, 40% SR)
        performance_zscore = (
            0.6 * (wpa_diff / 0.03) +  # WPA normalized by typical stddev
            0.4 * (sr_diff / 20.0)      # SR normalized
        )
        
        if performance_zscore > 0.5:
            rating = "EXCELLENT"
        elif performance_zscore > 0.1:
            rating = "ABOVE_AVERAGE"
        elif performance_zscore > -0.1:
            rating = "AVERAGE"
        else:
            rating = "BELOW_AVERAGE"
    else:
        rating = "UNKNOWN"
        performance_zscore = 0.0
        sr_diff = 0.0
        avg_diff = 0.0

    sample_weight = min(1.0, balls / 200.0)
    pvt_adjustment = performance_zscore * sample_weight
    
    return {
        "player": player,
        "opponent": opponent_team,
        "venue": venue or "ALL",
        "matches": int(matches),
        "innings": int(innings),
        "balls_faced": int(balls),
        "runs_scored": int(runs),
        "dismissals": int(dismissals),
        "strike_rate": round(strike_rate, 2),
        "average": round(average, 2),
        "total_wpa": round(total_wpa, 4),
        "wpa_per_ball": round(wpa_per_ball, 4),
        "boundaries": int(boundaries),
        "sixes": int(sixes),
        "boundary_pct": round(boundary_pct, 2),
        "venues_played": int(venues),
        "not_out_heavy": not_out_heavy,
        "sample_quality": sample,
        "performance_rating": rating,
        "performance_zscore": round(performance_zscore, 3),
        "pvt_adjustment": round(pvt_adjustment, 3),
        "baseline_comparison": {
            "career_sr": baseline['career_sr'] if baseline else 0,
            "career_avg": baseline['career_avg'] if baseline else 0,
            "career_wpa_per_ball": baseline['career_wpa_per_ball'] if baseline else 0,
            "sr_diff": round(sr_diff, 2),
            "avg_diff": round(avg_diff, 2)
        }
    }


def get_player_vs_team_bowling(
    conn: db.Connection,
    player: str,
    opponent_team: str,
    venue: Optional[str] = None
) -> Dict:
    """
    Get player's bowling performance against a specific team.
    """
    
    venue_filter = "AND venue = ?" if venue else ""
    params = [player, opponent_team]
    if venue:
        params.append(venue)

    query = f"""
        SELECT 
            COUNT(DISTINCT match_id) as matches,
            COUNT(*) as balls_bowled,
            SUM(runs_off_bat + extras) as runs_conceded,
            SUM(CASE WHEN player_dismissed IS NOT NULL THEN 1 ELSE 0 END) as wickets,
            SUM(wpa) as total_wpa,
            SUM(CASE WHEN runs_off_bat = 0 AND extras = 0 THEN 1 ELSE 0 END) as dots,
            COUNT(DISTINCT venue) as venues_played
        FROM ball_by_ball
        WHERE bowler = ?
        AND batting_team = ?
        {venue_filter}
    """
    
    params_query = [player, opponent_team] + ([venue] if venue else [])
    row = conn.execute(query, params_query).fetchone()
    
    if not row or row[1] == 0:  # balls_bowled = 0
        return {
            "player": player,
            "opponent": opponent_team,
            "venue": venue or "ALL",
            "matches": 0,
            "balls_bowled": 0,
            "runs_conceded": 0,
            "wickets": 0,
            "economy": 0.0,
            "strike_rate": 0.0,
            "average": 0.0,
            "total_wpa": 0.0,
            "wpa_per_ball": 0.0,
            "dot_pct": 0.0,
            "venues_played": 0,
            "sample_quality": "INSUFFICIENT",
            "pvt_adjustment": 0.0
        }
    
    matches, balls, runs, wickets, total_wpa, dots, venues = row
    
    economy = (runs * 6.0 / balls) if balls > 0 else 0.0
    bowl_strike_rate = (balls / wickets) if wickets > 0 else 999.0  # High SR = bad for bowler
    bowl_average = (runs / wickets) if wickets > 0 else runs
    dot_pct = (dots / balls * 100) if balls > 0 else 0.0
    wpa_per_ball = (total_wpa / balls) if balls > 0 else 0.0

    if balls >= BOWLING_SAMPLE_STRONG:
        sample = "STRONG"
    elif balls >= BOWLING_SAMPLE_MODERATE:
        sample = "MODERATE"
    elif balls >= BOWLING_SAMPLE_WEAK:
        sample = "WEAK"
    else:
        sample = "INSUFFICIENT"
    
    # Get baseline for comparison
    baseline = _get_bowling_baseline(conn, player)
    
    if baseline:
        econ_diff = baseline['career_economy'] - economy  # Lower is better for bowler
        wpa_diff = baseline['career_wpa_per_ball'] - wpa_per_ball  # More negative WPA is better
        
        # WPA-dominant scoring (60% WPA, 40% economy)
        performance_zscore = (
            0.6 * (wpa_diff / 0.03) +
            0.4 * (econ_diff / 1.0)
        )
        
        if performance_zscore > 0.5:
            rating = "EXCELLENT"
        elif performance_zscore > 0.1:
            rating = "ABOVE_AVERAGE"
        elif performance_zscore > -0.1:
            rating = "AVERAGE"
        else:
            rating = "BELOW_AVERAGE"
    else:
        rating = "UNKNOWN"
        performance_zscore = 0.0
        econ_diff = 0.0

    sample_weight = min(1.0, balls / 200.0)
    pvt_adjustment = performance_zscore * sample_weight
    
    return {
        "player": player,
        "opponent": opponent_team,
        "venue": venue or "ALL",
        "matches": int(matches),
        "balls_bowled": int(balls),
        "runs_conceded": int(runs),
        "wickets": int(wickets),
        "economy": round(economy, 2),
        "strike_rate": round(bowl_strike_rate, 2),
        "average": round(bowl_average, 2),
        "total_wpa": round(total_wpa, 4),
        "wpa_per_ball": round(wpa_per_ball, 4),
        "dot_pct": round(dot_pct, 2),
        "venues_played": int(venues),
        "sample_quality": sample,
        "performance_rating": rating,
        "performance_zscore": round(performance_zscore, 3),
        "pvt_adjustment": round(pvt_adjustment, 3),
        "baseline_comparison": {
            "career_economy": baseline['career_economy'] if baseline else 0,
            "career_strike_rate": baseline['career_strike_rate'] if baseline else 0,
            "career_wpa_per_ball": baseline['career_wpa_per_ball'] if baseline else 0,
            "econ_diff": round(econ_diff, 2)
        }
    }


def get_player_vs_all_teams(
    conn: db.Connection,
    player: str,
    role: str,
    min_balls: int = 30
) -> List[Dict]:
    """
    Get player's performance against all teams they've faced.
    """
    
    if role == "batting":
        query = """
            SELECT bowling_team as opponent, COUNT(*) as balls
            FROM ball_by_ball
            WHERE striker = ?
            GROUP BY bowling_team
            HAVING balls >= ?
            ORDER BY balls DESC
        """
    else:
        query = """
            SELECT batting_team as opponent, COUNT(*) as balls
            FROM ball_by_ball
            WHERE bowler = ?
            GROUP BY batting_team
            HAVING balls >= ?
            ORDER BY balls DESC
        """
    
    teams = conn.execute(query, (player, min_balls)).fetchall()
    
    results = []
    for team, balls in teams:
        if role == "batting":
            stats = get_player_vs_team_batting(conn, player, team)
        else:
            stats = get_player_vs_team_bowling(conn, player, team)
        
        results.append(stats)
    
    # Sort by pvt_adjustment (most impactful first)
    results.sort(key=lambda x: x['pvt_adjustment'], reverse=True)
    
    return results


def get_player_vs_strength_tiers(
    conn: db.Connection,
    player: str,
    role: str
) -> Dict:
    """
    Analyze player performance by opponent strength tiers.
    Uses team ELO ratings if available, otherwise uses safe fallback.
    """
    
    # Get all teams player faced
    all_teams = get_player_vs_all_teams(conn, player, role, min_balls=20)
    
    if not all_teams:
        return {
            "player": player,
            "role": role,
            "error": "Insufficient data"
        }
    
    #ELO ratings (if team_elo table exists)
    team_elos = {}
    try:
        elo_rows = conn.execute("""
            SELECT team, AVG(elo) as avg_elo
            FROM team_elo
            GROUP BY team
        """).fetchall()
        
        for team, elo in elo_rows:
            team_elos[team] = elo
    except:
        pass
    
    # Categorize teams into tiers
    tiers = {
        "ELITE": [],
        "STRONG": [],
        "AVERAGE": [],
        "WEAK": [],
        "BOTTOM": []
    }
    
    for team_stats in all_teams:
        team = team_stats['opponent']
        balls = team_stats.get('balls_faced', team_stats.get('balls_bowled', 0))
        
        if team in team_elos:
            # Use ELO if available
            elo = team_elos[team]
            if elo >= 1800:
                tier = "ELITE"
            elif elo >= 1650:
                tier = "STRONG"
            elif elo >= 1500:
                tier = "AVERAGE"
            elif elo >= 1350:
                tier = "WEAK"
            else:
                tier = "BOTTOM"
        else:
            if balls >= 150:
                tier = "STRONG"  
            elif balls >= 75:
                tier = "AVERAGE"
            else:
                tier = "WEAK" 
        
        tiers[tier].append(team_stats)
    
    # Aggregate stats for each tier
    tier_summary = {}
    for tier_name, teams in tiers.items():
        if not teams:
            continue
        
        if role == "batting":
            total_balls = sum(t['balls_faced'] for t in teams)
            total_runs = sum(t['runs_scored'] for t in teams)
            total_dismissals = sum(t['dismissals'] for t in teams)
            
            tier_summary[tier_name.lower()] = {
                "teams": [t['opponent'] for t in teams],
                "matches": sum(t['matches'] for t in teams),
                "balls_faced": total_balls,
                "runs_scored": total_runs,
                "dismissals": total_dismissals,
                "strike_rate": round(total_runs * 100.0 / total_balls, 2) if total_balls > 0 else 0,
                "average": round(total_runs / max(total_dismissals, 1), 2),
                "total_wpa": round(sum(t['total_wpa'] for t in teams), 4),
                "wpa_per_ball": round(sum(t['total_wpa'] for t in teams) / total_balls, 4) if total_balls > 0 else 0,
                "avg_pvt_adjustment": round(np.mean([t['pvt_adjustment'] for t in teams]), 3)
            }
        else:
            total_balls = sum(t['balls_bowled'] for t in teams)
            total_wickets = sum(t['wickets'] for t in teams)
            total_runs = sum(t['runs_conceded'] for t in teams)
            
            tier_summary[tier_name.lower()] = {
                "teams": [t['opponent'] for t in teams],
                "matches": sum(t['matches'] for t in teams),
                "balls_bowled": total_balls,
                "wickets": total_wickets,
                "runs_conceded": total_runs,
                "economy": round(total_runs * 6.0 / total_balls, 2) if total_balls > 0 else 0,
                "strike_rate": round(total_balls / max(total_wickets, 1), 2),
                "total_wpa": round(sum(t['total_wpa'] for t in teams), 4),
                "wpa_per_ball": round(sum(t['total_wpa'] for t in teams) / total_balls, 4) if total_balls > 0 else 0,
                "avg_pvt_adjustment": round(np.mean([t['pvt_adjustment'] for t in teams]), 3)
            }
    
    interpretation = _interpret_tier_performance(tier_summary, role)
    
    return {
        "player": player,
        "role": role,
        "by_strength_tier": tier_summary,
        "interpretation": interpretation
    }


def _get_batting_baseline(conn: db.Connection, player: str) -> Optional[Dict]:
    """Get player's career batting baseline"""
    
    row = conn.execute("""
        SELECT 
            COUNT(*) as balls,
            SUM(runs_off_bat) as runs,
            SUM(CASE WHEN player_dismissed = ? THEN 1 ELSE 0 END) as dismissals,
            SUM(wpa) as total_wpa
        FROM ball_by_ball
        WHERE striker = ?
    """, (player, player)).fetchone()
    
    if not row or row[0] == 0:
        return None
    
    balls, runs, dismissals, total_wpa = row
    sr = (runs * 100.0 / balls) if balls > 0 else 0
    avg = (runs / max(dismissals, 1))
    wpa_per_ball = (total_wpa / balls) if balls > 0 else 0
    
    return {
        "career_sr": round(sr, 2),
        "career_avg": round(avg, 2),
        "career_wpa_per_ball": round(wpa_per_ball, 4),
        "total_balls": int(balls)
    }


def _get_bowling_baseline(conn: db.Connection, player: str) -> Optional[Dict]:
    """Get player's career bowling baseline"""
    
    row = conn.execute("""
        SELECT 
            COUNT(*) as balls,
            SUM(runs_off_bat + extras) as runs,
            SUM(CASE WHEN player_dismissed IS NOT NULL THEN 1 ELSE 0 END) as wickets,
            SUM(wpa) as total_wpa
        FROM ball_by_ball
        WHERE bowler = ?
    """, (player,)).fetchone()
    
    if not row or row[0] == 0:
        return None
    
    balls, runs, wickets, total_wpa = row
    economy = (runs * 6.0 / balls) if balls > 0 else 0
    sr = (balls / max(wickets, 1))
    wpa_per_ball = (total_wpa / balls) if balls > 0 else 0
    
    return {
        "career_economy": round(economy, 2),
        "career_strike_rate": round(sr, 2),
        "career_wpa_per_ball": round(wpa_per_ball, 4),
        "total_balls": int(balls)
    }


def _interpret_tier_performance(tier_summary: Dict, role: str) -> str:
    """Generate human-readable interpretation of tier performance"""
    
    if not tier_summary:
        return "Insufficient data for tier analysis"

    tier_order = ['elite', 'strong', 'average', 'weak', 'bottom']
    available_tiers = [t for t in tier_order if t in tier_summary]
    
    if len(available_tiers) < 2:
        return "Limited sample across strength tiers"
    
    pvt_scores = [tier_summary[t]['avg_pvt_adjustment'] for t in available_tiers]

    check_tiers = available_tiers[:min(3, len(available_tiers))]
    check_scores = [tier_summary[t]['avg_pvt_adjustment'] for t in check_tiers]
    
    if len(check_scores) >= 2:
        if all(check_scores[i] >= check_scores[i+1] for i in range(len(check_scores)-1)):
            trend = "worsens"
        elif all(check_scores[i] <= check_scores[i+1] for i in range(len(check_scores)-1)):
            trend = "improves"
        else:
            trend = "is inconsistent"
    else:
        trend = "is inconsistent"
    
    if role == "batting":
        if trend == "improves":
            return "Performs better against stronger teams (big-match temperament)"
        elif trend == "worsens":
            return "Performs better against weaker teams"
        else:
            return "Inconsistent performer across strength levels"
    else:
        if trend == "improves":
            return "More effective against stronger batting lineups"
        elif trend == "worsens":
            return "More effective against weaker batting lineups"
        else:
            return "Consistent performer across all opposition levels"
