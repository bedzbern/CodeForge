"""
Groq API provider for CodeForge.

Uses httpx to make async requests to the Groq cloud API (free tier).
Requires GROQ_API_KEY environment variable.
"""

import os
import httpx

from server.providers.base import AIProvider


class GroqProvider(AIProvider):
    """Groq cloud API provider (free tier, fast inference)."""

    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY", "")
        self.default_model = "llama-3.3-70b-versatile"
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def generate(self, messages: list[dict], model: str | None = None, max_tokens: int = 512) -> str:
        """Send chat messages to Groq and return the response text."""
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY environment variable is not set")

        client = await self._get_client()
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = await client.post(self.BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def health_check(self) -> bool:
        """Check if Groq API is reachable and the key is valid."""
        if not self.api_key:
            return False
        try:
            client = await self._get_client()
            response = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
