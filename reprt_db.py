import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE capital ADD COLUMN description TEXT;")
except sqlite3.OperationalError:
    pass  # Column already exists

try:
    cur.execute("ALTER TABLE income ADD COLUMN description TEXT;")
except sqlite3.OperationalError:
    pass

try:
    cur.execute("ALTER TABLE liabilities ADD COLUMN description TEXT;")
except sqlite3.OperationalError:
    pass

try:
    cur.execute("ALTER TABLE assets ADD COLUMN description TEXT;")
except sqlite3.OperationalError:
    pass

conn.commit()
conn.close()
