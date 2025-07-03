"""Custom metrics OpenTelemetry integration."""

from typing import Optional, Dict, Any
from loguru import logger
from opentelemetry import metrics


class CustomMetricsIntegration:
    """Custom metrics OpenTelemetry integration handler."""
    
    def __init__(self):
        self._metrics_created = False
        self._meters = {}
    
    def create_metrics(self, app, telemetry_config: Dict[str, Any]) -> bool:
        """Create custom metrics for the application."""
        if self._metrics_created:
            return True
        
        if not telemetry_config:
            logger.warning("No telemetry config provided, skipping custom metrics creation")
            return False
        
        try:
            meter = metrics.get_meter(__name__)
            
            # HTTP Request metrics (for FastAPI instrumentation)
            request_counter = meter.create_counter(
                name="http_requests_total",
                description="Total number of HTTP requests",
                unit="1"
            )
            
            request_duration = meter.create_histogram(
                name="http_request_duration_seconds",
                description="HTTP request duration in seconds",
                unit="s"
            )
            
            error_counter = meter.create_counter(
                name="http_errors_total",
                description="Total number of HTTP errors",
                unit="1"
            )
            
            # Function-level metrics (for trace_function decorator)
            function_counter = meter.create_counter(
                name="function_calls_total",
                description="Total number of function calls",
                unit="1"
            )
            
            function_duration = meter.create_histogram(
                name="function_duration_seconds",
                description="Function execution duration in seconds",
                unit="s"
            )
            
            # Database operation metrics
            db_operation_counter = meter.create_counter(
                name="db_operations_total",
                description="Total number of database operations",
                unit="1"
            )
            
            db_operation_duration = meter.create_histogram(
                name="db_operation_duration_seconds",
                description="Database operation duration in seconds",
                unit="s"
            )
            
            # External service call metrics
            external_call_counter = meter.create_counter(
                name="external_calls_total",
                description="Total number of external service calls",
                unit="1"
            )
            
            external_call_duration = meter.create_histogram(
                name="external_call_duration_seconds",
                description="External service call duration in seconds",
                unit="s"
            )
            
            # Store meters for use in decorators
            self._meters = {
                # HTTP metrics
                "request_counter": request_counter,
                "request_duration": request_duration,
                "error_counter": error_counter,
                
                # Function metrics
                "function_counter": function_counter,
                "function_duration": function_duration,
                
                # Database metrics
                "db_operation_counter": db_operation_counter,
                "db_operation_duration": db_operation_duration,
                
                # External service metrics
                "external_call_counter": external_call_counter,
                "external_call_duration": external_call_duration
            }
            
            # Store meters in app state for access from decorators
            app.state.meters = self._meters
            
            self._metrics_created = True
            logger.info("Custom metrics created successfully")
            return True
        except Exception as e:
            logger.warning(f"Could not create custom metrics: {e}")
            return False
    
    def get_meters(self) -> Dict[str, Any]:
        """Get the created meters."""
        return self._meters
    
    def is_created(self) -> bool:
        """Check if custom metrics are created."""
        return self._metrics_created 