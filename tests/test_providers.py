"""
Tests for AI provider abstractions.

Covers:
- MockAIProvider returns expected responses
- Provider health check
- Message format validation
"""

import pytest
from unittest.mock import AsyncMock

from server.providers.base import AIProvider
from tests.conftest import MockAIProvider


class TestMockAIProvider:
    def test_generate_returns_response(self):
        provider = MockAIProvider(response="Test response")
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            provider.generate([{"role": "user", "content": "Hello"}])
        )
        assert result == "Test response"

    def test_generate_stores_messages(self):
        provider = MockAIProvider()
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"},
        ]
        import asyncio
        asyncio.get_event_loop().run_until_complete(provider.generate(messages))
        assert provider.last_messages == messages

    def test_health_check_returns_true(self):
        provider = MockAIProvider()
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(provider.health_check())
        assert result is True

    def test_provider_is_abstract(self):
        """Cannot instantiate base AIProvider directly."""
        with pytest.raises(TypeError):
            AIProvider()
