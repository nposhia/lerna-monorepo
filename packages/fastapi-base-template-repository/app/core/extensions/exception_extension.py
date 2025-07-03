"""This module contains the exception extension.

Functions:
    enable_exception_extension: Enables the exception extension.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.exceptions.api_exceptions import BaseApiError
from app.core.exceptions.exception_handlers import api_exception_handler, request_validation_exception_handler, unhandled_exception_handler


def enable_exception_extension(app: FastAPI) -> None:
    """Enables the exception extension.

    Args:
        app (FastAPI): The FastAPI app.
    """
    app.add_exception_handler(BaseApiError, api_exception_handler)  # type: ignore

    app.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler,  # type: ignore
    )

    app.add_exception_handler(Exception, unhandled_exception_handler)
