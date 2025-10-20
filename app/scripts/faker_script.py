#!/usr/bin/env python3
"""
Comprehensive Faker script to generate 1000 realistic expense records
"""
import asyncio
import random
import sys
import os
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.core.database import async_engine
from app.models.expense import Expense
from app.core.redis_cache import redis_cache, get_expense_pattern_key, get_expenses_pattern_key

# Initialize Faker with multiple locales for better data variety
fake = Faker(['en_US', 'en_GB', 'en_CA', 'en_AU'])

# Comprehensive expense categories with realistic subcategories and amount ranges
EXPENSE_CATEGORIES = {
    "Food & Dining": {
        "subcategories": [
            "Groceries", "Restaurant", "Fast Food", "Coffee & Tea", "Lunch",
            "Dinner", "Snacks", "Takeout", "Food Delivery", "Catering",
            "Bakery", "Deli", "Food Truck", "Fine Dining", "Café"
        ],
        "amount_range": (3.50, 250.00),
        "frequency_weight": 25,  # 25% of expenses
        "note_templates": [
            "Lunch at {company}",
            "Dinner with {person}",
            "Groceries from {company}",
            "Coffee at {company}",
            "Takeout from {company}",
            "Food delivery from {company}",
            "Catering for {event}",
            "Snacks at {company}",
            "Fine dining at {company}",
            "Food truck {company}"
        ]
    },
    "Transportation": {
        "subcategories": [
            "Gas", "Public Transit", "Taxi/Uber", "Parking", "Tolls",
            "Car Maintenance", "Bus", "Train", "Flight", "Rental Car",
            "Car Insurance", "DMV Fees", "Car Wash", "Oil Change", "Repairs"
        ],
        "amount_range": (5.00, 500.00),
        "frequency_weight": 15,  # 15% of expenses
        "note_templates": [
            "Gas at {company}",
            "Uber ride to {location}",
            "Parking at {location}",
            "Public transit pass",
            "Car maintenance at {company}",
            "Flight to {location}",
            "Car rental in {location}",
            "Tolls on {highway}",
            "Car insurance payment",
            "DMV registration"
        ]
    },
    "Shopping": {
        "subcategories": [
            "Clothing", "Electronics", "Books", "Gifts", "Home & Garden",
            "Sports & Recreation", "Beauty & Health", "Office Supplies", "Toys",
            "Jewelry", "Shoes", "Accessories", "Furniture", "Appliances", "Tools"
        ],
        "amount_range": (10.00, 2000.00),
        "frequency_weight": 20,  # 20% of expenses
        "note_templates": [
            "Purchase at {company}",
            "Online order from {company}",
            "Gift for {person}",
            "Clothing from {company}",
            "Electronics from {company}",
            "Books from {company}",
            "Furniture from {company}",
            "Tools from {company}",
            "Jewelry from {company}",
            "Shoes from {company}"
        ]
    },
    "Entertainment": {
        "subcategories": [
            "Movies", "Concerts", "Sports Events", "Games", "Streaming Services",
            "Museums", "Theater", "Amusement Parks", "Hobbies", "Subscriptions",
            "Music", "Video Games", "Books", "Magazines", "Events"
        ],
        "amount_range": (8.00, 300.00),
        "frequency_weight": 12,  # 12% of expenses
        "note_templates": [
            "Movie tickets at {company}",
            "Concert at {venue}",
            "Streaming subscription",
            "Game purchase",
            "Event at {venue}",
            "Museum visit",
            "Theater tickets",
            "Amusement park",
            "Music subscription",
            "Hobby supplies"
        ]
    },
    "Health & Fitness": {
        "subcategories": [
            "Doctor Visits", "Pharmacy", "Gym Membership", "Fitness Classes",
            "Medical Equipment", "Health Insurance", "Dental", "Vision", "Mental Health",
            "Supplements", "Personal Training", "Yoga", "Massage", "Therapy", "Medications"
        ],
        "amount_range": (15.00, 800.00),
        "frequency_weight": 10,  # 10% of expenses
        "note_templates": [
            "Doctor visit at {company}",
            "Gym membership",
            "Pharmacy at {company}",
            "Fitness class",
            "Health checkup",
            "Dental cleaning",
            "Eye exam",
            "Massage therapy",
            "Personal training",
            "Medication refill"
        ]
    },
    "Utilities": {
        "subcategories": [
            "Electricity", "Water", "Gas", "Internet", "Phone", "Cable",
            "Trash", "Sewer", "Heating", "Cooling", "Security", "Maintenance"
        ],
        "amount_range": (25.00, 400.00),
        "frequency_weight": 8,  # 8% of expenses
        "note_templates": [
            "Electricity bill",
            "Internet service",
            "Phone bill",
            "Water bill",
            "Gas bill",
            "Cable TV",
            "Security system",
            "Home maintenance",
            "Trash service",
            "Sewer service"
        ]
    },
    "Education": {
        "subcategories": [
            "Tuition", "Books", "School Supplies", "Online Courses", "Certifications",
            "Workshops", "Training", "Software Licenses", "Educational Materials",
            "Textbooks", "Course Fees", "Exam Fees", "Library", "Research", "Tools"
        ],
        "amount_range": (20.00, 1500.00),
        "frequency_weight": 5,  # 5% of expenses
        "note_templates": [
            "Course at {company}",
            "Books for {subject}",
            "Online learning platform",
            "Certification exam",
            "Workshop at {company}",
            "Software license",
            "Educational materials",
            "Textbook purchase",
            "Course registration",
            "Exam fee"
        ]
    },
    "Travel": {
        "subcategories": [
            "Hotels", "Flights", "Car Rental", "Travel Insurance", "Sightseeing",
            "Tours", "Travel Gear", "Visa Fees", "Airport Parking", "Baggage Fees",
            "Cruise", "Train", "Bus", "Taxi", "Activities"
        ],
        "amount_range": (50.00, 3000.00),
        "frequency_weight": 3,  # 3% of expenses
        "note_templates": [
            "Hotel in {location}",
            "Flight to {location}",
            "Car rental in {location}",
            "Travel insurance",
            "Vacation in {location}",
            "Cruise to {location}",
            "Tour in {location}",
            "Travel gear",
            "Visa application",
            "Airport parking"
        ]
    },
    "Personal Care": {
        "subcategories": [
            "Haircut", "Spa", "Cosmetics", "Personal Hygiene", "Clothing Care",
            "Dry Cleaning", "Laundry", "Personal Services", "Beauty Products",
            "Skincare", "Makeup", "Perfume", "Nails", "Massage", "Facial"
        ],
        "amount_range": (12.00, 300.00),
        "frequency_weight": 2,  # 2% of expenses
        "note_templates": [
            "Haircut at {company}",
            "Spa treatment",
            "Personal care products",
            "Beauty services",
            "Self-care day",
            "Skincare products",
            "Makeup purchase",
            "Nail salon",
            "Facial treatment",
            "Dry cleaning"
        ]
    }
}

