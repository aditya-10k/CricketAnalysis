'''# test/check_ball_columns.py
"""Check what columns exist in ball_by_ball CSV"""

import pandas as pd

csv_path = "C:/Desktop/crickanal/outputs/ball_by_ball_rpa_wpa_combined.csv"

print("\n" + "="*80)
print("  CHECKING BALL-BY-BALL CSV COLUMNS")
print("="*80 + "\n")

try:
    # Read just the first row to check columns
    df = pd.read_csv(csv_path, nrows=1)
    
    print(f"✅ File found: {csv_path}")
    print(f"   Total columns: {len(df.columns)}\n")
    
    print("📋 All Columns:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2}. {col}")
    
    print("\n🔍 Critical Columns Check:")
    
    critical = {
        'striker': 'striker' in df.columns,
        'bowler': 'bowler' in df.columns,
        'runs_off_bat': 'runs_off_bat' in df.columns,
        'player_dismissed': 'player_dismissed' in df.columns,
        'venue': 'venue' in df.columns,
        'match_id': 'match_id' in df.columns,
    }
    
    for col, exists in critical.items():
        status = "✅" if exists else "❌"
        print(f"   {status} {col}")
    
    # Check for RPA/WPA columns
    print("\n📊 RPA/WPA Columns:")
    rpa_cols = [col for col in df.columns if 'rpa' in col.lower()]
    wpa_cols = [col for col in df.columns if 'wpa' in col.lower()]
    
    if rpa_cols:
        for col in rpa_cols:
            print(f"   ✅ {col}")
    else:
        print("   ❌ No RPA columns found")
    
    if wpa_cols:
        for col in wpa_cols:
            print(f"   ✅ {col}")
    else:
        print("   ❌ No WPA columns found")
    
    # Show sample data
    print("\n📦 Sample Row (first 10 columns):")
    for col in df.columns[:10]:
        print(f"   {col}: {df[col].iloc[0]}")
    
    print("\n" + "="*80)
    
    # Tell user what to do based on findings
    if rpa_cols and wpa_cols:
        print("✅ READY TO LOAD")
        print(f"\n⚠️  NOTE: Your RPA column is: '{rpa_cols[0]}'")
        print(f"⚠️  NOTE: Your WPA column is: '{wpa_cols[0]}'")
        
        if rpa_cols[0] != 'rpa' or wpa_cols[0] != 'wpa':
            print("\n🔧 ACTION REQUIRED:")
            print("   pvp_util.py expects columns named 'rpa' and 'wpa'")
            print("   Your columns are named differently.")
            print("\n   Option 1: Rename columns in CSV before loading")
            print("   Option 2: Update pvp_util.py queries to use your column names")
    else:
        print("❌ MISSING RPA/WPA COLUMNS")
        print("   Cannot proceed with PVP module")
    
    print("="*80 + "\n")

except FileNotFoundError:
    print(f"❌ File not found: {csv_path}\n")
except Exception as e:
    print(f"❌ Error reading file: {e}\n")
'''

import sqlite3

db_path = "analytics.db"   # adjust path if needed

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("""
    SELECT name 
    FROM sqlite_master 
    WHERE type='table'
""")

tables = cursor.fetchall()

for (table_name,) in tables:
    print(f"\n📦 Table: {table_name}")
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    for col in columns:
        cid, name, dtype, notnull, default, pk = col
        print(f"  - {name} ({dtype})")

conn.close()
