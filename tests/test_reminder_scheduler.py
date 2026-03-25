"""
测试 - ReminderScheduler 提醒调度器
"""

import time
import pytest
from unittest.mock import MagicMock, patch
from core.reminder_scheduler import ReminderScheduler
from core.reminder_types import ReminderType, REMINDER_CONFIGS
from core.process_monitor import ProcessMonitor
from core.settings_manager import SettingsManager


class TestReminderScheduler:
    """提醒调度器测试"""

    @pytest.fixture
    def temp_settings(self, tmp_path):
        return SettingsManager(config_dir=str(tmp_path / "test_sched"))

    @pytest.fixture
    def monitor(self):
        return ProcessMonitor()

    @pytest.fixture
    def callback(self):
        return MagicMock()

    @pytest.fixture
    def scheduler(self, temp_settings, monitor, callback):
        return ReminderScheduler(
            settings_manager=temp_settings,
            process_monitor=monitor,
            on_reminder=callback,
        )

    def test_initial_state_not_running(self, scheduler):
        assert scheduler.is_running is False

    def test_start_sets_running(self, scheduler):
        scheduler.start()
        assert scheduler.is_running is True
        scheduler.stop()

    def test_stop_sets_not_running(self, scheduler):
        scheduler.start()
        scheduler.stop()
        assert scheduler.is_running is False

    def test_start_twice_is_safe(self, scheduler):
        scheduler.start()
        scheduler.start()  # 不应报错
        assert scheduler.is_running is True
        scheduler.stop()

    def test_stop_without_start_is_safe(self, scheduler):
        scheduler.stop()  # 不应报错
        assert scheduler.is_running is False

    def test_trigger_test_reminder_calls_callback(self, scheduler, callback):
        scheduler.trigger_test_reminder(ReminderType.DRINK_WATER)
        assert callback.called
        args = callback.call_args[0]
        assert args[0] == ReminderType.DRINK_WATER

    def test_trigger_test_reminder_random(self, scheduler, callback):
        scheduler.trigger_test_reminder(None)
        assert callback.called
        # 应该是某个有效的ReminderType
        assert callback.call_args[0][0] in ReminderType

    def test_trigger_test_reminder_all_types(self, scheduler, callback):
        for rtype in ReminderType:
            callback.reset_mock()
            scheduler.trigger_test_reminder(rtype)
            assert callback.called
            args = callback.call_args[0]
            assert args[0] == rtype
            assert isinstance(args[1], str)  # title
            assert isinstance(args[2], str)  # message
            assert isinstance(args[3], str)  # art

    def test_callback_receives_non_empty_content(self, scheduler, callback):
        scheduler.trigger_test_reminder(ReminderType.KEGEL)
        args = callback.call_args[0]
        _, title, message, art = args
        assert title.strip()
        assert message.strip()
        assert art.strip()

    def test_get_enabled_types_default(self, scheduler):
        # 需要访问私有方法进行测试
        enabled = scheduler._get_enabled_types()
        # 默认全部启用
        assert ReminderType.DRINK_WATER in enabled
        assert ReminderType.KEGEL in enabled
        assert ReminderType.FISH_TOUCH in enabled

    def test_get_enabled_types_with_disabled(self, scheduler, temp_settings):
        temp_settings.settings.drink_water_enabled = False
        enabled = scheduler._get_enabled_types()
        assert ReminderType.DRINK_WATER not in enabled
        assert ReminderType.KEGEL in enabled

    def test_check_app_limits_fires_on_over(self, scheduler, monitor, callback, temp_settings):
        # 设置微信限制为5分钟
        temp_settings.settings.wechat_limit = 5
        temp_settings.save()

        # 模拟微信使用了10分钟
        record = monitor.get_usage("wechat")
        record.total_seconds = 600  # 10分钟

        scheduler._check_app_limits()
        assert callback.called

    def test_check_app_limits_no_fire_under_limit(self, scheduler, monitor, callback, temp_settings):
        temp_settings.settings.wechat_limit = 30
        temp_settings.save()

        record = monitor.get_usage("wechat")
        record.total_seconds = 60  # 1分钟

        scheduler._check_app_limits()
        assert not callback.called

    def test_check_app_limits_alerts_only_once(self, scheduler, monitor, callback, temp_settings):
        temp_settings.settings.wechat_limit = 5
        temp_settings.save()

        record = monitor.get_usage("wechat")
        record.total_seconds = 600

        scheduler._check_app_limits()
        scheduler._check_app_limits()  # 第二次不应再次触发
        assert callback.call_count == 1


class TestSchedulerDailyReset:
    """调度器日重置测试"""

    @pytest.fixture
    def temp_settings(self, tmp_path):
        return SettingsManager(config_dir=str(tmp_path / "test_daily"))

    def test_daily_reset_clears_alerted_apps(self, temp_settings):
        monitor = ProcessMonitor()
        scheduler = ReminderScheduler(
            settings_manager=temp_settings,
            process_monitor=monitor,
        )
        scheduler._alerted_apps.add("wechat")
        scheduler._today = ""  # 强制重置
        scheduler._check_daily_reset()
        assert len(scheduler._alerted_apps) == 0
