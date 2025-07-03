"""OpenTelemetry decorators for function tracing and metrics collection."""

from functools import wraps
from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode
import time
import logging
from typing import Callable, Any, Dict, Optional
import asyncio

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


def trace_function(
    name: str = None, 
    record_metrics: bool = True, 
    include_args: bool = False,
    service_name: str = None,
    operation: str = None,
    component: str = "function"
):
    """
    Unified decorator for tracing functions with comprehensive observability.
    
    This decorator handles both sync/async functions and can be used for:
    - Internal business logic functions
    - External service calls
    - Any custom tracing needs
    
    Args:
        name: Custom name for the span (defaults to module.function_name)
        record_metrics: Whether to record custom metrics
        include_args: Whether to include function arguments in span attributes
        service_name: Name of external service (for external calls)
        operation: Specific operation being performed
        component: Component type (function, external_service, etc.)
    """
    def decorator(func: Callable) -> Callable:
        is_async = asyncio.iscoroutinefunction(func)
        
        def _execute_with_tracing(func_executor, *args, **kwargs):
            start_time = time.time()
            
            # Determine span name
            if name:
                span_name = name
            elif service_name:
                span_name = f"external.{service_name}"
                if operation:
                    span_name += f".{operation}"
            else:
                span_name = f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                try:
                    # Set base attributes
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    span.set_attribute("function.qualname", func.__qualname__)
                    span.set_attribute("span.kind", "client" if service_name else "internal")
                    span.set_attribute("component", component)
                    span.set_attribute("function.type", "async" if is_async else "sync")
                    
                    # Set service-specific attributes if provided
                    if service_name:
                        span.set_attribute("service.name", service_name)
                        if operation:
                            span.set_attribute("service.operation", operation)
                    
                    # Add function arguments as attributes if requested
                    if include_args:
                        for i, arg in enumerate(args):
                            if isinstance(arg, (int, str, float, bool)) and len(str(arg)) < 100:
                                span.set_attribute(f"function.arg.{i}", str(arg))
                        
                        for key, value in kwargs.items():
                            if isinstance(value, (int, str, float, bool)) and len(str(value)) < 100:
                                span.set_attribute(f"function.param.{key}", str(value))
                    
                    # Execute the function
                    result = func_executor(*args, **kwargs)
                    
                    # Calculate duration
                    duration_ms = (time.time() - start_time) * 1000
                    duration_seconds = duration_ms / 1000
                    span.set_attribute("function.duration_ms", duration_ms)
                    span.set_attribute("function.success", True)
                    
                    # Record metrics if requested
                    if record_metrics:
                        _record_success_metrics(func, duration_seconds, service_name)
                    
                    return result
                    
                except Exception as e:
                    # Calculate duration for errors
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Set error status
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("function.duration_ms", duration_ms)
                    span.set_attribute("function.success", False)
                    
                    # Record error metrics
                    if record_metrics:
                        _record_error_metrics(func, e, service_name)
                    
                    raise
        
        if is_async:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await _execute_with_tracing(lambda *a, **kw: func(*a, **kw), *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return _execute_with_tracing(func, *args, **kwargs)
            return sync_wrapper
        
    return decorator


def trace_database_operation(operation_type: str = "query", table_name: str = None):
    """
    Specialized decorator for database operations.
    
    Args:
        operation_type: Type of database operation (query, insert, update, delete)
        table_name: Name of the table being operated on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            span_name = f"db.{operation_type}"
            if table_name:
                span_name += f".{table_name}"
            
            start_time = time.time()
            
            with tracer.start_as_current_span(span_name) as span:
                try:
                    # Set database-specific attributes
                    span.set_attribute("db.system", "postgresql")
                    span.set_attribute("db.operation", operation_type)
                    span.set_attribute("span.kind", "client")
                    span.set_attribute("component", "database")
                    
                    if table_name:
                        span.set_attribute("db.table", table_name)
                    
                    # Add function context
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    # Execute the function
                    result = await func(*args, **kwargs)
                    
                    # Calculate duration
                    duration_ms = (time.time() - start_time) * 1000
                    span.set_attribute("db.duration_ms", duration_ms)
                    span.set_attribute("db.success", True)
                    
                    # Record database metrics
                    _record_db_metrics(operation_type, table_name, duration_ms / 1000, True)
                    
                    return result
                    
                except Exception as e:
                    # Calculate duration for errors
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Set error status
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("db.duration_ms", duration_ms)
                    span.set_attribute("db.success", False)
                    
                    # Record database error metrics
                    _record_db_metrics(operation_type, table_name, duration_ms / 1000, False)
                    
                    raise
        
        return wrapper
    return decorator


def _record_success_metrics(func: Callable, duration_seconds: float, service_name: str = None):
    """Record success metrics for function execution."""
    try:
        from app.web.application import get_app
        app = get_app()
        if hasattr(app.state, 'meters'):
            meters = app.state.meters
            
            if service_name:
                # External service metrics
                if "external_call_counter" in meters:
                    meters["external_call_counter"].add(1, {
                        "service": service_name,
                        "function": func.__name__,
                        "status": "success"
                    })
                if "external_call_duration" in meters:
                    meters["external_call_duration"].record(duration_seconds, {
                        "service": service_name,
                        "function": func.__name__
                    })
            else:
                # Function metrics
                if "function_counter" in meters:
                    meters["function_counter"].add(1, {
                        "function": func.__name__,
                        "module": func.__module__,
                        "status": "success"
                    })
                if "function_duration" in meters:
                    meters["function_duration"].record(duration_seconds, {
                        "function": func.__name__,
                        "module": func.__module__
                    })
    except Exception as e:
        logger.debug(f"Could not record success metrics: {e}")


def _record_error_metrics(func: Callable, error: Exception, service_name: str = None):
    """Record error metrics for function execution."""
    try:
        from app.web.application import get_app
        app = get_app()
        if hasattr(app.state, 'meters'):
            meters = app.state.meters
            
            if service_name:
                # External service error metrics
                if "external_call_counter" in meters:
                    meters["external_call_counter"].add(1, {
                        "service": service_name,
                        "function": func.__name__,
                        "status": "error",
                        "error_type": type(error).__name__
                    })
            else:
                # Function error metrics
                if "error_counter" in meters:
                    meters["error_counter"].add(1, {
                        "function": func.__name__,
                        "module": func.__module__,
                        "error_type": type(error).__name__
                    })
    except Exception as e:
        logger.debug(f"Could not record error metrics: {e}")


def _record_db_metrics(operation_type: str, table_name: str, duration_seconds: float, success: bool):
    """Record database operation metrics."""
    try:
        from app.web.application import get_app
        app = get_app()
        if hasattr(app.state, 'meters'):
            meters = app.state.meters
            
            if "db_operation_counter" in meters:
                meters["db_operation_counter"].add(1, {
                    "operation": operation_type,
                    "table": table_name or "unknown",
                    "status": "success" if success else "error"
                })
            
            if "db_operation_duration" in meters:
                meters["db_operation_duration"].record(duration_seconds, {
                    "operation": operation_type,
                    "table": table_name or "unknown"
                })
    except Exception as e:
        logger.debug(f"Could not record database metrics: {e}") 