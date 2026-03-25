"""
测试 - ProcessMonitor 进程监控
"""

import pytest
from unittest.mock import patch, MagicMock
from core.process_monitor import (
    ProcessMonitor,
    AppInfo,
    UsageRecord,
    MONITORED_APPS,
)


class TestUsageRecord:
    """使用记录数据测试"""

    def test_default_values(self):
        record = UsageRecord(app_name="Test")
        assert record.app_name == "Test"
        assert record.total_seconds == 0.0
        assert record.is_running is False
        assert record.total_minutes == 0

    def test_total_minutes_calculation(self):
        record = UsageRecord(app_name="Test", total_seconds=150)
        assert record.total_minutes == 2  # 150秒 = 2分钟（取整）

    def test_total_minutes_rounds_down(self):
        record = UsageRecord(app_name="Test", total_seconds=179)
        assert record.total_minutes == 2  # 179秒 = 2分钟

    def test_format_time_minutes_only(self):
        record = UsageRecord(app_name="Test", total_seconds=1500)  # 25分钟
        assert record.format_time() == "25分钟"

    def test_format_time_hours_and_minutes(self):
        record = UsageRecord(app_name="Test", total_seconds=5400)  # 90分钟
        assert record.format_time() == "1小时30分钟"

    def test_format_time_zero(self):
        record = UsageRecord(app_name="Test", total_seconds=0)
        assert record.format_time() == "0分钟"

    def test_format_time_exact_hour(self):
        record = UsageRecord(app_name="Test", total_seconds=3600)  # 60分钟
        assert record.format_time() == "1小时0分钟"


class TestAppInfo:
    """应用信息测试"""

    def test_app_info_creation(self):
        info = AppInfo(
            name="test",
            process_names=["test.exe"],
            display_name="测试",
            icon_emoji="🔧",
        )
        assert info.name == "test"
        assert "test.exe" in info.process_names

    def test_monitored_apps_has_wechat(self):
        assert "wechat" in MONITORED_APPS
        assert MONITORED_APPS["wechat"].display_name == "微信"

    def test_monitored_apps_has_douyin(self):
        assert "douyin" in MONITORED_APPS
        assert MONITORED_APPS["douyin"].display_name == "抖音"

    def test_monitored_apps_has_qq(self):
        assert "qq" in MONITORED_APPS

    def test_monitored_apps_has_bilibili(self):
        assert "bilibili" in MONITORED_APPS

    def test_each_app_has_process_names(self):
        for key, info in MONITORED_APPS.items():
            assert len(info.process_names) > 0, f"{key} should have process names"

    def test_each_app_has_emoji(self):
        for key, info in MONITORED_APPS.items():
            assert info.icon_emoji.strip(), f"{key} should have icon emoji"


class TestProcessMonitor:
    """进程监控器测试"""

    def test_init_creates_records_for_all_apps(self):
        monitor = ProcessMonitor()
        usage = monitor.get_all_usage()
        for app_key in MONITORED_APPS:
            assert app_key in usage

    def test_get_usage_returns_record(self):
        monitor = ProcessMonitor()
        record = monitor.get_usage("wechat")
        assert record is not None
        assert isinstance(record, UsageRecord)

    def test_get_usage_unknown_app_returns_none(self):
        monitor = ProcessMonitor()
        assert monitor.get_usage("unknown_app") is None

    def test_is_over_limit_false_initially(self):
        monitor = ProcessMonitor()
        assert monitor.is_over_limit("wechat", 30) is False

    def test_is_over_limit_true_when_exceeded(self):
        monitor = ProcessMonitor()
        record = monitor.get_usage("wechat")
        record.total_seconds = 1800 + 60  # 31分钟
        assert monitor.is_over_limit("wechat", 30) is True

    def test_is_over_limit_unknown_app(self):
        monitor = ProcessMonitor()
        assert monitor.is_over_limit("nonexist", 10) is False

    def test_reset_all(self):
        monitor = ProcessMonitor()
        record = monitor.get_usage("wechat")
        record.total_seconds = 999
        record.is_running = True

        monitor.reset_all()

        record = monitor.get_usage("wechat")
        assert record.total_seconds == 0.0
        assert record.is_running is False

    def test_reset_app(self):
        monitor = ProcessMonitor()
        record = monitor.get_usage("douyin")
        record.total_seconds = 500

        monitor.reset_app("douyin")

        record = monitor.get_usage("douyin")
        assert record.total_seconds == 0.0

    @patch.object(ProcessMonitor, 'get_running_processes')
    def test_check_app_running_true(self, mock_procs):
        mock_procs.return_value = ["WeChat.exe", "explorer.exe"]
        monitor = ProcessMonitor()
        assert monitor.check_app_running("wechat") is True

    @patch.object(ProcessMonitor, 'get_running_processes')
    def test_check_app_running_false(self, mock_procs):
        mock_procs.return_value = ["explorer.exe", "chrome.exe"]
        monitor = ProcessMonitor()
        assert monitor.check_app_running("wechat") is False

    @patch.object(ProcessMonitor, 'get_running_processes')
    def test_update_adds_time_when_running(self, mock_procs):
        mock_procs.return_value = ["WeChat.exe"]
        monitor = ProcessMonitor()

        # 模拟经过10秒
        import time
        monitor._last_check_time = time.time() - 10
        monitor.update()

        record = monitor.get_usage("wechat")
        assert record.total_seconds >= 9  # 允许小误差
        assert record.is_running is True

    @patch.object(ProcessMonitor, 'get_running_processes')
    def test_update_no_time_when_not_running(self, mock_procs):
        mock_procs.return_value = ["explorer.exe"]
        monitor = ProcessMonitor()
        monitor.update()

        record = monitor.get_usage("wechat")
        # 应该接近0（可能有微小的初始化时间差）
        assert record.total_seconds < 1
        assert record.is_running is False

    def test_get_all_usage_returns_copy(self):
        monitor = ProcessMonitor()
        usage1 = monitor.get_all_usage()
        usage2 = monitor.get_all_usage()
        assert usage1 is not usage2  # 应该是副本
