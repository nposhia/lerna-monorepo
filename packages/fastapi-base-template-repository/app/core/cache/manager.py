"""Cache manager and decorators.

This module provides the main cache manager and caching decorators.
"""

import json
from typing import Any, Optional, Union, Callable, Awaitable
from datetime import timedelta
from functools import wraps
from loguru import logger
from fastapi.responses import JSONResponse

from app.core.cache.base import CacheBackend


class CacheManager:
    """Cache manager for handling different cache backends.
    
    This class provides a high-level interface for cache operations,
    abstracting away the specific backend implementation.
    """

    def __init__(self, backend: CacheBackend):
        """Initialize cache manager.
        
        Args:
            backend: The cache backend to use
        """
        self.backend = backend
        logger.info(f"Initialized cache manager with {backend.__class__.__name__}")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: The cache key to retrieve
            
        Returns:
            The cached value or None if not found
        """
        return await self.backend.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache.
        
        Args:
            key: The cache key
            value: The value to cache
            expire: Expiration time in seconds or timedelta
            
        Returns:
            True if successful, False otherwise
        """
        return await self.backend.set(key, value, expire)

    async def delete(self, key: str) -> bool:
        """Delete value from cache.
        
        Args:
            key: The cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        return await self.backend.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.
        
        Args:
            key: The cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        return await self.backend.exists(key)

    async def clear(self) -> bool:
        """Clear all cache entries.
        
        Returns:
            True if successful, False otherwise
        """
        return await self.backend.clear()

    async def close(self) -> None:
        """Close cache connection.
        
        This method closes the underlying cache backend connection.
        """
        await self.backend.close()
        logger.info("Closed cache manager connection")

    async def health_check(self) -> bool:
        """Perform a health check on the cache backend.
        
        Returns:
            True if cache is healthy, False otherwise
        """
        if hasattr(self.backend, 'health_check'):
            return await self.backend.health_check()
        
        # Fallback health check
        try:
            test_key = "_health_check"
            test_value = {"status": "healthy"}
            await self.set(test_key, test_value, expire=60)
            result = await self.get(test_key)
            await self.delete(test_key)
            return result == test_value
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False


def cache_response(
    cache_manager: CacheManager,
    key_prefix: str,
    expire: Optional[Union[int, timedelta]] = None
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Decorator for caching function responses.
    
    This decorator automatically caches the return value of async functions.
    It handles FastAPI JSONResponse objects properly and provides comprehensive
    error handling.
    
    Args:
        cache_manager: The cache manager instance
        key_prefix: Prefix for cache keys
        expire: Cache expiration time in seconds or timedelta
        
    Returns:
        Decorated function with caching capability
        
    Example:
        @cache_response(
            cache_manager=get_cache_manager(),
            key_prefix="user_data",
            expire=300
        )
        async def get_user_data(user_id: str) -> JSONResponse:
            # Your function code here
            pass
    """
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Build cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            try:
                # Try to get from cache
                cached_data = await cache_manager.get(cache_key)
                if cached_data is not None:
                    logger.info(f"Cache hit for key: {cache_key}")
                    
                    # Handle cached JSONResponse objects
                    if isinstance(cached_data, dict) and "content" in cached_data:
                        try:
                            content = json.loads(cached_data["content"])
                            return JSONResponse(
                                content=content,
                                status_code=cached_data.get("status_code", 200)
                            )
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to deserialize cached JSONResponse content: {e}")
                            # Fallback to executing the function
                            result = await func(*args, **kwargs)
                            return result
                    return cached_data
                # If not in cache, execute function
                result = await func(*args, **kwargs)
                
                # Handle JSONResponse objects for caching
                if isinstance(result, JSONResponse):
                    cache_value = {
                        "content": result.body.decode(),
                        "status_code": result.status_code
                    }
                else:
                    cache_value = result
                
                # Cache the result
                await cache_manager.set(cache_key, cache_value, expire)
                logger.info(f"Cached result for key: {cache_key}")
                
                return result
                
            except Exception as e:
                logger.error(f"Cache operation failed for key {cache_key}: {e}")
                # Fallback to executing the function without caching
                return await func(*args, **kwargs)
                
        return wrapper
    return decorator

def invalidate_cache(
    cache_manager: CacheManager,
    keys: Union[str, list[str]]
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Decorator for invalidating cache after write operations.
    
    This decorator automatically invalidates cache entries after a function
    is executed, useful for write operations that should clear related cache.
    
    Args:
        cache_manager: The cache manager instance
        keys: Single key string or list of keys to invalidate. 
              Use "*" at the end for pattern matching (e.g., "user_data*")
        
    Returns:
        Decorated function with cache invalidation capability
        
    Example:
        @invalidate_cache(
            cache_manager=get_cache_manager(),
            keys="user_data:123"
        )
        async def update_user(user_id: str, data: dict) -> JSONResponse:
            # Update user data
            # Cache will be automatically invalidated after this function
            pass
            
        @invalidate_cache(
            cache_manager=get_cache_manager(),
            keys=["user_data*", "profile*"]
        )
        async def update_user_profile(user_id: str, data: dict) -> JSONResponse:
            # Update user profile
            # All cache entries matching patterns will be invalidated
            pass
    """
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Execute the function first
            result = await func(*args, **kwargs)
            
            try:
                # Convert single key to list for uniform processing
                keys_to_invalidate = [keys] if isinstance(keys, str) else keys
                total_invalidated = 0
                
                for key in keys_to_invalidate:
                    if key.endswith('*'):
                        # Pattern-based invalidation using Redis KEYS command
                        try:
                            # Get all keys matching the pattern
                            if hasattr(cache_manager.backend, 'redis'):
                                redis_client = cache_manager.backend.redis
                                matching_keys = await redis_client.keys(key)
                                
                                if matching_keys:
                                    # Delete all matching keys
                                    deleted_count = await redis_client.delete(*matching_keys)
                                    total_invalidated += deleted_count
                                    logger.info(f"Invalidated {deleted_count} keys matching pattern: {key}")
                                else:
                                    logger.info(f"No keys found matching pattern: {key}")
                            else:
                                logger.warning(f"Backend doesn't support pattern deletion for: {key}")
                        except Exception as e:
                            logger.error(f"Pattern invalidation failed for {key}: {e}")
                    else:
                        # Specific key invalidation
                        if await cache_manager.delete(key):
                            total_invalidated += 1
                            logger.info(f"Invalidated key: {key}")
                
                if total_invalidated > 0:
                    logger.info(f"Invalidated {total_invalidated} cache entries after {func.__name__}")
                
            except Exception as e:
                logger.error(f"Cache invalidation failed after {func.__name__}: {e}")
            
            return result
        return wrapper
    return decorator