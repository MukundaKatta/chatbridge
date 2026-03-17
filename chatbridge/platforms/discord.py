"""Discord adapter using discord.py."""

import logging
from typing import Callable, Optional

from chatbridge.bridge import PlatformAdapter, IncomingMessage, OutgoingMessage

logger = logging.getLogger(__name__)


class DiscordAdapter(PlatformAdapter):
    """Connect ChatBridge to Discord using discord.py."""

    def __init__(self, token, command_prefix="!", allowed_channels=None):
        self.token = token
        self.command_prefix = command_prefix
        self.allowed_channels = set(allowed_channels) if allowed_channels else None
        self._handler = None
        self._client = None
        self._channel_cache = {}

    def set_message_handler(self, handler):
        self._handler = handler

    async def start(self):
        try:
            import discord

            intents = discord.Intents.default()
            intents.message_content = True
            self._client = discord.Client(intents=intents)

            @self._client.event
            async def on_ready():
                logger.info(f"Discord bot ready as {self._client.user}")

            @self._client.event
            async def on_message(message):
                if message.author == self._client.user:
                    return
                if self.allowed_channels and str(message.channel.id) not in self.allowed_channels:
                    return
                if message.content.startswith(self.command_prefix):
                    text = message.content[len(self.command_prefix):].strip()
                else:
                    # Only respond to mentions or DMs
                    if self._client.user not in message.mentions and not isinstance(message.channel, discord.DMChannel):
                        return
                    text = message.content.replace(f"<@{self._client.user.id}>", "").strip()

                if not text:
                    return

                self._channel_cache[str(message.channel.id)] = message.channel

                incoming = IncomingMessage(
                    text=text, user_id=str(message.author.id), platform="discord",
                    channel_id=str(message.channel.id),
                    metadata={"username": str(message.author), "guild": str(message.guild) if message.guild else "DM"})

                if self._handler:
                    await self._handler(incoming)

            await self._client.start(self.token)

        except ImportError:
            logger.error("discord.py not installed. Run: pip install discord.py")

    async def stop(self):
        if self._client:
            await self._client.close()

    async def send_message(self, message):
        if not self._client:
            return
        channel = self._channel_cache.get(message.channel_id)
        if channel:
            try:
                # Split long messages
                text = message.text
                while text:
                    chunk = text[:2000]
                    text = text[2000:]
                    await channel.send(chunk)
            except Exception as e:
                logger.error(f"Failed to send Discord message: {e}")
