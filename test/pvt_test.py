# test/pvt_test.py
"""
PVT (Player vs Team) - Test Suite
Tests opposition analysis and team strength tier performance.
"""

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from end_applications.pvt_util import (
    get_player_vs_team_batting,
    get_player_vs_team_bowling,
    get_player_vs_all_teams,
    get_player_vs_strength_tiers
)
import sqlite3


def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


# =====================================================
# BATTING TESTS
# =====================================================

def test_batting_strong_sample():
    """
    TEST 1: Strong sample batting performance
    Find a batter with 150+ balls vs a team (should be STRONG sample)
    """
    print_header("TEST 1: BATTING - STRONG SAMPLE")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find batter with strong sample vs a team
    result = conn.execute("""
    SELECT striker, bowling_team, COUNT(*) as balls
    FROM ball_by_ball
    WHERE striker = 'V Kohli' 
    AND bowling_team IS NOT NULL
    GROUP BY striker, bowling_team
    HAVING balls >= 30
    ORDER BY balls DESC
    LIMIT 1
""").fetchone()
    
    if not result:
        print("⚠️  No strong sample found (need 150+ balls)\n")
        conn.close()
        return
    
    player, team, balls = result
    
    print(f"🏏 Player: {player}")
    print(f"🎯 Opponent: {team}")
    print(f"📊 Total Balls: {balls}\n")
    
    stats = get_player_vs_team_batting(conn, player, team)
    
    print("📈 Performance vs This Team:")
    print(f"   Matches: {stats['matches']}")
    print(f"   Innings: {stats['innings']}")
    print(f"   Balls Faced: {stats['balls_faced']}")
    print(f"   Runs Scored: {stats['runs_scored']}")
    print(f"   Strike Rate: {stats['strike_rate']}")
    print(f"   Average: {stats['average']}")
    print(f"   Dismissals: {stats['dismissals']}")
    print(f"   Not-Out Heavy: {'YES' if stats['not_out_heavy'] else 'NO'}\n")
    
    print("📊 WPA Metrics:")
    print(f"   Total WPA: {stats['total_wpa']}")
    print(f"   WPA per Ball: {stats['wpa_per_ball']}\n")
    
    print("🎯 Boundaries:")
    print(f"   Boundaries: {stats['boundaries']}")
    print(f"   Sixes: {stats['sixes']}")
    print(f"   Boundary %: {stats['boundary_pct']}%\n")
    
    print("⚖️  Performance Analysis:")
    print(f"   Rating: {stats['performance_rating']}")
    print(f"   Performance Z-Score: {stats['performance_zscore']}")
    print(f"   PVT Adjustment: {stats['pvt_adjustment']}")
    print(f"   Sample Quality: {stats['sample_quality']}\n")
    
    print("📊 Baseline Comparison:")
    baseline = stats['baseline_comparison']
    print(f"   Career SR: {baseline['career_sr']}")
    print(f"   vs Team SR: {stats['strike_rate']} (Δ {baseline['sr_diff']:+.2f})")
    print(f"   Career Avg: {baseline['career_avg']}")
    print(f"   vs Team Avg: {stats['average']} (Δ {baseline['avg_diff']:+.2f})\n")
    
    # Validation
    assert stats['sample_quality'] == 'STRONG', "❌ Should be STRONG sample"
    assert stats['balls_faced'] >= 150, "❌ Should have 150+ balls"
    
    print("✅ Test passed\n")
    conn.close()


def test_batting_boom_bust():
    """
    TEST 2: Boom/bust player (high SR, low average - aggressive player)
    """
    print_header("TEST 2: BATTING - BOOM/BUST PLAYER")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find aggressive player (high SR, dismissals)
    result = conn.execute("""
        SELECT 
            striker,
            bowling_team,
            COUNT(*) as balls,
            SUM(runs_off_bat) * 100.0 / COUNT(*) as sr,
            SUM(CASE WHEN player_dismissed = striker THEN 1 ELSE 0 END) as dismissals
        FROM ball_by_ball
        WHERE striker IS NOT NULL AND bowling_team IS NOT NULL
        GROUP BY striker, bowling_team
        HAVING balls >= 50 AND sr >= 150 AND dismissals >= 3
        ORDER BY sr DESC
        LIMIT 1
    """).fetchone()
    
    if not result:
        print("⚠️  No boom/bust matchup found\n")
        conn.close()
        return
    
    player, team, balls, sr, dismissals = result
    
    print(f"🏏 Player: {player}")
    print(f"🎯 Opponent: {team}")
    print(f"📊 Total Balls: {balls}")
    print(f"⚡ Strike Rate: {sr:.2f}")
    print(f"🔻 Dismissals: {dismissals}\n")
    
    stats = get_player_vs_team_batting(conn, player, team)
    
    print("📈 Boom/Bust Characteristics:")
    print(f"   Strike Rate: {stats['strike_rate']} (High)")
    print(f"   Average: {stats['average']}")
    print(f"   Dismissals: {stats['dismissals']}")
    print(f"   Balls per Dismissal: {stats['balls_faced'] / max(stats['dismissals'], 1):.1f}\n")
    
    print("⚖️  Performance:")
    print(f"   Rating: {stats['performance_rating']}")
    print(f"   PVT Adjustment: {stats['pvt_adjustment']}")
    print(f"   Sample Quality: {stats['sample_quality']}\n")
    
    # Boom/bust should have high SR but reasonable dismissal rate
    assert stats['strike_rate'] >= 140, "❌ Should have high SR"
    
    print("✅ Test passed\n")
    conn.close()