def generate_realistic_expense_data():
    """Generate realistic expense data using Faker"""
    
    # Select category based on frequency weights
    categories = list(EXPENSE_CATEGORIES.keys())
    weights = [EXPENSE_CATEGORIES[cat]["frequency_weight"] for cat in categories]
    category = random.choices(categories, weights=weights)[0]
    
    category_data = EXPENSE_CATEGORIES[category]
    
    # Generate realistic date (within last 2 years, weighted towards recent)
    days_ago = random.choices(
        list(range(1, 730)),  # Last 2 years
        weights=[1 / (i + 1) for i in range(1, 730)]  # More recent dates are more likely
    )[0]
    expense_date = datetime.now() - timedelta(days=days_ago)
    
    # Generate realistic amount based on category
    min_amount, max_amount = category_data["amount_range"]
    
    # Use different distributions for different categories
    if category in ["Travel", "Shopping"]:
        # Higher amounts more likely for expensive categories
        amount = random.choices(
            [random.uniform(min_amount, max_amount) for _ in range(100)],
            weights=[i for i in range(100, 0, -1)]
        )[0]
    else:
        # Normal distribution for regular categories
        mean = (min_amount + max_amount) / 2
        std_dev = (max_amount - min_amount) / 6
        amount = max(min_amount, min(max_amount, random.normalvariate(mean, std_dev)))
    
    amount = round(amount, 2)
    
    # Select subcategory
    subcategory = random.choice(category_data["subcategories"])
    
    # Generate realistic note
    note_template = random.choice(category_data["note_templates"])
    
    # Replace placeholders with realistic data
    note = note_template.format(
        company=fake.company(),
        person=fake.name(),
        location=fake.city(),
        venue=fake.company(),
        event=fake.word(),
        highway=fake.word() + " Highway",
        subject=fake.word(),
        subject2=fake.word()
    )
    
    # Sometimes add additional context
    if random.random() < 0.3:  # 30% chance
        additional_contexts = [
            f" - {fake.sentence().rstrip('.')}",
            f" for {fake.word()}",
            f" with {fake.name()}",
            f" at {fake.time()}"
        ]
        note += random.choice(additional_contexts)
    
    return {
        "date": expense_date.strftime("%Y-%m-%d"),
        "amount": amount,
        "category": category,
        "subcategory": subcategory,
        "note": note
    }

