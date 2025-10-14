from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import json


class Settings(BaseSettings):
    """Application settings and configuration."""

    # Application
    APP_NAME: str = "Property Listing Service"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:UV7bDpcLAaazRFsqVf16@eygardatabase-instance.cj480emqyx9y.me-central-1.rds.amazonaws.com:5432/dev_eygar_property_listing"

    # Auth Service Integration
    AUTH_SERVICE_URL: str = "http://127.0.0.1:8000"
    JWT_SECRET_KEY: str = "abcdefgh"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: str = '["http://localhost:3000","http://127.0.0.1:3000"]'

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6380/0"
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # File Upload
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif", "webp"}

    # Local Storage (Development)
    MEDIA_DIR: str = "media/images"
    BASE_URL: str = "http://127.0.0.1:8001"

    # AWS S3 (Production)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    S3_FOLDER: str = "property-images"
    CLOUDFRONT_DOMAIN: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from JSON string."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            try:
                return json.loads(self.ALLOWED_ORIGINS)
            except json.JSONDecodeError:
                return [self.ALLOWED_ORIGINS]
        return self.ALLOWED_ORIGINS


settings = Settings()
