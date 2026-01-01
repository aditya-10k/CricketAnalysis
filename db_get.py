import sqlite3

conn = sqlite3.connect("analytics.db")
cur = conn.cursor()

cur.execute('''SELECT role
FROM player_vectors
WHERE player = 'V Kohli';
''')
for row in cur.fetchall():
    print(row)

conn.close()
