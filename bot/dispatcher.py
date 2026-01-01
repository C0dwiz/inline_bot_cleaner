# SPDX-License-Identifier: MIT
# Copyright (C) 2026 CodWiz

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import StateFilter, Command

from handlers.commands import cmd_start, cmd_settings
from handlers.messages import handle_text_input, handle_all_messages
from handlers.callbacks import handle_settings_callback
from domain.states import SettingsState


def setup_dispatcher() -> Dispatcher:
    """Настройка диспетчера и регистрация всех обработчиков"""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_settings, Command("settings"))

    dp.message.register(handle_text_input, StateFilter(SettingsState))
    dp.message.register(handle_all_messages)

    dp.callback_query.register(handle_settings_callback)

    return dp
