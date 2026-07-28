import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # OpenRouter LLM settings
    OPENROUTER_API_KEY: str = "mock_key_for_testing"
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Token limits
    MAX_RESPONSE_TOKENS: int = 512
    MAX_HISTORY_MESSAGES: int = 6
    MAX_EMAIL_BODY_LENGTH: int = 400
    
    # Application settings
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
