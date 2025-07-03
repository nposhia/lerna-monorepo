"""New Relic OpenTelemetry integration."""

import os
from typing import Optional, Dict, Any
from loguru import logger
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider
import logging
from app.web.settings import settings

class NewRelicIntegration:
    """New Relic OpenTelemetry integration handler."""
    
    def __init__(self):
        self._initialized = False
        self._config = None
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """Get New Relic configuration from environment variables."""
        service_name = settings.new_relic_app_name
        new_relic_license_key = settings.new_relic_license_key
        environment = settings.new_relic_environment
        
        if not new_relic_license_key:
            logger.warning("NEW_RELIC_LICENSE_KEY not set, OpenTelemetry will not send data to New Relic")
            return None
        
        return {
            "service_name": service_name,
            "license_key": new_relic_license_key,
            "environment": environment,
            "endpoint": settings.new_relic_endpoint,
            "headers": {"api-key": new_relic_license_key}
        }
    
    def create_resource(self, config: Dict[str, Any]) -> Resource:
        """Create OpenTelemetry resource with New Relic attributes."""
        return Resource.create({
            "service.name": config["service_name"],
            "service.version": settings.new_relic_app_version,
            "deployment.environment": config["environment"],
            "service.instance.id": settings.new_relic_hostname,
            "cloud.provider": "docker",
            "container.runtime": "docker",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.language": "python",
            "telemetry.sdk.version": "1.21.0"
        })
    
    def setup_tracing(self, config: Dict[str, Any], resource: Resource) -> TracerProvider:
        """Set up tracing with New Relic OTLP exporter."""
        trace_provider = TracerProvider(resource=resource)
        trace_exporter = OTLPSpanExporter(
            endpoint=config["endpoint"],
            headers=config["headers"]
        )
        trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
        trace.set_tracer_provider(trace_provider)
        return trace_provider
    
    def setup_metrics(self, config: Dict[str, Any], resource: Resource) -> MeterProvider:
        """Set up metrics with New Relic OTLP exporter."""
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(
                endpoint=config["endpoint"],
                headers=config["headers"]
            ),
            export_interval_millis=5000  # Export every 5 seconds
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)
        return meter_provider
    
    def setup_logging(self, config: Dict[str, Any], resource: Resource) -> LoggerProvider:
        """Set up logging with New Relic OTLP exporter."""
        logs_exporter = OTLPLogExporter(
            endpoint=config["endpoint"],
            headers=config["headers"]
        )
        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(logs_exporter))
        set_logger_provider(logger_provider)

        otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
        logging.getLogger().addHandler(otel_handler)
        logging.getLogger().setLevel(logging.INFO)
        
        return logger_provider
    
    def initialize(self) -> Optional[Dict[str, Any]]:
        """Initialize New Relic telemetry integration."""
        if self._initialized:
            return self._config
        
        config = self.get_config()
        if not config:
            return None
        
        # Setup basic logging first
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        resource = self.create_resource(config)
        trace_provider = self.setup_tracing(config, resource)
        meter_provider = self.setup_metrics(config, resource)
        logger_provider = self.setup_logging(config, resource)
        
        self._config = {
            "tracer_provider": trace_provider,
            "meter_provider": meter_provider,
            "logger_provider": logger_provider,
            "resource": resource,
            "config": config
        }
        
        self._initialized = True
        logger.info(f"New Relic OpenTelemetry integration initialized for {config['service_name']} in {config['environment']}")
        
        return self._config 