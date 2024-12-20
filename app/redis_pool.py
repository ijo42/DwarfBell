# -*- coding: utf-8 -*-
from enum import Enum

from redis.asyncio import Redis, ConnectionPool

from app.settings import get_settings

cfg = get_settings()

pool = ConnectionPool.from_url(cfg.redis_url)


class RedisKeys(Enum):
    ENDPOINT = 'endpoint'
    TOKEN = 'token'
    TASK_TRY = 'task_try_{}'
    TASK_QUEUE = 'task_queue'


async def get_redis_key(key: str) -> str:
    async with Redis.from_pool(pool) as redis:
        return await redis.get(key)


async def get_redis_keys(keys: list[str]) -> list[str]:
    async with Redis.from_pool(pool) as redis:
        values = await redis.mget(*keys)
        return [value.decode('utf-8') if value else None for value in values]

# содержит ли список `key` значение `value`
async def find_key_list(key: str, value: str) -> bool:
    async with Redis.from_pool(pool) as redis:
        return await redis.exists(key) and (await redis.lrange(key, 0, -1)).count(value.encode('utf-8')) > 0


async def push_list_tail(key: str, value: str):
    async with Redis.from_pool(pool) as redis:
        await redis.rpush(key, value)


async def push_list_head(key: str, value: str):
    async with Redis.from_pool(pool) as redis:
        await redis.lpush(key, value)


async def pop_list_tail(key: str):
    async with Redis.from_pool(pool) as redis:
        return await redis.rpop(key)


async def get_list_head(key: str):
    async with Redis.from_pool(pool) as redis:
        return await redis.lrange(key, 0, 1)


async def get_list(key: str):
    async with Redis.from_pool(pool) as redis:
        return await redis.lrange(key, 0, -1)


async def pop_list_head(key: str):
    async with Redis.from_pool(pool) as redis:
        return await redis.lpop(key)


async def set_redis_key(key: str, value: str):
    async with Redis.from_pool(pool) as redis:
        await redis.set(key, value)


async def set_redis_keys(kvalues: dict):
    async with Redis.from_pool(pool) as redis:
        await redis.mset(kvalues)


async def delete_redis_key(key: str):
    async with Redis.from_pool(pool) as redis:
        await redis.delete(key)
