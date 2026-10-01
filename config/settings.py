from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Multi-Agent Research System"
    app_version: str = "0.1.0"
    debug: bool = True

    model_provider: str = "openrouter"
    model_name: str = "openai/gpt-4o-mini"

    max_agent_steps: int = 8
    max_retries: int = 2
    request_timeout: int = 30

    openrouter_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()