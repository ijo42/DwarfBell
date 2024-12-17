# -*- coding: utf-8 -*-
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from app.settings import get_settings

cfg = get_settings()

pool = ConnectionPool.from_url(cfg.redis_url)

def get_redis_client():
    return Redis(connection_pool=pool)

async def get_redis_key(key: str) -> str:
    redis = await get_redis_client()
    value = await redis.get(key)
    await pool.release(redis)
    return value

async def set_redis_key(key: str, value: str):
    redis = await get_redis_client()
    await redis.set(key, value)
    await pool.release(redis)