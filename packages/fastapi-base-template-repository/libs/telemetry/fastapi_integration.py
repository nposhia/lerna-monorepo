"""FastAPI OpenTelemetry integration."""

from typing import Optional, Dict, Any
from loguru import logger
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


class FastAPITelemetryIntegration:
    """FastAPI OpenTelemetry integration handler."""
    
    def __init__(self):
        self._instrumented_apps = set()
    
    def instrument_app(self, app, telemetry_config: Dict[str, Any]) -> bool:
        """Instrument FastAPI application with OpenTelemetry."""
        if not telemetry_config:
            logger.warning("No telemetry config provided, skipping FastAPI instrumentation")
            return False
        
        # Check if this app is already instrumented
        app_id = id(app)
        if app_id in self._instrumented_apps:
            return True
        
        # Check if FastAPI is already instrumented via app state
        if hasattr(app.state, '_fastapi_instrumented') and app.state._fastapi_instrumented:
            self._instrumented_apps.add(app_id)
            return True
        
        try:
            FastAPIInstrumentor.instrument_app(
                app,
                tracer_provider=telemetry_config["tracer_provider"],
                meter_provider=telemetry_config["meter_provider"]
            )
            app.state._fastapi_instrumented = True
            self._instrumented_apps.add(app_id)
            logger.info("FastAPI instrumentation added successfully")
            return True
        except Exception as e:
            logger.warning(f"Could not instrument FastAPI: {e}")
            return False
    
    def is_instrumented(self, app) -> bool:
        """Check if the FastAPI app is already instrumented."""
        app_id = id(app)
        return app_id in self._instrumented_apps or (
            hasattr(app.state, '_fastapi_instrumented') and app.state._fastapi_instrumented
        ) 