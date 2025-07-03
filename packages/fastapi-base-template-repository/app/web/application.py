"""FastAPI application factory module.

This module contains the factory function for creating and configuring
the FastAPI application instance with all necessary extensions,
middleware, and routes.
"""

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from loguru import logger

from libs.sentry import SentrySetup

from app.core.db.database import get_db_session
from app.core.extensions.cors_extension import enable_cors_extension
from app.core.extensions.exception_extension import enable_exception_extension
from app.core.extensions.logging_extension import enable_logging_extension
from app.core.extensions.rate_limit_extension import enable_rate_limit_extension
from app.core.extensions.route_extension import initialize_routes
from app.core.middleware.gzip_middleware import GZipMiddleware
from app.core.middleware.logging_middleware import LoggingMiddleware
from app.core.middleware.response_transformer_middleware import ResponseTransformerMiddleware
from app.web.lifespan import lifespan_setup
from app.core.telemetry.setup import setup_telemetry_core, setup_fastapi_instrumentation, create_custom_metrics


def get_app() -> FastAPI:
    """Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        version="1.0.0",
        title="Jeavio FastAPI Backend",
        summary="FastAPI Backend Application",
        description="Jeavio backend application created with FastAPI and PostgreSQL",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/api/v1/openapi.json",
        default_response_class=UJSONResponse,
        contact={
            "name": "Paras Bhardava",
            "email": "paras.bhardava@jeavio.com",
        },
        debug=False,
        lifespan=lifespan_setup,
    )
    # Setup Sentry and Loguru
    app = SentrySetup.setup_all(app)
    # Set up OpenTelemetry AFTER Sentry
    telemetry_config = setup_telemetry_core()
    if telemetry_config:
        # Set up FastAPI instrumentation early
        setup_fastapi_instrumentation(app, telemetry_config)
        
        # Create custom metrics
        create_custom_metrics(app, telemetry_config)
        
        # Store telemetry config in app state
        app.state.telemetry = telemetry_config

    # Main router for the API.
    initialize_routes(app)

    # Add CORS extension
    enable_cors_extension(app)

    # Add logging extension
    enable_logging_extension()

    # Add exception extension
    enable_exception_extension(app)

    # Add response transformer middleware (transforms snake_case to camelCase)
    app.add_middleware(ResponseTransformerMiddleware)

    # Add rate limiting extension
    enable_rate_limit_extension(app)

    # Add logging middleware
    app.add_middleware(LoggingMiddleware)

    # Add GZip middleware with minimum size threshold
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    app.dependency_overrides[get_db_session] = get_db_session
    return app
