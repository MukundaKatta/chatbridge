# chatbridge

**Agentic IM chatbot infrastructure — integrates WhatsApp, Telegram, Discord, Slack with any LLM**

![Build](https://img.shields.io/badge/build-passing-brightgreen) ![License](https://img.shields.io/badge/license-proprietary-red)

## Install
```bash
pip install -e ".[dev]"
```

## Quick Start
```python
from src.core import Chatbridge
 instance = Chatbridge()
r = instance.connect_platform(input="test")
```

## CLI
```bash
python -m src status
python -m src run --input "data"
```

## API
| Method | Description |
|--------|-------------|
| `connect_platform()` | Connect platform |
| `route_message()` | Route message |
| `manage_session()` | Manage session |
| `switch_llm()` | Switch llm |
| `get_history()` | Get history |
| `disconnect()` | Disconnect |
| `get_stats()` | Get stats |
| `reset()` | Reset |

## Test
```bash
pytest tests/ -v
```

## License
(c) 2026 Officethree Technologies. All Rights Reserved.
