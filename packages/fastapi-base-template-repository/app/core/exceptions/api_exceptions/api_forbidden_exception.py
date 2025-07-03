"""This module contains the ApiForbiddenError class which is a subclass of BaseApiError.

Classes:
    ApiForbiddenError: Exception raised for forbidden access.
"""

from typing import Any

from fastapi import status

from app.core.exceptions.api_exceptions.base_api_exception import BaseApiError


class ApiForbiddenError(BaseApiError):
    """Exception raised for forbidden access.

    Attributes:
        error (Any): The error type/code of the exception.
        message (str): The message of the exception.
    """
    def __init__(self, error: Any, message: str) -> None:
        super().__init__(error, message, status.HTTP_403_FORBIDDEN)
