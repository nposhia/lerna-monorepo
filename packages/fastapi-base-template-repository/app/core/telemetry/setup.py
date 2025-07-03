"""OpenTelemetry setup orchestrator for telemetry initialization."""

from typing import Optional, Dict, Any
from loguru import logger
from libs.telemetry import (
    NewRelicIntegration,
    FastAPITelemetryIntegration,
    SQLAlchemyTelemetryIntegration,
    HTTPClientTelemetryIntegration,
    RedisTelemetryIntegration,
    CustomMetricsIntegration
)


class TelemetryOrchestrator:
    """
    This class is responsible for orchestrating the setup of all telemetry integrations.
    Implements singleton pattern to ensure only one instance exists.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Ensure only one instance of TelemetryOrchestrator exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(TelemetryOrchestrator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the telemetry orchestrator with all integration instances."""
        # Prevent re-initialization of the singleton
        if TelemetryOrchestrator._initialized:
            return
            
        self._telemetry_initialized = False
        self._telemetry_config: Optional[Dict[str, Any]] = None
        
        # Integration instances
        self.newrelic_integration = NewRelicIntegration()
        self.fastapi_integration = FastAPITelemetryIntegration()
        self.sqlalchemy_integration = SQLAlchemyTelemetryIntegration()
        self.http_clients_integration = HTTPClientTelemetryIntegration()
        self.redis_integration = RedisTelemetryIntegration()
        self.metrics_integration = CustomMetricsIntegration()
        
        TelemetryOrchestrator._initialized = True

    def setup_telemetry_core(self) -> Optional[Dict[str, Any]]:
        """
        Initialize core OpenTelemetry components without FastAPI instrumentation.
        This should be called before the FastAPI app is fully configured.
        """
        if self._telemetry_initialized:
            return self._telemetry_config
        
        # Initialize New Relic integration (core telemetry setup)
        telemetry_config = self.newrelic_integration.initialize()
        if not telemetry_config:
            logger.warning("Failed to initialize New Relic integration")
            return None
        
        # Setup HTTP client instrumentations
        self.http_clients_integration.instrument_all(telemetry_config)
        
        # Setup Redis instrumentation
        self.redis_integration.instrument(telemetry_config)
        
        self._telemetry_initialized = True
        self._telemetry_config = telemetry_config
        logger.info("OpenTelemetry core setup complete")
        
        return telemetry_config

    def setup_fastapi_instrumentation(self, app, telemetry_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Set up FastAPI instrumentation after the app is created but before middleware is added.
        """
        config = telemetry_config or self._telemetry_config
        if not config:
            logger.warning("No telemetry config provided, skipping FastAPI instrumentation")
            return False
        
        return self.fastapi_integration.instrument_app(app, config)

    def setup_sqlalchemy_instrumentation(self, engine, telemetry_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Set up SQLAlchemy instrumentation.
        """
        config = telemetry_config or self._telemetry_config
        if not config:
            logger.warning("No telemetry config provided, skipping SQLAlchemy instrumentation")
            return False
        
        return self.sqlalchemy_integration.instrument_engine(engine, config)

    def create_custom_metrics(self, app, telemetry_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create custom metrics for the application.
        """
        config = telemetry_config or self._telemetry_config
        if not config:
            logger.warning("No telemetry config provided, skipping custom metrics creation")
            return False
        
        return self.metrics_integration.create_metrics(app, config)

    def setup_tracing(self, app, engine) -> Optional[Dict[str, Any]]:
        """
        Initialize comprehensive OpenTelemetry observability with New Relic.
        This function sets up:
        1. Distributed tracing with spans
        2. Metrics collection
        3. Structured logging (basic)
        4. Error tracking and correlation
        5. Database monitoring
        6. HTTP client monitoring
        
        This is the main entry point for telemetry setup.
        """
        # Set up core telemetry
        telemetry_config = self.setup_telemetry_core()
        
        if telemetry_config:
            # Set up FastAPI instrumentation
            self.setup_fastapi_instrumentation(app, telemetry_config)
            
            # Set up SQLAlchemy instrumentation
            self.setup_sqlalchemy_instrumentation(engine, telemetry_config)
            
            # Create custom metrics
            self.create_custom_metrics(app, telemetry_config)
            
            # Store telemetry config in app state
            app.state.telemetry = telemetry_config
            
            logger.info("Complete telemetry setup finished successfully")
            return telemetry_config
        else:
            logger.warning("OpenTelemetry setup skipped due to missing configuration")
            return None

    def get_integration_status(self) -> Dict[str, bool]:
        """Get the status of all telemetry integrations."""
        return {
            "newrelic": self.newrelic_integration._initialized,
            "http_clients_requests": self.http_clients_integration.is_requests_instrumented(),
            "http_clients_urllib3": self.http_clients_integration.is_urllib3_instrumented(),
            "redis": self.redis_integration.is_instrumented(),
            "custom_metrics": self.metrics_integration.is_created()
        }

    @property
    def is_initialized(self) -> bool:
        """Check if telemetry has been initialized."""
        return self._telemetry_initialized

    @property
    def config(self) -> Optional[Dict[str, Any]]:
        """Get the current telemetry configuration."""
        return self._telemetry_config

    @classmethod
    def get_instance(cls) -> 'TelemetryOrchestrator':
        """Get the singleton instance of TelemetryOrchestrator."""
        return cls()


# Convenience functions that use the singleton instance
def setup_telemetry_core() -> Optional[Dict[str, Any]]:
    """Initialize core telemetry using singleton orchestrator."""
    return TelemetryOrchestrator.get_instance().setup_telemetry_core()


def setup_fastapi_instrumentation(app, telemetry_config: Optional[Dict[str, Any]]) -> bool:
    """Set up FastAPI instrumentation using singleton orchestrator."""
    return TelemetryOrchestrator.get_instance().setup_fastapi_instrumentation(app, telemetry_config)


def setup_sqlalchemy_instrumentation(engine, telemetry_config: Optional[Dict[str, Any]]) -> bool:
    """Set up SQLAlchemy instrumentation using singleton orchestrator."""
    return TelemetryOrchestrator.get_instance().setup_sqlalchemy_instrumentation(engine, telemetry_config)


def create_custom_metrics(app, telemetry_config: Optional[Dict[str, Any]]) -> bool:
    """Create custom metrics using singleton orchestrator."""
    return TelemetryOrchestrator.get_instance().create_custom_metrics(app, telemetry_config)


def setup_tracing(app, engine) -> Optional[Dict[str, Any]]:
    """Initialize comprehensive telemetry using singleton orchestrator."""
    return TelemetryOrchestrator.get_instance().setup_tracing(app, engine)


def get_integration_status() -> Dict[str, bool]:
    """Get integration status using singleton orchestrator."""
    return TelemetryOrchestrator.get_instance().get_integration_status() 