from aiogram.enums import ParseMode
from loguru import logger
from aiogram.types import Message
from aiogram.filters import Command

from app.redis_pool import get_redis_client
from app.bot import telegram_router
from app.rest_client import test_connection


@telegram_router.message(Command("setup"))
async def cmd_endpoint(message: Message) -> None:
    command_parts = message.text.split(maxsplit=2)

    if len(command_parts) != 3:
        await message.answer("Format: `/setup <url> <token>`", parse_mode=ParseMode.MARKDOWN)
        return

    url = command_parts[1].strip()
    token = command_parts[2].strip()

    if not url.startswith(('http://', 'https://')):
        await message.answer("Please provide a valid URL starting with http:// or https://")
        return

    connection = await test_connection(url, token)
    if not connection:
        await message.answer("Unable to connect to the provided URL or token is invalid.")
        return

    client = get_redis_client()
    try:
        await client.set("endpoint", url)
        await client.set("token", token)
        await message.answer(f"Connection setup successful. Username: {connection}")
    except Exception as e:
        await message.answer("An error occurred while saving data. Please try again later.")
        logger.error(f"Error saving endpoint: {e}")
