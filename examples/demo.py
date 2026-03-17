"""Example: Set up a Telegram bot with OpenAI."""

import asyncio
from chatbridge.bridge import ChatBridge, IncomingMessage
from chatbridge.config import BridgeConfig, LLMConfig, SessionConfig
from chatbridge.session import SessionManager


def main():
    print("=== ChatBridge Demo ===\n")

    # Configure the bridge
    config = BridgeConfig(
        llm=LLMConfig(provider="openai", model="gpt-4o-mini",
                       system_prompt="You are a friendly assistant. Keep responses concise."),
        session=SessionConfig(max_history=20, ttl_seconds=1800),
    )

    bridge = ChatBridge(config=config)

    # Demonstrate session management
    print("--- Session Management ---")
    sm = bridge.session_manager

    sm.add_message("user123", "telegram", "user", "Hello! What is Python?")
    sm.add_message("user123", "telegram", "assistant", "Python is a versatile programming language!")
    sm.add_message("user123", "telegram", "user", "Can you tell me more?")

    history = sm.get_history("user123", "telegram")
    print(f"Session has {len(history)} messages:")
    for msg in history:
        print(f"  [{msg['role']}] {msg['content'][:60]}")

    context = sm.get_context_messages("user123", "telegram", system_prompt=config.llm.system_prompt)
    print(f"\nContext for LLM ({len(context)} messages including system prompt)")
    print(f"Active sessions: {len(sm.list_sessions())}")

    # Demonstrate sync message handling (without real LLM)
    print("\n--- Message Handling ---")
    incoming = IncomingMessage(text="What is the capital of France?", user_id="demo_user",
                               platform="test", channel_id="test_channel")
    print(f"Incoming: [{incoming.platform}] {incoming.user_id}: {incoming.text}")

    # In production, you would:
    # 1. Register platform adapters (TelegramAdapter, DiscordAdapter, etc.)
    # 2. Set an LLM provider (OpenAIProvider, AnthropicProvider, etc.)
    # 3. Call bridge.start() to begin processing messages

    print("\n--- Configuration ---")
    print(f"LLM: {config.llm.provider}/{config.llm.model}")
    print(f"System prompt: {config.llm.system_prompt[:50]}...")
    print(f"Session TTL: {config.session.ttl_seconds}s")
    print(f"Max history: {config.session.max_history}")

    print("\nTo run a real bot:")
    print("  1. Set environment variables (OPENAI_API_KEY, TELEGRAM_TOKEN)")
    print("  2. Create config.yml from config.example.yml")
    print("  3. Run: python -m chatbridge")


if __name__ == "__main__":
    main()
