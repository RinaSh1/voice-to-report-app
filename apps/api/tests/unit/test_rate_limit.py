import pytest

from app.api.deps import get_llm, get_rate_limiter
from app.core.errors import RateLimitExceeded
from app.core.rate_limit import HOUR, RateLimiter
from app.main import app
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

    with pytest.raises(RateLimitExceeded):
        limiter.check("a")

    limiter.check("b")  # another visitor is not affected
    clock.now += HOUR + 1
    limiter.check("a")  # an hour later it works again


def test_daily_limit_is_shared_by_everyone():
    limiter = RateLimiter(per_hour=10, per_day=2, clock=Clock())
    limiter.check("a")
    limiter.check("b")
    with pytest.raises(RateLimitExceeded, match="today's limit"):
        limiter.check("c")


def test_generate_route_is_limited_per_forwarded_ip(client, valid_report):
    limiter = RateLimiter(per_hour=1, per_day=100, clock=Clock())
    app.dependency_overrides[get_rate_limiter] = lambda: limiter
    app.dependency_overrides[get_llm] = lambda: FakeProvider(valid_report, valid_report)

    def post(ip):
        return client.post("/api/reports/generate", json={"transcript": "x"}, headers={"x-forwarded-for": ip})

    assert post("1.2.3.4").status_code == 200
    second = post("1.2.3.4, 10.0.0.1")
    assert second.status_code == 429 and "per hour" in second.json()["detail"]
    assert post("5.6.7.8").status_code == 200
