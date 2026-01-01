# SPDX-License-Identifier: MIT
# Copyright (C) 2026 CodWiz

from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.storage import chat_settings
from domain.states import SettingsState
from domain.models import ChatConfig, DeleteMode
from domain.services import check_and_handle_inline_bot
from utils.decorators import admin_required
from utils.helpers import delete_message_silently, send_message_with_auto_delete


@admin_required
async def handle_text_input(message: Message, bot: Bot, state: FSMContext):
    """Обработчик текстового ввода для настроек"""
    chat_id = message.chat.id
    if chat_id not in chat_settings:
        chat_settings[chat_id] = ChatConfig()

    config = chat_settings[chat_id]
    current_state = await state.get_state()

    input_states = [
        SettingsState.whitelist_add,
        SettingsState.auto_delete_time_set,
        SettingsState.time_range_set_start,
        SettingsState.time_range_set_end,
    ]

    if current_state not in input_states:
        return

    await delete_message_silently(bot, chat_id, message.message_id)

    if current_state == SettingsState.whitelist_add:
        user_input = message.text.strip()

        if not user_input:
            await send_message_with_auto_delete(
                bot, chat_id, "❌ Введите username ботов с @", config
            )
            return

        usernames = []
        lines = user_input.split("\n")
        for line in lines:
            items = line.strip().split()
            usernames.extend(items)

        added_bots = []
        already_exists = []
        invalid_format = []

        for bot_username in usernames:
            if not bot_username.startswith("@"):
                invalid_format.append(bot_username)
                continue

            if config.is_whitelisted(bot_username):
                already_exists.append(bot_username)
            else:
                config.whitelist.append(bot_username)
                added_bots.append(bot_username)

        result_text = ""
        if added_bots:
            result_text += f"✅ Добавлены боты: {', '.join(added_bots)}\n"
        if already_exists:
            result_text += f"ℹ️ Уже в списке: {', '.join(already_exists)}\n"
        if invalid_format:
            result_text += (
                f"❌ Неверный формат (должно быть с @): {', '.join(invalid_format)}\n"
            )

        if not added_bots and not already_exists and not invalid_format:
            result_text = "❌ Не найдено корректных username ботов"

        await send_message_with_auto_delete(bot, chat_id, result_text.strip(), config)

        from handlers.settings_menu import show_whitelist_menu

        await show_whitelist_menu(message, bot, state)

    elif current_state == SettingsState.auto_delete_time_set:
        try:
            seconds = int(message.text.strip())
            if 5 <= seconds <= 3600:
                config.auto_delete.delete_after = seconds
                await send_message_with_auto_delete(
                    bot,
                    chat_id,
                    f"✅ Время автоудаления установлено: {seconds} секунд",
                    config,
                )
                from handlers.settings_menu import show_auto_delete_settings

                await show_auto_delete_settings(message, bot, state)
            else:
                await send_message_with_auto_delete(
                    bot, chat_id, "❌ Введите число от 5 до 3600 секунд", config
                )
        except ValueError:
            await send_message_with_auto_delete(
                bot, chat_id, "❌ Введите целое число (секунды)", config
            )

    elif current_state == SettingsState.time_range_set_start:
        try:
            if ":" in message.text:
                hours, minutes = map(int, message.text.strip().split(":"))
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    config.time_range.start_hour = hours
                    config.time_range.start_minute = minutes

                    from aiogram import types

                    keyboard = types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                types.InlineKeyboardButton(
                                    text="◀️ Назад", callback_data="back_to_time"
                                )
                            ]
                        ]
                    )

                    msg = await send_message_with_auto_delete(
                        bot=bot,
                        chat_id=chat_id,
                        text=(
                            "⏰ <b>Установка времени удаления</b>\n\n"
                            f"Время начала: <b>{hours:02d}:{minutes:02d}</b>\n\n"
                            "Теперь введите время окончания в формате <b>HH:MM</b>\n"
                            "Например: <code>08:00</code>"
                        ),
                        config=config,
                        reply_markup=keyboard,
                    )
                    await state.set_state(SettingsState.time_range_set_end)
                    if msg:
                        await state.update_data(last_message_id=msg.message_id)
                else:
                    raise ValueError
            else:
                raise ValueError
        except:  # noqa: E722
            await send_message_with_auto_delete(
                bot,
                chat_id,
                "❌ Неверный формат времени. Используйте HH:MM\nПример: 22:00",
                config,
            )

    elif current_state == SettingsState.time_range_set_end:
        try:
            if ":" in message.text:
                hours, minutes = map(int, message.text.strip().split(":"))
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    config.time_range.end_hour = hours
                    config.time_range.end_minute = minutes

                    config.time_range.mode = DeleteMode.TIME_RANGE

                    await send_message_with_auto_delete(
                        bot,
                        chat_id,
                        f"✅ Время удаления установлено и режим активирован!\n"
                        f"С {config.time_range.get_start_time().strftime('%H:%M')} "
                        f"до {config.time_range.get_end_time().strftime('%H:%M')}",
                        config,
                    )
                    from handlers.settings_menu import show_time_settings

                    await show_time_settings(message, bot, state)
                else:
                    raise ValueError
            else:
                raise ValueError
        except:  # noqa: E722
            await send_message_with_auto_delete(
                bot,
                chat_id,
                "❌ Неверный формат времени. Используйте HH:MM\nПример: 08:00",
                config,
            )


async def handle_all_messages(message: Message, bot: Bot, state: FSMContext):
    """Обработчик всех сообщений"""
    if message.text and message.text.startswith("/"):
        return

    await check_and_handle_inline_bot(message, bot)
