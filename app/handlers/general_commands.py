from loguru import logger
from aiogram import types
from aiogram import F
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import bold
from aiogram.types import Message

from app.bot import dp

@dp.message(Command("id"))
async def cmd_id(message: Message) -> None:
    await message.answer(f"Your ID: {message.from_user.id}")

@dp.message(Command("chat"))
async def cmd_chat(message: Message) -> None:
    await message.answer(f"Chat ID: {message.chat.id}")

@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(f"Hello, {bold(message.from_user.full_name)}!")

@dp.message(F.text == "echo")
async def echo(message: types.Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except Exception as e:
        logger.error(f"Can't send message - {e}")
        await message.answer("Nice try!")

@dp.message(F.text == "ping")
async def hello(message: types.Message) -> None:
    try:
        await message.answer("pong")
    except Exception as e:
        logger.error(f"Can't send message - {e}")
        await message.answer("Nice try!")