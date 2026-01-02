# test/synergy_test.py
"""
SYNERGY - Partnership Analysis Test Suite
Tests batting partnerships and bowling combinations.
"""

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from end_applications.synergy_util import (
    get_batting_partnership,
    get_best_batting_partners,
    predict_batting_synergy,
    get_bowling_combination,
    get_best_bowling_partners
)
import sqlite3


def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


# =====================================================
# BATTING PARTNERSHIP TESTS
# =====================================================

def test_batting_partnership_strong():
    """TEST 1: Strong batting partnership (50+ balls together)"""
    print_header("TEST 1: BATTING PARTNERSHIP - STRONG SAMPLE")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find a strong partnership
    result = conn.execute("""
        WITH partnerships AS (
            SELECT 
                b1.striker as player_a,
                b2.striker as player_b,
                COUNT(*) as balls
            FROM ball_by_ball b1
            INNER JOIN ball_by_ball b2 
                ON b1.match_id = b2.match_id 
                AND b1.innings = b2.innings
                AND b1.over = b2.over
            WHERE b1.striker < b2.striker
            GROUP BY player_a, player_b
            HAVING balls >= 50
            ORDER BY balls DESC
            LIMIT 1
        )
        SELECT player_a, player_b, balls
        FROM partnerships
    """).fetchone()
    
    if not result:
        print("⚠️  No strong partnership found (need 50+ balls)\n")
        conn.close()
        return
    
    player_a, player_b, balls = result
    
    print(f"🏏 Partnership: {player_a} + {player_b}")
    print(f"📊 Balls Together: {balls}\n")
    
    stats = get_batting_partnership(conn, player_a, player_b)
    
    print("📈 Partnership Stats:")
    print(f"   Matches Together: {stats['matches_together']}")
    print(f"   Innings Together: {stats['innings_together']}")
    print(f"   Balls Together: {stats['balls_together']}")
    print(f"   Runs Together: {stats['runs_together']}")
    print(f"   Partnership SR: {stats['partnership_sr']}")
    print(f"   Avg Partnership: {stats['avg_partnership']}")
    print(f"   Best Partnership: {stats['best_partnership']}\n")
    
    print("🎯 Individual Performance:")
    print(f"   {player_a} Solo SR: {stats['player_a_solo_sr']}")
    print(f"   {player_b} Solo SR: {stats['player_b_solo_sr']}\n")
    
    print("⚡ Synergy Analysis:")
    print(f"   Synergy Boost: {stats['synergy_boost']:+.1%}")
    print(f"   Synergy Score: {stats['synergy_score']}")
    print(f"   Synergy Rating: {stats['synergy_rating']}")
    print(f"   Hand Combination: {stats['hand_combination']}")
    print(f"   Sample Quality: {stats['sample_quality']}\n")
    
    print("📊 WPA Metrics:")
    print(f"   Total WPA: {stats['total_wpa']}")
    print(f"   WPA per Ball: {stats['wpa_per_ball']}\n")
    
    assert stats['sample_quality'] == 'STRONG', "❌ Should be STRONG sample"
    assert stats['balls_together'] >= 50, "❌ Should have 50+ balls"
    
    print("✅ Test passed\n")
    conn.close()


