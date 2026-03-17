# ChatBridge

Connect any LLM to any messaging platform with a unified message routing architecture.

## Features

- **Platform Adapters**: Telegram, Discord, Slack, WhatsApp
- **LLM Providers**: OpenAI/GPT, Anthropic/Claude, local Ollama
- **Session Management**: Per-user conversation history with persistence
- **YAML Configuration**: Simple config file for all settings
- **Middleware Support**: Custom message processing pipeline
- **Multi-platform**: Run one bot across all platforms simultaneously

## Quick Start

```python
from chatbridge.bridge import ChatBridge
from chatbridge.platforms.telegram import TelegramAdapter
from chatbridge.llm.openai_provider import OpenAIProvider

bridge = ChatBridge()
bridge.register_platform("telegram", TelegramAdapter(token="YOUR_TOKEN"))
bridge.set_llm_provider(OpenAIProvider(api_key="YOUR_KEY"))

import asyncio
asyncio.run(bridge.start())
```

## Configuration

Copy `config.example.yml` to `config.yml` and fill in your credentials.

## Installation

```bash
pip install -e ".[all]"
```

## Testing

```bash
pip install -e ".[dev]"
pytest tests/
```

## License

MIT
