"""This module initializes API exception classes.

Classes:
    ApiBadRequestError: Exception raised for bad requests.
    ApiConflictError: Exception raised for conflicts.
    ApiInternalServerError: Exception raised for internal server errors.
    ApiNotFoundError: Exception raised for not found errors.
    BaseApiError: Base class for API exceptions.
    ApiAdminKeyError: Exception raised for invalid admin API key.
    ApiAuthenticationError: Exception raised for authentication errors.
    ApiNotFoundError: Exception raised for not found errors.
    ApiForbiddenError: Exception raised for forbidden access.
"""

from app.core.exceptions.api_exceptions.api_admin_key_exception import ApiAdminKeyError
from app.core.exceptions.api_exceptions.api_authentication_exception import ApiAuthenticationError
from app.core.exceptions.api_exceptions.api_bad_request_exception import ApiBadRequestError
from app.core.exceptions.api_exceptions.api_conflict_exception import ApiConflictError
from app.core.exceptions.api_exceptions.api_forbidden_exception import ApiForbiddenError
from app.core.exceptions.api_exceptions.api_internal_server_error_exception import ApiInternalServerError
from app.core.exceptions.api_exceptions.api_not_found_exception import ApiNotFoundError
from app.core.exceptions.api_exceptions.api_too_many_request_exception import ApiTooManyRequestsError
from app.core.exceptions.api_exceptions.base_api_exception import BaseApiError


__all__ = [
    "ApiBadRequestError",
    "ApiConflictError",
    "ApiNotFoundError",
    "ApiInternalServerError",
    "BaseApiError",
    "ApiAuthenticationError",
    "ApiAdminKeyError",
    "ApiForbiddenError",
    "ApiTooManyRequestsError",
]
