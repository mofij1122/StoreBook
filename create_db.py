import sqlite3

try:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON")

    # Create users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Create stores table linked to user
    c.execute("""
    CREATE TABLE IF NOT EXISTS stores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        store_name TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Create store_details table
    c.execute("""
    CREATE TABLE IF NOT EXISTS store_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        storename TEXT NOT NULL,
        storetype TEXT NOT NULL,
        ownername TEXT NOT NULL
    )
    """)

    # Create capital table
    c.execute("""
    CREATE TABLE IF NOT EXISTS capital (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        store_id INTEGER,
        FOREIGN KEY(store_id) REFERENCES stores(id)
    )
    """)

    # Create income table with category column added
    c.execute("""
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        store_id INTEGER,
        FOREIGN KEY(store_id) REFERENCES stores(id)
    )
    """)

    # Create expenses table
    c.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        store_id INTEGER,
        FOREIGN KEY(store_id) REFERENCES stores(id)
    )
    """)

    # Create assets table with category field
    c.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        asset_name TEXT NOT NULL,
        value REAL NOT NULL,
        category TEXT,
        store_id INTEGER,
        FOREIGN KEY(store_id) REFERENCES stores(id)
    )
    """)

    # Create liabilities table with category field
    c.execute("""
    CREATE TABLE IF NOT EXISTS liabilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        liability_name TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        store_id INTEGER,
        FOREIGN KEY(store_id) REFERENCES stores(id)
    )
    """)

    conn.commit()
    print("✅ All tables created successfully.")

    # Verify table creation
    tables = ['users', 'stores', 'store_details', 'income', 'expenses', 'capital', 'assets', 'liabilities']
    for table in tables:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if c.fetchone():
            print(f"{table} table created successfully.")
        else:
            print(f"Warning: {table} table creation failed.")

except sqlite3.Error as e:
    print(f"Database error during creation: {e}")

finally:
    conn.close()
