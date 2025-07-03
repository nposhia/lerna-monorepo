"""Logging extension.

This module configures and enables application-wide logging using loguru.

Classes:
    InterceptHandler: Default handler from examples in loguru documentation.

Functions:
    record_formatter: Custom formatter for log records with essential context.
    enable_logging_extension: Enables logging extension with enhanced configuration.
"""

import logging
import sys
from typing import Any

from loguru import logger
import sentry_sdk

from app.core.enums.app_env_enum import AppEnv
from app.web.settings import settings


class InterceptHandler(logging.Handler):
    """Default handler from examples in loguru documentation.

    This handler intercepts all log requests and passes them to loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record by passing it to loguru.

        Args:
            record (logging.LogRecord): The log record to emit.
        """
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


class SentryHandler:
    """Handler to send Loguru logs directly to Sentry."""
    
    def __init__(self):
        self.enabled = bool(settings.sentry_dsn)
        if self.enabled:
            logger.info("Sentry handler initialized for Loguru")
    
    def write(self, message):
        """Handle Loguru message and send ERROR/CRITICAL logs to Sentry."""
        if not self.enabled:
            return
            
        try:
            # Check if we received a string or a record object
            if isinstance(message, str):
                # Simple string handling - just send to Sentry as error
                with sentry_sdk.push_scope() as scope:
                    scope.set_tag("log_source", "loguru_string")
                    sentry_sdk.capture_message(message, level="error")
                return
                
            # Extract level and determine if we should send to Sentry
            level_name = message["level"].name
            msg_text = message["message"]

            if level_name in ["INFO", "WARNING"]:
                sentry_sdk.add_breadcrumb(
                    category="loguru",
                    message=message["message"],
                    level=level_name.lower(),
                    data={
                        "logger": message["name"],
                        "function": message["function"],
                        "line": message["line"],
                        "file": str(message["file"]),
                    }
                )
            if level_name not in ["ERROR", "CRITICAL"]:
                return
                
            # Extract message text
            msg_text = message["message"]
            level = level_name.lower()
            
            # Get exception info if available
            exception = message.get("exception")
            
            # Use a fresh scope for each message
            with sentry_sdk.push_scope() as scope:
                # Add basic metadata
                scope.set_tag("log_source", "loguru")
                scope.set_extra("logger_name", message["name"])
                scope.set_extra("function", message["function"])
                scope.set_extra("line", message["line"])
                scope.set_extra("file", message["file"].name if hasattr(message["file"], "name") else str(message["file"]))
                scope.set_extra("module", message["module"])
                
                # Add any extra context from the record
                if "extra" in message:
                    for key, value in message["extra"].items():
                        scope.set_extra(f"loguru_{key}", value)
                
                # Capture with appropriate method
                if exception and exception.type:
                    # Capture the exception
                    exc_type = exception.type
                    exc_value = exception.value
                    exc_traceback = exception.traceback
                    sentry_sdk.capture_exception((exc_type, exc_value, exc_traceback))
                else:
                    # Capture as message
                    sentry_sdk.capture_message(msg_text, level=level)
                
        except Exception as e:
            # Don't let logging errors crash the app
            if settings.app_env == AppEnv.LOCAL:
                logger.error(f"SentryHandler error: {e}")
                import traceback
                traceback.print_exc()


