from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "NU Learning"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    SYNC_DATABASE_URL: str  # for alembic and celery

    REDIS_URL: str = "redis://localhost:6379/0"

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    AWS_SECRET_KEY: str
    AWS_ACCESS_KEY: str
    AWS_BUCKET_NAME: str = ""
    AWS_REGION: str = ""

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    OPENAI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=[Path(__file__).resolve().parent.parent / ".env",], extra="ignore"
    )


settings = Settings()
