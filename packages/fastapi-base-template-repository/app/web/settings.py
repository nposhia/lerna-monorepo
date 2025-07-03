"""Settings module.

This module provides access to configuration settings for the application.
"""

from pathlib import Path
from tempfile import gettempdir

from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from yarl import URL

from app.core.enums import AppEnv, ApplicationLogLevel


TEMP_DIR = Path(gettempdir())


class Settings(BaseSettings):
    """Application settings.

    These parameters are loaded from environment variables.
    """

    app_env: AppEnv = Field(
        AppEnv.DEV,
        alias="APP_ENV",
        description="Application runtime environment (dev/stage/prod)",
    )
    # Enable uvicorn reloading
    reload: bool = Field(False, alias="APPLICATION_AUTO_RELOAD")

    # Application settings
    application_name: str = Field("jeavio-fastapi-backend", alias="APPLICATION_NAME")
    host: str = Field("127.0.0.1", alias="HOST")
    port: int = Field(9000, alias="PORT")

    # CORS settings
    cors_allow_origins: str = Field("*", alias="CORS_ALLOW_ORIGINS")
    cors_allow_methods: str = Field("GET,POST,PUT,DELETE", alias="CORS_ALLOW_METHODS")
    cors_allow_headers: str = Field(
        "Content-Type,Authorization",
        alias="CORS_ALLOW_HEADERS",
    )

    # quantity of workers for uvicorn
    workers_count: int = Field(1, alias="APPLICATION_UVICORN_WORKERS_COUNT")

    log_level: ApplicationLogLevel = Field(
        ApplicationLogLevel.INFO,
        alias="APPLICATION_LOG_LEVEL",
    )

    # Swagger UI Authentication
    swagger_username: str = Field("admin", alias="SWAGGER_USERNAME")
    swagger_password: str = Field(..., alias="SWAGGER_PASSWORD")

    # Logging settings
    enable_file_logging: bool = Field(True, alias="ENABLE_FILE_LOGGING")
    logs_dir: Path = Field(Path("logs"), alias="LOGS_DIR")
    log_retention_days: int = Field(30, alias="LOG_RETENTION_DAYS")
    log_rotation: str = Field("daily", alias="LOG_ROTATION")

    # Variables for the postgres database
    postgres_database_host: str = Field(..., alias="POSTGRES_DATABASE_HOST")
    postgres_database_port: int = Field(5432, alias="POSTGRES_DATABASE_PORT")
    postgres_database_username: str = Field(..., alias="POSTGRES_DATABASE_USERNAME")
    postgres_database_password: str = Field(..., alias="POSTGRES_DATABASE_PASSWORD")
    postgres_database_name: str = Field(..., alias="POSTGRES_DATABASE_NAME")
    postgres_database_echo: bool = Field(False, alias="POSTGRES_DATABASE_ECHO")

    # Sentry Configuration
    sentry_dsn: str = Field("", alias="SENTRY_DSN")
    sentry_environment: str = Field("development", alias="SENTRY_ENVIRONMENT")
    sentry_sample_rate: float = Field(1.0, alias="SENTRY_SAMPLE_RATE")
    sentry_attach_stacktrace: bool = Field(True, alias="SENTRY_ATTACH_STACKTRACE")
    sentry_send_default_pii: bool = Field(False, alias="SENTRY_SEND_DEFAULT_PII")
    sentry_trace_sample_rate: float = Field(1.0, alias="SENTRY_TRACE_SAMPLE_RATE")
    sentry_profile_sample_rate: float = Field(1.0, alias="SENTRY_PROFILE_SAMPLE_RATE")
    sentry_release: str = Field("", alias="SENTRY_RELEASE")
    # Admin API Key
    admin_api_key: str = Field(..., alias="ADMIN_API_KEY")

    # Rate Limiting settings
    enable_global_rate_limit: bool = Field(True, alias="ENABLE_GLOBAL_RATE_LIMIT")
    global_rate_limit: str = Field("100/minute", alias="GLOBAL_RATE_LIMIT")
    # New Relic Configuration
    new_relic_license_key: str = Field("",alias="NEW_RELIC_LICENSE_KEY")
    new_relic_app_name: str = Field("jeavio-fastapi-backend", alias="NEW_RELIC_APP_NAME")
    new_relic_environment: str = Field(..., alias="APP_ENV")
    new_relic_endpoint: str = Field("https://otlp.nr-data.net:4318", alias="NEW_RELIC_ENDPOINT")
    new_relic_app_version: str = Field("1.0.0", alias="APP_VERSION")
    new_relic_hostname: str = Field("unknown", alias="HOSTNAME")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=True,
    )

    @classmethod
    # pylint: disable=no-self-argument,too-many-arguments,too-many-positional-arguments
    def settings_customise_sources(
        cls,
        _settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customise the settings sources and their priority."""
        return (
            dotenv_settings,  # First priority: .env file
            env_settings,  # Second priority: environment variables
            init_settings,  # Third priority: init settings
            file_secret_settings,  # Fourth priority: secrets file
        )

    @property
    def postgres_database_url(self) -> str:
        """Returns the URL for the postgres database."""
        database_url = URL.build(
            scheme="postgresql+asyncpg",
            host=self.postgres_database_host,
            port=self.postgres_database_port,
            user=self.postgres_database_username,
            password=self.postgres_database_password,
            path=f"/{self.postgres_database_name}",
        )
        return str(database_url)

    @property
    def postgres_sync_database_url(self) -> str:
        """Returns the URL for the postgres database."""
        database_url = URL.build(
            scheme="postgresql+psycopg",
            host=self.postgres_database_host,
            port=self.postgres_database_port,
            user=self.postgres_database_username,
            password=self.postgres_database_password,
            path=f"/{self.postgres_database_name}",
        )
        return str(database_url)

    @property
    # pylint: disable=no-member
    def cors_allow_origins_list(self) -> list[str]:
        """Returns a list of allowed CORS origins split from the cors_allow_origins string."""
        return self.cors_allow_origins.split(",")

    @property
    # pylint: disable=no-member
    def cors_allow_methods_list(self) -> list[str]:
        """Returns a list of allowed CORS HTTP methods split from the cors_allow_methods string."""
        return self.cors_allow_methods.split(",")

    @property
    # pylint: disable=no-member
    def cors_allow_headers_list(self) -> list[str]:
        """Returns a list of allowed CORS headers split from the cors_allow_headers string."""
        return self.cors_allow_headers.split(",")


settings = Settings.model_validate({})
