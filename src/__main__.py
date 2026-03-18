"""CLI for chatbridge."""
import sys, json, argparse
from .core import Chatbridge

def main():
    parser = argparse.ArgumentParser(description="Agentic IM chatbot infrastructure — integrates WhatsApp, Telegram, Discord, Slack with any LLM")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Chatbridge()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.connect_platform(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"chatbridge v0.1.0 — Agentic IM chatbot infrastructure — integrates WhatsApp, Telegram, Discord, Slack with any LLM")

if __name__ == "__main__":
    main()
