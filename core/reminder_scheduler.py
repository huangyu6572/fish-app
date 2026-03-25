"""
提醒调度器 - 管理定时提醒和超时检测
"""

import time
import random
import threading
from datetime import datetime, date
from typing import Callable, Optional, List

from .reminder_types import ReminderType, REMINDER_CONFIGS
from .process_monitor import ProcessMonitor, MONITORED_APPS
from .settings_manager import SettingsManager


class ReminderScheduler:
    """
    提醒调度器
    负责定期检查应用使用时间和发送轮询提醒
    """

    def __init__(
        self,
        settings_manager: SettingsManager,
        process_monitor: ProcessMonitor,
        on_reminder: Optional[Callable] = None,
    ):
        self._settings = settings_manager
        self._monitor = process_monitor
        self._on_reminder = on_reminder

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._reminder_cycle = 0
        self._last_remind_time: float = 0
        self._alerted_apps: set = set()  # 已经提醒过超时的应用
        self._today: str = ""

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self):
        """启动调度器"""
        if self._running:
            return
        self._running = True
        self._last_remind_time = time.time()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    def _loop(self):
        """主循环"""
        while self._running:
            try:
                self._check_daily_reset()
                self._monitor.update()
                self._check_app_limits()
                self._check_periodic_reminder()
            except Exception as e:
                print(f"调度器错误: {e}")

            # 每10秒检查一次
            for _ in range(10):
                if not self._running:
                    break
                time.sleep(1)

    def _check_daily_reset(self):
        """检查是否需要日期重置"""
        today = date.today().isoformat()
        if self._today != today:
            self._today = today
            settings = self._settings.settings
            if settings.today_date != today:
                self._settings.reset_daily_stats()
                settings.today_date = today
                self._settings.save()
            self._alerted_apps.clear()

    def _check_app_limits(self):
        """检查各应用是否超过使用时间限制"""
        for app_key in MONITORED_APPS:
            limit = self._settings.get_app_limit(app_key)
            if self._monitor.is_over_limit(app_key, limit):
                if app_key not in self._alerted_apps:
                    self._alerted_apps.add(app_key)
                    app_info = MONITORED_APPS[app_key]
                    usage = self._monitor.get_usage(app_key)
                    msg = (
                        f"⚠️ {app_info.display_name}已使用 "
                        f"{usage.format_time()}，超过{limit}分钟限制！\n"
                        f"放下手机/电脑，休息一下吧~"
                    )
                    self._fire_reminder(ReminderType.FISH_TOUCH, custom_message=msg)
                    self._settings.increment_stat("today_fish_count")

    def _check_periodic_reminder(self):
        """检查是否到了定期提醒时间"""
        settings = self._settings.settings
        interval_seconds = settings.remind_interval * 60
        now = time.time()

        if now - self._last_remind_time >= interval_seconds:
            self._last_remind_time = now
            enabled_types = self._get_enabled_types()
            if enabled_types:
                self._reminder_cycle += 1
                current_type = enabled_types[self._reminder_cycle % len(enabled_types)]
                self._fire_reminder(current_type)

                # 更新统计
                stat_map = {
                    ReminderType.DRINK_WATER: "today_drink_count",
                    ReminderType.KEGEL: "today_kegel_count",
                    ReminderType.FISH_TOUCH: "today_fish_count",
                }
                stat_key = stat_map.get(current_type)
                if stat_key:
                    self._settings.increment_stat(stat_key)

    def _get_enabled_types(self) -> List[ReminderType]:
        """获取已启用的提醒类型"""
        settings = self._settings.settings
        types = []
        if settings.drink_water_enabled:
            types.append(ReminderType.DRINK_WATER)
        if settings.kegel_enabled:
            types.append(ReminderType.KEGEL)
        if settings.fish_touch_enabled:
            types.append(ReminderType.FISH_TOUCH)
        if settings.rest_eyes_enabled:
            types.append(ReminderType.REST_EYES)
        if settings.stretch_enabled:
            types.append(ReminderType.STRETCH)
        return types

    def _fire_reminder(
        self, reminder_type: ReminderType, custom_message: Optional[str] = None
    ):
        """触发提醒回调"""
        if self._on_reminder is None:
            return

        config = REMINDER_CONFIGS[reminder_type]
        message = custom_message or config.get_random_message()
        art = config.get_random_art()

        self._on_reminder(reminder_type, config.title, message, art)

    def trigger_test_reminder(self, reminder_type: Optional[ReminderType] = None):
        """手动触发测试提醒"""
        if reminder_type is None:
            reminder_type = random.choice(list(ReminderType))
        self._fire_reminder(reminder_type)
