"""Redis OpenTelemetry integration."""

from typing import Optional, Dict, Any
from loguru import logger


class RedisTelemetryIntegration:
    """Redis OpenTelemetry integration handler."""
    
    def __init__(self):
        self._instrumented = False
    
    def instrument(self, telemetry_config: Dict[str, Any]) -> bool:
        """Instrument Redis with OpenTelemetry."""
        if not telemetry_config:
            logger.warning("No telemetry config provided, skipping Redis instrumentation")
            return False
        
        if self._instrumented:
            logger.info("Redis already instrumented")
            return True
        
        try:
            from opentelemetry.instrumentation.redis import RedisInstrumentor
            RedisInstrumentor().instrument(
                tracer_provider=telemetry_config["tracer_provider"],
                meter_provider=telemetry_config["meter_provider"]
            )
            self._instrumented = True
            logger.info("Redis instrumentation added successfully")
            return True
        except ImportError:
            logger.info("Redis instrumentation not available - redis package not installed")
            return False
        except Exception as e:
            logger.warning(f"Could not instrument Redis: {e}")
            return False
    
    def is_instrumented(self) -> bool:
        """Check if Redis is instrumented."""
        return self._instrumented 