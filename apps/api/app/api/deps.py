"""FastAPI dependencies. Tests replace them with app.dependency_overrides."""

from functools import lru_cache
from pathlib import Path

from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.core.rate_limit import RateLimiter
from app.db.repository import ReportRepository
from app.llm import LLMProvider, create_provider


def get_llm(settings: Settings = Depends(get_settings)) -> LLMProvider:
    return create_provider(settings)


@lru_cache
def _repository(path: Path) -> ReportRepository:
    return ReportRepository(path)


def get_repository(settings: Settings = Depends(get_settings)) -> ReportRepository:
    return _repository(settings.db_path)


@lru_cache
def get_rate_limiter() -> RateLimiter:
    settings = get_settings()
    return RateLimiter(per_hour=settings.rate_limit_per_hour, per_day=settings.rate_limit_per_day)


def client_ip(request: Request) -> str:
    """Behind a proxy (e.g. Render) the real client IP is the first entry of X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def enforce_rate_limit(request: Request, limiter: RateLimiter = Depends(get_rate_limiter)) -> None:
    limiter.check(client_ip(request))
