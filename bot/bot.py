# SPDX-License-Identifier: MIT
# Copyright (C) 2026 CodWiz

import asyncio
from aiogram import Bot
from core.config import BOT_TOKEN, logger
from bot.dispatcher import setup_dispatcher


async def main():
    """Основная функция запуска бота"""
    bot = Bot(token=BOT_TOKEN)
    dp = setup_dispatcher()

    logger.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
