import os
from functools import lru_cache
from pydantic_settings import BaseSettings

INSTALLED_ADDONS = ['core', 'user']


class Settings(BaseSettings):
    APP_NAME: str = "Totem"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite://db.sqlite3")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    DEBUG: bool = bool(int(os.getenv("DEBUG", "0")))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
