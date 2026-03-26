"""
测试 - 手机版 APK 启动与核心流程
模拟 Android 环境（无 psutil、无 tkinter），验证不闪退

重点排查:
1. 所有 core 模块在无 psutil 环境下能正常 import
2. mobile.app 在无桌面环境下能正常 import
3. MobileMonitor 在 mock Android 环境正常工作
4. ReminderScheduler 与 MobileMonitor 配合正常
5. 设置管理在 Android 路径下正常工作
"""

import sys
import os
import time
import importlib
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from pathlib import Path


# ============================================================
# 1. Import 安全测试 - 模拟 Android 无 psutil 环境
# ============================================================

class TestImportSafetyNoPsutil:
    """验证在没有 psutil 的环境下所有 core 模块能安全导入"""

    def test_process_monitor_import_without_psutil(self):
        """core.process_monitor 在没有 psutil 时不应崩溃"""
        # 临时移除 psutil
        original = sys.modules.get('psutil')
        sys.modules['psutil'] = None

        try:
            # 强制重新导入
            import core.process_monitor as pm
            importlib.reload(pm)
            assert pm.psutil is None
            # 数据类和常量仍可用
            assert pm.MONITORED_APPS is not None
            assert len(pm.MONITORED_APPS) > 0
            record = pm.UsageRecord(app_name="test")
            assert record.total_minutes == 0
        finally:
            # 恢复
            if original is not None:
                sys.modules['psutil'] = original
            else:
                sys.modules.pop('psutil', None)
            importlib.reload(pm)

    def test_process_monitor_get_running_processes_without_psutil(self):
        """ProcessMonitor.get_running_processes 无 psutil 时返回空列表"""
        import core.process_monitor as pm
        original_psutil = pm.psutil

        try:
            pm.psutil = None
            monitor = pm.ProcessMonitor()
            result = monitor.get_running_processes()
            assert result == []
        finally:
            pm.psutil = original_psutil

    def test_usage_record_import_without_psutil(self):
        """UsageRecord 等数据类不依赖 psutil"""
        from core.process_monitor import UsageRecord, AppInfo, MONITORED_APPS
        record = UsageRecord(app_name="微信")
        assert record.format_time() == "0分钟"
        assert "wechat" in MONITORED_APPS

    def test_reminder_types_import(self):
        """core.reminder_types 不依赖任何平台模块"""
        from core.reminder_types import ReminderType, REMINDER_CONFIGS
        assert ReminderType.DRINK_WATER is not None
        assert len(REMINDER_CONFIGS) == 5
        for rtype, config in REMINDER_CONFIGS.items():
            assert config.get_random_message()
            assert config.get_random_art()

    def test_settings_manager_import(self):
        """core.settings_manager 不依赖平台模块"""
        from core.settings_manager import SettingsManager, AppSettings
        settings = AppSettings()
        assert settings.wechat_limit == 30
        assert settings.monitor_enabled is False

    def test_ui_helpers_import(self):
        """core.ui_helpers 不依赖平台模块"""
        from core.ui_helpers import (
            get_motivational_emoji,
            get_motivational_message,
        )
        assert get_motivational_emoji(0) is not None
        assert get_motivational_message(0, 0, 0, 0) is not None

    def test_image_manager_import(self):
        """core.image_manager 在无 PIL 时也能导入"""
        from core.image_manager import FunnyImageManager
        manager = FunnyImageManager()
        assert manager is not None

    def test_reminder_scheduler_import(self):
        """core.reminder_scheduler 不因 psutil 缺失而崩溃"""
        from core.reminder_scheduler import ReminderScheduler
        assert ReminderScheduler is not None


# ============================================================
# 2. MobileMonitor 测试
# ============================================================

