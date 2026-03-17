"""YAML-based configuration for ChatBridge."""

import os
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: str = ""
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: str = "You are a helpful assistant."


@dataclass
class PlatformConfig:
    enabled: bool = True
    token: str = ""
    webhook_url: Optional[str] = None
    options: dict = field(default_factory=dict)


@dataclass
class SessionConfig:
    max_history: int = 50
    ttl_seconds: int = 3600
    persist: bool = False
    storage_path: str = "./sessions"


@dataclass
class BridgeConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    platforms: dict = field(default_factory=dict)
    session: SessionConfig = field(default_factory=SessionConfig)
    log_level: str = "INFO"


def load_config(path="config.yml"):
    """Load configuration from a YAML file."""
    try:
        import yaml
        with open(path, "r") as f:
            raw = yaml.safe_load(f) or {}
    except (ImportError, FileNotFoundError):
        raw = {}

    llm_raw = raw.get("llm", {})
    llm = LLMConfig(
        provider=llm_raw.get("provider", os.environ.get("LLM_PROVIDER", "openai")),
        model=llm_raw.get("model", os.environ.get("LLM_MODEL", "gpt-4o-mini")),
        api_key=llm_raw.get("api_key", os.environ.get("OPENAI_API_KEY", "")),
        base_url=llm_raw.get("base_url"),
        temperature=llm_raw.get("temperature", 0.7),
        max_tokens=llm_raw.get("max_tokens", 1000),
        system_prompt=llm_raw.get("system_prompt", "You are a helpful assistant."),
    )

    platforms = {}
    for name, pconf in raw.get("platforms", {}).items():
        platforms[name] = PlatformConfig(
            enabled=pconf.get("enabled", True),
            token=pconf.get("token", os.environ.get(f"{name.upper()}_TOKEN", "")),
            webhook_url=pconf.get("webhook_url"),
            options=pconf.get("options", {}),
        )

    sess_raw = raw.get("session", {})
    session = SessionConfig(
        max_history=sess_raw.get("max_history", 50),
        ttl_seconds=sess_raw.get("ttl_seconds", 3600),
        persist=sess_raw.get("persist", False),
        storage_path=sess_raw.get("storage_path", "./sessions"),
    )

    return BridgeConfig(llm=llm, platforms=platforms, session=session,
                        log_level=raw.get("log_level", "INFO"))
