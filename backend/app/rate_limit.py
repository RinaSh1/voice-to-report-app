"""Usage limit for the public demo, so strangers can't use up the Claude credit.

- Per visitor: RATE_LIMIT_PER_HOUR reports per hour (default 20)
- In total:    RATE_LIMIT_PER_DAY reports per day for everyone together (default 200)

Kept in memory: simple, and enough for one small server. It resets when the server restarts.
"""

import os
import time
from collections import deque
from collections.abc import Callable

from fastapi import HTTPException, Request

HOUR = 3600
DAY = 24 * HOUR


class RateLimiter:
    def __init__(self, per_hour: int, per_day: int, clock: Callable[[], float] = time.monotonic) -> None:
        self.per_hour = per_hour
        self.per_day = per_day
        self._clock = clock
        self._visitors: dict[str, deque[float]] = {}
        self._everyone: deque[float] = deque()

    def check(self, visitor: str) -> None:
        """Count one request, or raise 429 if a limit is reached."""
        now = self._clock()
        mine = self._visitors.setdefault(visitor, deque())
        _forget_older_than(mine, now - HOUR)
        _forget_older_than(self._everyone, now - DAY)

        if len(self._everyone) >= self.per_day:
            raise HTTPException(429, "The demo has reached today's limit. Please try again tomorrow.")
        if len(mine) >= self.per_hour:
            raise HTTPException(429, f"Limit of {self.per_hour} reports per hour reached. Please try again later.")

        mine.append(now)
        self._everyone.append(now)


def _forget_older_than(times: deque[float], cutoff: float) -> None:
    while times and times[0] <= cutoff:
        times.popleft()


def visitor_id(request: Request) -> str:
    """The visitor's IP. Behind a host like Render, the real IP is the first one in X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


limiter = RateLimiter(
    per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "20")),
    per_day=int(os.getenv("RATE_LIMIT_PER_DAY", "200")),
)


def limit_usage(request: Request) -> None:
    """FastAPI dependency for routes that call the LLM."""
    limiter.check(visitor_id(request))
