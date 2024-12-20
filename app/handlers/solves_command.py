from typing import Optional

from aiogram import F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hblockquote, hbold

from app.bot import dp
from app.rest_client import get_all_tasks
from app.solve_queue_worker import get_solve_queue_worker
from app.solves_pool import SolvesResponse, push_solve_attempt


class AttemptCallbackFactory(CallbackData, prefix="attempt"):
    task_id: Optional[int] = None
    type: Optional[str] = None # like available_methods
    answer: Optional[str | list[str]] = None

available_methods = ['str', 'range', 'dict']

class AttemptStage(StatesGroup):
    choosing_task = State()
    choosing_method = State()
    choosing_params = State()
    confirm = State()

@dp.message(Command("start_solve"))
async def cmd_endpoint(message: Message) -> None:
    command_parts = message.text.split(maxsplit=2)
    solve_queue_worker = get_solve_queue_worker()
    if len(command_parts) > 1:
        solve_queue_worker.reconfigure(float(command_parts[1].strip()))
    solve_queue_worker.start()
    await message.answer("Solve queue worker started.")


@dp.message(StateFilter(None), Command("attempt"))
async def cmd_food(message: Message, state: FSMContext):
    tasks = await get_all_tasks()

    builder = InlineKeyboardBuilder()
    for task in tasks:
        builder.button(
            text=task.name, callback_data=AttemptCallbackFactory(task_id=task.id)
        )

    await message.answer(
        text="Выберите таску:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(AttemptStage.choosing_task)

@dp.callback_query(StateFilter(AttemptStage.choosing_task), AttemptCallbackFactory.filter())
async def callbacks_num_change_fab(
        callback: CallbackQuery,
        callback_data: AttemptCallbackFactory,
        state: FSMContext
):
    await state.update_data(task_id=callback_data.task_id)

    await callback.message.edit_text(
        text="Каким способом будет решать?\n* str - конкретная строка\n* range - диапазон чисел\n* dict - по словарю",
        reply_markup=
            InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=item, callback_data=item) for item in available_methods]],
                resize_keyboard=True
            )
    )
    await state.set_state(AttemptStage.choosing_method)
    await callback.answer()

@dp.callback_query(StateFilter(AttemptStage.choosing_method))
async def callbacks_num(
        callback: CallbackQuery,
        state: FSMContext
):

    method_texts = {
        available_methods[0]: "Введите ответ:",
        available_methods[1]: "Введите 3 числа через пробел <начало конец шаг>:",
        available_methods[2]: "Введите ответы каждый в новой строке:"
    }

    if callback.data in method_texts:
        await callback.message.edit_text(
            text=method_texts[callback.data],
        )
        await state.set_state(AttemptStage.choosing_params)
        await state.update_data(type=callback.data)
        await callback.answer()
    else:
        await callback.answer("Неверный ввод", show_alert=True)


def create_number_list(input_string):
    parts = input_string.split()
    if len(parts) != 3:
        return None

    try:
        start = int(parts[0])
        end = int(parts[1])
        step = int(parts[2])

        if step == 0:
            return None

        return list(map(str, range(start, end + 1, step)))
    except ValueError:
        return None


@dp.message(StateFilter(AttemptStage.choosing_params), F.text)
async def answer_chosen(message: Message, state: FSMContext):
    data = await state.get_data()

    if data.get('type') == available_methods[0]:
        await state.update_data(answer=message.text)
    if data.get('type') == available_methods[1]:
        await state.update_data(answer=create_number_list(message.text))
    if data.get('type') == available_methods[2]:
        await state.update_data(answer=message.text.split('\n'))
    data = await state.get_data()

    await message.reply(
        text=f"Добавляю в очередь?\nTask_ID: {hbold(data.get('task_id'))}\nAnswer:\n{hblockquote(data.get('answer'))}",
        parse_mode=ParseMode.HTML,
        reply_markup=
            InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=item, callback_data=key) for item, key in
                                  [("LOW PRIO❄️", "low"), ("HIGH PRIO🔥", "high"), ("Отмена", "cancel")]
                                  ]],
                resize_keyboard=True
            )
    )
    await state.set_state(AttemptStage.confirm)


@dp.callback_query(StateFilter(AttemptStage.confirm))
async def callbacks_num_change_fab(
        callback: CallbackQuery,
        state:FSMContext
):
    if callback.data == "cancel":
        await callback.message.edit_text("Отмена добавления в очередь.")
        await state.clear()
    elif callback.data in ["low", "high"]:
        responses_def = {
            SolvesResponse.SCHEDULED: "Успешно добавлено",
            SolvesResponse.ALREADY_QUEUED: "Уже были в очереди",
            SolvesResponse.ALREADY_TRIED: "Уже испытанные"
        }

        await state.update_data(priority=callback.data)
        data = await state.get_data()
        if data.get('type') == available_methods[0]:
            response = await push_solve_attempt(data.get('task_id'), data.get('answer'), data.get('priority'))
            await callback.message.reply(f"Response: {responses_def[response]}")
        else:
            awaited_responses = responses = [await push_solve_attempt(data.get('task_id'), answer, data.get('priority')) for answer in data.get('answer')]
            # awaited_responses = await asyncio.gather(*responses)

            response_text = "\n".join(
                f"{count_value}: {awaited_responses.count(count_key)}"
                for count_key, count_value in responses_def.items()
                if awaited_responses.count(count_key) > 0
            )

            await callback.message.reply(response_text)
        await callback.answer()
        await state.clear()
    else:
        await callback.answer("Неверный ввод", show_alert=True)
