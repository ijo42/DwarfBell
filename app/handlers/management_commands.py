from typing import Optional

from aiogram.utils.markdown import bold, blockquote, pre
from aiohttp.helpers import quoted_string
from magic_filter import F
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from loguru import logger
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from app.redis_pool import set_redis_keys
from app.bot import dp
from app.rest_client import test_connection, get_all_tasks, get_task_by_id


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
        await set_redis_keys({'endpoint': url, 'token': token})
        await message.answer(f"Connection setup successful. Username: {connection}")
    except Exception as e:
        await message.answer("An error occurred while saving data. Please try again later.")
        logger.error(f"Error saving endpoint: {e}")


class TaskCallbackFactory(CallbackData, prefix="task"):
    action: str
    value: Optional[int] = None

@dp.message(Command("tasks"))
async def cmd_tasks(message: Message) -> None:
    tasks = await get_all_tasks()
    if not tasks:
        await message.answer("Unable to fetch tasks. Please check your connection.")
        return
    builder = InlineKeyboardBuilder()
    response = "Available tasks:\n\n"
    for task in tasks:
        response += f"- {task['name']} ({task['value']})\n"
        builder.button(
            text=task['name'], callback_data=TaskCallbackFactory(action="get", value=task['id'])
        )
    builder.adjust(4)
    await message.answer(response, reply_markup=builder.as_markup())

@dp.callback_query(TaskCallbackFactory.filter(F.action == "get"))
async def callbacks_num_change_fab(
        callback: CallbackQuery,
        callback_data: TaskCallbackFactory
):
    task = await get_task_by_id(callback_data.value)
    if task:
        response = (
            f"*Task:* {task['name']}\n"
            f"*Category:* {task['category']}\n"
            f"*Value:* {task['value']}\n"
            f"*Description:*\n"
            f"{pre(f"{task['description'][:500]}{"..." if len(task['description']) > 500 else ""}").replace('\\', '')}\n"
            f"*Connection Info:* {task['connection_info']}\n"
            f"*Solves:* {task['solves']}"
        )
        await callback.message.answer(text=response, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback.message.answer(text="Failed to retrieve task details.")
    await callback.answer()