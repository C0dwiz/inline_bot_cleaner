# SPDX-License-Identifier: MIT
# Copyright (C) 2026 CodWiz

from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatMemberStatus

from core.storage import chat_settings
from domain.models import ChatConfig
from utils.decorators import admin_required
from utils.helpers import (
    delete_message_silently,
    send_message_with_auto_delete,
)
from handlers.settings_menu import show_settings_menu


@admin_required
async def cmd_start(message: Message, bot: Bot):
    """Обработчик команды /start"""
    await delete_message_silently(bot, message.chat.id, message.message_id)

    if message.chat.id not in chat_settings:
        chat_settings[message.chat.id] = ChatConfig()
    config = chat_settings[message.chat.id]

    if message.chat.type in ["group", "supergroup"]:
        try:
            member = await bot.get_chat_member(message.chat.id, bot.id)
            if member.status == ChatMemberStatus.ADMINISTRATOR:
                await send_message_with_auto_delete(
                    bot,
                    message.chat.id,
                    "✅ Бот активирован!\n"
                    "Используйте /settings для настройки бота.\n\n"
                    "Основные функции:\n"
                    "• Удаление сообщений от инлайн-ботов\n"
                    "• Настройка времени удаления\n"
                    "• Белый список ботов\n"
                    "• Автоудаление сообщений бота",
                    config,
                )
            else:
                await send_message_with_auto_delete(
                    bot,
                    message.chat.id,
                    "⚠️ Мне нужны права администратора!\n"
                    "Выдайте мне права на удаление сообщений.",
                    config,
                )
        except Exception as e:
            from core.config import logger

            logger.error(f"Error in /start: {e}")
    else:
        await message.answer("Добавьте меня в группу и выдайте права администратора.")


@admin_required
async def cmd_settings(message: Message, bot: Bot, state: FSMContext):
    """Обработчик команды /settings"""
    await show_settings_menu(message, bot, state)
