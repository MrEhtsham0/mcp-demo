import os
import asyncio
import aiosqlite

# Use project directory for database - use absolute path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
print(PROJECT_DIR)
DB_PATH = os.path.join(PROJECT_DIR, "expenses.db")

# Ensure the path is absolute
DB_PATH = os.path.abspath(DB_PATH)

async def init_db_async():
    """Async version of database initialization"""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            await c.execute("PRAGMA journal_mode=WAL")
            await c.execute("""
                CREATE TABLE IF NOT EXISTS expenses(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
            """)
            # Test write access
            await c.execute("INSERT OR IGNORE INTO expenses(date, amount, category) VALUES ('2000-01-01', 0, 'test')")
            await c.execute("DELETE FROM expenses WHERE category = 'test'")
            await c.commit()
            print("Database initialized successfully with write access")
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

def init_db():
    """Synchronous wrapper for async database initialization"""
    try:
        asyncio.run(init_db_async())
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise
