from enum import auto, Enum

from loguru import logger

from app.redis_pool import push_list_tail, RedisKeys, push_list_head, get_list_head, pop_list_head, find_key_list

class SolvesResponse(Enum):
    ALREADY_QUEUED = auto()
    ALREADY_TRIED = auto()
    SCHEDULED = auto()


async def _push_solve_attempt(task_id: int, flag: str) -> SolvesResponse:
    flag_value = f'{task_id}:{flag}'
    if await find_key_list(RedisKeys.TASK_QUEUE.value, flag_value):
        logger.debug("Флаг уже есть в очереди")
        return SolvesResponse.ALREADY_QUEUED
    if await find_key_list(RedisKeys.TASK_TRY.value.format(task_id), flag):
        logger.debug("Флаг уже в попытках решения")
        return SolvesResponse.ALREADY_TRIED
    return SolvesResponse.SCHEDULED

async def push_solve_attempt_tail(task_id: int, flag: str) -> SolvesResponse:
    state = await _push_solve_attempt(task_id, flag)
    if state == SolvesResponse.SCHEDULED:
        flag_value = f'{task_id}:{flag}'
        await push_list_tail(RedisKeys.TASK_QUEUE.value, flag_value)
        logger.info(f"Флаг добавлен в попытки решения для задачи {task_id}: {flag}")
    return state


async def push_solve_attempt_head(task_id: int, flag: str) -> SolvesResponse:
    state = await _push_solve_attempt(task_id, flag)
    if state == SolvesResponse.SCHEDULED:
        flag_value = f'{task_id}:{flag}'
        await push_list_head(RedisKeys.TASK_QUEUE.value, flag_value)
        logger.info(f"Флаг добавлен в попытки решения для задачи {task_id}: {flag}")
    return state

async def push_solve_attempt(task_id: int, flag: str, priority: str) -> SolvesResponse:
    if priority == 'high':
        return await push_solve_attempt_head(task_id, str(flag))
    elif priority == 'low':
        return await push_solve_attempt_tail(task_id, str(flag))

async def get_solve_queue_head() -> list[str] | None:
    queue_head = await get_list_head(RedisKeys.TASK_QUEUE.value)
    if not queue_head:
        return None
    return queue_head.split(':')

async def pop_solve_queue_head():
    task_id, flag = (await pop_list_head(RedisKeys.TASK_QUEUE.value)).split(':')
    await push_list_tail(RedisKeys.TASK_TRY.value.format(task_id), flag)