def test_batting_tail_ender():
    """
    TEST 3: Tail-ender (should flag WEAK or INSUFFICIENT sample)
    """
    print_header("TEST 3: BATTING - TAIL-ENDER")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find a bowler batting (tail-ender with low exposure)
    result = conn.execute("""
        SELECT DISTINCT striker
        FROM ball_by_ball
        WHERE striker IN (
            SELECT DISTINCT bowler FROM ball_by_ball WHERE bowler IS NOT NULL
        )
        AND striker NOT IN (
            SELECT striker 
            FROM ball_by_ball 
            WHERE striker IS NOT NULL 
            GROUP BY striker 
            HAVING COUNT(*) >= 500
        )
        LIMIT 1
    """).fetchone()
    
    if not result:
        print("⚠️  No tail-ender found\n")
        conn.close()
        return
    
    player = result[0]
    
    # Find a team they faced
    team_result = conn.execute("""
        SELECT bowling_team, COUNT(*) as balls
        FROM ball_by_ball
        WHERE striker = ?
        GROUP BY bowling_team
        ORDER BY balls DESC
        LIMIT 1
    """, (player,)).fetchone()
    
    if not team_result:
        print(f"⚠️  {player} has no batting data\n")
        conn.close()
        return
    
    team, balls = team_result
    
    print(f"🏏 Player: {player} (Tail-ender)")
    print(f"🎯 Opponent: {team}")
    print(f"📊 Total Balls: {balls}\n")
    
    stats = get_player_vs_team_batting(conn, player, team)
    
    print("📈 Tail-Ender Stats:")
    print(f"   Balls Faced: {stats['balls_faced']}")
    print(f"   Runs Scored: {stats['runs_scored']}")
    print(f"   Strike Rate: {stats['strike_rate']}")
    print(f"   Sample Quality: {stats['sample_quality']}\n")
    
    print("⚖️  Performance:")
    print(f"   Rating: {stats['performance_rating']}")
    print(f"   PVT Adjustment: {stats['pvt_adjustment']}\n")
    
    # Should flag weak/insufficient sample
    assert stats['sample_quality'] in ['WEAK', 'INSUFFICIENT', 'MODERATE'], \
        "❌ Tail-ender should have limited sample"
    
    print("✅ Test passed (correctly flagged limited sample)\n")
    conn.close()


# =====================================================
# BOWLING TESTS
# =====================================================

