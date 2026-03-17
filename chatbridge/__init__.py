"""ChatBridge - Connect any LLM to any messaging platform."""
__version__ = "0.1.0"

from chatbridge.bridge import ChatBridge
from chatbridge.session import SessionManager

__all__ = ["ChatBridge", "SessionManager"]
