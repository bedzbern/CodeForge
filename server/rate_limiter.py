"""
Per-IP rate limiter for CodeForge.

Enforces a minimum interval between requests from the same IP.
Default: 1 request per 30 seconds.

Includes automatic cleanup to prevent unbounded memory growth.
"""

import time
import threading


class RateLimiter:
    """Simple in-memory per-IP rate limiter with automatic cleanup."""

    def __init__(self, min_interval_seconds: float = 30.0, cleanup_interval: float = 600.0):
        self.min_interval = min_interval_seconds
        self._cleanup_interval = cleanup_interval
        self._last_request: dict[str, float] = {}
        self._last_cleanup = time.time()

    def is_allowed(self, ip_address: str) -> bool:
        """Return True if the IP is allowed to make a request now."""
        self._maybe_cleanup()

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

    def _maybe_cleanup(self):
        """Run cleanup if enough time has passed since the last run."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        self._last_cleanup = now
        self.cleanup()

    def cleanup(self, max_age: float = 3600.0):
        """Remove entries older than max_age seconds to prevent memory growth."""
        now = time.time()
        expired = [ip for ip, ts in self._last_request.items() if now - ts > max_age]
        for ip in expired:
            del self._last_request[ip]
        if expired:
            print(f"[CodeForge] Rate limiter cleanup: removed {len(expired)} stale entries")


rate_limiter = RateLimiter(min_interval_seconds=30.0, cleanup_interval=600.0)
