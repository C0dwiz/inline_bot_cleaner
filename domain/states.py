# SPDX-License-Identifier: MIT
# Copyright (C) 2026 CodWiz

from aiogram.fsm.state import State, StatesGroup


class SettingsState(StatesGroup):
    main_menu = State()
    time_settings = State()
    time_range_set_start = State()
    time_range_set_end = State()
    whitelist_menu = State()
    whitelist_add = State()
    whitelist_remove = State()
    auto_delete_settings = State()
    auto_delete_time_set = State()
