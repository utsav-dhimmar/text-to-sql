from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All values can be overridden in .env file.
    """

    # Database Configuration
    POSTGRES_USER: str = Field(default="postgres", alias="DB_USER")
    POSTGRES_PASSWORD: str = Field(default="", alias="DB_PASSWORD")
    POSTGRES_DB: str = Field(default="nifty500", alias="DB_NAME")
    POSTGRES_HOST: str = Field(default="localhost", alias="DB_HOST")
    POSTGRES_PORT: str = Field(default="5432", alias="DB_PORT")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """
        Dynamically construct the asyncpg connection string.
        """
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @computed_field
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """
        Synchronous psycopg2 connection string for AG2 tools.
        """
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for caching and session management.",
    )

    # Security Configuration
    JWT_SECRET: str = Field(
        default="your-super-long-random-secret-32-plus-characters",
        description="Secret key for signing JWT tokens (use a long random string, min 32 chars).",
    )

    SESSION_SECRET: str = Field(
        default="your-session-secret-key",
        description="Secret key for session middleware.",
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

    # LLM Integrations
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key for LLM integrations (format: sk-...).",
    )

    # Application Configuration
    ENV: str = Field(
        default="development",
        description="Runtime environment (development, staging, production).",
    )

    FRONTEND_URL: str = Field(
        default="http://localhost:5173",
        description="Frontend URL for CORS and redirects.",
    )

    # Super Admin Configuration
    SUPER_ADMIN_EMAIL: str = Field(
        default="",
        description="Initial Super Admin email address.",
    )
    SUPER_ADMIN_PASSWORD: str = Field(
        default="",
        description="Initial Super Admin password.",
    )

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth Client ID")
    GOOGLE_CLIENT_SECRET: str = Field(
        default="", description="Google OAuth Client Secret"
    )
    GOOGLE_CONF_URL: str = Field(
        default="https://accounts.google.com/.well-known/openid-configuration",
        description="Google OpenID configuration URL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        populate_by_name=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached Settings instance.
    Use this instead of directly instantiating Settings.
    """
    return Settings()
