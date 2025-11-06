"""Caching layer with Redis support."""

import json
import logging
from typing import Any, Optional, Callable
from datetime import timedelta
from functools import wraps

logger = logging.getLogger(__name__)


class CacheBackend:
    """Base cache backend interface."""

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        raise NotImplementedError

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ):
        """Set value in cache."""
        raise NotImplementedError

    async def delete(self, key: str):
        """Delete value from cache."""
        raise NotImplementedError

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        raise NotImplementedError

    async def clear(self):
        """Clear all cache."""
        raise NotImplementedError


class MemoryCache(CacheBackend):
    """In-memory cache implementation."""

    def __init__(self):
        """Initialize memory cache."""
        self.cache: dict = {}
        self.expiry: dict = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        import time

        if key in self.cache:
            # Check expiry
            if key in self.expiry:
                if time.time() > self.expiry[key]:
                    # Expired
                    del self.cache[key]
                    del self.expiry[key]
                    return None

            return self.cache[key]
        return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ):
        """Set value in cache."""
        import time

        self.cache[key] = value
        if ttl:
            self.expiry[key] = time.time() + ttl

    async def delete(self, key: str):
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
        if key in self.expiry:
            del self.expiry[key]

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        value = await self.get(key)
        return value is not None

    async def clear(self):
        """Clear all cache."""
        self.cache.clear()
        self.expiry.clear()


class RedisCache(CacheBackend):
    """Redis cache implementation."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize Redis cache.

        Args:
            redis_url: Redis connection URL
        """
        try:
            import redis.asyncio as redis
            
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.available = True
            logger.info(f"Redis cache initialized: {redis_url}")
        except ImportError:
            logger.warning("redis package not installed, using memory cache")
            self.redis = None
            self.available = False
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None
            self.available = False

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.available:
            return None

        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ):
        """Set value in cache."""
        if not self.available:
            return

        try:
            serialized = json.dumps(value)
            if ttl:
                await self.redis.setex(key, ttl, serialized)
            else:
                await self.redis.set(key, serialized)
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    async def delete(self, key: str):
        """Delete value from cache."""
        if not self.available:
            return

        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.available:
            return False

        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    async def clear(self):
        """Clear all cache."""
        if not self.available:
            return

        try:
            await self.redis.flushdb()
        except Exception as e:
            logger.error(f"Cache clear error: {e}")


class CacheManager:
    """Cache manager with fallback support."""

    def __init__(self, backend: Optional[CacheBackend] = None):
        """
        Initialize cache manager.

        Args:
            backend: Cache backend to use
        """
        if backend is None:
            # Try Redis, fallback to memory
            import os
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            
            try:
                redis_backend = RedisCache(redis_url)
                if redis_backend.available:
                    backend = redis_backend
                else:
                    backend = MemoryCache()
            except Exception:
                backend = MemoryCache()

        self.backend = backend
        logger.info(f"Cache manager initialized with {type(backend).__name__}")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return await self.backend.get(key)

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ):
        """Set value in cache."""
        await self.backend.set(key, value, ttl)

    async def delete(self, key: str):
        """Delete value from cache."""
        await self.backend.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self.backend.exists(key)

    async def clear(self):
        """Clear all cache."""
        await self.backend.clear()

    async def get_or_set(
        self,
        key: str,
        factory: Callable,
        ttl: Optional[int] = None,
    ) -> Any:
        """
        Get value from cache or compute and cache it.

        Args:
            key: Cache key
            factory: Function to compute value if not cached
            ttl: Time to live in seconds

        Returns:
            Cached or computed value
        """
        # Try to get from cache
        value = await self.get(key)
        if value is not None:
            return value

        # Compute value
        import asyncio
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()

        # Cache it
        await self.set(key, value, ttl)
        return value


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys

    Usage:
        @cached(ttl=60, key_prefix="user")
        async def get_user(user_id: str):
            return fetch_user(user_id)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            import hashlib
            
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            key_str = ":".join(key_parts)
            cache_key = hashlib.md5(key_str.encode()).hexdigest()

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value

            # Compute value
            import asyncio
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Cache it
            await cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache set: {cache_key}")
            
            return result

        return wrapper
    return decorator


# Global cache manager
cache_manager = CacheManager()

