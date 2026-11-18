import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.llm import get_provider
from app.main import app
from app.rate_limit import HOUR, RateLimiter
from tests.conftest import FakeProvider


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_visitor_is_limited_per_hour_then_allowed_again():
    clock = Clock()
    limiter = RateLimiter(per_hour=2, per_day=100, clock=clock)
    limiter.check("a")
    limiter.check("a")

    with pytest.raises(HTTPException) as error:
        limiter.check("a")
    assert error.value.status_code == 429

    limiter.check("b")  # another visitor is not affected
    clock.now += HOUR + 1
    limiter.check("a")  # an hour later it works again


def test_daily_limit_is_shared_by_everyone():
    limiter = RateLimiter(per_hour=10, per_day=2, clock=Clock())
    limiter.check("a")
    limiter.check("b")
    with pytest.raises(HTTPException, match="today's limit"):
        limiter.check("c")


def test_generate_route_uses_the_limit_and_the_forwarded_ip(valid_report, monkeypatch):
    limiter = RateLimiter(per_hour=1, per_day=100, clock=Clock())
    monkeypatch.setattr("app.rate_limit.limiter", limiter)
    app.dependency_overrides[get_provider] = lambda: FakeProvider(valid_report, valid_report)
    client = TestClient(app)
    try:
        first = client.post("/api/reports/generate", json={"transcript": "x"}, headers={"x-forwarded-for": "1.2.3.4"})
        second = client.post("/api/reports/generate", json={"transcript": "x"}, headers={"x-forwarded-for": "1.2.3.4, 10.0.0.1"})
        other = client.post("/api/reports/generate", json={"transcript": "x"}, headers={"x-forwarded-for": "5.6.7.8"})
    finally:
        app.dependency_overrides.clear()

    assert first.status_code == 200
    assert second.status_code == 429 and "per hour" in second.json()["detail"]
    assert other.status_code == 200

