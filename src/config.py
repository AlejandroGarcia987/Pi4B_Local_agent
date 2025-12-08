from pydantic import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    #Pydantic config to load form .env
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    #Variables
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot Token. Must be loaded from .env")

settings = Settings()