# test/player_replacement_test.py
"""COMPREHENSIVE PLAYER REPLACEMENT TEST - PRODUCTION VERSION"""

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from end_applications.player_replacement_util import (
    get_player_replacements, 
    get_player_info,
    get_player_replacements_smart  # Smart version with adaptive filters
)
import sqlite3


# your_app.py (YOUR PRODUCTION CODE)

import sqlite3
from end_applications.player_replacement_util import get_player_replacements_smart

def find_ipl_replacement(injured_player, team_nationality_slot):
    """Example: IPL team needs replacement"""
    
    conn = sqlite3.connect("analytics.db")
    
    replacements = get_player_replacements_smart(
        conn=conn,
        target_player=injured_player,
        top_k=5,
        allowed_nationalities=[team_nationality_slot],
        match_batting_style=True  # Keep similar style
    )
    
    conn.close()
    
    return replacements


# Usage:
if __name__ == "__main__":
    # Example: RCB needs to replace injured Kohli with Indian player
    options = find_ipl_replacement("HH Pandya", "India")
    
    for i, player in enumerate(options, 1):
        print(f"{i}. {player['player']} - Score: {player['final_score']}")

