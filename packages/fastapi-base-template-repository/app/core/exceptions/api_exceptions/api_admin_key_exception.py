"""This module defines the ApiAdminKeyError class.

Classes:
    ApiAdminKeyError: Exception raised when an invalid admin API key is provided.
"""

from typing import Any

from fastapi import status

from app.core.exceptions.api_exceptions.base_api_exception import BaseApiError


class ApiAdminKeyError(BaseApiError):
    """Exception raised when an invalid admin API key is provided.

    Attributes:
        error (Any): The error type/code of the exception.
        message (str): The message of the exception.
    """

    def __init__(self, error: Any, message: str = "Invalid admin API key") -> None:
        """Initialize the ApiAdminKeyError."""
        super().__init__(error=error, message=message, status_code=status.HTTP_403_FORBIDDEN)
