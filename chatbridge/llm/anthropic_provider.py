"""Anthropic/Claude LLM provider."""

import logging
from typing import Any, Optional

from chatbridge.bridge import LLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Generate responses using Anthropic's Claude API."""

    def __init__(self, api_key=None, model="claude-sonnet-4-20250514"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic
            kwargs = {}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            self._client = anthropic.AsyncAnthropic(**kwargs)
        return self._client

    async def generate(self, messages, **kwargs):
        client = self._get_client()

        # Extract system prompt
        system = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)

        try:
            response = await client.messages.create(
                model=kwargs.get("model", self.model),
                system=system,
                messages=chat_messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