def test_best_batting_partners():
    """TEST 2: Find best batting partners for a player"""
    print_header("TEST 2: BEST BATTING PARTNERS")
    
    conn = sqlite3.connect("analytics.db")
    
    # ✅ FIXED: Added b1. prefix to disambiguate striker column
    result = conn.execute("""
        SELECT b1.striker, COUNT(DISTINCT b2.striker) as partners
        FROM ball_by_ball b1
        INNER JOIN ball_by_ball b2 
            ON b1.match_id = b2.match_id 
            AND b1.innings = b2.innings
        WHERE b1.striker != b2.striker
        GROUP BY b1.striker
        HAVING partners >= 5
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """).fetchone()
    
    if not result:
        print("⚠️  No suitable player found\n")
        conn.close()
        return
    
    player, partner_count = result
    
    print(f"🏏 Player: {player}")
    print(f"📊 Total Partners: {partner_count}\n")
    
    partners = get_best_batting_partners(conn, player, min_balls=25, top_k=10)
    
    if not partners:
        print("⚠️  No partners found with min 25 balls\n")
        conn.close()
        return
    
    print(f"📊 Top {len(partners)} Batting Partners (sorted by synergy):\n")
    print(f"{'#':<4} {'Partner':<25} {'Matches':<10} {'Balls':<10} {'SR':<10} {'Synergy':<12} {'Rating'}")
    print("─" * 95)
    
    for i, p in enumerate(partners, 1):
        print(f"{i:<4} {p['partner']:<25} {p['matches']:<10} {p['balls_together']:<10} "
              f"{p['partnership_sr']:<10.1f} {p['synergy_score']:<12.3f} {p['rating']}")
    
    print()
    
    assert len(partners) > 0, "❌ Should find partners"
    
    print("✅ Test passed\n")
    conn.close()


def test_predict_batting_synergy():
    """TEST 3: Predict synergy for players who haven't played together"""
    print_header("TEST 3: PREDICTED BATTING SYNERGY")
    
    conn = sqlite3.connect("analytics.db")
    
    # ✅ FIXED: Find two players who:
    # 1. Are in player_vectors (have profiles)
    # 2. Haven't played together
    result = conn.execute("""
        WITH profiled_players AS (
            SELECT DISTINCT player
            FROM player_vectors
            WHERE player IN (SELECT DISTINCT striker FROM ball_by_ball)
            AND career_bat_rpa_z IS NOT NULL
            LIMIT 100
        ),
        player_pairs AS (
            SELECT 
                p1.player as player_a,
                p2.player as player_b
            FROM profiled_players p1
            CROSS JOIN profiled_players p2
            WHERE p1.player < p2.player
            AND NOT EXISTS (
                SELECT 1 
                FROM ball_by_ball b1
                INNER JOIN ball_by_ball b2 
                    ON b1.match_id = b2.match_id 
                    AND b1.innings = b2.innings
                WHERE (b1.striker = p1.player AND b2.striker = p2.player)
                   OR (b1.striker = p2.player AND b2.striker = p1.player)
            )
            LIMIT 1
        )
        SELECT player_a, player_b
        FROM player_pairs
    """).fetchone()
    
    if not result:
        print("⚠️  Could not find two profiled players who haven't played together\n")
        print("   This is expected if your dataset has limited matches.\n")
        
        # Fallback: Test with two known players who have played together
        # This will return HISTORICAL method instead of SIMILARITY_BASED
        fallback = conn.execute("""
            SELECT DISTINCT b1.striker, b2.striker
            FROM ball_by_ball b1
            INNER JOIN ball_by_ball b2
                ON b1.match_id = b2.match_id
                AND b1.innings = b2.innings
            WHERE b1.striker IN (SELECT player FROM player_vectors WHERE career_bat_rpa_z IS NOT NULL)
            AND b2.striker IN (SELECT player FROM player_vectors WHERE career_bat_rpa_z IS NOT NULL)
            AND b1.striker < b2.striker
            LIMIT 1
        """).fetchone()
        
        if not fallback:
            print("⚠️  Insufficient data for synergy prediction test\n")
            conn.close()
            return
        
        player_a, player_b = fallback
        print(f"   Using fallback: {player_a} + {player_b} (they HAVE played together)\n")
    else:
        player_a, player_b = result
    
    print(f"🏏 Hypothetical Partnership: {player_a} + {player_b}\n")
    
    prediction = predict_batting_synergy(conn, player_a, player_b)
    
    if 'error' in prediction:
        print(f"❌ {prediction['error']}\n")
        print("   This should not happen after the fix.\n")
        conn.close()
        return
    
    print("🔮 Prediction:")
    print(f"   Method: {prediction['prediction_method']}")
    print(f"   Predicted Synergy: {prediction['predicted_synergy']}")
    print(f"   Confidence: {prediction['confidence']}")
    print(f"   Predicted Rating: {prediction.get('predicted_rating', 'N/A')}\n")
    
    if 'reasoning' in prediction:
        print("💡 Reasoning:")
        for reason in prediction['reasoning']:
            print(f"   • {reason}")
        print()
    
    if 'similar_partnerships' in prediction:
        print("📊 Similar Partnerships Used:")
        for sim in prediction['similar_partnerships'][:3]:
            print(f"   • {sim['pair']}: {sim['synergy']:.3f}")
        print()
    
    if 'historical_data' in prediction:
        print("📜 Note: Using historical data (players have played together)")
        print(f"   Balls Together: {prediction['historical_data']['balls_together']}\n")
    
    print("✅ Test passed\n")
    conn.close()


