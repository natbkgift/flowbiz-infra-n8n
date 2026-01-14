from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Runtime Configuration (APP_*)
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_log_level: str = "info"

    # Metadata (FLOWBIZ_*)
    flowbiz_service_name: str = "flowbiz-template-service"
    flowbiz_version: str = "0.1.0"
    flowbiz_build_sha: str = "local"


settings = Settings()
