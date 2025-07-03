"""Rate limiting extension for FastAPI application.

This module provides rate limiting functionality using slowapi library.
It supports both global rate limiting and per-API rate limiting.
"""

from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from collections import defaultdict
from loguru import logger

from app.web.settings import settings


class GlobalRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply global rate limiting to all endpoints."""
    
    def __init__(self, app, limit_string: str):
        super().__init__(app)
        self.limit_string = limit_string
        self.requests = defaultdict(list)
        self._parse_limit_string()
    
    def _parse_limit_string(self):
        """Parse the rate limit string (e.g., '100/minute')."""
        parts = self.limit_string.split('/')
        self.max_requests = int(parts[0])
        self.time_window = parts[1]
        
        # Convert time window to seconds
        if self.time_window.startswith('second'):
            self.window_seconds = 1
        elif self.time_window.startswith('minute'):
            self.window_seconds = 60
        elif self.time_window.startswith('hour'):
            self.window_seconds = 3600
        elif self.time_window.startswith('day'):
            self.window_seconds = 86400
        else:
            self.window_seconds = 60  # Default to minute
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = get_remote_address(request)
        
        # Check if endpoint has its own rate limiting
        if hasattr(request, 'endpoint') and hasattr(request.endpoint, '_rate_limit'):
            return await call_next(request)
        
        # Apply global rate limiting
        current_time = time.time()
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.max_requests:
            return Response(
                content=f"Rate limit exceeded: {self.limit_string}",
                status_code=429,
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + self.window_seconds))
                }
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Continue with the request
        return await call_next(request)


def enable_rate_limit_extension(app: FastAPI) -> None:
    """Enable rate limiting extension for the FastAPI application.

    This function configures slowapi with global and per-API rate limiting.
    It sets up the limiter, middleware, and exception handlers.

    :param app: FastAPI application instance.
    """
    # Create limiter instance
    limiter = Limiter(key_func=get_remote_address)
    
    # Add rate limit exceeded handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Apply global rate limiting only if enabled
    if settings.enable_global_rate_limit:
        # Add global rate limiting middleware
        app.add_middleware(GlobalRateLimitMiddleware, limit_string=settings.global_rate_limit)
        logger.info(f"Global rate limiting enabled: {settings.global_rate_limit}")
    else:
        logger.info("Global rate limiting disabled - only per-endpoint limits will apply")
    


def get_limiter():
    """Get the limiter instance from the application state.
    
    This function should be used in dependency injection to access the limiter
    for applying rate limits to specific endpoints.
    
    :return: Limiter instance.
    """
    from fastapi import Request
    
    def _get_limiter(request: Request) -> Limiter:
        return request.app.state.limiter
    
    return _get_limiter 