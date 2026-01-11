import sqlite3

try:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON")

    # Verify stores table exists
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

    # Add store_id column to financial tables
    tables = ['income', 'expenses', 'capital', 'assets', 'liabilities']
    for table in tables:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN store_id INTEGER")
            print(f"Added store_id to {table}")
        except sqlite3.OperationalError as e:
            print(f"Column store_id already exists in {table}: {e}")

    # Assign default store_id to existing records
    c.execute("SELECT id FROM stores LIMIT 1")
    result = c.fetchone()
    default_store_id = result[0] if result else 1
    for table in tables:
        c.execute(f"UPDATE {table} SET store_id = ? WHERE store_id IS NULL", (default_store_id,))

    conn.commit()
    print("Database migration completed successfully.")
except sqlite3.Error as e:
    print(f"Migration error: {e}")
finally:
    conn.close()