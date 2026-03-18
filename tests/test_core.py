from src.core import ChatBridge
def test_init(): assert ChatBridge().get_stats()["ops"] == 0
def test_op(): c = ChatBridge(); c.connect_platform(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = ChatBridge(); [c.connect_platform() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = ChatBridge(); c.connect_platform(); c.reset(); assert c.get_stats()["ops"] == 0
