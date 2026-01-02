# test/pvp_test.py
"""
PVP (Player vs Player) - Test Suite
Each function can be called independently for modular testing.
"""

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from end_applications.pvp_util import (
    get_head_to_head,
    predict_matchup,
    get_bowler_vs_batters,
    get_venue_specific_h2h
)
import sqlite3


def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


# =====================================================
# TEST FUNCTION 1: Basic Head-to-Head
# =====================================================
def test_head_to_head():
    """Test basic head-to-head statistics"""
    print_header("TEST 1: HEAD-TO-HEAD STATS")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find a common matchup
    matchup = conn.execute("""
        SELECT striker, bowler, COUNT(*) as balls
        FROM ball_by_ball
        WHERE striker IS NOT NULL AND bowler IS NOT NULL
        GROUP BY striker, bowler
        HAVING balls >= 20
        ORDER BY balls DESC
        LIMIT 1
    """).fetchone()
    
    if not matchup:
        print("⚠️  No suitable matchups found (need 20+ balls)\n")
        conn.close()
        return
    
    striker, bowler, balls = matchup
    
    print(f"🏏 Matchup: {striker} vs {bowler} ({balls} balls)\n")
    
    h2h = get_head_to_head(conn, striker, bowler)
    
    print(f"📊 Historical Stats:")
    print(f"   Balls Faced: {h2h['balls_faced']}")
    print(f"   Runs Scored: {h2h['runs_scored']}")
    print(f"   Dismissals: {h2h['dismissals']}")
    print(f"   Strike Rate: {h2h['strike_rate']}")
    print(f"   Boundaries: {h2h['boundaries']} ({h2h['boundary_pct']}%)")
    print(f"   Avg WPA: {h2h['avg_wpa']}")
    print(f"   Dismissal Probability: {h2h['dismissal_probability']}%")
    print(f"   Matches Together: {h2h['matches']}")
    print(f"   Sample Quality: {h2h['sample_size']}\n")
    
    conn.close()
    print("✅ Test completed\n")


# =====================================================
# TEST FUNCTION 2: Matchup Prediction
# =====================================================
def test_matchup_prediction():
    """Test matchup prediction with different sample sizes"""
    print_header("TEST 2: MATCHUP PREDICTION (Bayesian)")
    
    conn = sqlite3.connect("analytics.db")
    
    # Test cases with different sample sizes
    test_cases = []
    
    # Strong sample (30+ balls)
    strong = conn.execute("""
        SELECT striker, bowler, COUNT(*) as balls
        FROM ball_by_ball
        WHERE striker IS NOT NULL AND bowler IS NOT NULL
        GROUP BY striker, bowler
        HAVING balls >= 30
        ORDER BY balls DESC
        LIMIT 1
    """).fetchone()
    
    if strong:
        test_cases.append(("STRONG Sample (30+ balls)", strong[0], strong[1]))
    
    # Moderate sample (12-29 balls)
    moderate = conn.execute("""
        SELECT striker, bowler, COUNT(*) as balls
        FROM ball_by_ball
        WHERE striker IS NOT NULL AND bowler IS NOT NULL
        GROUP BY striker, bowler
        HAVING balls BETWEEN 12 AND 29
        ORDER BY balls DESC
        LIMIT 1
    """).fetchone()
    
    if moderate:
        test_cases.append(("MODERATE Sample (12-29 balls)", moderate[0], moderate[1]))
    
    # Weak sample (6-11 balls)
    weak = conn.execute("""
        SELECT striker, bowler, COUNT(*) as balls
        FROM ball_by_ball
        WHERE striker IS NOT NULL AND bowler IS NOT NULL
        GROUP BY striker, bowler
        HAVING balls BETWEEN 6 AND 11
        ORDER BY balls DESC
        LIMIT 1
    """).fetchone()
    
    if weak:
        test_cases.append(("WEAK Sample (6-11 balls)", weak[0], weak[1]))
    
    for desc, striker, bowler in test_cases:
        print(f"\n{'─'*80}")
        print(f"  {desc}")
        print(f"{'─'*80}\n")
        
        prediction = predict_matchup(conn, striker, bowler)
        
        if 'error' in prediction:
            print(f"⚠️  {prediction['error']}\n")
            continue
        
        h2h = prediction['historical_data']
        pred = prediction['prediction']
        
        print(f"🏏 Matchup: {striker} vs {bowler}\n")
        
        print(f"📈 Historical Data:")
        print(f"   Balls: {h2h['balls_faced']}")
        print(f"   Strike Rate: {h2h['strike_rate']}")
        print(f"   Dismissals: {h2h['dismissals']}")
        print(f"   Sample: {h2h['sample_size']}\n")
        
        print(f"🎯 Prediction:")
        print(f"   Expected Strike Rate: {pred['expected_strike_rate']}")
        print(f"   Dismissal Probability: {pred['dismissal_probability_pct']}%")
        print(f"   Expected WPA/ball: {pred['expected_wpa_per_ball']}")
        print(f"   Confidence: {pred['confidence']}\n")
        
        print(f"⚖️  Matchup Advantage: {pred['matchup_advantage']}")
        print(f"   {pred['advantage_interpretation']}\n")
        
        print(f"🔢 Weighting:")
        print(f"   H2H Weight: {pred['h2h_weight']} (direct history)")
        print(f"   Baseline Weight: {pred['baseline_weight']} (career stats)")
        
        if pred.get('style_adjustment'):
            print(f"   Style Adjustment: {pred['style_adjustment']}\n")
        
        # Show style context if available
        if prediction.get('style_context'):
            style = prediction['style_context']
            print(f"\n🎨 Style Matchup:")
            print(f"   Batting: {style['batting_style']}")
            print(f"   Bowling: {style['bowling_style']}")
            if style.get('notes'):
                for note in style['notes']:
                    print(f"   → {note}")
        print()
    
    conn.close()
    print("✅ Test completed\n")


