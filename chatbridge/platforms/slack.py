"""Slack adapter using slack-sdk."""

import logging
from typing import Callable, Optional

from chatbridge.bridge import PlatformAdapter, IncomingMessage, OutgoingMessage

logger = logging.getLogger(__name__)


class SlackAdapter(PlatformAdapter):
    """Connect ChatBridge to Slack using slack-sdk and socket mode."""

    def __init__(self, bot_token, app_token, allowed_channels=None):
        self.bot_token = bot_token
        self.app_token = app_token
        self.allowed_channels = set(allowed_channels) if allowed_channels else None
        self._handler = None
        self._client = None
        self._socket = None

    def set_message_handler(self, handler):
        self._handler = handler

    async def start(self):
        try:
            from slack_sdk.web.async_client import AsyncWebClient
            from slack_sdk.socket_mode.aiohttp import SocketModeClient
            from slack_sdk.socket_mode.request import SocketModeRequest
            from slack_sdk.socket_mode.response import SocketModeResponse

            self._client = AsyncWebClient(token=self.bot_token)
            self._socket = SocketModeClient(app_token=self.app_token, web_client=self._client)

            async def handle_event(client, req):
                if req.type == "events_api":
                    event = req.payload.get("event", {})
                    if event.get("type") == "message" and "subtype" not in event:
                        channel = event.get("channel", "")
                        if self.allowed_channels and channel not in self.allowed_channels:
                            return

                        # Ignore bot's own messages
                        if event.get("bot_id"):
                            return

                        incoming = IncomingMessage(
                            text=event.get("text", ""), user_id=event.get("user", ""),
                            platform="slack", channel_id=channel,
                            metadata={"thread_ts": event.get("thread_ts", event.get("ts", ""))})

                        if self._handler:
                            await self._handler(incoming)

                    response = SocketModeResponse(envelope_id=req.envelope_id)
                    await client.send_socket_mode_response(response)

            self._socket.socket_mode_request_listeners.append(handle_event)
            logger.info("Slack bot starting...")
            await self._socket.connect()

        except ImportError:
            logger.error("slack-sdk not installed. Run: pip install slack-sdk aiohttp")

    async def stop(self):
        if self._socket:
            await self._socket.close()

    async def send_message(self, message):
        if not self._client:
            return
        try:
            thread_ts = message.metadata.get("thread_ts")
            await self._client.chat_postMessage(
                channel=message.channel_id, text=message.text,
                thread_ts=thread_ts if thread_ts else None)
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