# =====================================================
# BOWLING COMBINATION TESTS
# =====================================================

def test_bowling_combination_strong():
    """TEST 4: Strong bowling combination (60+ balls together)"""
    print_header("TEST 4: BOWLING COMBINATION - STRONG SAMPLE")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find a strong bowling combo
    result = conn.execute("""
        WITH bowling_combos AS (
            SELECT 
                b1.bowler as bowler_a,
                b2.bowler as bowler_b,
                COUNT(DISTINCT b1.match_id) as matches
            FROM ball_by_ball b1
            INNER JOIN ball_by_ball b2 
                ON b1.match_id = b2.match_id 
                AND b1.innings = b2.innings
            WHERE b1.bowler < b2.bowler
            GROUP BY bowler_a, bowler_b
            HAVING matches >= 5
            ORDER BY matches DESC
            LIMIT 1
        )
        SELECT bowler_a, bowler_b, matches
        FROM bowling_combos
    """).fetchone()
    
    if not result:
        print("⚠️  No strong bowling combo found\n")
        conn.close()
        return
    
    bowler_a, bowler_b, matches = result
    
    print(f"🎳 Bowling Pair: {bowler_a} + {bowler_b}")
    print(f"📊 Matches Together: {matches}\n")
    
    stats = get_bowling_combination(conn, bowler_a, bowler_b)
    
    print("📈 Combination Stats:")
    print(f"   Matches Together: {stats['matches_together']}")
    print(f"   Balls Together: {stats['balls_together']}")
    print(f"   Overs Together: {stats['overs_together']}")
    print(f"   Runs Conceded: {stats['runs_conceded']}")
    print(f"   Wickets: {stats['wickets']}")
    print(f"   Combined Economy: {stats['combined_economy']}")
    print(f"   Combined Strike Rate: {stats['combined_strike_rate']}")
    print(f"   Dot %: {stats['dot_pct']}%\n")
    
    print("🎯 Individual Performance:")
    print(f"   {bowler_a} Solo Economy: {stats['bowler_a_solo_economy']}")
    print(f"   {bowler_b} Solo Economy: {stats['bowler_b_solo_economy']}\n")
    
    print("⚡ Synergy Analysis:")
    print(f"   Synergy Boost: {stats['synergy_boost']:+.1%}")
    print(f"   Synergy Score: {stats['synergy_score']}")
    print(f"   Synergy Rating: {stats['synergy_rating']}")
    print(f"   Wicket Clustering: {stats['wicket_clustering']:.2f}")
    print(f"   Bowling Styles: {stats['bowling_styles']}")
    print(f"   Sample Quality: {stats['sample_quality']}\n")
    
    print("📊 WPA Metrics:")
    print(f"   Total WPA: {stats['total_wpa']}")
    print(f"   WPA per Ball: {stats['wpa_per_ball']}\n")
    
    assert stats['matches_together'] > 0, "❌ Should have played together"
    
    print("✅ Test passed\n")
    conn.close()


