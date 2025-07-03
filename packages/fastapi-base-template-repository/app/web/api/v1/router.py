from fastapi import APIRouter

from app.web.api.v1.healthcheck.routes import router as healthcheck_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(healthcheck_router)