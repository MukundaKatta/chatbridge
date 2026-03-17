"""Local Ollama LLM provider."""

import logging
from typing import Any, Optional

from chatbridge.bridge import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Generate responses using a local Ollama instance."""

    def __init__(self, model="llama3", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def generate(self, messages, **kwargs):
        try:
            import httpx

            url = f"{self.base_url}/api/chat"
            payload = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 1000),
                },
            }

            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")

        except ImportError:
            logger.error("httpx not installed. Run: pip install httpx")
            raise
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise

    async def list_models(self):
        """List available models on the Ollama instance."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return []
