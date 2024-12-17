# -*- coding: utf-8 -*-
from redis.asyncio import Redis, ConnectionPool

from app.settings import get_settings

cfg = get_settings()

pool = ConnectionPool.from_url(cfg.redis_url)

async def get_redis_key(key: str) -> str:
    async with Redis.from_pool(pool) as redis:
        return await redis.get(key)

async def get_redis_keys(keys: list) -> list[str]:
    async with Redis.from_pool(pool) as redis:
        values = await redis.mget(*keys)
        return [value.decode('utf-8') if value else None for value in values]

async def set_redis_key(key: str, value: str):
    async with Redis.from_pool(pool) as redis:
        await redis.set(key, value)

async def set_redis_keys(kvalues: dict):
    async with Redis.from_pool(pool) as redis:
        await redis.mset(kvalues)

async def delete_redis_key(key: str):
    async with Redis.from_pool(pool) as redis:
        await redis.delete(key)