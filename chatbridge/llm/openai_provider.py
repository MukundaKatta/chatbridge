"""OpenAI/GPT LLM provider."""

import logging
from typing import Any, Optional

from chatbridge.bridge import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """Generate responses using OpenAI's API (GPT-4, GPT-3.5, etc.)."""

    def __init__(self, api_key=None, model="gpt-4o-mini", base_url=None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        if self._client is None:
            import openai
            kwargs = {}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = openai.AsyncOpenAI(**kwargs)
        return self._client

    async def generate(self, messages, **kwargs):
        client = self._get_client()
        try:
            response = await client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
