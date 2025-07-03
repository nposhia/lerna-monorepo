"""HTTP clients OpenTelemetry integration."""

from typing import Optional, Dict, Any
from loguru import logger
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor


class HTTPClientTelemetryIntegration:
    """HTTP clients OpenTelemetry integration handler."""
    
    def __init__(self):
        self._requests_instrumented = False
        self._urllib3_instrumented = False
    
    def instrument_requests(self, telemetry_config: Dict[str, Any]) -> bool:
        """Instrument requests library with OpenTelemetry."""
        if not telemetry_config:
            logger.warning("No telemetry config provided, skipping requests instrumentation")
            return False
        
        if self._requests_instrumented:
            return True
        
        try:
            RequestsInstrumentor().instrument(
                tracer_provider=telemetry_config["tracer_provider"],
                meter_provider=telemetry_config["meter_provider"]
            )
            self._requests_instrumented = True
            logger.info("Requests instrumentation added successfully")
            return True
        except Exception as e:
            logger.warning(f"Could not instrument requests: {e}")
            return False
    
    def instrument_urllib3(self, telemetry_config: Dict[str, Any]) -> bool:
        """Instrument urllib3 library with OpenTelemetry."""
        if not telemetry_config:
            logger.warning("No telemetry config provided, skipping urllib3 instrumentation")
            return False
        
        if self._urllib3_instrumented:
            return True
        
        try:
            URLLib3Instrumentor().instrument(
                tracer_provider=telemetry_config["tracer_provider"],
                meter_provider=telemetry_config["meter_provider"]
            )
            self._urllib3_instrumented = True
            logger.info("urllib3 instrumentation added successfully")
            return True
        except Exception as e:
            logger.warning(f"Could not instrument urllib3: {e}")
            return False
    
    def instrument_all(self, telemetry_config: Dict[str, Any]) -> bool:
        """Instrument all HTTP client libraries."""
        requests_success = self.instrument_requests(telemetry_config)
        urllib3_success = self.instrument_urllib3(telemetry_config)
        return requests_success and urllib3_success
    
    def is_requests_instrumented(self) -> bool:
        """Check if requests library is instrumented."""
        return self._requests_instrumented
    
    def is_urllib3_instrumented(self) -> bool:
        """Check if urllib3 library is instrumented."""
        return self._urllib3_instrumented 