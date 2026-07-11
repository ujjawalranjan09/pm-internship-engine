"""PM Internship Smart Allocation Engine - Configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "PM Internship Allocation Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pm_internship"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # OpenSearch
    OPENSEARCH_URL: str = "https://localhost:9200"
    OPENSEARCH_INDEX: str = "opportunities"
    OPENSEARCH_USER: str = "admin"
    OPENSEARCH_PASSWORD: str = "admin"

    # ML
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"

    # Matching
    MATCH_TOP_K: int = 50
    MATCH_MIN_SCORE: float = 0.1
    MATCH_WEIGHTS: dict[str, float] = {
        "skill_similarity": 0.30,
        "location_preference": 0.20,
        "education_fit": 0.15,
        "sector_interest": 0.15,
        "social_equity": 0.10,
        "profile_completeness": 0.10,
    }

    # Fairness
    FAIRNESS_ENABLED: bool = True
    FAIRNESS_SOCIAL_CATEGORY_BOOST: float = 0.15
    FAIRNESS_RURAL_BOOST: float = 0.10
    FAIRNESS_GENDER_PARITY_TARGET: float = 0.40

    # CORS
    ALLOWED_HOSTS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
