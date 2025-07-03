"""This module defines the ApiAuthenticationError class.

Classes:
    ApiAuthenticationError: Exception raised for authentication failures.
"""

from typing import Any

from fastapi import status

from app.core.exceptions.api_exceptions.base_api_exception import BaseApiError


class ApiAuthenticationError(BaseApiError):
    """Exception raised for authentication failures.

    Attributes:
        error (Any): The error type/code of the exception.
        message (str): The message of the exception.
    """

    def __init__(self, error: Any, message: str) -> None:
        super().__init__(error, message, status.HTTP_401_UNAUTHORIZED)
