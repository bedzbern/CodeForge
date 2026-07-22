"""
Tests for the rate limiter.

Covers:
- First request is allowed
- Second request within interval is blocked
- Request after interval is allowed
- Time until allowed calculation
- Cleanup removes old entries
"""

import time
import pytest

from server.rate_limiter import RateLimiter


class TestRateLimiter:
    def test_first_request_allowed(self):
        limiter = RateLimiter(min_interval_seconds=30.0)
        assert limiter.is_allowed("192.168.1.2") is True

    def test_second_request_within_interval_blocked(self):
        limiter = RateLimiter(min_interval_seconds=30.0)
        limiter.is_allowed("192.18.1.2")
        assert limiter.is_allowed("192.168.1.2") is False

    def test_request_after_interval_allowed(self):
        limiter = RateLimiter(min_interval_seconds=0.1)
        limiter.is_allowed("192.168.1.2")
        time.sleep(0.15)
        assert limiter.is_allowed("192.168.1.2") is True

    def test_different_ips_independent(self):
        limiter = RateLimiter(min_interval_seconds=30.0)
        limiter.is_allowed("192.168.1.2")
        assert limiter.is_allowed("192.168.1.3") is True

    def test_time_until_allowed(self):
        limiter = RateLimiter(min_interval_seconds=30.0)
        limiter.is_allowed("192.168.1.2")
        remaining = limiter.time_until_allowed("192.168.1.2")
        assert 29 < remaining <= 30

    def test_time_until_allowed_unknown_ip(self):
        limiter = RateLimiter(min_interval_seconds=30.0)
        remaining = limiter.time_until_allowed("192.168.1.99")
        assert remaining == 0.0

    def test_cleanup_removes_old_entries(self):
        limiter = RateLimiter(min_interval_seconds=30.0)
        limiter._last_request["192.168.1.2"] = time.time() - 7200
        limiter._last_request["192.168.1.3"] = time.time()
        limiter.cleanup(max_age=3600)
        assert "192.168.1.2" not in limiter._last_request
        assert "192.168.1.3" in limiter._last_request

    def test_cleanup_keeps_recent_entries(self):
        limiter = RateLimiter(min_interval_seconds=30.0)
        limiter._last_request["192.168.1.2"] = time.time() - 100
        limiter.cleanup(max_age=3600)
        assert "192.168.1.2" in limiter._last_request
