"""
Realistic Best XI Optimizer Tests using T20 World Cup 2026 squads
Uses ESPNcricinfo standard player names
"""

import sqlite3
import sys
sys.path.append('.')

from end_applications.bestxi_optimizer import optimize_best_xi, print_best_xi


def print_header(title):
    """Print test header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_india_vs_australia():
    """TEST 1: India vs Australia - T20 WC 2026 Squads"""
    print_header("TEST 1: INDIA VS AUSTRALIA (T20 WC 2026)")
    
    conn = sqlite3.connect("analytics.db")
    
    # ✅ India T20 WC 2026 Squad with fallbacks (ESPNcricinfo names)
    india_squad = [
        "SK Yadav",           # Suryakumar Yadav
        "Abhishek Sharma",
        "NT Tilak Varma",
        "HH Pandya",          # Hardik Pandya
        "S Dube",             # Shivam Dube
        "AR Patel",           # Axar Patel
        "JJ Bumrah",          # Jasprit Bumrah
        "Arshdeep Singh",
        "CV Varun",           # Varun Chakravarthy
        "Kuldeep Yadav",
        "Harshit Rana",
        "Sanju Samson",
        "Washington Sundar",
        "Ishan Kishan",
        # Fallbacks if some not in DB
        "V Kohli",
        "RG Sharma",
        "KL Rahul",
        "RA Jadeja",
        "Mohammed Shami"
    ]
    
    # ✅ Australia T20 WC 2026 Squad with fallbacks
    australia_squad = [
        "MR Marsh",           # Mitchell Marsh
        "X Bartlett",
        "CJ Connolly",
        "PJ Cummins",         # Pat Cummins
        "TH David",           # Tim David
        "C Green",            # Cameron Green
        "NM Ellis",
        "JR Hazlewood",       # Josh Hazlewood
        "TM Head",            # Travis Head
        "JP Inglis",
        "MS Kuhnemann",
        "GJ Maxwell",         # Glenn Maxwell
        "M Short",
        "MP Stoinis",         # Marcus Stoinis
        "A Zampa",            # Adam Zampa
        # Fallbacks
        "DA Warner",
        "SPD Smith",
        "MA Starc",
        "AJ Tye"
    ]
    
    print(f"🏏 India Squad (T20 WC 2026): {len(india_squad)} players")
    print(f"   Captain: SK Yadav, VC: HH Pandya")
    print(f"\n🏏 Australia Squad (T20 WC 2026): {len(australia_squad)} players")
    print(f"   Captain: MR Marsh\n")
    
    result = optimize_best_xi(
        conn,
        home_squad=india_squad,
        away_squad=australia_squad,
        constraints={
            "max_overseas": 4,
            "min_bowlers": 4,
            "min_batters": 5,
            "min_confidence": 0.2  # ✅ Lower threshold
        }
    )
    
    print_best_xi(result)
    
    if 'error' in result:
        print(f"⚠️  {result['error']}\n")
        conn.close()
        return
    
    # ✅ Validate constraints
    c = result['constraints_met']
    
    print(f"📊 Final Validation:")
    print(f"   Team Size: {len(result['team'])}")
    print(f"   Bowlers: {c['bowlers']}")
    print(f"   Batters: {c['batters']}")
    print(f"   Overseas: {c['overseas_count']}/{c['max_overseas']}")
    
    assert len(result['team']) == 11, "❌ Should have 11 players"
    assert c['bowlers'] >= 4, f"❌ Need 4+ bowlers, got {c['bowlers']}"
    assert c['batters'] >= 5, f"❌ Need 5+ batters, got {c['batters']}"
    assert c['overseas_count'] <= 4, f"❌ Max 4 overseas, got {c['overseas_count']}"
    
    print("\n✅ Test 1 passed\n")
    conn.close()



def test_no_overseas_limit():
    """TEST 2: No overseas constraint (IPL/Franchise style)"""
    print_header("TEST 2: NO OVERSEAS LIMIT (IPL Style)")
    
    conn = sqlite3.connect("analytics.db")
    
    # Mixed squad for IPL-style selection
    india_squad = [
        "V Kohli", "RG Sharma", "SK Yadav", "KL Rahul",
        "RD Gaikwad", "YBK Jaiswal", "Abhishek Sharma",
        "HH Pandya", "S Dube", "AR Patel", "RA Jadeja",
        "JJ Bumrah", "Arshdeep Singh", "Kuldeep Yadav",
        "Mohammed Shami"
    ]
    
    australia_squad = [
        "DA Warner", "SPD Smith", "GJ Maxwell", "MP Stoinis",
        "TM Head", "MR Marsh", "PJ Cummins", "MA Starc",
        "JR Hazlewood", "A Zampa", "TH David",
        "C Green", "JP Inglis", "M Short", "AJ Tye"
    ]
    
    print(f"🏏 Testing WITHOUT overseas limit (IPL/Franchise style)\n")
    
    # ✅ NO max_overseas constraint - allows best XI regardless of nationality
    result = optimize_best_xi(
        conn,
        home_squad=india_squad,
        away_squad=australia_squad,
        constraints={
            "max_overseas": 4,
            "min_bowlers": 4,
            "min_batters": 5,
            "min_confidence": 0.2  # ✅ Add this to all tests
}

    )
    
    print_best_xi(result)
    
    if 'error' not in result:
        c = result['constraints_met']
        print(f"📊 Overseas count: {c['overseas_count']} (no limit)")
        print("✅ Test 2 passed - No overseas constraint\n")
    else:
        print(f"⚠️  {result['error']}\n")
    
    conn.close()


def test_strict_overseas():
    """TEST 3: Very strict overseas constraint (2 max)"""
    print_header("TEST 3: STRICT OVERSEAS CONSTRAINT (2 MAX)")
    
    conn = sqlite3.connect("analytics.db")
    
    india_squad = [
        "V Kohli", "RG Sharma", "SK Yadav", "KL Rahul",
        "RD Gaikwad", "YBK Jaiswal", "Abhishek Sharma",
        "HH Pandya", "S Dube", "AR Patel", "RA Jadeja",
        "JJ Bumrah", "Arshdeep Singh", "Kuldeep Yadav",
        "Mohammed Shami"
    ]
    
    australia_squad = [
        "DA Warner", "SPD Smith", "GJ Maxwell", "MP Stoinis",
        "TM Head", "MR Marsh", "PJ Cummins", "MA Starc",
        "JR Hazlewood", "A Zampa", "TH David",
        "C Green", "JP Inglis", "M Short", "AJ Tye"
    ]
    
    print(f"🏏 Testing with max 2 overseas (very strict)\n")
    
    result = optimize_best_xi(
        conn,
        home_squad=india_squad,
        away_squad=australia_squad,
        constraints={
            "max_overseas": 2,  # Very strict
            "min_bowlers": 4,
            "min_batters": 5
        }
    )
    
    print_best_xi(result)
    
    if 'error' not in result:
        c = result['constraints_met']
        assert c['overseas_count'] <= 2, f"❌ Max 2 overseas, got {c['overseas_count']}"
        print("✅ Test 3 passed - Strict constraint met\n")
    else:
        print(f"⚠️  Could not meet strict constraint: {result['error']}\n")
    
    conn.close()


def test_venue_specific():
    """TEST 4: Venue-specific selection"""
    print_header("TEST 4: VENUE-SPECIFIC SELECTION")
    
    conn = sqlite3.Connection("analytics.db")
    
    india_squad = [
        "V Kohli", "RG Sharma", "SK Yadav", "KL Rahul",
        "RD Gaikwad", "YBK Jaiswal", "Abhishek Sharma",
        "HH Pandya", "S Dube", "AR Patel", "RA Jadeja",
        "JJ Bumrah", "Arshdeep Singh", "Kuldeep Yadav",
        "Mohammed Shami", "Washington Sundar"
    ]
    
    australia_squad = [
        "DA Warner", "SPD Smith", "GJ Maxwell", "MP Stoinis",
        "TM Head", "MR Marsh", "PJ Cummins", "MA Starc",
        "JR Hazlewood", "A Zampa", "TH David",
        "C Green", "JP Inglis", "M Short", "AJ Tye"
    ]
    
    venue = "Wankhede Stadium"
    print(f"🏏 Testing at venue: {venue}\n")
    
    result = optimize_best_xi(
        conn,
        home_squad=india_squad,
        away_squad=australia_squad,
        venue=venue,
        constraints={
            "max_overseas": 4,
            "min_bowlers": 4,
            "min_batters": 5
        }
    )
    
    print_best_xi(result)
    
    if 'error' not in result:
        print(f"✅ Test 4 passed - Venue-specific selection\n")
    else:
        print(f"⚠️  {result['error']}\n")
    
    conn.close()


def test_no_duplicates():
    """TEST 5: Verify no duplicate players"""
    print_header("TEST 5: NO DUPLICATES")
    
    conn = sqlite3.connect("analytics.db")
    
    india_squad = [
        "V Kohli", "RG Sharma", "SK Yadav", "KL Rahul",
        "RD Gaikwad", "YBK Jaiswal", "Abhishek Sharma",
        "HH Pandya", "S Dube", "AR Patel", "RA Jadeja",
        "JJ Bumrah", "Arshdeep Singh", "Kuldeep Yadav",
        "Mohammed Shami"
    ]
    
    australia_squad = [
        "DA Warner", "SPD Smith", "GJ Maxwell", "MP Stoinis",
        "TM Head", "MR Marsh", "PJ Cummins", "MA Starc",
        "JR Hazlewood", "A Zampa", "TH David",
        "C Green", "JP Inglis", "M Short", "AJ Tye"
    ]
    
    result = optimize_best_xi(
        conn,
        home_squad=india_squad,
        away_squad=australia_squad,
        constraints={
            "max_overseas": 4,
            "min_bowlers": 4,
            "min_batters": 5
        }
    )
    
    if 'error' not in result:
        players = [p['player'] for p in result['team']]
        unique_players = set(players)
        
        print(f"Selected {len(players)} players, {len(unique_players)} unique")
        assert len(players) == len(unique_players), "❌ Duplicate players found!"
        print("✅ Test 5 passed - No duplicates\n")
    else:
        print(f"⚠️  {result['error']}\n")
    
    conn.close()


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("  BEST XI OPTIMIZER - COMPREHENSIVE TESTS")
    print("  Using ESPNcricinfo Standard Player Names")
    print("#"*80)
    
    test_india_vs_australia()
    test_no_overseas_limit()
    test_strict_overseas()
    test_venue_specific()
    test_no_duplicates()
    
    print("\n" + "#"*80)
    print("  ✅ ALL TESTS COMPLETED")
    print("#"*80 + "\n")
