import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "mysql+aiomysql://root:rootpassword@db:3306/fastapi_db"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "supersecretkey_change_in_production_min_32_characters_long_1234",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DOCS_USER: str = os.getenv("DOCS_USER", "admin")
    DOCS_PASS: str = os.getenv("DOCS_PASS", "admin")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()