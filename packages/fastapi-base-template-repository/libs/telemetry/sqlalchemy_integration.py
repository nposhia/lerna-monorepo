"""SQLAlchemy OpenTelemetry integration."""

from typing import Optional, Dict, Any
from loguru import logger
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


class SQLAlchemyTelemetryIntegration:
    """SQLAlchemy OpenTelemetry integration handler."""
    
    def __init__(self):
        self._instrumented_engines = set()
    
    def instrument_engine(self, engine, telemetry_config: Dict[str, Any]) -> bool:
        """Instrument SQLAlchemy engine with OpenTelemetry."""
        if not telemetry_config:
            logger.warning("No telemetry config provided, skipping SQLAlchemy instrumentation")
            return False
        
        # Check if this engine is already instrumented
        engine_id = id(engine)
        if engine_id in self._instrumented_engines:
            logger.info("SQLAlchemy engine already instrumented")
            return True
        
        # Check if SQLAlchemy is already instrumented via engine attribute
        if hasattr(engine, '_sqlalchemy_instrumented') and engine._sqlalchemy_instrumented:
            self._instrumented_engines.add(engine_id)
            return True
        
        try:
            # For async engines, we need to instrument the sync engine
            target_engine = engine
            if hasattr(engine, 'sync_engine'):
                target_engine = engine.sync_engine
                
            SQLAlchemyInstrumentor().instrument(
                engine=target_engine,
                tracer_provider=telemetry_config["tracer_provider"],
                meter_provider=telemetry_config["meter_provider"]
            )
            engine._sqlalchemy_instrumented = True
            self._instrumented_engines.add(engine_id)
            logger.info("SQLAlchemy instrumentation added successfully")
            return True
        except Exception as e:
            logger.warning(f"Could not instrument SQLAlchemy: {e}")
            return False
    
    def is_instrumented(self, engine) -> bool:
        """Check if the SQLAlchemy engine is already instrumented."""
        engine_id = id(engine)
        return engine_id in self._instrumented_engines or (
            hasattr(engine, '_sqlalchemy_instrumented') and engine._sqlalchemy_instrumented
        ) 