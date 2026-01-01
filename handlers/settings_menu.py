# SPDX-License-Identifier: MIT
# Copyright (C) 2026 CodWiz

from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import types

from core.storage import chat_settings
from domain.states import SettingsState
from domain.models import DeleteMode
from domain.models import ChatConfig
from utils.helpers import send_message_with_auto_delete, delete_message_silently


async def show_settings_menu(message: Message, bot: Bot, state: FSMContext):
    """Показывает главное меню настроек"""
    chat_id = message.chat.id
    if chat_id not in chat_settings:
        chat_settings[chat_id] = ChatConfig()

    config = chat_settings[chat_id]

    is_disabled = config.time_range.mode == DeleteMode.DISABLED
    toggle_text = "🔴 Включить удаление" if is_disabled else "🟢 Выключить удаление"
    toggle_callback = "toggle_global_on" if is_disabled else "toggle_global_off"

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=toggle_text, callback_data=toggle_callback
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="⏰ Режим (Всегда/Таймер)", callback_data="settings_time"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="📋 Белый список", callback_data="settings_whitelist"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🗑️ Автоудаление ответов бота",
                    callback_data="settings_auto_delete",
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="📊 Статус", callback_data="settings_status"
                )
            ],
        ]
    )

    text = (
        "⚙️ <b>Главное меню настроек</b>\n\n"
        f"Текущие настройки:\n"
        f"• Режим удаления: <b>{config.time_range}</b>\n"
        f"• Белый список: <b>{len(config.whitelist)} ботов</b>\n"
        f"• Автоудаление ответов: <b>{config.auto_delete}</b>"
    )

    data = await state.get_data()
    if "last_message_id" in data:
        await delete_message_silently(bot, chat_id, data["last_message_id"])

    msg = await send_message_with_auto_delete(
        bot, chat_id, text, config, reply_markup=keyboard
    )

    await state.set_state(SettingsState.main_menu)
    if msg:
        await state.update_data(last_message_id=msg.message_id)


async def show_time_settings(message: Message, bot: Bot, state: FSMContext):
    """Показывает настройки времени"""
    chat_id = message.chat.id
    config = chat_settings[chat_id]
    time_range = config.time_range

    status_icon = "✅" if time_range.mode == DeleteMode.TIME_RANGE else "⚪"
    always_icon = "✅" if time_range.mode == DeleteMode.ALWAYS else "⚪"

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=f"{always_icon} Всегда удалять", callback_data="time_always"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=f"{status_icon} По промежутку времени",
                    callback_data="time_range",
                )
            ],
            [types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")],
        ]
    )

    text = (
        "⏰ <b>Настройка режима удаления</b>\n\n"
        f"Текущий режим: <b>{time_range}</b>\n"
        f"Начало: <b>{time_range.get_start_time().strftime('%H:%M')}</b>\n"
        f"Конец: <b>{time_range.get_end_time().strftime('%H:%M')}</b>\n\n"
        "Выберите режим работы:"
    )

    msg = await send_message_with_auto_delete(
        bot, chat_id, text, config, reply_markup=keyboard
    )
    await state.set_state(SettingsState.time_settings)
    if msg:
        await state.update_data(last_message_id=msg.message_id)


async def show_whitelist_menu(message: Message, bot: Bot, state: FSMContext):
    """Показывает меню белого списка"""
    chat_id = message.chat.id
    config = chat_settings[chat_id]

    whitelist_text = (
        "\n".join([f"• {bot}" for bot in config.whitelist])
        if config.whitelist
        else "Пусто"
    )

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="➕ Добавить бота/ботов", callback_data="whitelist_add"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="➖ Удалить бота", callback_data="whitelist_remove"
                )
            ],
            [types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")],
        ]
    )

    text = (
        "📋 <b>Управление белым списком</b>\n\n"
        f"Текущий список ({len(config.whitelist)}):\n{whitelist_text}"
    )

    msg = await send_message_with_auto_delete(
        bot, chat_id, text, config, reply_markup=keyboard
    )
    await state.set_state(SettingsState.whitelist_menu)
    if msg:
        await state.update_data(last_message_id=msg.message_id)


async def show_auto_delete_settings(message: Message, bot: Bot, state: FSMContext):
    """Показывает настройки автоудаления"""
    chat_id = message.chat.id
    config = chat_settings[chat_id]
    auto_del = config.auto_delete

    status_icon = "✅" if auto_del.enabled else "⚪"

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=f"{status_icon} {'Выключить' if auto_del.enabled else 'Включить'}",
                    callback_data="autodel_toggle",
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=f"⏱️ Установить время ({auto_del.delete_after} сек)",
                    callback_data="autodel_set_time",
                )
            ],
            [types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")],
        ]
    )

    text = (
        "🗑️ <b>Автоудаление сообщений бота</b>\n\n"
        f"Статус: <b>{'Включено' if auto_del.enabled else 'Выключено'}</b>\n"
        f"Время: <b>{auto_del.delete_after} секунд</b>\n\n"
        "Мои сообщения (меню, ответы) будут автоматически удаляться через указанное время, чтобы не засорять чат."
    )

    msg = await send_message_with_auto_delete(
        bot, chat_id, text, config, reply_markup=keyboard
    )
    await state.set_state(SettingsState.auto_delete_settings)
    if msg:
        await state.update_data(last_message_id=msg.message_id)


async def show_status(message: Message, bot: Bot, state: FSMContext):
    """Показывает статус всех настроек"""
    from datetime import datetime

    chat_id = message.chat.id
    config = chat_settings[chat_id]
    time_range = config.time_range

    is_active_now = time_range.should_delete_at(None)
    current_time = datetime.now().strftime("%H:%M")

    status_text = (
        "📊 <b>Статус бота</b>\n\n"
        f"<b>Настройки удаления:</b>\n"
        f"• Режим: {time_range}\n"
        f"• Диапазон: {time_range.get_start_time().strftime('%H:%M')} - "
        f"{time_range.get_end_time().strftime('%H:%M')}\n"
        f"• Текущее время сервера: {current_time}\n"
        f"• Удаление активно прямо сейчас: <b>{'✅ ДА' if is_active_now else '❌ НЕТ'}</b>\n\n"
        f"<b>Белый список:</b>\n"
        f"• Ботов в списке: {len(config.whitelist)}\n"
        f"• Примеры: {', '.join(config.whitelist[:3]) if config.whitelist else 'нет'}\n\n"
        f"<b>Автоудаление моих ответов:</b>\n"
        f"• Статус: {'✅ Включено' if config.auto_delete.enabled else '❌ Выключено'}\n"
        f"• Время: {config.auto_delete.delete_after} секунд"
    )

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
        ]
    )

    msg = await send_message_with_auto_delete(
        bot, chat_id, status_text, config, reply_markup=keyboard
    )
    await state.set_state(SettingsState.main_menu)
    if msg:
        await state.update_data(last_message_id=msg.message_id)
