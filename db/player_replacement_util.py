def get_candidate_players(conn, target_player):
    row = conn.execute(
        "SELECT role FROM player_vectors WHERE player = ?",
        (target_player,)
    ).fetchone()

    if row is None:
        raise ValueError("Target player not found")

    role = row[0]

    rows = conn.execute(
        """
        SELECT player
        FROM player_vectors
        WHERE role = ?
        AND days_since_last_match <= 365
        AND player != ?

        """,
        (role, target_player)
    ).fetchall()

    return [r[0] for r in rows]
