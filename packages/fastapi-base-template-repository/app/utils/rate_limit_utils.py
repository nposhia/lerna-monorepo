"""Rate limiting utilities for FastAPI endpoints.

This module provides utilities and decorators for applying rate limits
to specific API endpoints using a simple, reliable implementation.
"""

from functools import wraps
from typing import Callable, Optional, Union
import time
from collections import defaultdict
import hashlib

from fastapi import Depends, Request, HTTPException
from slowapi import Limiter


def get_limiter(request: Request) -> Limiter:
    """Dependency to get the limiter instance from the application state.
    
    :param request: FastAPI request object.
    :return: Limiter instance.
    """
    return request.app.state.limiter


class SimpleRateLimiter:
    """Simple rate limiter that tracks requests per key."""
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    def _parse_limit_string(self, limit_string: str):
        """Parse rate limit string (e.g., '100/minute')."""
        parts = limit_string.split('/')
        max_requests = int(parts[0])
        time_window = parts[1]
        
        # Convert time window to seconds
        if time_window.startswith('second'):
            window_seconds = 1
        elif time_window.startswith('minute'):
            window_seconds = 60
        elif time_window.startswith('hour'):
            window_seconds = 3600
        elif time_window.startswith('day'):
            window_seconds = 86400
        else:
            window_seconds = 60  # Default to minute
        
        return max_requests, window_seconds
    
    def is_allowed(self, key: str, limit_string: str) -> bool:
        """Check if request is allowed based on rate limit."""
        max_requests, window_seconds = self._parse_limit_string(limit_string)
        current_time = time.time()
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if current_time - req_time < window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= max_requests:
            return False
        
        # Add current request
        self.requests[key].append(current_time)
        return True


# Global rate limiter instance
_rate_limiter = SimpleRateLimiter()


def create_rate_limit_decorator(limit_string: str, key_func: Optional[Callable] = None):
    """Create a rate limiting decorator.
    
    :param limit_string: Rate limit string (e.g., "10/minute", "100/hour").
    :param key_func: Function to generate the key for rate limiting.
    :return: Decorator function.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **func_kwargs):
            # Generate rate limiting key
            if key_func:
                key = key_func()
            else:
                # Default key based on client IP and endpoint
                client_ip = request.client.host if request.client else "unknown"
                endpoint = f"{request.method}:{request.url.path}"
                key = f"{client_ip}:{endpoint}"
            
            # Check rate limit
            if not _rate_limiter.is_allowed(key, limit_string):
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {limit_string}",
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": limit_string.split('/')[0],
                        "X-RateLimit-Remaining": "0"
                    }
                )
            
            # Call the original function
            return await func(request, *args, **func_kwargs)
        
        return wrapper
    return decorator


def rate_limit(
    limit_string: str,
    key_func: Optional[Callable] = None,

):
    """Decorator to apply rate limiting to a specific endpoint.
    
    This is a simplified wrapper that uses our custom rate limiter.
    
    :param limit_string: Rate limit string (e.g., "10/minute", "100/hour").
    :param key_func: Function to generate the key for rate limiting.
    :return: Decorated function.
    """
    return create_rate_limit_decorator(limit_string, key_func)


# Predefined rate limit decorators for common use cases
def rate_limit_strict(func):
    """Apply strict rate limiting (5 requests per minute)."""
    return create_rate_limit_decorator("5/minute")(func)


def rate_limit_moderate(func):
    """Apply moderate rate limiting (20 requests per minute)."""
    return create_rate_limit_decorator("20/minute")(func)


def rate_limit_generous(func):
    """Apply generous rate limiting (100 requests per minute)."""
    return create_rate_limit_decorator("100/minute")(func)


def rate_limit_hourly(func):
    """Apply hourly rate limiting (1000 requests per hour)."""
    return create_rate_limit_decorator("1000/hour")(func)


def rate_limit_daily(func):
    """Apply daily rate limiting (10000 requests per day)."""
    return create_rate_limit_decorator("10000/day")(func) 