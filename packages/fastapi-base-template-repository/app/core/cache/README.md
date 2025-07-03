# Cache Module

This module provides a unified caching interface with support for multiple backends, currently supporting Redis with a robust, production-ready implementation.

## Structure

```
app/core/cache/
├── __init__.py          # Module exports and public API
├── base.py              # Abstract base classes for cache backends
├── config.py            # Configuration management and factory functions
├── manager.py           # Cache manager and decorators
├── backends/            # Backend implementations
│   ├── __init__.py
│   └── redis.py         # Redis backend implementation
└── README.md           # This file
```

## Features

- **Unified Interface**: Single interface for different cache backends with abstract base classes
- **Connection Pooling**: Efficient Redis connection management with configurable pool sizes
- **JSON Serialization**: Automatic serialization/deserialization of complex data types
- **Comprehensive Error Handling**: Graceful error handling with detailed logging
- **Health Checks**: Built-in health check functionality with fallback mechanisms
- **Decorators**: Easy-to-use caching decorators with FastAPI JSONResponse support
- **Cache Invalidation**: Pattern-based cache invalidation for write operations
- **Factory Pattern**: Clean dependency injection and configuration management
- **Type Safety**: Full type hints and Pydantic configuration validation

## Quick Start

### Basic Usage

```python
from app.core.cache import get_cache_manager

# Get cache manager
cache_manager = get_cache_manager()

# Set a value with expiration
await cache_manager.set("user:123", {"name": "John", "email": "john@example.com"}, expire=300)

# Get a value
user_data = await cache_manager.get("user:123")

# Check if key exists
exists = await cache_manager.exists("user:123")

# Delete a key
await cache_manager.delete("user:123")

# Clear all cache entries
await cache_manager.clear()

# Health check
is_healthy = await cache_manager.health_check()
```

### Using the Cache Decorator

```python
from app.core.cache import cache_response, get_cache_manager
from fastapi.responses import JSONResponse

@cache_response(
    cache_manager=get_cache_manager(),
    key_prefix="user_data",
    expire=300  # 5 minutes
)
async def get_user_data(user_id: str) -> JSONResponse:
    # Expensive database operation here
    user_data = await database.get_user(user_id)
    return JSONResponse(content=user_data)
```

### Using Cache Invalidation

```python
from app.core.cache import invalidate_cache, get_cache_manager

@invalidate_cache(
    cache_manager=get_cache_manager(),
    keys=["user_data*", "profile*"]  # Pattern-based invalidation
)
async def update_user_profile(user_id: str, data: dict) -> JSONResponse:
    # Update user profile
    # All cache entries matching patterns will be automatically invalidated
    updated_profile = await database.update_user(user_id, data)
    return JSONResponse(content=updated_profile)
```


## Configuration

Set these environment variables:

```bash
# Cache Backend Configuration
CACHE_BACKEND=redis

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password
REDIS_MAX_CONNECTIONS=10
REDIS_TIMEOUT=5

# Cache Behavior
CACHE_DEFAULT_TTL=300
CACHE_KEY_PREFIX=app
```

## API Reference

### CacheManager

The main cache manager class that provides a high-level interface for cache operations.

#### Methods

- `get(key: str) -> Optional[Any]`: Retrieve a value from cache
- `set(key: str, value: Any, expire: Optional[Union[int, timedelta]] = None) -> bool`: Set a value in cache with optional expiration
- `delete(key: str) -> bool`: Delete a key from cache
- `exists(key: str) -> bool`: Check if key exists in cache
- `clear() -> bool`: Clear all cache entries
- `close() -> None`: Close cache connection and cleanup resources
- `health_check() -> bool`: Perform health check on cache backend

### cache_response Decorator

A decorator that automatically caches function responses with comprehensive error handling.

#### Parameters

- `cache_manager`: The cache manager instance
- `key_prefix`: Prefix for cache keys (used in key generation)
- `expire`: Cache expiration time in seconds or timedelta (optional)

#### Features

- Automatic key generation from function name and arguments
- Full support for FastAPI JSONResponse objects
- Comprehensive error handling with fallback to function execution
- Detailed logging for cache hits and misses
- Graceful degradation when cache operations fail

### invalidate_cache Decorator

A decorator for invalidating cache entries after write operations.

#### Parameters

- `cache_manager`: The cache manager instance
- `keys`: Single key string or list of keys to invalidate. Supports pattern matching with "*" wildcard

#### Features

- Pattern-based invalidation using Redis KEYS command
- Automatic invalidation after function execution
- Support for multiple key patterns
- Detailed logging of invalidation operations

### CacheBackend

Abstract base class for cache backends. Implement this to add new backends.

#### Required Methods

- `get(key: str) -> Optional[Any]`
- `set(key: str, value: Any, expire: Optional[Union[int, timedelta]] = None) -> bool`
- `delete(key: str) -> bool`
- `exists(key: str) -> bool`
- `clear() -> bool`
- `close() -> None`

### CacheFactory

Factory class for creating and managing cache manager instances with dependency injection support.

#### Methods

- `create_cache_manager() -> CacheManager`: Create a new cache manager instance
- `get_cache_manager() -> CacheManager`: Get or create a cache manager (lazy singleton)
- `close_cache_manager() -> None`: Close cache manager connection
- `health_check_cache() -> bool`: Perform health check
- `get_cache_key_prefix() -> str`: Get configured cache key prefix
- `get_default_ttl() -> int`: Get default cache TTL

