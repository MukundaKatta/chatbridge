"""SessionManager — per-user conversation history management."""

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Message:
    role: str          # user, assistant, system
    content: str
    timestamp: float = field(default_factory=time.time)
    platform: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class Session:
    user_id: str
    platform: str
    messages: list = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


class SessionManager:
    """Manage per-user conversation sessions with history and persistence."""

    def __init__(self, max_history=50, ttl_seconds=3600, persist=False, storage_path="./sessions"):
        self.max_history = max_history
        self.ttl_seconds = ttl_seconds
        self.persist = persist
        self.storage_path = storage_path
        self._sessions = {}

        if persist and storage_path:
            os.makedirs(storage_path, exist_ok=True)
            self._load_sessions()

    def _session_key(self, user_id, platform):
        return f"{platform}:{user_id}"

    def get_or_create(self, user_id, platform):
        key = self._session_key(user_id, platform)
        if key in self._sessions:
            session = self._sessions[key]
            if time.time() - session.last_active > self.ttl_seconds:
                session.messages = []
                session.last_active = time.time()
            return session

        session = Session(user_id=user_id, platform=platform)
        self._sessions[key] = session
        return session

    def add_message(self, user_id, platform, role, content, metadata=None):
        session = self.get_or_create(user_id, platform)
        msg = Message(role=role, content=content, platform=platform, metadata=metadata or {})
        session.messages.append(msg)
        session.last_active = time.time()

        if len(session.messages) > self.max_history:
            session.messages = session.messages[-self.max_history:]

        if self.persist:
            self._save_session(session)

        return msg

    def get_history(self, user_id, platform, n=None):
        session = self.get_or_create(user_id, platform)
        messages = session.messages
        if n:
            messages = messages[-n:]
        return [{"role": m.role, "content": m.content} for m in messages]

    def get_context_messages(self, user_id, platform, system_prompt=None):
        """Get messages formatted for LLM API calls."""
        history = self.get_history(user_id, platform)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)
        return messages

    def clear_session(self, user_id, platform):
        key = self._session_key(user_id, platform)
        if key in self._sessions:
            self._sessions[key].messages = []
            if self.persist:
                self._save_session(self._sessions[key])

    def delete_session(self, user_id, platform):
        key = self._session_key(user_id, platform)
        self._sessions.pop(key, None)
        if self.persist:
            path = os.path.join(self.storage_path, f"{key.replace(':', '_')}.json")
            if os.path.exists(path):
                os.remove(path)

    def list_sessions(self):
        return [{"key": k, "user_id": s.user_id, "platform": s.platform,
                 "messages": len(s.messages), "last_active": s.last_active}
                for k, s in self._sessions.items()]

    def cleanup_expired(self):
        now = time.time()
        expired = [k for k, s in self._sessions.items() if now - s.last_active > self.ttl_seconds]
        for key in expired:
            del self._sessions[key]
        return len(expired)

    def _save_session(self, session):
        if not self.storage_path:
            return
        key = self._session_key(session.user_id, session.platform)
        path = os.path.join(self.storage_path, f"{key.replace(':', '_')}.json")
        data = {
            "user_id": session.user_id, "platform": session.platform,
            "created_at": session.created_at, "last_active": session.last_active,
            "messages": [{"role": m.role, "content": m.content, "timestamp": m.timestamp}
                         for m in session.messages],
        }
        with open(path, "w") as f:
            json.dump(data, f)

    def _load_sessions(self):
        if not os.path.exists(self.storage_path):
            return
        for fname in os.listdir(self.storage_path):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(self.storage_path, fname)
            with open(path, "r") as f:
                data = json.load(f)
            session = Session(user_id=data["user_id"], platform=data["platform"],
                              created_at=data.get("created_at", time.time()),
                              last_active=data.get("last_active", time.time()))
            for m in data.get("messages", []):
                session.messages.append(Message(role=m["role"], content=m["content"],
                                                timestamp=m.get("timestamp", time.time())))
            key = self._session_key(session.user_id, session.platform)
            self._sessions[key] = session
