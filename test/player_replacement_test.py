# this is solely for testing the function
from end_applications.player_replacement import get_player_replacements

if __name__ == "__main__":
    import sqlite3

    # Connect to analytics DB
    conn = sqlite3.connect("analytics.db")

    # Target player
    target = "V Kohli"

    # ---- Scenario 1: Global replacement (no nationality restriction)
    print("\n=== Global replacements (any nationality, active only) ===\n")

    res_global = get_player_replacements(
        conn=conn,
        target_player=target,
        top_k=5,
        allowed_nationalities=None,     # allow all
        exclude_retired=True,            # enforce 12-month rule
        max_days_since_last_match=365
    )

    for r in res_global:
        print(r)

    # ---- Scenario 2: Same-nationality replacement (e.g. IPL Indian slot)
    print("\n=== Same-nationality replacements (India only) ===\n")

    res_india = get_player_replacements(
        conn=conn,
        target_player=target,
        top_k=5,
        allowed_nationalities=["India" , "West Indies" , "Australia"],
        exclude_retired=True,
        max_days_since_last_match=365
    )

    for r in res_india:
        print(r)

    conn.close()