async def insert_expense_records(num_records: int = 1000):
    """Insert expense records into the database with progress tracking"""
    print(f"🚀 Generating {num_records} realistic expense records...")
    print("=" * 60)
    
    # Generate all expense data first
    print("📊 Generating expense data...")
    expenses_data = []
    
    for i in range(num_records):
        expense_data = generate_realistic_expense_data()
        expenses_data.append(expense_data)
        
        if (i + 1) % 100 == 0:
            print(f"   Generated {i + 1}/{num_records} records...")
    
    print(f"✅ Generated {num_records} expense records")
    
    # Insert in batches for optimal performance
    batch_size = 50
    total_inserted = 0
    
    print(f"\n💾 Inserting records in batches of {batch_size}...")
    
    async with AsyncSession(async_engine) as session:
        try:
            for i in range(0, len(expenses_data), batch_size):
                batch = expenses_data[i:i + batch_size]
                expenses = [Expense(**data) for data in batch]
                
                session.add_all(expenses)
                await session.commit()
                total_inserted += len(expenses)
                
                progress = (total_inserted / num_records) * 100
                print(f"   Batch {i//batch_size + 1}: Inserted {total_inserted}/{num_records} records ({progress:.1f}%)")
            
            print(f"\n✅ Successfully inserted {total_inserted} expense records!")
            
            # Invalidate cache after bulk insert
            await invalidate_cache()
            
            # Warm up cache with fresh data
            await warmup_cache()
            
            # Generate comprehensive statistics
            await generate_statistics(expenses_data)
                
        except Exception as e:
            await session.rollback()
            print(f"❌ Error inserting records: {e}")
            raise

