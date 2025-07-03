"""Cache module for the application.

This module provides a unified caching interface with support for multiple backends.
"""

from app.core.cache.manager import CacheManager, cache_response, invalidate_cache
from app.core.cache.backends import RedisBackend
from app.core.cache.config import get_cache_manager, close_cache_manager, health_check_cache

__all__ = [
    "CacheManager",
    "cache_response", 
    "invalidate_cache",
    "RedisBackend",
    "get_cache_manager",
    "close_cache_manager",
    "health_check_cache"
] 