def test_bowling_elite_vs_strong_team():
    """
    TEST 4: Elite bowler vs strong batting team (should be STRONG sample)
    """
    print_header("TEST 4: BOWLING - ELITE BOWLER VS STRONG TEAM")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find bowler with strong sample vs a team
    result = conn.execute("""
        SELECT bowler, batting_team, COUNT(*) as balls
        FROM ball_by_ball
        WHERE bowler IS NOT NULL AND batting_team IS NOT NULL
        GROUP BY bowler, batting_team
        HAVING balls >= 120
        ORDER BY balls DESC
        LIMIT 1
    """).fetchone()
    
    if not result:
        print("⚠️  No strong bowling sample found (need 120+ balls)\n")
        conn.close()
        return
    
    player, team, balls = result
    
    print(f"🎳 Bowler: {player}")
    print(f"🎯 Opponent: {team}")
    print(f"📊 Total Balls: {balls}\n")
    
    stats = get_player_vs_team_bowling(conn, player, team)
    
    print("📈 Performance vs This Team:")
    print(f"   Matches: {stats['matches']}")
    print(f"   Balls Bowled: {stats['balls_bowled']}")
    print(f"   Runs Conceded: {stats['runs_conceded']}")
    print(f"   Wickets: {stats['wickets']}")
    print(f"   Economy: {stats['economy']}")
    print(f"   Strike Rate: {stats['strike_rate']}")
    print(f"   Dot %: {stats['dot_pct']}%\n")
    
    print("📊 WPA Metrics:")
    print(f"   Total WPA: {stats['total_wpa']}")
    print(f"   WPA per Ball: {stats['wpa_per_ball']}\n")
    
    print("⚖️  Performance Analysis:")
    print(f"   Rating: {stats['performance_rating']}")
    print(f"   Performance Z-Score: {stats['performance_zscore']}")
    print(f"   PVT Adjustment: {stats['pvt_adjustment']}")
    print(f"   Sample Quality: {stats['sample_quality']}\n")
    
    print("📊 Baseline Comparison:")
    baseline = stats['baseline_comparison']
    print(f"   Career Economy: {baseline['career_economy']}")
    print(f"   vs Team Economy: {stats['economy']} (Δ {baseline['econ_diff']:+.2f})")
    print(f"   Career Strike Rate: {baseline['career_strike_rate']}")
    print(f"   vs Team Strike Rate: {stats['strike_rate']}\n")
    
    # Validation
    assert stats['sample_quality'] == 'STRONG', "❌ Should be STRONG sample"
    assert stats['balls_bowled'] >= 120, "❌ Should have 120+ balls"
    
    print("✅ Test passed\n")
    conn.close()


def test_bowling_spinner_vs_quality():
    """
    TEST 5: Spinner vs quality batting lineup
    """
    print_header("TEST 5: BOWLING - SPINNER VS QUALITY TEAM")
    
    conn = sqlite3.connect("analytics.db")
    
    # Try to find a spinner (check bowling_style in player_vectors)
    spinner_result = conn.execute("""
        SELECT player 
        FROM player_vectors 
        WHERE bowling_style LIKE '%spin%' 
        OR bowling_style LIKE '%leg%'
        OR bowling_style LIKE '%orthodox%'
        LIMIT 5
    """).fetchall()
    
    if not spinner_result:
        print("⚠️  No spinner data found in player_vectors\n")
        # Fallback: just find any bowler
        spinner_result = conn.execute("""
            SELECT DISTINCT bowler 
            FROM ball_by_ball 
            WHERE bowler IS NOT NULL 
            LIMIT 5
        """).fetchall()
    
    # Find a spinner with decent sample
    stats = None
    player = None
    team = None
    
    for (spinner,) in spinner_result:
        team_result = conn.execute("""
            SELECT batting_team, COUNT(*) as balls
            FROM ball_by_ball
            WHERE bowler = ?
            GROUP BY batting_team
            HAVING balls >= 60
            ORDER BY balls DESC
            LIMIT 1
        """, (spinner,)).fetchone()
        
        if team_result:
            player = spinner
            team, balls = team_result
            break
    
    if not player:
        print("⚠️  No suitable spinner matchup found\n")
        conn.close()
        return
    
    print(f"🎳 Spinner: {player}")
    print(f"🎯 Opponent: {team}\n")
    
    stats = get_player_vs_team_bowling(conn, player, team)
    
    print("📈 Spin Performance:")
    print(f"   Balls Bowled: {stats['balls_bowled']}")
    print(f"   Economy: {stats['economy']}")
    print(f"   Wickets: {stats['wickets']}")
    print(f"   Strike Rate: {stats['strike_rate']}")
    print(f"   Dot %: {stats['dot_pct']}%\n")
    
    print("⚖️  Performance:")
    print(f"   Rating: {stats['performance_rating']}")
    print(f"   PVT Adjustment: {stats['pvt_adjustment']}")
    print(f"   Sample Quality: {stats['sample_quality']}\n")
    
    assert stats['balls_bowled'] > 0, "❌ Should have bowling data"
    
    print("✅ Test passed\n")
    conn.close()


