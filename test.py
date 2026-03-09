# test/verify_schema.py
"""Verify ball_by_ball table schema"""

import sqlite3

conn = sqlite3.connect("analytics.db")

print("\n" + "="*80)
print("  BALL-BY-BALL SCHEMA VERIFICATION")
print("="*80 + "\n")

# Check if table exists
check = conn.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='ball_by_ball'
""").fetchone()

if not check:
    print(" ball_by_ball table does NOT exist")
    print("\nTo create it:")
    print("1. Uncomment load_ball_by_ball_combined() in db/build_analytics_db.py")
    print("2. Run: python db/build_analytics_db.py\n")
    conn.close()
    exit(1)

print(" ball_by_ball table EXISTS\n")

# Get columns
columns = conn.execute("PRAGMA table_info(ball_by_ball)").fetchall()

print(" Columns:")
for col in columns:
    print(f"   - {col[1]} ({col[2]})")

print("\n Checking critical columns...")

critical_cols = {
    'striker': False,
    'bowler': False,
    'runs_off_bat': False,
    'player_dismissed': False,
    'venue': False,
    'match_id': False
}

# Check for RPA/WPA columns
rpa_col = None
wpa_col = None

for col in columns:
    col_name = col[1].lower()
    if col_name in critical_cols:
        critical_cols[col_name] = True
    if 'rpa' in col_name:
        rpa_col = col[1]
    if 'wpa' in col_name:
        wpa_col = col[1]

print()
for col, exists in critical_cols.items():
    status = "Correct" if exists else "Wrong"
    print(f"{status} {col}")

print(f"\n RPA column: {rpa_col if rpa_col else ' NOT FOUND'}")
print(f" WPA column: {wpa_col if wpa_col else ' NOT FOUND'}")

if not rpa_col or not wpa_col:
    print("\n  WARNING: RPA/WPA columns not found!")
    print("   PVP queries assume columns named 'rpa' and 'wpa'")
    print("   If yours are named differently, update pvp_util.py queries\n")

# Sample data
print("\n Sample data (first 3 rows):\n")
sample = conn.execute("SELECT * FROM ball_by_ball LIMIT 3").fetchall()

if sample:
    col_names = [col[1] for col in columns]
    for i, row in enumerate(sample, 1):
        print(f"Row {i}:")
        for name, val in zip(col_names[:10], row[:10]):  # Show first 10 cols
            print(f"   {name}: {val}")
        print()
else:
    print(" Table is EMPTY\n")

conn.close()
