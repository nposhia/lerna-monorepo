"""OpenTelemetry telemetry module for observability."""

from .decorators import trace_function, trace_database_operation

__all__ = ["trace_function", "trace_database_operation"] 