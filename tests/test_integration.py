"""Integration tests for Chatbridge."""
from src.core import Chatbridge

class TestChatbridge:
    def setup_method(self):
        self.c = Chatbridge()
    def test_10_ops(self):
        for i in range(10): self.c.connect_platform(i=i)
        assert self.c.get_stats()["ops"] == 10
    def test_service_name(self):
        assert self.c.connect_platform()["service"] == "chatbridge"
    def test_different_inputs(self):
        self.c.connect_platform(type="a"); self.c.connect_platform(type="b")
        assert self.c.get_stats()["ops"] == 2
    def test_config(self):
        c = Chatbridge(config={"debug": True})
        assert c.config["debug"] is True
    def test_empty_call(self):
        assert self.c.connect_platform()["ok"] is True
    def test_large_batch(self):
        for _ in range(100): self.c.connect_platform()
        assert self.c.get_stats()["ops"] == 100
