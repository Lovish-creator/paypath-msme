from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "PayPath MSME"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./paypath.db"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    SECRET_KEY: str = "dev-insecure-secret-key-change-in-production-only"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ENABLE_DEMO_SEEDING: bool = False
    ALLOW_DEMO_RESET: bool = False
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB
    RBI_BANK_RATE_PERCENT: float = 6.75
    MSME_INTEREST_MULTIPLIER: float = 3.0
    STORAGE_LOCAL_DIR: str = "./backend/data"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def validate_production_configuration(self) -> None:
        """Validates that production environment variables meet security requirements."""
        if self.ENVIRONMENT.lower() == "production":
            if (
                not self.SECRET_KEY
                or self.SECRET_KEY == "dev-insecure-secret-key-change-in-production-only"
                or len(self.SECRET_KEY) < 32
            ):
                raise RuntimeError(
                    "FATAL SECURITY CONFIGURATION: Production deployment requires a secure, unpredictable "
                    "SECRET_KEY of at least 32 characters set via environment variable."
                )
            if self.ALLOW_DEMO_RESET:
                raise RuntimeError(
                    "FATAL SECURITY CONFIGURATION: ALLOW_DEMO_RESET must be False in production environments."
                )
            if self.ENABLE_DEMO_SEEDING:
                raise RuntimeError(
                    "FATAL SECURITY CONFIGURATION: ENABLE_DEMO_SEEDING must be False in production environments."
                )
            if "*" in self.cors_origins_list:
                raise RuntimeError(
                    "FATAL SECURITY CONFIGURATION: Wildcard CORS origins are forbidden in production with credentials."
                )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

