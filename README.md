# DWARF Bot (FastAPI & Aiogram Telegram bot)
Telegram bot for playing ctfs

## Prerequisites

- Python 3.10+
- Aiogram 3.0+
- FastAPI 0.100+
- redis

#### Description

Setup you own environment variables in settings.py file or in `[prod|dev].env` file. Put your own handlers in handlers directory and import them in __init__.py file. In REDIS saved ppid for checking if bot is running first time or not. But also you cat use it for cache or other purposes.