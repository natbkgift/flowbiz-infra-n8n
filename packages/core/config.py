from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Runtime Configuration (APP_*)
    app_env: str = "dev"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_log_level: str = "info"

    # Metadata (FLOWBIZ_*)
    flowbiz_service_name: str = "flowbiz-template-service"
    flowbiz_version: str = "0.1.0"
    flowbiz_build_sha: str = "local"

    # n8n Webhook
    n8n_webhook_base_url: str = "http://127.0.0.1:5678/webhook"
    n8n_api_base_url: str = "http://127.0.0.1:5678/api/v1"
    n8n_api_key: str | None = None

    # Jobs API limits
    jobs_max_timeout_seconds: int = 300
    jobs_rate_limit_per_minute: int = 60

    # Callback verification
    callback_signing_secret: str | None = None

    # Audit log persistence (SQLite)
    audit_db_path: str = "data/audit.db"


settings = Settings()
