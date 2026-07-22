"""
Ollama API provider for CodeForge.

Calls a local Ollama instance for fully offline AI inference.
Slower on CPU but works without internet access.
"""

import os
import httpx

from server.providers.base import AIProvider


class OllamaProvider(AIProvider):
    """Local Ollama provider (offline fallback)."""

    BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    def __init__(self):
        self.default_model = "llama3"
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def generate(self, messages: list[dict], model: str | None = None) -> str:
        """Send chat messages to Ollama and return the response text."""
        client = await self._get_client()

        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        payload = {
            "model": model or self.default_model,
            "messages": ollama_messages,
            "stream": False,
        }

        response = await client.post(f"{self.BASE_URL}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]

    async def health_check(self) -> bool:
        """Check if Ollama is running locally."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.BASE_URL}/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
