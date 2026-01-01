# SPDX-License-Identifier: MIT
# Copyright (C) 2026 CodWiz

from dataclasses import dataclass, field
from datetime import time, datetime
from enum import Enum
from typing import Optional, Dict
import asyncio


class DeleteMode(Enum):
    ALWAYS = "always"
    TIME_RANGE = "time_range"
    DISABLED = "disabled"


@dataclass
class TimeRange:
    start_hour: int = 22
    start_minute: int = 0
    end_hour: int = 8
    end_minute: int = 0
    mode: DeleteMode = DeleteMode.ALWAYS

    def get_start_time(self) -> time:
        return time(self.start_hour, self.start_minute)

    def get_end_time(self) -> time:
        return time(self.end_hour, self.end_minute)

    def should_delete_at(self, check_time: Optional[time] = None) -> bool:
        if self.mode == DeleteMode.DISABLED:
            return False
        elif self.mode == DeleteMode.ALWAYS:
            return True
        elif self.mode == DeleteMode.TIME_RANGE:
            target_time = check_time if check_time else datetime.now().time()
            start_time = self.get_start_time()
            end_time = self.get_end_time()

            if start_time < end_time:
                return start_time <= target_time < end_time
            else:
                return target_time >= start_time or target_time < end_time
        return False

    def __str__(self) -> str:
        if self.mode == DeleteMode.ALWAYS:
            return "Всегда"
        elif self.mode == DeleteMode.DISABLED:
            return "Отключено"
        elif self.mode == DeleteMode.TIME_RANGE:
            start = self.get_start_time().strftime("%H:%M")
            end = self.get_end_time().strftime("%H:%M")
            return f"{start} - {end}"


@dataclass
class AutoDeleteSettings:
    enabled: bool = True
    delete_after: int = 30

    def __str__(self) -> str:
        if not self.enabled:
            return "Отключено"
        return f"{self.delete_after} секунд"


@dataclass
class ChatConfig:
    whitelist: list = field(default_factory=lambda: ["@gif", "@vid", "@music"])
    time_range: TimeRange = field(default_factory=TimeRange)
    auto_delete: AutoDeleteSettings = field(default_factory=AutoDeleteSettings)
    last_bot_message_id: Optional[int] = None
    message_tasks: Dict[int, asyncio.Task] = field(default_factory=dict)

    def is_whitelisted(self, bot_username: str) -> bool:
        if not bot_username:
            return False
        bot_lower = bot_username.lower()
        return any(whitelisted.lower() == bot_lower for whitelisted in self.whitelist)
