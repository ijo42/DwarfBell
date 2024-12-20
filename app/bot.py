# -*- coding: utf-8 -*-
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import WebhookInfo, BotCommand
from loguru import logger

from app.settings import get_settings, Settings
from app.system import first_run, check_ctfd

cfg: Settings = get_settings()

bot = Bot(token=cfg.bot_token)
dp = Dispatcher()


async def start_polling(my_bot: Bot) -> None:
    async def check_webhook() -> WebhookInfo | None:
        try:
            webhook_info = await my_bot.get_webhook_info()
            return webhook_info
        except Exception as e:
            logger.error(f"Can't get webhook info - {e}")
            return

    current_webhook_info = await check_webhook()
    if cfg.debug:
        logger.debug(f"Current bot info: {current_webhook_info}")
    try:
        if len(current_webhook_info.url) > 0:
            logger.debug("Cleaning webhook...")
            await bot.delete_webhook()
        if cfg.debug:
            logger.debug(f"Bot starting {await my_bot.get_my_name()}...")
        asyncio.create_task(dp.start_polling(my_bot))
    except Exception as e:
        logger.error(f"Can't set webhook - {e}")


async def set_bot_commands_menu(my_bot: Bot) -> None:
    # Register commands for Telegram bot (menu)
    commands = [
        BotCommand(command="/id", description="👋 Get my ID"),
        BotCommand(command="/chat", description="👋 Get chat ID"),
        BotCommand(command="/setup", description="Set ctfd endpoint. Format: <endpoint> <token>"),
        BotCommand(command="/tasks", description="Get tasks"),
    ]
    try:
        await my_bot.set_my_commands(commands)
    except Exception as e:
        logger.error(f"Can't set commands - {e}")


async def start_telegram():
    fr = await first_run()
    if cfg.debug:
        logger.debug(f"First run: {fr}")
    if fr:
        await set_bot_commands_menu(bot)
    await check_ctfd()
    await start_polling(bot)


async def stop_telegram():
    await dp.stop_polling()
