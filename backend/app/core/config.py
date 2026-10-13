from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "PayPath MSME"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./paypath.db"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    SECRET_KEY: str = "paypath-msme-production-secure-key-2026-sliet"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ENABLE_DEMO_SEEDING: bool = False
    RBI_BANK_RATE_PERCENT: float = 6.75
    MSME_INTEREST_MULTIPLIER: float = 3.0
    STORAGE_LOCAL_DIR: str = "./backend/data"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

