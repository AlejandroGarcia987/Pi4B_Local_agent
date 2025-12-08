from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    #Pydantic config to load form .env
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    #Variables
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot Token. Must be loaded from .env")

    #LLM Service
    LLM_URL: str = Field("http://127.0.0.1:11434/api/generate", description="Endpoint for LLM")
    LLM_MODEL: str = Field("gemma2:2b", description="LLM Model")

    #Optionals
    LLM_TIMEOUT_S: int = Field(60, description="Timeout for LLM petitions")
    LLM_MAX_CONCURRENCY: int = Field(2, description="Max simultaneous petitions")

settings = Settings()