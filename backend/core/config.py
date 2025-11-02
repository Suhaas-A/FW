from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # backend/
ENV_PATH = BASE_DIR.parent / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str

    API_PREFIX: str = "/api"
    DEBUG: bool = True

    ALLOWED_ORIGINS: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return v.split(",") if v else []

    class Config:
        env_file = '.env'
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
