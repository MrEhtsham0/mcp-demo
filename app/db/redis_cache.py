"""
Redis connection and caching utilities
"""
import json
from typing import Any, Optional
import redis.asyncio as redis
from config import settings

class RedisCache:
    """Redis caching service"""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            # Create Redis connection
            self._redis = redis.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                retry_on_timeout=True
            )
            
            # Test connection
            await self._redis.ping()
            print("✅ Connected to Redis successfully")
            
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self._redis:
            await self._redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._redis:
            return None
        
        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self._redis:
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            if ttl:
                await self._redis.setex(key, ttl, serialized_value)
            else:
                await self._redis.set(key, serialized_value)
            return True
        except Exception as e:
            print(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._redis:
            return False
        
        try:
            result = await self._redis.delete(key)
            return result > 0
        except Exception as e:
            print(f"Redis DELETE error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self._redis:
            return 0
        
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                return await self._redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis DELETE PATTERN error for pattern {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self._redis:
            return False
        
        try:
            result = await self._redis.exists(key)
            return result > 0
        except Exception as e:
            print(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """Get TTL for key"""
        if not self._redis:
            return -1
        
        try:
            return await self._redis.ttl(key)
        except Exception as e:
            print(f"Redis TTL error for key {key}: {e}")
            return -1

# Global Redis cache instance
redis_cache = RedisCache()

# Cache key generators
def get_expense_key(expense_id: int) -> str:
    """Generate cache key for expense by ID"""
    return f"expense:{expense_id}"

def get_expenses_list_key() -> str:
    """Generate cache key for all expenses list"""
    return "expenses:all"

def get_expenses_range_key(start_date: str, end_date: str) -> str:
    """Generate cache key for expenses by date range"""
    return f"expenses:range:{start_date}:{end_date}"

def get_expense_summary_key(start_date: str, end_date: str, category: Optional[str] = None) -> str:
    """Generate cache key for expense summary"""
    if category:
        return f"expenses:summary:{start_date}:{end_date}:{category}"
    return f"expenses:summary:{start_date}:{end_date}"

def get_expense_pattern_key() -> str:
    """Generate pattern for all expense-related cache keys"""
    return "expense*"

def get_expenses_pattern_key() -> str:
    """Generate pattern for all expenses-related cache keys"""
    return "expenses*"

# Cache decorator
def cache_result(ttl: int = None, key_func: callable = None):
    """Decorator to cache function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = await redis_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await redis_cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
