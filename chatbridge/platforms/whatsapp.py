"""WhatsApp adapter using webhook API (Meta Cloud API)."""

import logging
from typing import Callable, Optional

from chatbridge.bridge import PlatformAdapter, IncomingMessage, OutgoingMessage

logger = logging.getLogger(__name__)


class WhatsAppAdapter(PlatformAdapter):
    """Connect ChatBridge to WhatsApp via Meta Cloud API webhooks.

    Requires a FastAPI/Flask server to receive webhooks and the Meta
    WhatsApp Business API access token.
    """

    def __init__(self, access_token, phone_number_id, verify_token="chatbridge"):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.verify_token = verify_token
        self._handler = None
        self._app = None

    def set_message_handler(self, handler):
        self._handler = handler

    async def start(self):
        """Start webhook server for receiving WhatsApp messages."""
        try:
            from fastapi import FastAPI, Request, Response

            self._app = FastAPI()

            @self._app.get("/webhook")
            async def verify(request: Request):
                params = request.query_params
                mode = params.get("hub.mode")
                token = params.get("hub.verify_token")
                challenge = params.get("hub.challenge")
                if mode == "subscribe" and token == self.verify_token:
                    return Response(content=challenge, media_type="text/plain")
                return Response(status_code=403)

            @self._app.post("/webhook")
            async def receive(request: Request):
                body = await request.json()
                entries = body.get("entry", [])
                for entry in entries:
                    for change in entry.get("changes", []):
                        value = change.get("value", {})
                        messages = value.get("messages", [])
                        for msg in messages:
                            if msg.get("type") != "text":
                                continue
                            incoming = IncomingMessage(
                                text=msg["text"]["body"], user_id=msg["from"],
                                platform="whatsapp", channel_id=msg["from"],
                                metadata={"message_id": msg.get("id", ""),
                                          "timestamp": msg.get("timestamp", "")})
                            if self._handler:
                                await self._handler(incoming)
                return {"status": "ok"}

            logger.info("WhatsApp webhook server configured. Start with uvicorn.")

        except ImportError:
            logger.error("fastapi not installed. Run: pip install fastapi uvicorn")

    async def stop(self):
        pass

    async def send_message(self, message):
        """Send message via WhatsApp Cloud API."""
        try:
            import httpx
            url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
            headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
            payload = {
                "messaging_product": "whatsapp",
                "to": message.user_id,
                "type": "text",
                "text": {"body": message.text},
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    logger.error(f"WhatsApp send failed: {resp.text}")
        except ImportError:
            logger.error("httpx not installed. Run: pip install httpx")
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