class NewRelicHandler:
    """Handler to send logs to New Relic via OpenTelemetry."""
    
    def __init__(self):
        self.otel_handler = None
        try:
            from opentelemetry.sdk._logs import LoggingHandler
            from opentelemetry._logs import get_logger_provider
            
            logger_provider = get_logger_provider()
            if logger_provider:
                self.otel_handler = LoggingHandler(level=logging.DEBUG, logger_provider=logger_provider)
        except Exception as e:
            logger.error(f"Could not initialize New Relic handler: {e}")
    
    def write(self, message):
        """Send log message to New Relic."""
        if self.otel_handler and message.strip():
            try:
                # Parse the Loguru message format
                # Expected format: "2025-06-19 16:48:10.862 | ERROR | __main__:25 | This is an error message"
                parts = message.strip().split(" | ")
                
                if len(parts) >= 4:
                    # Extract components
                    timestamp = parts[0]
                    level_str = parts[1].strip()
                    module_line = parts[2].strip()
                    actual_message = " | ".join(parts[3:]).strip()
                    
                    # Map Loguru levels to Python logging levels
                    level_mapping = {
                        "TRACE": logging.DEBUG,
                        "DEBUG": logging.DEBUG,
                        "INFO": logging.INFO,
                        "SUCCESS": logging.INFO,
                        "WARNING": logging.WARNING,
                        "ERROR": logging.ERROR,
                        "CRITICAL": logging.CRITICAL
                    }
                    
                    # Get the correct logging level
                    log_level = level_mapping.get(level_str, logging.INFO)
                    
                    # Extract module and line information
                    if ":" in module_line:
                        module_name, line_no = module_line.split(":", 1)
                        try:
                            line_number = int(line_no)
                        except ValueError:
                            line_number = 0
                    else:
                        module_name = module_line
                        line_number = 0
                    
                    # Create a proper log record with correct level
                    record = logging.LogRecord(
                        name=module_name,
                        level=log_level,
                        pathname="",
                        lineno=line_number,
                        msg=actual_message,
                        args=(),
                        exc_info=None
                    )
                    
                    # Set all required standard attributes
                    record.funcName = "app_logger"
                    record.levelno = log_level
                    record.levelname = logging.getLevelName(log_level)
                    record.filename = ""
                    record.module = module_name
                    record.pathname = ""
                    record.created = 0.0
                    record.msecs = 0.0
                    record.relativeCreated = 0.0
                    record.thread = 0
                    record.threadName = "MainThread"
                    record.processName = "MainProcess"
                    record.process = 0
                    
                    # Set OpenTelemetry specific attributes to avoid warnings
                    record.taskName = "app_logging"  # Fix the taskName issue
                    record.service_name = settings.application_name
                    record.service_environment = str(settings.app_env)
                    record.log_level = level_str
                    
                else:
                    # Fallback for messages that don't match expected format
                    record = logging.LogRecord(
                        name="app",
                        level=logging.INFO,
                        pathname="",
                        lineno=0,
                        msg=message.strip(),
                        args=(),
                        exc_info=None
                    )
                    
                    # Set all required standard attributes
                    record.funcName = "app_logger"
                    record.levelno = logging.INFO
                    record.levelname = "INFO"
                    
                    # Set OpenTelemetry specific attributes
                    record.taskName = "app_logging"
                    record.service_name = settings.application_name
                    record.service_environment = str(settings.app_env)
                
                # Send to New Relic
                self.otel_handler.emit(record)
                
            except Exception as e:
                if settings.app_env == AppEnv.LOCAL:
                    logger.error(f"Error sending log to New Relic: {e}")
                    logger.error(f"Original message: {message}")


def record_formatter(record: dict[str, Any]) -> str:
    """Custom formatter for log records with essential context."""
    if settings.app_env == AppEnv.LOCAL:
        # Keep the existing detailed format for local development
        log_format = (
            "<white>{time:YYYY-MM-DD HH:mm:ss}</white> | "
            "<yellow>{extra[app_env]}</yellow> | "
            "<level>{level: <8}</level> | "
            "<green>{extra[request_id]}</green> | "
            "<cyan>{name}</cyan>:{line} | "
            "<level>{message}</level>\n"
        )

        # Add payload and exception for local format
        if record["extra"].get("payload"):
            log_format += "<dim>Payload: {extra[payload]}</dim>\n"
        if record["exception"]:
            # Simplified exception format
            log_format += "<red>Error: {exception!s}</red>\n"

        return log_format

    return "{message}"


