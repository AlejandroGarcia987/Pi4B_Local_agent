from pydantic import BaseSettings, ConfigDict
from pydantic import Field

class Settings(BaseSettings):
    #Pydantic config to load form .env
    model_config = ConfigDict(env_file='.env', env_file_config='utf-8')

    #Variables
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot Token. Must be loaded from .env")

settings = Settings()