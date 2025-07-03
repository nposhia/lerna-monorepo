# library/setup.py

import sys
import logging

from fastapi import FastAPI
from loguru import logger
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.web.settings import settings

class SentrySetup:
    @staticmethod
    def configure_sentry(app: FastAPI) -> FastAPI:
        """
        Configure Sentry for error tracking and performance monitoring.
        """
        if not settings.sentry_dsn:
            logger.warning("Sentry DSN not configured - Sentry disabled")
            return app
            
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment,
            release=settings.sentry_release,
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,        
                    event_level=logging.ERROR  
                ),
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            profiles_sample_rate=settings.sentry_profile_sample_rate,
            debug=False,
            send_default_pii=settings.sentry_send_default_pii,
            sample_rate=settings.sentry_sample_rate,
            attach_stacktrace=settings.sentry_attach_stacktrace,
        )

        logger.info("Sentry initialized successfully")
        return app

    @classmethod
    def setup_all(cls, app: FastAPI) -> FastAPI:
        """Setup Sentry integration."""
        cls.configure_sentry(app)
        return app

