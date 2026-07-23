"""
Shared test fixtures for CodeForge test suite.

Provides:
- In-memory SQLite test database (isolated per test)
- Pre-populated test students
- Mocked AI provider
- FastAPI test client with mocked dependencies
"""

import os
import sys
import pytest
from unittest.mock import AsyncMock, patch
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from server.database import Base, get_db
from server.models import Student, Rule, Session, Query
from server.providers.base import AIProvider
from server.rate_limiter import rate_limiter


class MockAIProvider(AIProvider):
    """Mock AI provider that returns predictable responses."""

    def __init__(self, response: str = "Mock AI response"):
        self.response = response
        self.last_messages = []

    async def generate(self, messages: list[dict], model: str | None = None, max_tokens: int = 512) -> str:
        self.last_messages = messages
        return self.response

    async def health_check(self) -> bool:
        return True

    async def close(self):
        pass


@pytest.fixture(scope="function")
def mock_ai():
    """Provide a fresh mock AI provider for each test."""
    return MockAIProvider(response="What does the return keyword do in Python?")


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()

    students = [
        Student(seat_number=1, ip_address="192.168.1.2", label="Student 1"),
        Student(seat_number=2, ip_address="192.168.1.3", label="Student 2"),
        Student(seat_number=3, ip_address="192.168.1.4", label="Student 3"),
    ]
    for s in students:
        session.add(s)

    rules = [
        Rule(student_ip="192.168.1.2", hint_level=1),
        Rule(student_ip="192.168.1.3", hint_level=2),
        Rule(student_ip="192.168.1.4", hint_level=3),
    ]
    for r in rules:
        session.add(r)

    session.commit()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(db_session, mock_ai):
    """Provide a FastAPI test client with mocked DB and AI provider."""
    from fastapi.testclient import TestClient
    from server.main import fastapi_app as app

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    app.state.active_session_id = None

    rate_limiter._last_request.clear()

    with TestClient(app, raise_server_exceptions=False) as c:
        app.state.ai_provider = mock_ai
        yield c

    app.dependency_overrides.clear()
