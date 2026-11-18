"""Application settings, read from environment variables (and an optional .env file)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

API_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: Literal["claude", "ollama"] = "claude"
    claude_model: str = "claude-haiku-5-5"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    db_path: Path = API_ROOT / "reports.db"

    rate_limit_per_hour: int = 20
    rate_limit_per_day: int = 200


@lru_cache
def get_settings() -> Settings:
    return Settings()
