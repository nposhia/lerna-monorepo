"""This module contains the views for the healthcheck endpoint.

Functions:
    healthcheck: Returns a simple healthcheck response.
    migration_status: Returns the status of the data migration system.
"""

from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from app.core.schema.api_schema import create_json_api_response
from app.core.cache.config import get_cache_manager

router = APIRouter(tags=["Healthcheck"])


@router.get("")
async def healthcheck(request: Request) -> JSONResponse:
    """Checks the health of the application.

    Args:
        request: FastAPI request object for tracing

    Returns:
        JSONResponse: A JSON response indicating the health status.
    """
    return create_json_api_response(
        message="Healthcheck successful!",
        status_code=status.HTTP_200_OK,
    )

@router.get("/redis")
async def redis_healthcheck() -> JSONResponse:
    """Checks the health of the Redis connection.

    Returns:
        JSONResponse: A JSON response indicating the health status.
    """
    cache_manager = get_cache_manager()
    is_healthy = await cache_manager.health_check()
    if not is_healthy:
        return create_json_api_response(
            message="Redis healthcheck failed!",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return create_json_api_response(
        message="Redis healthcheck successful!",
        status_code=status.HTTP_200_OK,
    )