# =====================================================
# TEST FUNCTION 3: Bowler Dominance
# =====================================================
def test_bowler_dominance():
    """Test which batters a bowler dominates"""
    print_header("TEST 3: BOWLER DOMINANCE ANALYSIS")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find a bowler with good data
    bowler_data = conn.execute("""
        SELECT bowler, COUNT(DISTINCT striker) as unique_batters
        FROM ball_by_ball
        WHERE bowler IS NOT NULL
        GROUP BY bowler
        HAVING unique_batters >= 5
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """).fetchone()
    
    if not bowler_data:
        print("⚠️  No suitable bowlers found\n")
        conn.close()
        return
    
    bowler = bowler_data[0]
    
    print(f"🎳 Bowler: {bowler}\n")
    
    dominance = get_bowler_vs_batters(conn, bowler, min_balls=12, top_k=10)
    
    if not dominance:
        print("⚠️  No matchup data found\n")
        conn.close()
        return
    
    print(f"📊 TOP 10 BATTERS FACED (sorted by dismissals):\n")
    print(f"{'#':<4} {'Batter':<25} {'Balls':<8} {'Runs':<8} {'Outs':<6} {'SR':<8} {'Out%':<8} {'Venues':<8} {'Result'}")
    print("─" * 110)
    
    for i, m in enumerate(dominance, 1):
        print(f"{i:<4} {m['striker']:<25} {m['balls_faced']:<8} {m['runs_conceded']:<8} "
              f"{m['dismissals']:<6} {m['strike_rate_allowed']:<8.1f} "
              f"{m['dismissal_rate_pct']:<8.2f} {m['venues_faced_at']:<8} {m['bowler_performance']}")
    
    print()
    conn.close()
    print("✅ Test completed\n")


# =====================================================
# TEST FUNCTION 4: Venue-Specific H2H
# =====================================================
def test_venue_specific():
    """Test head-to-head broken down by venue"""
    print_header("TEST 4: VENUE-SPECIFIC HEAD-TO-HEAD")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find a matchup that occurred at multiple venues
    matchup = conn.execute("""
        SELECT striker, bowler, COUNT(DISTINCT venue) as venues
        FROM ball_by_ball
        WHERE striker IS NOT NULL AND bowler IS NOT NULL AND venue IS NOT NULL
        GROUP BY striker, bowler
        HAVING venues >= 2
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """).fetchone()
    
    if not matchup:
        print("⚠️  No multi-venue matchups found\n")
        conn.close()
        return
    
    striker, bowler, venues = matchup
    
    print(f"🏏 Matchup: {striker} vs {bowler}")
    print(f"   Met at {venues} different venues\n")
    
    venue_stats = get_venue_specific_h2h(conn, striker, bowler)
    
    if not venue_stats:
        print("⚠️  No venue data found\n")
        conn.close()
        return
    
    print(f"📍 Breakdown by Venue:\n")
    print(f"{'Venue':<35} {'Balls':<8} {'Runs':<8} {'Outs':<6} {'SR':<8} {'Out%'}")
    print("─" * 85)
    
    for v in venue_stats:
        print(f"{v['venue']:<35} {v['balls']:<8} {v['runs']:<8} "
              f"{v['dismissals']:<6} {v['strike_rate']:<8.1f} {v['dismissal_rate_pct']:<8.2f}")
    
    print()
    conn.close()
    print("✅ Test completed\n")


