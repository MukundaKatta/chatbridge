"""Basic usage example for chatbridge."""
from src.core import Chatbridge

def main():
    instance = Chatbridge(config={"verbose": True})

    print("=== chatbridge Example ===\n")

    # Run primary operation
    result = instance.connect_platform(input="example data", mode="demo")
    print(f"Result: {result}")

    # Run multiple operations
    ops = ["connect_platform", "route_message", "manage_session]
    for op in ops:
        r = getattr(instance, op)(source="example")
        print(f"  {op}: {"✓" if r.get("ok") else "✗"}")

    # Check stats
    print(f"\nStats: {instance.get_stats()}")

if __name__ == "__main__":
    main()
