import sqlite3

try:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Check and create stores table
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stores'")
    if not c.fetchone():
        print("Stores table missing. Creating now...")
        c.execute("""
        CREATE TABLE stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            store_name TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
    else:
        print("Stores table exists.")

    # Check and create financial tables if missing
    financial_tables = {
        'income': """
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            store_id INTEGER,
            FOREIGN KEY(store_id) REFERENCES stores(id)
        )
        """,
        'expenses': """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            store_id INTEGER,
            FOREIGN KEY(store_id) REFERENCES stores(id)
        )
        """,
        'capital': """
        CREATE TABLE IF NOT EXISTS capital (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            store_id INTEGER,
            FOREIGN KEY(store_id) REFERENCES stores(id)
        )
        """,
        'assets': """
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            asset_name TEXT NOT NULL,
            value REAL NOT NULL,
            store_id INTEGER,
            FOREIGN KEY(store_id) REFERENCES stores(id)
        )
        """,
        'liabilities': """
        CREATE TABLE IF NOT EXISTS liabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            liability_name TEXT NOT NULL,
            amount REAL NOT NULL,
            store_id INTEGER,
            FOREIGN KEY(store_id) REFERENCES stores(id)
        )
        """
    }

    for table, sql in financial_tables.items():
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not c.fetchone():
            print(f"{table} table missing. Creating now...")
            c.execute(sql)
        else:
            print(f"{table} table exists.")

    # Add store_id column to financial tables if not present
    for table in financial_tables.keys():
        c.execute(f"PRAGMA table_info({table})")
        columns = {row[1] for row in c.fetchall()}
        if 'store_id' not in columns:
            print(f"Adding store_id to {table}...")
            c.execute(f"ALTER TABLE {table} ADD COLUMN store_id INTEGER")

    conn.commit()
    print("Database schema verified and repaired successfully.")
except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    conn.close()