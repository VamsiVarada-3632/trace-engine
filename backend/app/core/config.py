from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "TRACE"
    app_env: str = "development"
    debug: bool = True

    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Hindsight Configuration
    hindsight_api_url: str = "http://localhost:8100"
    hindsight_api_key: str = ""
    hindsight_namespace: str = "trace-manufacturing"

    # Database
    database_url: str = "sqlite+aiosqlite:///./trace.db"

    # CORS
    cors_origins: str = '["http://localhost:3000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
