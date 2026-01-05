from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


BACKEND_ENV_PATH = Path(__file__).with_name(".env")
DEFAULT_ENV_PATH = Path(".env")
ENV_FILE = BACKEND_ENV_PATH if BACKEND_ENV_PATH.exists() else DEFAULT_ENV_PATH


class Settings(BaseSettings):
    google_client_id: str = Field(..., alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., alias="GOOGLE_CLIENT_SECRET")
    oauth_redirect_uri: str = Field(
        "http://localhost:8000/auth/google/callback", alias="OAUTH_REDIRECT_URI"
    )
    subscription_query: str = Field(
        'subject:unsubscribe OR "subscription" OR "receipt" OR "billing"',
        alias="SUBSCRIPTION_QUERY",
    )
    sync_interval_minutes: int = Field(15, alias="SYNC_INTERVAL_MINUTES")
    database_url: str = Field("sqlite:///./subscription_eater.db", alias="DATABASE_URL")

    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
