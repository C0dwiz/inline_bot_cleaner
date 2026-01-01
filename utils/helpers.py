# SPDX-License-Identifier: MIT
# Copyright (C) 2026 CodWiz

import asyncio
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus

from core.config import logger
from core.storage import chat_settings
from domain.models import ChatConfig


async def delete_message_silently(bot: Bot, chat_id: int, message_id: int) -> bool:
    """Безопасно удаляет сообщение с обработкой ошибок"""
    try:
        await bot.delete_message(chat_id, message_id)
        return True
    except TelegramBadRequest as e:
        error_text = str(e).lower()
        if "message to delete not found" in error_text:
            logger.warning(f"Message {message_id} already deleted or not found.")
        elif "message can't be deleted" in error_text:
            logger.warning(f"Bot lacks permissions to delete message {message_id}.")
        else:
            logger.error(f"TelegramBadRequest deleting message: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting message {message_id}: {e}")
        return False


async def is_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором чата"""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        ]
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False


async def schedule_auto_delete(bot: Bot, chat_id: int, message_id: int, delay: int):
    """Планирует автоматическое удаление сообщения"""
    await asyncio.sleep(delay)

    if chat_id in chat_settings:
        config = chat_settings[chat_id]
        if message_id in config.message_tasks:
            await delete_message_silently(bot, chat_id, message_id)
            if message_id in config.message_tasks:
                del config.message_tasks[message_id]


async def send_message_with_auto_delete(
    bot: Bot, chat_id: int, text: str, config: ChatConfig, reply_markup=None
) -> Optional[Message]:
    """Отправляет сообщение с автоматическим удалением"""
    try:
        message = await bot.send_message(
            chat_id, text, reply_markup=reply_markup, parse_mode="HTML"
        )

        if config.auto_delete.enabled and config.auto_delete.delete_after > 0:
            task = asyncio.create_task(
                schedule_auto_delete(
                    bot, chat_id, message.message_id, config.auto_delete.delete_after
                )
            )
            config.message_tasks[message.message_id] = task

        return message
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None
