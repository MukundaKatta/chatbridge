from setuptools import setup, find_packages

setup(
    name="chatbridge",
    version="0.1.0",
    description="Connect any LLM to any messaging platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="MukundaKatta",
    url="https://github.com/MukundaKatta/chatbridge",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["pydantic>=2.0", "pyyaml>=6.0"],
    extras_require={
        "telegram": ["python-telegram-bot>=20.0"],
        "discord": ["discord.py>=2.0"],
        "slack": ["slack-sdk>=3.20", "aiohttp>=3.8"],
        "openai": ["openai>=1.0"],
        "anthropic": ["anthropic>=0.20"],
        "ollama": ["httpx>=0.24"],
        "all": ["python-telegram-bot>=20.0", "discord.py>=2.0", "slack-sdk>=3.20",
                "openai>=1.0", "anthropic>=0.20", "httpx>=0.24"],
        "dev": ["pytest>=7.0", "pytest-asyncio>=0.21"],
    },
)
