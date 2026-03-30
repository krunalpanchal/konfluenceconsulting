from functools import lru_cache
import os

class Settings:
    app_name: str = os.getenv("APP_NAME", "Konfluence Full Real Engines API")
    app_env: str = os.getenv("APP_ENV", "production")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/konfluence.db")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")
    serpapi_key: str = os.getenv("SERPAPI_KEY", "")

@lru_cache
def get_settings() -> Settings:
    return Settings()
