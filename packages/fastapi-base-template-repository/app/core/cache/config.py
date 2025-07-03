"""Cache configuration module.

This module handles cache configuration and provides factory functions
for creating cache managers.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from loguru import logger

from app.core.cache.manager import CacheManager
from app.core.cache.backends.redis import RedisBackend


class CacheSettings(BaseSettings):
    """Cache configuration settings.

    This class defines all cache-related configuration options
    that can be set via environment variables.
    """

    # Cache backend configuration
    CACHE_BACKEND: str = Field("redis", description="Cache backend to use")

    # Redis configuration
    REDIS_HOST: str = Field(..., description="Redis server hostname")
    REDIS_PORT: int = Field(..., description="Redis server port")
    REDIS_DB: int = Field(0, description="Redis database number")
    REDIS_PASSWORD: str = Field(..., description="Redis authentication password")
    REDIS_MAX_CONNECTIONS: int = Field(10, description="Maximum Redis connections")
    REDIS_TIMEOUT: int = Field(5, description="Redis connection timeout")

    # Cache behavior settings
    CACHE_DEFAULT_TTL: int = Field(300, description="Default cache TTL in seconds")
    CACHE_KEY_PREFIX: str = Field("app", description="Default cache key prefix")

    class Config:
        env_prefix = ""
        case_sensitive = True


class CacheFactory:
    """Factory for creating and managing cache manager instances.

    This class provides a centralized way to create cache managers
    without using global variables or singletons.
    """

    def __init__(self, settings: Optional[CacheSettings] = None):
        """Initialize the cache factory.

        Args:
            settings: Cache settings instance. If None, creates a new instance.
        """
        self.settings = settings or CacheSettings()
        self._cache_manager: Optional[CacheManager] = None

    def create_cache_manager(self) -> CacheManager:
        """Create a new cache manager instance.

        Returns:
            CacheManager: A new cache manager instance

        Raises:
            ValueError: If an unsupported cache backend is configured
            RuntimeError: If cache manager initialization fails
        """
        try:
            if self.settings.CACHE_BACKEND.lower() == "redis":
                backend = RedisBackend(
                    host=self.settings.REDIS_HOST,
                    port=self.settings.REDIS_PORT,
                    db=self.settings.REDIS_DB,
                    password=self.settings.REDIS_PASSWORD,
                    max_connections=self.settings.REDIS_MAX_CONNECTIONS,
                    timeout=self.settings.REDIS_TIMEOUT,
                    default_ttl=self.settings.CACHE_DEFAULT_TTL,
                )
                cache_manager = CacheManager(backend)
                logger.info("Created Redis cache manager")
                return cache_manager
            else:
                raise ValueError(
                    f"Unsupported cache backend: {self.settings.CACHE_BACKEND}"
                )

        except Exception as e:
            logger.error(f"Failed to create cache manager: {e}")
            raise RuntimeError(f"Cache manager creation failed: {e}") from e

    def get_cache_manager(self) -> CacheManager:
        """Get or create a cache manager instance.

        This method implements a lazy singleton pattern within the factory,
        creating the cache manager only when first requested.

        Returns:
            CacheManager: The cache manager instance

        Raises:
            ValueError: If an unsupported cache backend is configured
            RuntimeError: If cache manager initialization fails
        """
        if self._cache_manager is None:
            self._cache_manager = self.create_cache_manager()

        return self._cache_manager

    async def close_cache_manager(self) -> None:
        """Close the cache manager connection.

        This method closes the cache manager and cleans up resources.
        It should be called during application shutdown.
        """
        if self._cache_manager is not None:
            try:
                await self._cache_manager.close()
                self._cache_manager = None
                logger.info("Closed cache manager connection")
            except Exception as e:
                logger.error(f"Error closing cache manager: {e}")

    async def health_check_cache(self) -> bool:
        """Perform a health check on the cache system.

        Returns:
            bool: True if cache is healthy, False otherwise
        """
        try:
            cache_manager = self.get_cache_manager()
            return await cache_manager.health_check()
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False

    def get_cache_key_prefix(self) -> str:
        """Get the configured cache key prefix.

        Returns:
            str: The cache key prefix
        """
        return self.settings.CACHE_KEY_PREFIX

    def get_default_ttl(self) -> int:
        """Get the default cache TTL.

        Returns:
            int: Default TTL in seconds
        """
        return self.settings.CACHE_DEFAULT_TTL


# Default factory instance for backward compatibility
# This can be removed once all code is migrated to use dependency injection
_default_factory = CacheFactory()


def get_cache_manager() -> CacheManager:
    """Get the default cache manager instance.

    This function is provided for backward compatibility.
    New code should use dependency injection with CacheFactory.

    Returns:
        CacheManager: The default cache manager instance
    """
    return _default_factory.get_cache_manager()


async def close_cache_manager() -> None:
    """Close the default cache manager connection.

    This function is provided for backward compatibility.
    New code should use dependency injection with CacheFactory.
    """
    await _default_factory.close_cache_manager()


async def health_check_cache() -> bool:
    """Perform a health check on the default cache system.

    This function is provided for backward compatibility.
    New code should use dependency injection with CacheFactory.

    Returns:
        bool: True if cache is healthy, False otherwise
    """
    return await _default_factory.health_check_cache()


def get_default_ttl() -> int:
    """Get the default cache TTL.

    This function is provided for backward compatibility.
    New code should use dependency injection with CacheFactory.

    Returns:
        int: Default TTL in seconds
    """
    return _default_factory.get_default_ttl()