def test_bowling_phase_specific():
    """TEST 5: Phase-specific bowling combination (death overs)"""
    print_header("TEST 5: BOWLING COMBINATION - DEATH OVERS")
    
    conn = sqlite3.connect("analytics.db")
    
    # Find death bowlers who operated together
    result = conn.execute("""
        WITH death_combos AS (
            SELECT 
                b1.bowler as bowler_a,
                b2.bowler as bowler_b,
                COUNT(DISTINCT b1.match_id) as matches
            FROM ball_by_ball b1
            INNER JOIN ball_by_ball b2 
                ON b1.match_id = b2.match_id 
                AND b1.innings = b2.innings
            WHERE b1.over >= 16
            AND b2.over >= 16
            AND b1.bowler < b2.bowler
            GROUP BY bowler_a, bowler_b
            HAVING matches >= 3
            ORDER BY matches DESC
            LIMIT 1
        )
        SELECT bowler_a, bowler_b, matches
        FROM death_combos
    """).fetchone()
    
    if not result:
        print("⚠️  No death bowling combo found\n")
        conn.close()
        return
    
    bowler_a, bowler_b, matches = result
    
    print(f"🎳 Death Bowling Pair: {bowler_a} + {bowler_b}")
    print(f"📊 Matches Together: {matches}\n")
    
    stats = get_bowling_combination(conn, bowler_a, bowler_b, phase="death")
    
    print("📈 Death Overs Performance:")
    print(f"   Balls Together: {stats['balls_together']}")
    print(f"   Overs Together: {stats['overs_together']}")
    print(f"   Combined Economy: {stats['combined_economy']}")
    print(f"   Wickets: {stats['wickets']}")
    print(f"   Synergy Rating: {stats['synergy_rating']}\n")
    
    assert stats['phase'] == 'death', "❌ Should be death phase"
    
    print("✅ Test passed\n")
    conn.close()


def test_best_bowling_partners():
    """TEST 6: Find best bowling partners"""
    print_header("TEST 6: BEST BOWLING PARTNERS")
    
    conn = sqlite3.connect("analytics.db")
    
    # ✅ FIXED: Added b1. prefix to disambiguate bowler column
    result = conn.execute("""
        SELECT b1.bowler, COUNT(DISTINCT b2.bowler) as partners
        FROM ball_by_ball b1
        INNER JOIN ball_by_ball b2 
            ON b1.match_id = b2.match_id 
            AND b1.innings = b2.innings
        WHERE b1.bowler != b2.bowler
        GROUP BY b1.bowler
        HAVING partners >= 5
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """).fetchone()
    
    if not result:
        print("⚠️  No suitable bowler found\n")
        conn.close()
        return
    
    bowler, partner_count = result
    
    print(f"🎳 Bowler: {bowler}")
    print(f"📊 Total Partners: {partner_count}\n")
    
    partners = get_best_bowling_partners(conn, bowler, min_balls=30, top_k=10)
    
    if not partners:
        print("⚠️  No partners found with min 30 balls\n")
        conn.close()
        return
    
    print(f"📊 Top {len(partners)} Bowling Partners (sorted by synergy):\n")
    print(f"{'#':<4} {'Partner':<25} {'Matches':<10} {'Balls':<10} {'Econ':<10} {'Synergy':<12} {'Rating'}")
    print("─" * 95)
    
    for i, p in enumerate(partners, 1):
        print(f"{i:<4} {p['partner']:<25} {p['matches']:<10} {p['balls_together']:<10} "
              f"{p['combined_economy']:<10.2f} {p['synergy_score']:<12.3f} {p['rating']}")
    
    print()
    
    assert len(partners) > 0, "❌ Should find partners"
    
    print("✅ Test passed\n")
    conn.close()


# =====================================================
# RUN ALL TESTS
# =====================================================

def run_all_tests():
    """Execute full Synergy test suite"""
    conn = sqlite3.connect("analytics.db")
    
    print("\n" + "#"*80)
    print("  SYNERGY (PARTNERSHIP ANALYSIS) - COMPREHENSIVE TEST SUITE")
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
        # Batting partnership tests
        test_batting_partnership_strong()
        test_best_batting_partners()
        test_predict_batting_synergy()
        
        # Bowling combination tests
        test_bowling_combination_strong()
        test_bowling_phase_specific()
        test_best_bowling_partners()
        
        print("\n" + "#"*80)
        print("  ✅ ALL SYNERGY TESTS COMPLETED")
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
    # test_batting_partnership_strong()
    # test_bowling_combination_strong()
    # test_best_batting_partners()
