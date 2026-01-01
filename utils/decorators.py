# SPDX-License-Identifier: MIT
# Copyright (C) 2026 CodWiz

from functools import wraps
from aiogram.types import Message, CallbackQuery
from utils.helpers import is_admin, delete_message_silently


def admin_required(func):
    """Декоратор для проверки прав администратора"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        if len(args) > 0:
            if isinstance(args[0], Message):
                message = args[0]
                bot = kwargs.get("bot") or args[1] if len(args) > 1 else None
                kwargs.get("state")
            elif isinstance(args[0], CallbackQuery):
                callback = args[0]
                message = callback.message
                bot = kwargs.get("bot") or args[1] if len(args) > 1 else None
                kwargs.get("state")
            else:
                return await func(*args, **kwargs)

            if not bot:
                return

            if not await is_admin(bot, message.chat.id, message.from_user.id):
                if isinstance(args[0], Message):
                    await delete_message_silently(
                        bot, message.chat.id, message.message_id
                    )
                elif isinstance(args[0], CallbackQuery):
                    await callback.answer(
                        "Эта кнопка доступна только администраторам!", show_alert=True
                    )
                return

        return await func(*args, **kwargs)

    return wrapper
