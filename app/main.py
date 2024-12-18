# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.routes import root_router
from app.settings import get_settings

cfg = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    try:
        logger.info("🚀 Starting application")
        from app.bot import start_telegram, dp, bot
        await start_telegram()
        yield
        logger.info("⛔ Stopping application")
    finally:
        from app.bot import stop_telegram
        await stop_telegram()


app = FastAPI(lifespan=lifespan)
app.include_router(root_router)
