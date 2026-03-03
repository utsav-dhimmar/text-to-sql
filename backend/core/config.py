from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All values can be overridden in .env file.
    """

    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/analytics_db",
        description="PostgreSQL connection string. Auto-upgrades to +asyncpg if missing.",
    )

    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for caching and session management.",
    )

    JWT_SECRET: str = Field(
        default="your-super-long-random-secret-32-plus-characters",
        description="Secret key for signing JWT tokens (use a long random string, min 32 chars).",
    )

    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm used for JWT signing (HS256, HS384, HS512).",
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15,
        description="Access token expiration time in minutes.",
    )

    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration time in days.",
    )

    # MAY BE ANY OTHER
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key for LLM integrations (format: sk-...).",
    )

    ENV: str = Field(
        default="development",
        description="Runtime environment (development, staging, production).",
    )

    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for CORS and redirects.",
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def convert_to_asyncpg(cls, v: str) -> str:
        """
        Convert synchronous PostgreSQL URL to asyncpg format.
        postgresql:// -> postgresql+asyncpg://
        """
        return v.replace("postgresql://", "postgresql+asyncpg://")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached Settings instance.
    Use this instead of directly instantiating Settings.
    """
    return Settings()
