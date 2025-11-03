import asyncio
import sys
import os
import random
from faker import Faker

from sqlalchemy.ext.asyncio import AsyncSession
# Ensure the app directory is in the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import your app modules
from app.core.database import async_engine
from app.models.expense import Expense

# Optional imports — if you have Redis cache implemented
try:
    from app.core.redis_cache import redis_cache, get_expense_pattern_key, get_expenses_pattern_key
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

fake = Faker()


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

async def create_async_session():
    """Create an async database session."""
    async with AsyncSession(async_engine) as session:
        yield session


# ---------------------------------------------------------------------------
# Faker Data Generator
# ---------------------------------------------------------------------------

async def insert_expense_records(count: int = 1000):
    """
    Insert fake expense records asynchronously.
    Can be safely called from FastAPI startup or CLI.
    """
    print(f"🚀 Starting to insert {count} fake expense records...")

    async with AsyncSession(async_engine) as session:
        expenses = []

        categories = {
            "Food": ["Groceries", "Restaurants", "Cafes"],
            "Transportation": ["Fuel", "Maintenance", "Ride Share"],
            "Utilities": ["Electricity", "Water", "Internet"],
            "Entertainment": ["Movies", "Games", "Concerts"],
            "Health": ["Medicine", "Doctor", "Gym"],
            "Shopping": ["Clothes", "Electronics", "Furniture"],
        }

        for _ in range(count):
            category = random.choice(list(categories.keys()))
            subcategory = random.choice(categories[category])
            expense = Expense(
                date=fake.date_between(start_date="-180d", end_date="today"),
                amount=round(random.uniform(5.0, 500.0), 2),
                category=category,
                subcategory=subcategory,
                note=fake.sentence(nb_words=8),
            )
            expenses.append(expense)

        session.add_all(expenses)
        await session.commit()

        print(f"✅ Successfully inserted {count} expense records.")

        # Optional Redis cache cleanup
        if REDIS_AVAILABLE:
            await invalidate_expense_cache()
        else:
            print("⚠️ Redis not configured — skipping cache invalidation.")


# ---------------------------------------------------------------------------
# Redis Cache Invalidation (Optional)
# ---------------------------------------------------------------------------

async def invalidate_expense_cache():
    """Clear related expense cache keys (optional)."""
    try:
        keys_to_delete = [
            get_expense_pattern_key(),
            get_expenses_pattern_key()
        ]
        for pattern in keys_to_delete:
            await redis_cache.delete_pattern(pattern)
        print("🧹 Cleared Redis expense cache.")
    except Exception as e:
        print(f"⚠️ Failed to clear Redis cache: {e}")


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

async def main():
    """Run faker data insertion when executed directly."""
    # Read count from CLI args if provided
    count = 1000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        count = int(sys.argv[1])

    await insert_expense_records(count)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Script interrupted by user.")
