"""Redis cache backend implementation.

This module provides a Redis-based cache backend using redis-py.
"""

import json
from typing import Any, Optional, Union
from datetime import timedelta
from redis.asyncio import Redis, ConnectionPool
from loguru import logger

from app.core.cache.base import CacheBackend


class RedisBackend(CacheBackend):
    """Redis implementation of cache backend.
    
    This class provides a Redis-based cache backend with connection pooling,
    JSON serialization, and comprehensive error handling.
    """

    def __init__(
        self,
        host: str,
        port: int,
        db: int,
        password: Optional[str],
        max_connections: int,
        timeout: int,
        decode_responses: bool = True,
        default_ttl: Optional[int] = None,
    ):
        """Initialize Redis backend.
        
        Args:
            host: Redis server hostname
            port: Redis server port
            db: Redis database number
            password: Redis authentication password
            max_connections: Maximum number of connections in the pool
            timeout: Socket timeout in seconds
            decode_responses: Whether to decode responses as strings
            default_ttl: Default TTL in seconds when no expiration is provided
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self.timeout = timeout
        self.decode_responses = decode_responses
        self.default_ttl = default_ttl
        
        # Create connection pool
        self.pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            socket_timeout=timeout,
            decode_responses=decode_responses
        )
        
        self._redis: Optional[Redis] = None
        logger.info(f"Initialized Redis backend for {host}:{port}")

    @property
    def redis(self) -> Redis:
        """Get Redis client instance.
        
        Returns:
            Redis client instance
        """
        if self._redis is None:
            self._redis = Redis(connection_pool=self.pool)
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache.
        
        Args:
            key: The cache key to retrieve
            
        Returns:
            The cached value or None if not found
        """
        try:
            data = await self.redis.get(key)
            if data is None:
                return None
                
            # Handle JSON serialized data
            if isinstance(data, str):
                return json.loads(data)
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to deserialize cached data for key {key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting cached data for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in Redis cache with optional expiration.
        
        Args:
            key: The cache key
            value: The value to cache
            expire: Expiration time in seconds or timedelta
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize value to JSON
            serialized_value = json.dumps(value)
            
            # Calculate expiration time
            if isinstance(expire, timedelta):
                expire_seconds = int(expire.total_seconds())
            elif expire is not None:
                expire_seconds = expire
            else:
                # Use default TTL if no expiration provided
                expire_seconds = self.default_ttl
            
            # Set value in Redis
            await self.redis.set(key, serialized_value, ex=expire_seconds)
            return True
            
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize value for key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error setting cached data for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache.
        
        Args:
            key: The cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.redis.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting cached data for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache.
        
        Args:
            key: The cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error(f"Error checking existence of key {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all Redis cache entries.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.redis.flushdb()
            logger.info("Cleared all Redis cache entries")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    async def close(self) -> None:
        """Close Redis connection.
        
        This method closes the Redis client and connection pool.
        """
        if self._redis is not None:
            await self._redis.close()
            self._redis = None
            logger.info("Closed Redis connection")
        
        # Close the connection pool
        if hasattr(self, 'pool') and self.pool is not None:
            await self.pool.disconnect()
            logger.info("Closed Redis connection pool")

    async def health_check(self) -> bool:
        """Perform a health check on the Redis connection.
        
        Returns:
            True if Redis is healthy, False otherwise
        """
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False 