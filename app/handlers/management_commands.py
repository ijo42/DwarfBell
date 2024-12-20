from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from app.bot import dp
from app.redis_pool import set_redis_keys, RedisKeys
from app.rest_client import test_connection


@dp.message(Command("setup"))
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
    try:
        await set_redis_keys({RedisKeys.ENDPOINT.value: url, RedisKeys.TOKEN.value: token})
        await message.answer(f"Connection setup successful. Username: {connection}")
    except Exception as e:
        await message.answer("An error occurred while saving data. Please try again later.")
        logger.error(f"Error saving endpoint: {e}")
