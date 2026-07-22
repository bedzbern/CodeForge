"""
Abstract base class for AI providers.

Every backend (Groq, Ollama, etc.) must implement this interface.
"""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract base class for AI backends."""

    @abstractmethod
    async def generate(self, messages: list[dict], model: str | None = None) -> str:
        """Send a list of chat messages and return the AI response text."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable."""
        ...