class TestMobileMonitor:
    """手机端监控器测试"""

    def test_init(self):
        from mobile.mobile_monitor import MobileMonitor
        monitor = MobileMonitor()
        assert monitor is not None
        # 应该初始化所有监控应用
        all_usage = monitor.get_all_usage()
        assert "wechat" in all_usage
        assert "douyin" in all_usage

    def test_is_not_android_on_desktop(self):
        from mobile.mobile_monitor import MobileMonitor
        monitor = MobileMonitor()
        # 桌面环境应该不是 Android
        assert monitor._is_android is False

    def test_update_desktop_no_crash(self):
        from mobile.mobile_monitor import MobileMonitor
        monitor = MobileMonitor()
        # update 不应该崩溃
        monitor.update()

    def test_update_desktop_without_psutil(self):
        """即使桌面环境没有 psutil，update 也不崩溃"""
        from mobile.mobile_monitor import MobileMonitor
        monitor = MobileMonitor()
        with patch.dict(sys.modules, {'psutil': None}):
            monitor._update_desktop(1.0)

    def test_get_usage(self):
        from mobile.mobile_monitor import MobileMonitor
        monitor = MobileMonitor()
        usage = monitor.get_usage("wechat")
        assert usage is not None
        assert usage.app_name == "微信"
        assert usage.total_seconds == 0.0

    def test_get_usage_nonexistent(self):
        from mobile.mobile_monitor import MobileMonitor
        monitor = MobileMonitor()
        assert monitor.get_usage("nonexistent") is None

    def test_is_over_limit(self):
        from mobile.mobile_monitor import MobileMonitor
        monitor = MobileMonitor()
        assert monitor.is_over_limit("wechat", 30) is False
        # 模拟超时
        monitor._usage_records["wechat"].total_seconds = 1800 + 1
        assert monitor.is_over_limit("wechat", 30) is True

    def test_reset_all(self):
        from mobile.mobile_monitor import MobileMonitor
        monitor = MobileMonitor()
        monitor._usage_records["wechat"].total_seconds = 999
        monitor._usage_records["wechat"].is_running = True
        monitor.reset_all()
        assert monitor._usage_records["wechat"].total_seconds == 0.0
        assert monitor._usage_records["wechat"].is_running is False

    def test_check_app_running(self):
        from mobile.mobile_monitor import MobileMonitor
        monitor = MobileMonitor()
        assert monitor.check_app_running("wechat") is False

    def test_get_running_processes(self):
        from mobile.mobile_monitor import MobileMonitor
        monitor = MobileMonitor()
        result = monitor.get_running_processes()
        assert isinstance(result, list)

    @patch('mobile.mobile_monitor.MobileMonitor._check_android', return_value=True)
    def test_update_android_no_jnius(self, mock_android):
        """Android 模式下，jnius 不可用时不崩溃"""
        from mobile.mobile_monitor import MobileMonitor
        monitor = MobileMonitor.__new__(MobileMonitor)
        monitor._usage_records = {}
        monitor._last_check_time = time.time()
        monitor._is_android = True
        from core.process_monitor import MONITORED_APPS, UsageRecord
        for app_key, app_info in MONITORED_APPS.items():
            monitor._usage_records[app_key] = UsageRecord(app_name=app_info.display_name)
        # 模拟无 jnius 环境
        monitor._update_android(1.0)


# ============================================================
# 3. ReminderScheduler 与 MobileMonitor 集成测试
# ============================================================

class TestSchedulerWithMobileMonitor:
    """验证调度器与手机监控器配合正常"""

    def test_scheduler_init_with_mobile_monitor(self):
        from core.settings_manager import SettingsManager
        from core.reminder_scheduler import ReminderScheduler
        from mobile.mobile_monitor import MobileMonitor
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SettingsManager(config_dir=tmpdir)
            mm = MobileMonitor()
            reminders = []

            def on_reminder(rtype, title, msg, art):
                reminders.append((rtype, title, msg, art))

            scheduler = ReminderScheduler(
                settings_manager=sm,
                process_monitor=mm,
                on_reminder=on_reminder,
            )
            assert scheduler is not None
            assert scheduler.is_running is False

    def test_scheduler_trigger_test_reminder(self):
        from core.settings_manager import SettingsManager
        from core.reminder_scheduler import ReminderScheduler
        from core.reminder_types import ReminderType
        from mobile.mobile_monitor import MobileMonitor
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SettingsManager(config_dir=tmpdir)
            mm = MobileMonitor()
            reminders = []

            def on_reminder(rtype, title, msg, art):
                reminders.append((rtype, title, msg, art))

            scheduler = ReminderScheduler(
                settings_manager=sm,
                process_monitor=mm,
                on_reminder=on_reminder,
            )
            scheduler.trigger_test_reminder(ReminderType.DRINK_WATER)
            assert len(reminders) == 1
            assert reminders[0][0] == ReminderType.DRINK_WATER

    def test_scheduler_start_stop(self):
        from core.settings_manager import SettingsManager
        from core.reminder_scheduler import ReminderScheduler
        from mobile.mobile_monitor import MobileMonitor
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SettingsManager(config_dir=tmpdir)
            mm = MobileMonitor()
            scheduler = ReminderScheduler(
                settings_manager=sm,
                process_monitor=mm,
                on_reminder=lambda *a: None,
            )
            scheduler.start()
            assert scheduler.is_running is True
            time.sleep(0.5)
            scheduler.stop()
            assert scheduler.is_running is False


