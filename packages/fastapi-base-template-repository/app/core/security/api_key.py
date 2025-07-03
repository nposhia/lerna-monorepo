"""
This module provides functionality for verifying admin API keys.

Classes:
    ApiAdminKeyError: Exception raised when an invalid admin API key is provided.
"""

from fastapi import Security
from fastapi.security import APIKeyHeader

from app.core.exceptions.api_exceptions import ApiAdminKeyError
from app.web.settings import settings


# API key header with proper OpenAPI documentation
api_key_header = APIKeyHeader(
    name="X-Admin-API-Key",
    auto_error=False,
    description="Admin API key for protected endpoints",
    scheme_name="Admin API Key",
)


async def verify_admin_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the admin API key from the request header.

    Args:
        api_key: The API key from the request header

    Returns:
        The verified API key

    Raises:
        ApiAdminKeyError: If the API key is missing or invalid
    """
    if not api_key:
        raise ApiAdminKeyError(
            error="Missing admin API key", message="Admin API key is required in X-Admin-API-Key header"
        )

    if api_key != settings.admin_api_key:
        raise ApiAdminKeyError(error="Invalid admin API key", message="Admin API key is invalid")
    return api_key
