# -*- coding: utf-8 -*-
from os import getppid

from loguru import logger

from app.redis_pool import get_redis_key, set_redis_key, get_redis_keys
from app.rest_client import init_rest_client
from app.settings import get_settings

cfg = get_settings()


async def first_run() -> bool:
    """Check if this is the first run of service. ppid is the parent process id.
    Save ppid to redis and check it on next run. If ppid is the same - this is not the first run."""
    ppid = getppid()
    save_pid = await get_redis_key('tg_bot_ppid')
    if save_pid and int(save_pid) == ppid:
        return False
    await set_redis_key('tg_bot_ppid', str(ppid))
    return True

async def check_ctfd():
    endpoint, token = await get_redis_keys(['endpoint', 'token'])
    await init_rest_client(endpoint, token)
