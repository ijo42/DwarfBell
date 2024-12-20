from typing import Optional

from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import pre
from magic_filter import F

from app.bot import dp
from app.rest_client import get_all_tasks, get_task_by_id


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
        response += f"- {task.name} ({task.value})\n"
        builder.button(
            text=task.name, callback_data=TaskCallbackFactory(action="get", value=task.id)
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
            f"*Task:* {task.name}\n"
            f"*Category:* {task.category}\n"
            f"*Value:* {task.value}\n"
            f"*Description:*\n"
            f"{pre(f"{task.description[:500]}{"..." if len(task.description) > 500 else ""}").replace('\\', '')}\n"
            f"*Connection Info:* {task.connection_info}\n"
            f"*Solves:* {task.solves}"
        )
        await callback.message.answer(text=response, parse_mode=ParseMode.MARKDOWN)
    else:
        await callback.message.answer(text="Failed to retrieve task details.")
    await callback.answer()
