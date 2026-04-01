"""
Settings - Configuration management for the application.
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    api_title: str = "ResumeIQ"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

    # LLM Settings
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4")
    llm_temperature: float = 0.7

    # Database Settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///resumeiq.db")
    database_pool_size: int = 5

    # Embedding Settings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Logging Settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = os.getenv("LOG_FILE", None)

    # Service Settings
    enable_feedback_loop: bool = True
    max_retries: int = 3
    request_timeout: int = 300

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
