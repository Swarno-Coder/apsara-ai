import redis
import json
import pickle
from typing import Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        try:
            self.redis_client = redis.Redis.from_url(redis_url, decode_responses=False)
            self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {e}")
            self.redis_client = None
            self._memory_cache = {}
            self._cache_expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                data = self.redis_client.get(key)
                if data and isinstance(data, bytes):
                    return pickle.loads(data)
            else:
                # Check expiry for memory cache
                if key in self._cache_expiry:
                    if datetime.now() > self._cache_expiry[key]:
                        self._memory_cache.pop(key, None)
                        self._cache_expiry.pop(key, None)
                        return None
                return self._memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL in seconds"""
        try:
            if self.redis_client:
                serialized_value = pickle.dumps(value)
                result = self.redis_client.setex(key, ttl, serialized_value)
                return bool(result)
            else:
                # Memory cache with expiry
                self._memory_cache[key] = value
                self._cache_expiry[key] = datetime.now() + timedelta(seconds=ttl)
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                self._memory_cache.pop(key, None)
                self._cache_expiry.pop(key, None)
                return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.flushdb())
            else:
                self._memory_cache.clear()
                self._cache_expiry.clear()
                return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

# Global cache instance
cache = CacheService()
