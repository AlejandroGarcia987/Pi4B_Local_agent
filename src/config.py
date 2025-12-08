from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #Pydantic config to load form .env
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    #Variables
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot Token. Must be loaded from .env")

settings = Settings()