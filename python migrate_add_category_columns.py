import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Add category column to assets if not exists
try:
    c.execute("ALTER TABLE assets ADD COLUMN category TEXT")
    print("Added 'category' column to assets table.")
except sqlite3.OperationalError:
    print("'category' column already exists in assets table.")

# Add category column to liabilities if not exists
try:
    c.execute("ALTER TABLE liabilities ADD COLUMN category TEXT")
    print("Added 'category' column to liabilities table.")
except sqlite3.OperationalError:
    print("'category' column already exists in liabilities table.")

conn.commit()
conn.close()