def enable_logging_extension() -> None:
    """Enables and configures the logging extension."""
    # Remove default logger
    logger.remove()

    # Intercept standard logging
    intercept_handler = InterceptHandler()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers = [intercept_handler]
    root_logger.setLevel(logging.NOTSET)

    # Configure specific loggers without redundancy
    seen = set()
    for name in [
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".", maxsplit=1)[0])
            logging.getLogger(name).handlers = []  # Remove any existing handlers
            logging.getLogger(name).propagate = True  # Let root logger handle it

    # Common configuration for file handlers
    base_config = {
        "rotation": settings.log_rotation,
        "retention": f"{settings.log_retention_days} days",
        "compression": "zip",
        "format": record_formatter,
        "enqueue": True,
        "catch": True,
        "serialize": settings.app_env != AppEnv.LOCAL,
    }

    # Define handlers
    handlers = [
        {
            "sink": sys.stdout,
            "level": settings.log_level,
            "colorize": settings.app_env == AppEnv.LOCAL,
            "backtrace": settings.app_env in (AppEnv.LOCAL, AppEnv.DEV),
            "diagnose": settings.app_env in (AppEnv.LOCAL, AppEnv.DEV),
            "format": record_formatter,
            "enqueue": True,
            "serialize": settings.app_env != AppEnv.LOCAL,
        },
    ]

    # Add Sentry handler for Loguru logs
    try:
        if settings.sentry_dsn:
            sentry_handler = SentryHandler()
            handlers.append({
                "sink": sentry_handler.write,
                "level": "ERROR",  
                "format": "{message}",  
                "serialize": False,  
                "enqueue": False,  
            })
            
            # Also add a handler that uses serialize=True as fallback
            # This ensures we catch logs even if the record format changes
            handlers.append({
                "sink": sentry_handler.write,
                "level": "ERROR",
                "serialize": True,  # Send as string
                "enqueue": False,
            })
            
            logger.info("Sentry logging handler added successfully")
        else:
            logger.warning("Sentry DSN not configured - Sentry logging disabled")
    except Exception as e:
        logger.warning(f"Could not add Sentry logging handler: {e}")

    # Add New Relic handler
    try:
        new_relic_handler = NewRelicHandler()
        if new_relic_handler.otel_handler:
            handlers.append({
                "sink": new_relic_handler.write,
                "level": settings.log_level,
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{line} | {message}",  # Consistent format for parsing
                "enqueue": True,
                "serialize": False,
            })
            logger.info("New Relic logging handler added successfully")
        else:
            logger.warning("New Relic logging handler could not be initialized")
    except Exception as e:
        logger.warning(f"Could not add New Relic logging handler: {e}")

    # Add file handlers only if enabled in settings
    if settings.enable_file_logging:
        base_logs_dir = settings.logs_dir
        app_logs_dir = base_logs_dir / "application"
        error_logs_dir = base_logs_dir / "error"

        handlers.extend(
            [
                {
                    **base_config,
                    "sink": str(app_logs_dir / "app_{time:YYYY-MM-DD}.log"),
                    "level": "DEBUG" if settings.app_env == AppEnv.DEV else "INFO",
                    "filter": lambda record: record["level"].name not in ("ERROR", "CRITICAL"),  # type: ignore
                    "backtrace": False,
                    "diagnose": False,
                },
                {
                    **base_config,
                    "sink": str(error_logs_dir / "error_{time:YYYY-MM-DD}.log"),
                    "level": "ERROR",
                    "backtrace": settings.app_env == AppEnv.LOCAL,  # Only show backtraces in local error logs
                    "diagnose": False,
                },
            ]
        )

    # Configure logging with handlers
    logger.configure(
        handlers=handlers,  # type: ignore
        extra={
            "service_name": settings.application_name,
            "request_id": "",
            "app_env": settings.app_env,
        },
    )
