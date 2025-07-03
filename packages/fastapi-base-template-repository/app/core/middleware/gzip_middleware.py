"""GZip Middleware Module.

This module provides GZip compression middleware for FastAPI applications.
It uses FastAPI's built-in GZipMiddleware to compress responses.
"""

from fastapi.middleware.gzip import GZipMiddleware


# Export the GZip middleware for use in the application
__all__ = ["GZipMiddleware"]
