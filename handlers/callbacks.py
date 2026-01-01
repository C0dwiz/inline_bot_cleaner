# SPDX-License-Identifier: MIT
# Copyright (C) 2026 CodWiz

from aiogram import Bot, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from core.storage import chat_settings
from domain.states import SettingsState
from domain.models import DeleteMode
from domain.models import ChatConfig
from utils.decorators import admin_required
from utils.helpers import delete_message_silently, send_message_with_auto_delete
from handlers.settings_menu import (
    show_settings_menu,
    show_time_settings,
    show_whitelist_menu,
    show_auto_delete_settings,
    show_status,
)


@admin_required
async def handle_settings_callback(
    callback: CallbackQuery, bot: Bot, state: FSMContext
):
    """Обработчик callback'ов настроек"""
    chat_id = callback.message.chat.id

    if chat_id not in chat_settings:
        chat_settings[chat_id] = ChatConfig()

    config = chat_settings[chat_id]
    await state.get_data()

    await delete_message_silently(bot, chat_id, callback.message.message_id)

    if callback.data == "toggle_global_off":
        config.time_range.mode = DeleteMode.DISABLED
        await callback.answer("Удаление инлайн-сообщений отключено")
        await show_settings_menu(callback.message, bot, state)
        return

    elif callback.data == "toggle_global_on":
        config.time_range.mode = DeleteMode.ALWAYS
        await callback.answer("Удаление инлайн-сообщений включено")
        await show_settings_menu(callback.message, bot, state)
        return

    if callback.data == "settings_time":
        await show_time_settings(callback.message, bot, state)

    elif callback.data == "settings_whitelist":
        await show_whitelist_menu(callback.message, bot, state)

    elif callback.data == "settings_auto_delete":
        await show_auto_delete_settings(callback.message, bot, state)

    elif callback.data == "settings_status":
        await show_status(callback.message, bot, state)

    elif callback.data == "back_to_main":
        await show_settings_menu(callback.message, bot, state)

    elif callback.data == "back_to_time":
        await show_time_settings(callback.message, bot, state)

    elif callback.data == "back_to_whitelist":
        await show_whitelist_menu(callback.message, bot, state)

    elif callback.data == "back_to_auto_delete":
        await show_auto_delete_settings(callback.message, bot, state)

    elif callback.data.startswith("time_"):
        await handle_time_callback(callback, bot, state)

    elif callback.data.startswith("whitelist_"):
        await handle_whitelist_callback(callback, bot, state)

    elif callback.data.startswith("autodel_"):
        await handle_auto_delete_callback(callback, bot, state)

    elif callback.data.startswith("remove_"):
        bot_to_remove = callback.data[7:]
        if bot_to_remove in config.whitelist:
            config.whitelist.remove(bot_to_remove)
            await callback.answer(
                f"Бот {bot_to_remove} удален из белого списка", show_alert=False
            )
        await show_whitelist_menu(callback.message, bot, state)

    await callback.answer()


async def handle_time_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Обработчик callback'ов времени"""
    chat_id = callback.message.chat.id
    config = chat_settings[chat_id]

    await delete_message_silently(bot, chat_id, callback.message.message_id)

    if callback.data == "time_always":
        config.time_range.mode = DeleteMode.ALWAYS
        await show_time_settings(callback.message, bot, state)

    elif callback.data == "time_range":
        config.time_range.mode = DeleteMode.TIME_RANGE

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
                "Введите время начала в формате <b>HH:MM</b>\n"
                "Например: <code>22:00</code>"
            ),
            config=config,
            reply_markup=keyboard,
        )
        await state.set_state(SettingsState.time_range_set_start)
        if msg:
            await state.update_data(last_message_id=msg.message_id)


async def handle_whitelist_callback(
    callback: CallbackQuery, bot: Bot, state: FSMContext
):
    """Обработчик callback'ов белого списка"""
    chat_id = callback.message.chat.id
    config = chat_settings[chat_id]

    await delete_message_silently(bot, chat_id, callback.message.message_id)

    if callback.data == "whitelist_add":
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="◀️ Назад", callback_data="back_to_whitelist"
                    )
                ]
            ]
        )

        msg = await send_message_with_auto_delete(
            bot=bot,
            chat_id=chat_id,
            text=(
                "➕ <b>Добавление ботов в белый список</b>\n\n"
                "Введите username ботов через пробел или с новой строки\n"
                "Например:\n"
                "<code>@LyBot @gif @music</code>\n\n"
                "или:\n"
                "<code>@LyBot\n@gif\n@music</code>"
            ),
            config=config,
            reply_markup=keyboard,
        )
        await state.set_state(SettingsState.whitelist_add)
        if msg:
            await state.update_data(last_message_id=msg.message_id)

    elif callback.data == "whitelist_remove":
        if not config.whitelist:
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="◀️ Назад", callback_data="back_to_whitelist"
                        )
                    ]
                ]
            )

            msg = await send_message_with_auto_delete(
                bot=bot,
                chat_id=chat_id,
                text="Белый список пуст!",
                config=config,
                reply_markup=keyboard,
            )
            if msg:
                await state.update_data(last_message_id=msg.message_id)
            return

        buttons = []
        for bot_username in config.whitelist:
            buttons.append(
                [
                    types.InlineKeyboardButton(
                        text=f"❌ {bot_username}",
                        callback_data=f"remove_{bot_username}",
                    )
                ]
            )

        buttons.append(
            [
                types.InlineKeyboardButton(
                    text="◀️ Назад", callback_data="back_to_whitelist"
                )
            ]
        )

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        msg = await send_message_with_auto_delete(
            bot=bot,
            chat_id=chat_id,
            text=(
                "➖ <b>Удаление бота из белого списка</b>\n\n"
                "Выберите бота для удаления:"
            ),
            config=config,
            reply_markup=keyboard,
        )
        await state.set_state(SettingsState.whitelist_remove)
        if msg:
            await state.update_data(last_message_id=msg.message_id)


async def handle_auto_delete_callback(
    callback: CallbackQuery, bot: Bot, state: FSMContext
):
    """Обработчик callback'ов автоудаления"""
    chat_id = callback.message.chat.id
    config = chat_settings[chat_id]

    await delete_message_silently(bot, chat_id, callback.message.message_id)

    if callback.data == "autodel_toggle":
        config.auto_delete.enabled = not config.auto_delete.enabled
        await show_auto_delete_settings(callback.message, bot, state)

    elif callback.data == "autodel_set_time":
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="◀️ Назад", callback_data="back_to_auto_delete"
                    )
                ]
            ]
        )

        msg = await send_message_with_auto_delete(
            bot=bot,
            chat_id=chat_id,
            text=(
                "⏱️ <b>Установка времени автоудаления</b>\n\n"
                "Введите время в секундах (от 5 до 3600)\n"
                "Например: <code>30</code> - удалить через 30 секунд"
            ),
            config=config,
            reply_markup=keyboard,
        )
        await state.set_state(SettingsState.auto_delete_time_set)
        if msg:
            await state.update_data(last_message_id=msg.message_id)
