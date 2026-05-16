from typing import Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "PM Internship Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    ALLOWED_ORIGINS: list[str] = ["*"]
    MATCH_WEIGHTS: dict[str, Any] = {
        "skill_match": 0.4,
        "experience_match": 0.3,
        "preference_match": 0.3,
    }
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    MAX_MATCHES_PER_CANDIDATE: int = 10
    MIN_MATCH_SCORE: float = 0.5

    class Config:
        env_file = ".env"


settings = Settings()
