from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ──
    APP_NAME: str = "英语宝典"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-must-be-32-chars+"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # ── Database ──
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/english_treasure"
    )

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── DeepSeek ──
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-v4-flash"

    # ── 讯飞语音评测 ──
    IFLYTEK_APP_ID: str = ""
    IFLYTEK_API_KEY: str = ""
    IFLYTEK_API_SECRET: str = ""
    IFLYTEK_BASE_URL: str = "https://ise-api.xfyun.cn/v2/open-ise"

    # ── PaddleOCR ──
    PADDLEOCR_API_URL: str = ""
    PADDLEOCR_API_KEY: str = ""

    # ── S3 / MinIO ──
    S3_ENDPOINT: str = "localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "english-treasure"


settings = Settings()
