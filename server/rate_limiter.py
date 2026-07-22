"""
Per-IP rate limiter for CodeForge.

Enforces a minimum interval between requests from the same IP.
Default: 1 request per 30 seconds.
"""

import time


class RateLimiter:
    """Simple in-memory per-IP rate limiter."""

    def __init__(self, min_interval_seconds: float = 30.0):
        self.min_interval = min_interval_seconds
        self._last_request: dict[str, float] = {}

    def is_allowed(self, ip_address: str) -> bool:
        """Return True if the IP is allowed to make a request now."""
        now = time.time()
        last = self._last_request.get(ip_address, 0.0)

        if now - last >= self.min_interval:
            self._last_request[ip_address] = now
            return True

        return False

    def time_until_allowed(self, ip_address: str) -> float:
        """Return seconds remaining until the IP can make another request."""
        now = time.time()
        last = self._last_request.get(ip_address, 0.0)
        elapsed = now - last
        remaining = self.min_interval - elapsed
        return max(0.0, remaining)

    def cleanup(self, max_age: float = 3600.0):
        """Remove entries older than max_age seconds to prevent memory growth."""
        now = time.time()
        expired = [ip for ip, ts in self._last_request.items() if now - ts > max_age]
        for ip in expired:
            del self._last_request[ip]


rate_limiter = RateLimiter(min_interval_seconds=30.0)