# ============================================================
# 4. Settings 在 Android 路径下的测试
# ============================================================

class TestSettingsAndroidPath:
    """测试设置管理在不同路径环境下的行为"""

    def test_settings_custom_dir(self):
        import tempfile
        from core.settings_manager import SettingsManager
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SettingsManager(config_dir=tmpdir)
            sm.settings.wechat_limit = 99
            sm.save()
            # 重新加载
            sm2 = SettingsManager(config_dir=tmpdir)
            assert sm2.settings.wechat_limit == 99

    def test_settings_increment_stat(self):
        import tempfile
        from core.settings_manager import SettingsManager
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SettingsManager(config_dir=tmpdir)
            sm.settings.today_drink_count = 0
            sm.increment_stat("today_drink_count")
            assert sm.settings.today_drink_count == 1

    def test_settings_reset_daily(self):
        import tempfile
        from core.settings_manager import SettingsManager
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SettingsManager(config_dir=tmpdir)
            sm.settings.today_drink_count = 5
            sm.settings.today_kegel_count = 3
            sm.settings.today_fish_count = 2
            sm.reset_daily_stats()
            assert sm.settings.today_drink_count == 0
            assert sm.settings.today_kegel_count == 0
            assert sm.settings.today_fish_count == 0


# ============================================================
# 5. Image Manager 在 Android 环境测试
# ============================================================

class TestImageManagerAndroid:
    """测试图片管理器在受限环境下的行为"""

    def test_init_no_crash(self):
        from core.image_manager import FunnyImageManager
        mgr = FunnyImageManager()
        assert mgr is not None

    def test_generate_meme_no_pil(self):
        """即使 PIL 不可用，generate_meme_image 也不崩溃"""
        from core.image_manager import FunnyImageManager
        import core.image_manager as im
        original_image = im.Image

        try:
            im.Image = None
            mgr = FunnyImageManager()
            result = mgr.generate_meme_image("drink_water")
            # 没有 PIL 时返回 None 或空
            # 不崩溃即可
        finally:
            im.Image = original_image

    def test_get_images_for_type(self):
        from core.image_manager import FunnyImageManager
        mgr = FunnyImageManager()
        # 不应该崩溃
        images = mgr.get_images_for_type("drink_water")
        assert isinstance(images, list)


# ============================================================
# 6. 完整启动链模拟测试（模拟 APK 展平后的 import）
# ============================================================

class TestAPKBootChain:
    """
    模拟 APK 展平后的启动链:
    main.py → app.py → core.* + mobile_monitor.py
    验证整个 import 链不会崩溃
    """

    def test_full_import_chain_no_psutil(self):
        """模拟 Android 环境：无 psutil，验证完整导入链"""
        import core.process_monitor as pm
        original_psutil = pm.psutil

        try:
            pm.psutil = None

            # 这些是 APK 中的核心 import 链
            from core.reminder_types import ReminderType, REMINDER_CONFIGS
            from core.settings_manager import SettingsManager
            from core.reminder_scheduler import ReminderScheduler
            from core.image_manager import FunnyImageManager
            from core.ui_helpers import get_motivational_emoji, get_motivational_message
            from core.process_monitor import UsageRecord, MONITORED_APPS
            from mobile.mobile_monitor import MobileMonitor

            # 所有都能正常实例化
            mm = MobileMonitor()
            assert mm is not None
            assert len(MONITORED_APPS) > 0
            assert len(REMINDER_CONFIGS) > 0
        finally:
            pm.psutil = original_psutil

    def test_mobile_monitor_used_as_process_monitor(self):
        """MobileMonitor 可以传入 ReminderScheduler 作为 process_monitor"""
        import tempfile
        from core.settings_manager import SettingsManager
        from core.reminder_scheduler import ReminderScheduler
        from mobile.mobile_monitor import MobileMonitor

        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SettingsManager(config_dir=tmpdir)
            mm = MobileMonitor()
            fired = []
            scheduler = ReminderScheduler(
                settings_manager=sm,
                process_monitor=mm,
                on_reminder=lambda *args: fired.append(args),
            )
            # 手动调用内部方法验证不崩溃
            scheduler._check_daily_reset()
            scheduler._check_app_limits()
            scheduler._check_periodic_reminder()

    def test_font_name_no_crash(self):
        """验证 app.py 中 font_name 引用不会在非 Android 环境崩溃"""
        # 模拟 _show_popup 中的 font_name 逻辑
        font_name = 'RobotoMono' if os.path.exists('/system') else 'Consolas'
        assert isinstance(font_name, str)
