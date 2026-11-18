"""Sliding-window usage limits that protect the public demo's API credit.

- per visitor: `per_hour` requests per hour
- in total:    `per_day` requests per day, shared by everyone

State is kept in memory, which is enough for a single instance and resets on restart.
"""

import time
from collections import deque
from collections.abc import Callable

from app.core.errors import RateLimitExceeded

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
        """Record one request, or raise RateLimitExceeded."""
        now = self._clock()
        mine = self._visitors.setdefault(visitor, deque())
        _drop_older_than(mine, now - HOUR)
        _drop_older_than(self._everyone, now - DAY)

        if len(self._everyone) >= self.per_day:
            raise RateLimitExceeded("The demo has reached today's limit. Please try again tomorrow.")
        if len(mine) >= self.per_hour:
            raise RateLimitExceeded(f"Limit of {self.per_hour} reports per hour reached. Please try again later.")

        mine.append(now)
        self._everyone.append(now)


def _drop_older_than(times: deque[float], cutoff: float) -> None:
    while times and times[0] <= cutoff:
        times.popleft()
