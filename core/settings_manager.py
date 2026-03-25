"""
设置管理模块 - 保存和加载用户设置
使用JSON文件持久化
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path


@dataclass
class AppSettings:
    """应用设置"""
    # 时间限制（分钟）
    wechat_limit: int = 30
    douyin_limit: int = 20
    bilibili_limit: int = 30
    qq_limit: int = 30

    # 提醒间隔（分钟）
    remind_interval: int = 15

    # 开关
    monitor_enabled: bool = False
    sound_enabled: bool = True

    # 提醒类型开关
    drink_water_enabled: bool = True
    kegel_enabled: bool = True
    fish_touch_enabled: bool = True
    rest_eyes_enabled: bool = True
    stretch_enabled: bool = True

    # 今日统计
    today_drink_count: int = 0
    today_kegel_count: int = 0
    today_fish_count: int = 0
    today_date: str = ""

    # 窗口位置和大小
    window_x: int = 100
    window_y: int = 100
    window_width: int = 520
    window_height: int = 700

    # 主题
    theme: str = "cosmo"


class SettingsManager:
    """设置管理器"""

    DEFAULT_FILENAME = "fish_settings.json"

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            # 默认在用户目录下创建配置文件夹
            home = Path.home()
            config_dir = str(home / ".fish_assistant")

        self._config_dir = config_dir
        self._config_path = os.path.join(config_dir, self.DEFAULT_FILENAME)
        self._settings = AppSettings()

        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)

        # 加载设置
        self.load()

    @property
    def settings(self) -> AppSettings:
        return self._settings

    @property
    def config_path(self) -> str:
        return self._config_path

    def load(self) -> AppSettings:
        """从文件加载设置"""
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 只更新存在的字段，保持默认值兼容性
                for key, value in data.items():
                    if hasattr(self._settings, key):
                        setattr(self._settings, key, value)
        except (json.JSONDecodeError, IOError, OSError):
            # 文件损坏则使用默认设置
            self._settings = AppSettings()

        return self._settings

    def save(self):
        """保存设置到文件"""
        try:
            data = asdict(self._settings)
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (IOError, OSError) as e:
            print(f"保存设置失败: {e}")

    def reset(self):
        """重置为默认设置"""
        self._settings = AppSettings()
        self.save()

    def reset_daily_stats(self):
        """重置每日统计"""
        self._settings.today_drink_count = 0
        self._settings.today_kegel_count = 0
        self._settings.today_fish_count = 0
        self.save()

    def increment_stat(self, stat_name: str):
        """增加统计计数"""
        current = getattr(self._settings, stat_name, 0)
        setattr(self._settings, stat_name, current + 1)
        self.save()

    def get_app_limit(self, app_key: str) -> int:
        """获取指定应用的时间限制"""
        limit_key = f"{app_key}_limit"
        return getattr(self._settings, limit_key, 30)

    def set_app_limit(self, app_key: str, minutes: int):
        """设置指定应用的时间限制"""
        limit_key = f"{app_key}_limit"
        if hasattr(self._settings, limit_key):
            setattr(self._settings, limit_key, max(1, min(minutes, 480)))
            self.save()
