"""
测试 - SettingsManager 设置管理
"""

import os
import json
import tempfile
import pytest
from core.settings_manager import SettingsManager, AppSettings


class TestAppSettings:
    """应用设置数据类测试"""

    def test_default_wechat_limit(self):
        s = AppSettings()
        assert s.wechat_limit == 30

    def test_default_douyin_limit(self):
        s = AppSettings()
        assert s.douyin_limit == 20

    def test_default_remind_interval(self):
        s = AppSettings()
        assert s.remind_interval == 15

    def test_default_monitor_disabled(self):
        s = AppSettings()
        assert s.monitor_enabled is False

    def test_default_sound_enabled(self):
        s = AppSettings()
        assert s.sound_enabled is True

    def test_default_all_reminders_enabled(self):
        s = AppSettings()
        assert s.drink_water_enabled is True
        assert s.kegel_enabled is True
        assert s.fish_touch_enabled is True
        assert s.rest_eyes_enabled is True
        assert s.stretch_enabled is True

    def test_default_stats_are_zero(self):
        s = AppSettings()
        assert s.today_drink_count == 0
        assert s.today_kegel_count == 0
        assert s.today_fish_count == 0

    def test_default_limits_are_positive(self):
        s = AppSettings()
        assert s.wechat_limit > 0
        assert s.douyin_limit > 0
        assert s.remind_interval > 0


class TestSettingsManager:
    """设置管理器测试"""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        return str(tmp_path / "test_config")

    @pytest.fixture
    def manager(self, temp_dir):
        return SettingsManager(config_dir=temp_dir)

    def test_creates_config_dir(self, temp_dir):
        SettingsManager(config_dir=temp_dir)
        assert os.path.isdir(temp_dir)

    def test_config_file_path(self, manager, temp_dir):
        expected = os.path.join(temp_dir, "fish_settings.json")
        assert manager.config_path == expected

    def test_default_settings(self, manager):
        s = manager.settings
        assert isinstance(s, AppSettings)
        assert s.wechat_limit == 30

    def test_save_and_load(self, temp_dir):
        manager = SettingsManager(config_dir=temp_dir)
        manager.settings.wechat_limit = 45
        manager.settings.douyin_limit = 10
        manager.save()

        # 重新加载
        manager2 = SettingsManager(config_dir=temp_dir)
        assert manager2.settings.wechat_limit == 45
        assert manager2.settings.douyin_limit == 10

    def test_save_creates_json_file(self, manager, temp_dir):
        manager.save()
        config_path = os.path.join(temp_dir, "fish_settings.json")
        assert os.path.exists(config_path)

        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert "wechat_limit" in data

    def test_load_with_missing_file(self, temp_dir):
        manager = SettingsManager(config_dir=temp_dir)
        s = manager.load()
        assert s.wechat_limit == 30  # 使用默认值

    def test_load_with_corrupted_file(self, temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
        config_path = os.path.join(temp_dir, "fish_settings.json")
        with open(config_path, 'w') as f:
            f.write("invalid json {{{")

        manager = SettingsManager(config_dir=temp_dir)
        assert manager.settings.wechat_limit == 30  # 使用默认值

    def test_load_with_partial_data(self, temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
        config_path = os.path.join(temp_dir, "fish_settings.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump({"wechat_limit": 99}, f)

        manager = SettingsManager(config_dir=temp_dir)
        assert manager.settings.wechat_limit == 99
        assert manager.settings.douyin_limit == 20  # 默认值保持

    def test_reset(self, manager):
        manager.settings.wechat_limit = 999
        manager.reset()
        assert manager.settings.wechat_limit == 30

    def test_reset_daily_stats(self, manager):
        manager.settings.today_drink_count = 10
        manager.settings.today_kegel_count = 5
        manager.settings.today_fish_count = 3
        manager.reset_daily_stats()
        assert manager.settings.today_drink_count == 0
        assert manager.settings.today_kegel_count == 0
        assert manager.settings.today_fish_count == 0

    def test_increment_stat(self, manager):
        assert manager.settings.today_drink_count == 0
        manager.increment_stat("today_drink_count")
        assert manager.settings.today_drink_count == 1
        manager.increment_stat("today_drink_count")
        assert manager.settings.today_drink_count == 2

    def test_get_app_limit(self, manager):
        assert manager.get_app_limit("wechat") == 30
        assert manager.get_app_limit("douyin") == 20

    def test_set_app_limit(self, manager):
        manager.set_app_limit("wechat", 60)
        assert manager.settings.wechat_limit == 60

    def test_set_app_limit_clamps_min(self, manager):
        manager.set_app_limit("wechat", -5)
        assert manager.settings.wechat_limit == 1

    def test_set_app_limit_clamps_max(self, manager):
        manager.set_app_limit("wechat", 9999)
        assert manager.settings.wechat_limit == 480

    def test_set_app_limit_nonexistent_key(self, manager):
        manager.set_app_limit("nonexistent", 50)
        # 应该不会报错，也不会改变什么
        assert not hasattr(manager.settings, "nonexistent_limit")
