"""ChatBridge — unified message routing between platforms and LLMs."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from chatbridge.session import SessionManager
from chatbridge.config import BridgeConfig, load_config

logger = logging.getLogger(__name__)


@dataclass
class IncomingMessage:
    text: str
    user_id: str
    platform: str
    channel_id: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class OutgoingMessage:
    text: str
    user_id: str
    platform: str
    channel_id: str = ""
    metadata: dict = field(default_factory=dict)


class PlatformAdapter(ABC):
    """Abstract base for messaging platform adapters."""

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    @abstractmethod
    async def send_message(self, message):
        pass

    @abstractmethod
    def set_message_handler(self, handler):
        pass


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    async def generate(self, messages, **kwargs):
        pass


class ChatBridge:
    """Unified message routing between messaging platforms and LLM providers.

    Receives messages from any platform adapter, routes them through
    conversation history, sends to the configured LLM, and delivers
    the response back to the originating platform.
    """

    def __init__(self, config=None):
        self.config = config or BridgeConfig()
        self.session_manager = SessionManager(
            max_history=self.config.session.max_history,
            ttl_seconds=self.config.session.ttl_seconds,
            persist=self.config.session.persist,
            storage_path=self.config.session.storage_path,
        )
        self._platforms = {}
        self._llm_provider = None
        self._middleware = []

    def register_platform(self, name, adapter):
        """Register a messaging platform adapter."""
        self._platforms[name] = adapter
        adapter.set_message_handler(self._handle_message)
        logger.info(f"Registered platform: {name}")

    def set_llm_provider(self, provider):
        """Set the LLM provider for generating responses."""
        self._llm_provider = provider
        logger.info(f"LLM provider set: {type(provider).__name__}")

    def add_middleware(self, func):
        """Add middleware that processes messages before LLM call.

        Middleware receives (incoming_message, session_messages) and returns
        modified session_messages or None to skip LLM call.
        """
        self._middleware.append(func)

    async def _handle_message(self, incoming):
        """Core message handling pipeline."""
        logger.info(f"[{incoming.platform}] Message from {incoming.user_id}: {incoming.text[:50]}...")

        # Add user message to session
        self.session_manager.add_message(incoming.user_id, incoming.platform, "user", incoming.text)

        # Get conversation context
        messages = self.session_manager.get_context_messages(
            incoming.user_id, incoming.platform,
            system_prompt=self.config.llm.system_prompt)

        # Apply middleware
        for mw in self._middleware:
            result = mw(incoming, messages)
            if result is None:
                return  # Middleware cancelled the request
            messages = result

        # Generate LLM response
        if self._llm_provider is None:
            response_text = "I'm not connected to an LLM provider. Please configure one."
        else:
            try:
                response_text = await self._llm_provider.generate(messages,
                                                                    temperature=self.config.llm.temperature,
                                                                    max_tokens=self.config.llm.max_tokens)
            except Exception as e:
                logger.error(f"LLM error: {e}")
                response_text = "Sorry, I encountered an error generating a response."

        # Store assistant response
        self.session_manager.add_message(incoming.user_id, incoming.platform, "assistant", response_text)

        # Send response back
        outgoing = OutgoingMessage(text=response_text, user_id=incoming.user_id,
                                   platform=incoming.platform, channel_id=incoming.channel_id)

        platform = self._platforms.get(incoming.platform)
        if platform:
            await platform.send_message(outgoing)
        else:
            logger.warning(f"No platform adapter for: {incoming.platform}")

        return outgoing

    async def start(self):
        """Start all registered platform adapters."""
        for name, adapter in self._platforms.items():
            logger.info(f"Starting platform: {name}")
            await adapter.start()

    async def stop(self):
        """Stop all registered platform adapters."""
        for name, adapter in self._platforms.items():
            logger.info(f"Stopping platform: {name}")
            await adapter.stop()

    def handle_message_sync(self, incoming):
        """Synchronous message handling for testing."""
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self._handle_message(incoming))
        finally:
            loop.close()
