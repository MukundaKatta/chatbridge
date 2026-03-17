"""Telegram adapter using python-telegram-bot."""

import logging
from typing import Any, Callable, Optional

from chatbridge.bridge import PlatformAdapter, IncomingMessage, OutgoingMessage

logger = logging.getLogger(__name__)


class TelegramAdapter(PlatformAdapter):
    """Connect ChatBridge to Telegram using python-telegram-bot."""

    def __init__(self, token, allowed_users=None):
        self.token = token
        self.allowed_users = set(allowed_users) if allowed_users else None
        self._handler = None
        self._app = None

    def set_message_handler(self, handler):
        self._handler = handler

    async def start(self):
        try:
            from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters

            self._app = ApplicationBuilder().token(self.token).build()

            async def on_message(update, context):
                if not update.message or not update.message.text:
                    return
                user_id = str(update.message.from_user.id)
                if self.allowed_users and user_id not in self.allowed_users:
                    return

                incoming = IncomingMessage(
                    text=update.message.text, user_id=user_id, platform="telegram",
                    channel_id=str(update.message.chat_id),
                    metadata={"username": update.message.from_user.username or "",
                              "first_name": update.message.from_user.first_name or ""})

                if self._handler:
                    await self._handler(incoming)

            async def on_start(update, context):
                await update.message.reply_text("Hello! I'm ready to chat. Send me a message!")

            async def on_clear(update, context):
                await update.message.reply_text("Conversation cleared!")

            self._app.add_handler(CommandHandler("start", on_start))
            self._app.add_handler(CommandHandler("clear", on_clear))
            self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

            logger.info("Telegram bot starting...")
            await self._app.initialize()
            await self._app.start()
            await self._app.updater.start_polling()

        except ImportError:
            logger.error("python-telegram-bot not installed. Run: pip install python-telegram-bot")

    async def stop(self):
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()

    async def send_message(self, message):
        if not self._app:
            logger.warning("Telegram app not initialized")
            return
        try:
            await self._app.bot.send_message(chat_id=message.channel_id, text=message.text)
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
