from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from nutrack.semester import normalize_term


class Settings(BaseSettings):
    APP_NAME: str = "nutrack"
    API_V1_PREFIX: str = "/v1"

    DATABASE_URL: str
    SYNC_DATABASE_URL: str

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
    AWS_REGION: str = "us-east-1"
    AWS_ENDPOINT_URL: str = ""
    AWS_PUBLIC_ENDPOINT_URL: str = ""
    AWS_S3_FORCE_PATH_STYLE: bool = True
    MATERIAL_UPLOAD_STAGING_DIR: str = "/tmp/material_uploads"
    MATERIAL_PRESIGNED_URL_TTL_SECONDS: int = 900

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    OPENAI_API_KEY: str
    CURRENT_TERM: str = "Spring"
    CURRENT_YEAR: int = 2026

    RESEND_API_KEY: str = ""

    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=[Path(__file__).resolve().parents[2] / ".env"],
        extra="ignore",
    )

    @field_validator("CURRENT_TERM")
    @classmethod
    def validate_current_term(cls, value: str) -> str:
        return normalize_term(value)


settings = Settings()
