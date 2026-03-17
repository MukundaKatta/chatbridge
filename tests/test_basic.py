"""Tests for ChatBridge modules."""

import time
import pytest
from chatbridge.bridge import ChatBridge, IncomingMessage, OutgoingMessage, PlatformAdapter, LLMProvider
from chatbridge.session import SessionManager
from chatbridge.config import load_config, BridgeConfig, LLMConfig


class MockPlatform(PlatformAdapter):
    def __init__(self):
        self._handler = None
        self.sent_messages = []
        self.started = False

    async def start(self):
        self.started = True

    async def stop(self):
        self.started = False

    async def send_message(self, message):
        self.sent_messages.append(message)

    def set_message_handler(self, handler):
        self._handler = handler


class MockLLM(LLMProvider):
    async def generate(self, messages, **kwargs):
        last_msg = messages[-1]["content"] if messages else ""
        return f"Echo: {last_msg}"


class TestSessionManager:
    def test_create_session(self):
        sm = SessionManager()
        session = sm.get_or_create("user1", "telegram")
        assert session.user_id == "user1"
        assert session.platform == "telegram"

    def test_add_and_get_history(self):
        sm = SessionManager()
        sm.add_message("u1", "tg", "user", "hello")
        sm.add_message("u1", "tg", "assistant", "hi there")
        history = sm.get_history("u1", "tg")
        assert len(history) == 2
        assert history[0]["role"] == "user"

    def test_context_messages_with_system_prompt(self):
        sm = SessionManager()
        sm.add_message("u1", "tg", "user", "hi")
        msgs = sm.get_context_messages("u1", "tg", system_prompt="You are helpful.")
        assert msgs[0]["role"] == "system"
        assert msgs[1]["role"] == "user"

    def test_clear_session(self):
        sm = SessionManager()
        sm.add_message("u1", "tg", "user", "hello")
        sm.clear_session("u1", "tg")
        assert len(sm.get_history("u1", "tg")) == 0

    def test_max_history(self):
        sm = SessionManager(max_history=5)
        for i in range(10):
            sm.add_message("u1", "tg", "user", f"msg {i}")
        assert len(sm.get_history("u1", "tg")) == 5

    def test_ttl_expiry(self):
        sm = SessionManager(ttl_seconds=0)
        sm.add_message("u1", "tg", "user", "old message")
        time.sleep(0.1)
        session = sm.get_or_create("u1", "tg")
        assert len(session.messages) == 0

    def test_list_sessions(self):
        sm = SessionManager()
        sm.add_message("u1", "tg", "user", "hi")
        sm.add_message("u2", "discord", "user", "hey")
        sessions = sm.list_sessions()
        assert len(sessions) == 2

    def test_persist(self, tmp_path):
        sm = SessionManager(persist=True, storage_path=str(tmp_path))
        sm.add_message("u1", "tg", "user", "persisted message")
        # Reload
        sm2 = SessionManager(persist=True, storage_path=str(tmp_path))
        history = sm2.get_history("u1", "tg")
        assert len(history) == 1
        assert history[0]["content"] == "persisted message"


class TestChatBridge:
    def test_register_platform(self):
        bridge = ChatBridge()
        platform = MockPlatform()
        bridge.register_platform("test", platform)
        assert "test" in bridge._platforms

    def test_set_llm(self):
        bridge = ChatBridge()
        llm = MockLLM()
        bridge.set_llm_provider(llm)
        assert bridge._llm_provider is not None

    @pytest.mark.asyncio
    async def test_message_flow(self):
        bridge = ChatBridge()
        platform = MockPlatform()
        llm = MockLLM()
        bridge.register_platform("test", platform)
        bridge.set_llm_provider(llm)

        incoming = IncomingMessage(text="Hello", user_id="u1", platform="test", channel_id="ch1")
        result = await bridge._handle_message(incoming)

        assert result is not None
        assert "Echo: Hello" in result.text
        assert len(platform.sent_messages) == 1

    def test_middleware(self):
        bridge = ChatBridge()
        called = []

        def middleware(msg, messages):
            called.append(True)
            return messages

        bridge.add_middleware(middleware)
        assert len(bridge._middleware) == 1


class TestConfig:
    def test_default_config(self):
        config = BridgeConfig()
        assert config.llm.provider == "openai"
        assert config.session.max_history == 50

    def test_load_missing_file(self):
        config = load_config("nonexistent.yml")
        assert isinstance(config, BridgeConfig)