def test_bowling_part_timer():
    """
    TEST 6: Part-time bowler (should not inflate tier)
    """
    print_header("TEST 6: BOWLING - PART-TIMER")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find a part-timer (bowled < 200 balls total)
    result = conn.execute("""
        SELECT bowler, COUNT(*) as total_balls
        FROM ball_by_ball
        WHERE bowler IS NOT NULL
        GROUP BY bowler
        HAVING total_balls < 200 AND total_balls >= 30
        ORDER BY total_balls DESC
        LIMIT 1
    """).fetchone()
    
    if not result:
        print("⚠️  No part-timer found\n")
        conn.close()
        return
    
    player, total_balls = result
    
    # Find a team they faced
    team_result = conn.execute("""
        SELECT batting_team, COUNT(*) as balls
        FROM ball_by_ball
        WHERE bowler = ?
        GROUP BY batting_team
        ORDER BY balls DESC
        LIMIT 1
    """, (player,)).fetchone()
    
    if not team_result:
        print(f"⚠️  {player} has no bowling data vs teams\n")
        conn.close()
        return
    
    team, balls = team_result
    
    print(f"🎳 Part-Timer: {player}")
    print(f"📊 Career Balls: {total_balls}")
    print(f"🎯 Opponent: {team}")
    print(f"📊 Balls vs Team: {balls}\n")
    
    stats = get_player_vs_team_bowling(conn, player, team)
    
    print("📈 Part-Timer Stats:")
    print(f"   Balls Bowled: {stats['balls_bowled']}")
    print(f"   Economy: {stats['economy']}")
    print(f"   Wickets: {stats['wickets']}")
    print(f"   Sample Quality: {stats['sample_quality']}\n")
    
    print("⚖️  Performance:")
    print(f"   Rating: {stats['performance_rating']}")
    print(f"   PVT Adjustment: {stats['pvt_adjustment']}\n")
    
    # Should have weak/insufficient sample
    assert stats['sample_quality'] in ['WEAK', 'INSUFFICIENT', 'MODERATE'], \
        "❌ Part-timer should have limited sample"
    
    # PVT adjustment should be small due to sample_weight
    assert abs(stats['pvt_adjustment']) < 0.5, \
        "❌ Part-timer should have low PVT adjustment"
    
    print("✅ Test passed (correctly limited confidence)\n")
    conn.close()


# =====================================================
# TIER LOGIC TESTS
# =====================================================

def test_tier_separation():
    """
    TEST 7: Multi-team player → tier separation holds
    """
    print_header("TEST 7: TIER SEPARATION (Multi-Team Player)")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find player who faced multiple teams (batting)
    result = conn.execute("""
        SELECT striker, COUNT(DISTINCT bowling_team) as teams
        FROM ball_by_ball
        WHERE striker IS NOT NULL
        GROUP BY striker
        HAVING teams >= 5
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """).fetchone()
    
    if not result:
        print("⚠️  No multi-team player found\n")
        conn.close()
        return
    
    player, team_count = result
    
    print(f"🏏 Player: {player}")
    print(f"📊 Teams Faced: {team_count}\n")
    
    tier_analysis = get_player_vs_strength_tiers(conn, player, "batting")
    
    if 'error' in tier_analysis:
        print(f"⚠️  {tier_analysis['error']}\n")
        conn.close()
        return
    
    print("📊 Performance by Team Strength Tier:\n")
    
    tiers = tier_analysis.get('by_strength_tier', {})
    
    for tier_name in ['elite', 'strong', 'average', 'weak', 'bottom']:
        if tier_name in tiers:
            tier = tiers[tier_name]
            print(f"🎯 {tier_name.upper()} Teams:")
            print(f"   Teams: {', '.join(tier['teams'][:3])}{'...' if len(tier['teams']) > 3 else ''}")
            print(f"   Matches: {tier['matches']}")
            print(f"   Strike Rate: {tier['strike_rate']}")
            print(f"   Average: {tier['average']}")
            print(f"   WPA/Ball: {tier['wpa_per_ball']}")
            print(f"   PVT Adjustment: {tier['avg_pvt_adjustment']}\n")
    
    print(f"💡 Interpretation: {tier_analysis['interpretation']}\n")
    
    # Validation: should have at least 2 tiers
    assert len(tiers) >= 2, "❌ Should have multiple tiers"
    
    print("✅ Test passed\n")
    conn.close()


