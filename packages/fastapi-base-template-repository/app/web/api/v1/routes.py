"""This module contains the API router for the v1 version of the API.

Routes:
    healthcheck: Checks the health of the application.
    example: Example endpoints demonstrating rate limiting.
"""

from fastapi import APIRouter

from app.web.api.v1.healthcheck import healthcheck_router

v1_router = APIRouter()

v1_router.include_router(healthcheck_router, prefix="/health")