# =====================================================
# TEST FUNCTION 5: Unknown Matchup (Baseline Only)
# =====================================================
def test_unknown_matchup():
    """Test prediction for unknown matchup (no history)"""
    print_header("TEST 5: UNKNOWN MATCHUP PREDICTION")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find a striker and bowler who've never faced each other
    striker = conn.execute("""
        SELECT DISTINCT striker 
        FROM ball_by_ball 
        WHERE striker IS NOT NULL 
        LIMIT 1
    """).fetchone()
    
    bowler = conn.execute("""
        SELECT DISTINCT bowler 
        FROM ball_by_ball 
        WHERE bowler IS NOT NULL 
        AND bowler NOT IN (
            SELECT DISTINCT bowler FROM ball_by_ball WHERE striker = ?
        )
        LIMIT 1
    """, (striker[0] if striker else '',)).fetchone()
    
    if not striker or not bowler:
        print("⚠️  Could not find suitable unknown matchup\n")
        conn.close()
        return
    
    striker_name = striker[0]
    bowler_name = bowler[0]
    
    print(f"🏏 New Matchup: {striker_name} vs {bowler_name}")
    print(f"   (No previous encounters)\n")
    
    prediction = predict_matchup(conn, striker_name, bowler_name)
    
    if 'error' in prediction:
        print(f"⚠️  {prediction['error']}\n")
        conn.close()
        return
    
    h2h = prediction['historical_data']
    pred = prediction['prediction']
    striker_base = prediction['striker_baseline']
    bowler_base = prediction['bowler_baseline']
    
    print(f"📊 Prediction Based on Career Baselines:\n")
    
    print(f"   {striker_name} Batting Career:")
    print(f"      Avg Strike Rate: {striker_base['avg_strike_rate']}")
    print(f"      Avg Balls/Dismissal: {striker_base['avg_balls_per_dismissal']}")
    print(f"      Total Balls: {striker_base['total_balls']}\n")
    
    print(f"   {bowler_name} Bowling Career:")
    print(f"      Avg Runs/Ball: {bowler_base['avg_runs_per_ball']}")
    print(f"      Economy: {bowler_base['avg_economy']} RPO")
    print(f"      Wicket Rate: {bowler_base['wicket_rate']}")
    print(f"      Total Balls: {bowler_base['total_balls']}\n")
    
    print(f"🎯 Expected Outcome:")
    print(f"   Strike Rate: {pred['expected_strike_rate']}")
    print(f"   Dismissal Probability: {pred['dismissal_probability_pct']}%")
    print(f"   Matchup Advantage: {pred['matchup_advantage']}")
    print(f"   {pred['advantage_interpretation']}\n")
    
    conn.close()
    print("✅ Test completed\n")


# =====================================================
# TEST FUNCTION 6: Custom Matchup Query
# =====================================================
def test_custom_matchup(striker_name, bowler_name, venue=None):
    """
    Test custom matchup specified by user
    
    Usage:
        test_custom_matchup("V Kohli", "Rashid Khan")
        test_custom_matchup("AB de Villiers", "Jasprit Bumrah", "Wankhede Stadium")
    """
    print_header(f"CUSTOM MATCHUP: {striker_name} vs {bowler_name}")
    
    if venue:
        print(f"📍 Venue: {venue}\n")
    
    conn = sqlite3.connect("analytics.db")
    
    prediction = predict_matchup(conn, striker_name, bowler_name, venue=venue)
    
    if 'error' in prediction:
        print(f"⚠️  {prediction['error']}\n")
        conn.close()
        return
    
    h2h = prediction['historical_data']
    pred = prediction['prediction']
    
    print(f"📊 Historical Head-to-Head:")
    print(f"   Balls: {h2h['balls_faced']}")
    print(f"   Runs: {h2h['runs_scored']}")
    print(f"   Dismissals: {h2h['dismissals']}")
    print(f"   Strike Rate: {h2h['strike_rate']}")
    print(f"   Sample: {h2h['sample_size']}\n")
    
    print(f"🎯 Prediction:")
    print(f"   Expected Strike Rate: {pred['expected_strike_rate']}")
    print(f"   Dismissal Probability: {pred['dismissal_probability_pct']}%")
    print(f"   Expected WPA/ball: {pred['expected_wpa_per_ball']}\n")
    
    print(f"⚖️  Matchup: {pred['advantage_interpretation']}")
    print(f"   Advantage Score: {pred['matchup_advantage']}\n")
    
    conn.close()
    print("✅ Test completed\n")


# =====================================================
# RUN ALL TESTS
# =====================================================
def run_all_tests():
    """Execute full PVP test suite"""
    conn = sqlite3.connect("analytics.db")
    
    print("\n" + "#"*80)
    print("  PVP (PLAYER VS PLAYER) - COMPREHENSIVE TEST SUITE")
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
        test_head_to_head()
        test_matchup_prediction()
        test_bowler_dominance()
        test_venue_specific()
        test_unknown_matchup()
        
        print("\n" + "#"*80)
        print("  ✅ ALL PVP TESTS COMPLETED")
        print("#"*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


# =====================================================
# MAIN - Choose which tests to run
# =====================================================
if __name__ == "__main__":
    # Option 1: Run all tests
    # run_all_tests()
    
    # Option 2: Run specific tests (uncomment to use)
    # test_head_to_head()
    # test_matchup_prediction()
    # test_bowler_dominance()
    # test_venue_specific()
    # test_unknown_matchup()
    
    # Option 3: Test custom matchup (uncomment and edit)
    test_custom_matchup("V Kohli", "UT Yadav")
    # test_custom_matchup("AB de Villiers", "Jasprit Bumrah", venue="Wankhede Stadium")