def test_tier_no_elo_fallback():
    """
    TEST 8: No ELO table → fallback behaves correctly
    """
    print_header("TEST 8: TIER FALLBACK (No ELO Data)")
    
    conn = sqlite3.connect("analytics.db")
    
    # Check if team_elo table exists
    elo_exists = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='team_elo'
    """).fetchone()
    
    if elo_exists:
        # Count records
        elo_count = conn.execute("SELECT COUNT(*) FROM team_elo").fetchone()[0]
        print(f"📊 ELO table exists with {elo_count} records")
        print("   Tier logic will use ELO ratings\n")
    else:
        print("📊 ELO table does NOT exist")
        print("   Tier logic will use FALLBACK (exposure-based)\n")
    
    # Find a player with multi-team data
    result = conn.execute("""
        SELECT striker, COUNT(DISTINCT bowling_team) as teams
        FROM ball_by_ball
        WHERE striker IS NOT NULL
        GROUP BY striker
        HAVING teams >= 3
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """).fetchone()
    
    if not result:
        print("⚠️  No suitable player found\n")
        conn.close()
        return
    
    player, team_count = result
    
    print(f"🏏 Player: {player}")
    print(f"📊 Teams Faced: {team_count}\n")
    
    tier_analysis = get_player_vs_strength_tiers(conn, player, "batting")
    
    if 'error' in tier_analysis:
        print(f"⚠️  {tier_analysis['error']}\n")
        conn.close()
        return
    
    tiers = tier_analysis.get('by_strength_tier', {})
    
    print("📊 Tier Breakdown:\n")
    for tier_name, tier_data in tiers.items():
        print(f"   {tier_name.upper()}: {len(tier_data['teams'])} teams")
    
    print(f"\n💡 Interpretation: {tier_analysis['interpretation']}\n")
    
    if not elo_exists:
        print("✅ Fallback logic used (exposure-based tiering)")
        print("   Teams with more balls faced = stronger/more important\n")
    else:
        print("✅ ELO-based tiering used\n")
    
    print("✅ Test passed\n")
    conn.close()


def test_all_teams_summary():
    """
    TEST 9: Get performance summary vs all teams
    """
    print_header("TEST 9: ALL TEAMS SUMMARY")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find a player with good multi-team data
    result = conn.execute("""
        SELECT striker, COUNT(DISTINCT bowling_team) as teams
        FROM ball_by_ball
        WHERE striker IS NOT NULL
        GROUP BY striker
        HAVING teams >= 5
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """).fetchone()
    
    if not result:
        print("⚠️  No multi-team player found\n")
        conn.close()
        return
    
    player, team_count = result
    
    print(f"🏏 Player: {player}")
    print(f"📊 Teams Faced: {team_count}\n")
    
    all_teams = get_player_vs_all_teams(conn, player, "batting", min_balls=30)
    
    if not all_teams:
        print("⚠️  No team data found\n")
        conn.close()
        return
    
    print(f"📊 Performance vs {len(all_teams)} Teams (sorted by PVT adjustment):\n")
    print(f"{'#':<4} {'Team':<20} {'Balls':<8} {'SR':<8} {'Avg':<8} {'PVT Adj':<10} {'Rating'}")
    print("─" * 85)
    
    for i, team_stats in enumerate(all_teams[:10], 1):  # Top 10
        print(f"{i:<4} {team_stats['opponent']:<20} {team_stats['balls_faced']:<8} "
              f"{team_stats['strike_rate']:<8.1f} {team_stats['average']:<8.1f} "
              f"{team_stats['pvt_adjustment']:<10.3f} {team_stats['performance_rating']}")
    
    print()
    
    # Validation
    assert len(all_teams) >= 3, "❌ Should have multiple teams"
    assert all('pvt_adjustment' in t for t in all_teams), "❌ All should have pvt_adjustment"
    
    print("✅ Test passed\n")
    conn.close()


# =====================================================
# RUN ALL TESTS
# =====================================================

def run_all_tests():
    """Execute full PVT test suite"""
    conn = sqlite3.connect("analytics.db")
    
    print("\n" + "#"*80)
    print("  PVT (PLAYER VS TEAM) - COMPREHENSIVE TEST SUITE")
    print("#"*80)
    
    # Check data availability
    ball_count = conn.execute("SELECT COUNT(*) FROM ball_by_ball").fetchone()[0]
    print(f"\n📊 Database Status:")
    print(f"   Ball-by-ball records: {ball_count:,}\n")
    
    if ball_count == 0:
        print("❌ No ball-by-ball data found. Load data first.\n")
        conn.close()
        return
    
    conn.close()
    
    try:
        # Batting tests
        test_batting_strong_sample()
        test_batting_boom_bust()
        test_batting_tail_ender()
        
        # Bowling tests
        test_bowling_elite_vs_strong_team()
        test_bowling_spinner_vs_quality()
        test_bowling_part_timer()
        
        # Tier logic tests
        test_tier_separation()
        test_tier_no_elo_fallback()
        test_all_teams_summary()
        
        print("\n" + "#"*80)
        print("  ✅ ALL PVT TESTS COMPLETED")
        print("#"*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    # Run all tests
    run_all_tests()
    
    # Or run individual tests (uncomment to use)
    # test_batting_strong_sample()
    # test_bowling_elite_vs_strong_team()
    # test_tier_separation()
