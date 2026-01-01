# SPDX-License-Identifier: MIT
# Copyright (C) 2026 CodWiz

import re
from datetime import datetime
from typing import Optional, Tuple

from aiogram import Bot
from aiogram.types import Message

from core.storage import chat_settings
from domain.models import ChatConfig
from utils.helpers import delete_message_silently, is_admin


async def check_and_handle_inline_bot(message: Message, bot: Bot):
    """Основная логика проверки и удаления сообщений инлайн-ботов"""
    chat_id = message.chat.id

    if message.chat.type == "private":
        return

    if chat_id not in chat_settings:
        chat_settings[chat_id] = ChatConfig()

    config = chat_settings[chat_id]

    if message.from_user and await is_admin(bot, chat_id, message.from_user.id):
        return

    current_server_time = datetime.now().time()

    if not config.time_range.should_delete_at(current_server_time):
        return

    is_inline_msg, bot_username = await is_inline_bot_message(message)

    if not is_inline_msg:
        return

    if bot_username and config.is_whitelisted(bot_username):
        return

    await delete_message_silently(bot, chat_id, message.message_id)


async def is_inline_bot_message(message: Message) -> Tuple[bool, Optional[str]]:
    """Определяет, является ли сообщение результатом инлайн-запроса"""
    if message.via_bot:
        username = f"@{message.via_bot.username}" if message.via_bot.username else None
        return True, username

    if message.reply_markup and hasattr(message.reply_markup, "inline_keyboard"):
        text = message.text or message.caption or ""
        if text:
            patterns = [
                r"[Vv]ia\s+(@\w+[Bb]ot\b)",
                r"[Cc]\s+помощью\s+(@\w+[Bb]ot\b)",
                r"[Чч]ерез\s+(@\w+[Bb]ot\b)",
                r"[Ww]ith\s+(@\w+[Bb]ot\b)",
                r"[Bb]y\s+(@\w+[Bb]ot\b)",
            ]

            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    username = match.group(1)
                    return True, username

    return False, None
