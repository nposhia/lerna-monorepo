"""Main application entry point for the FastAPI service.

This module handles the initialization of either a development server (uvicorn)
or a production server (gunicorn) based on configuration settings.
"""

import uvicorn

from app.web.gunicorn_runner import GunicornApplication
from app.web.settings import settings


def main() -> None:
    """Entrypoint of the application."""
    if settings.reload:
        uvicorn.run(
            "app.web.application:get_app",
            workers=settings.workers_count,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=str(settings.log_level.value).lower(),  # pylint: disable=no-member
            factory=True,
        )
    else:
        # We choose gunicorn only if reload
        # option is not used, because reload
        # feature doesn't work with gunicorn workers.
        GunicornApplication(
            "app.web.application:get_app",
            host=settings.host,
            port=settings.port,
            workers=settings.workers_count,
            factory=True,
            loglevel=str(settings.log_level.value).lower(),  # pylint: disable=no-member
        ).run()


if __name__ == "__main__":
    main()