async def generate_statistics(expenses_data):
    """Generate and display comprehensive statistics"""
    print("\n📈 COMPREHENSIVE STATISTICS")
    print("=" * 60)
    
    # Basic statistics
    total_amount = sum(data['amount'] for data in expenses_data)
    avg_amount = total_amount / len(expenses_data)
    min_amount = min(data['amount'] for data in expenses_data)
    max_amount = max(data['amount'] for data in expenses_data)
    
    print(f"💰 Financial Summary:")
    print(f"   Total Amount: ${total_amount:,.2f}")
    print(f"   Average Amount: ${avg_amount:.2f}")
    print(f"   Min Amount: ${min_amount:.2f}")
    print(f"   Max Amount: ${max_amount:.2f}")
    
    # Date range
    dates = [data['date'] for data in expenses_data]
    print(f"\n📅 Date Range:")
    print(f"   From: {min(dates)}")
    print(f"   To: {max(dates)}")
    
    # Category breakdown
    category_stats = {}
    for data in expenses_data:
        category = data['category']
        if category not in category_stats:
            category_stats[category] = {
                'count': 0,
                'total_amount': 0,
                'avg_amount': 0,
                'min_amount': float('inf'),
                'max_amount': 0
            }
        
        stats = category_stats[category]
        stats['count'] += 1
        stats['total_amount'] += data['amount']
        stats['min_amount'] = min(stats['min_amount'], data['amount'])
        stats['max_amount'] = max(stats['max_amount'], data['amount'])
    
    # Calculate averages
    for stats in category_stats.values():
        stats['avg_amount'] = stats['total_amount'] / stats['count']
    
    print(f"\n📊 Category Breakdown:")
    print(f"{'Category':<20} {'Count':<8} {'Total':<12} {'Avg':<10} {'Min':<10} {'Max':<10}")
    print("-" * 80)
    
    for category, stats in sorted(category_stats.items(), key=lambda x: x[1]['total_amount'], reverse=True):
        print(f"{category:<20} {stats['count']:<8} ${stats['total_amount']:<11,.2f} ${stats['avg_amount']:<9.2f} ${stats['min_amount']:<9.2f} ${stats['max_amount']:<9.2f}")
    
    # Subcategory analysis
    print(f"\n🔍 Top Subcategories:")
    subcategory_counts = {}
    for data in expenses_data:
        subcategory = data['subcategory']
        subcategory_counts[subcategory] = subcategory_counts.get(subcategory, 0) + 1
    
    top_subcategories = sorted(subcategory_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for subcategory, count in top_subcategories:
        print(f"   {subcategory}: {count} records")
    
    # Amount distribution
    print(f"\n📊 Amount Distribution:")
    ranges = [
        (0, 25, "Under $25"),
        (25, 50, "$25-$50"),
        (50, 100, "$50-$100"),
        (100, 250, "$100-$250"),
        (250, 500, "$250-$500"),
        (500, 1000, "$500-$1000"),
        (1000, float('inf'), "Over $1000")
    ]
    
    for min_val, max_val, label in ranges:
        count = sum(1 for data in expenses_data if min_val <= data['amount'] < max_val)
        percentage = (count / len(expenses_data)) * 100
        print(f"   {label:<15}: {count:>4} records ({percentage:>5.1f}%)")
    
    # Monthly breakdown
    print(f"\n📅 Monthly Breakdown:")
    monthly_stats = {}
    for data in expenses_data:
        month_key = data['date'][:7]  # YYYY-MM
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {'count': 0, 'total': 0}
        monthly_stats[month_key]['count'] += 1
        monthly_stats[month_key]['total'] += data['amount']
    
    for month in sorted(monthly_stats.keys()):
        stats = monthly_stats[month]
        avg = stats['total'] / stats['count']
        print(f"   {month}: {stats['count']:>3} records, ${stats['total']:>8,.2f} total, ${avg:>6.2f} avg")

async def invalidate_cache():
    """Invalidate all expense-related cache entries"""
    print("\n🧹 Invalidating cache...")
    try:
        # Connect to Redis
        await redis_cache.connect()
        
        # Clear all expense-related cache keys
        expense_keys_deleted = await redis_cache.delete_pattern(get_expense_pattern_key())
        expenses_keys_deleted = await redis_cache.delete_pattern(get_expenses_pattern_key())
        
        total_deleted = expense_keys_deleted + expenses_keys_deleted
        
        if total_deleted > 0:
            print(f"✅ Cleared {total_deleted} cache entries")
        else:
            print("ℹ️  No cache entries found to clear")
        
        # Disconnect from Redis
        await redis_cache.disconnect()
        
    except Exception as e:
        print(f"⚠️  Cache invalidation failed: {e}")
        print("Continuing without cache invalidation...")

async def warmup_cache():
    """Warm up cache with fresh data"""
    print("\n🔥 Warming up cache...")
    try:
        # Connect to Redis
        await redis_cache.connect()
        
        from app.services.expense_service import ExpenseService
        from app.core.redis_cache import get_expenses_list_key, settings
        
        async with AsyncSession(async_engine) as session:
            service = ExpenseService(session)
            
            # Pre-populate cache with all expenses
            print("   Pre-populating all expenses cache...")
            all_expenses = await service.get_all_expenses()
            
            if not isinstance(all_expenses, dict):  # Check if it's not an error response
                cache_key = get_expenses_list_key()
                await redis_cache.set(cache_key, all_expenses, settings.cache_expense_ttl)
                print(f"   ✅ Cached {len(all_expenses)} expenses")
            else:
                print(f"   ⚠️  Failed to get expenses: {all_expenses.get('message', 'Unknown error')}")
        
        # Disconnect from Redis
        await redis_cache.disconnect()
        print("✅ Cache warmup completed!")
        
    except Exception as e:
        print(f"⚠️  Cache warmup failed: {e}")
        print("Continuing without cache warmup...")

async def main():
    """Main function to run the faker script"""
    # Parse command line arguments
    num_records = 1000
    if len(sys.argv) > 1:
        try:
            num_records = int(sys.argv[1])
            if num_records <= 0:
                print("❌ Number of records must be positive")
                return 1
            if num_records > 10000:
                print("⚠️  Warning: Large number of records may take a while to process")
        except ValueError:
            print("❌ Invalid number of records. Please provide a positive integer.")
            return 1
    
    print("🎭 COMPREHENSIVE EXPENSE FAKER SCRIPT")
    print("=" * 60)
    print(f"📝 Will generate {num_records} realistic expense records")
    print(f"🎯 Using Faker library with multiple locales")
    print(f"📊 Categories: {len(EXPENSE_CATEGORIES)} with realistic distributions")
    print(f"💾 Batch processing for optimal performance")
    print()
    
    try:
        await insert_expense_records(num_records)
        print("\n🎉 Faker script completed successfully!")
        print("💡 All data generated using realistic patterns and distributions")
    except Exception as e:
        print(f"\n💥 Faker script failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
