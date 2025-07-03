"""Base cache backend interface.

This module defines the abstract base class for cache backends.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from datetime import timedelta


class CacheBackend(ABC):
    """Abstract base class for cache backends.
    
    This class defines the interface that all cache backends must implement.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: The cache key to retrieve
            
        Returns:
            The cached value or None if not found
        """
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache with optional expiration.
        
        Args:
            key: The cache key
            value: The value to cache
            expire: Expiration time in seconds or timedelta
            
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache.
        
        Args:
            key: The cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.
        
        Args:
            key: The cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries.
        
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close cache connection.
        
        This method should clean up any resources used by the cache backend.
        """
        pass 