"""
手机端进程监控 - 模拟接口
Android 端需要通过 UsageStats API 获取应用使用信息，
但在开发阶段提供与 ProcessMonitor 兼容的接口用于桌面调试。
真机运行时通过 pyjnius 调用 Android UsageStatsManager。
"""

import platform
import time
from dataclasses import dataclass
from typing import Dict, Optional

from core.process_monitor import UsageRecord, MONITORED_APPS


class MobileMonitor:
    """
    手机端应用监控器
    提供与 ProcessMonitor 相同的接口，
    桌面端使用 psutil 模拟，Android 端使用 UsageStats API。
    """

    def __init__(self):
        self._usage_records: Dict[str, UsageRecord] = {}
        self._last_check_time: float = time.time()
        self._is_android = self._check_android()

        # 初始化所有监控应用的记录
        for app_key, app_info in MONITORED_APPS.items():
            self._usage_records[app_key] = UsageRecord(app_name=app_info.display_name)

    @staticmethod
    def _check_android() -> bool:
        """检测是否在 Android 环境"""
        try:
            import android  # noqa: F401
            return True
        except ImportError:
            pass
        # Kivy on Android 也可以通过平台检查
        return platform.system() == 'Linux' and hasattr(platform, 'android_ver')

    def update(self):
        """
        更新使用时间统计
        桌面端：尝试用 psutil 扫描进程
        Android 端：查询 UsageStatsManager
        """
        current_time = time.time()
        elapsed = current_time - self._last_check_time
        self._last_check_time = current_time

        if self._is_android:
            self._update_android(elapsed)
        else:
            self._update_desktop(elapsed)

    def _update_desktop(self, elapsed: float):
        """桌面环境下使用 psutil 模拟"""
        try:
            import psutil
            running = []
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info.get('name', '')
                    if name:
                        running.append(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied,
                        psutil.ZombieProcess):
                    continue

            for app_key, app_info in MONITORED_APPS.items():
                record = self._usage_records[app_key]
                is_running = any(p in running for p in app_info.process_names)
                if is_running:
                    record.total_seconds += elapsed
                    record.is_running = True
                else:
                    record.is_running = False

        except ImportError:
            # psutil 不可用，跳过
            pass

    def _update_android(self, elapsed: float):
        """Android 端通过 UsageStats API 获取应用使用时间"""
        try:
            from jnius import autoclass

            Context = autoclass('android.content.Context')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            UsageStatsManager = autoclass(
                'android.app.usage.UsageStatsManager'
            )

            activity = PythonActivity.mActivity
            usm = activity.getSystemService(Context.USAGE_STATS_SERVICE)

            # 查询过去 24 小时
            end_time = int(time.time() * 1000)
            start_time = end_time - 24 * 60 * 60 * 1000

            stats = usm.queryUsageStats(
                UsageStatsManager.INTERVAL_DAILY, start_time, end_time
            )

            # Android 包名映射
            package_map = {
                "com.tencent.mm": "wechat",
                "com.ss.android.ugc.aweme": "douyin",
                "tv.danmaku.bili": "bilibili",
                "com.tencent.mobileqq": "qq",
            }

            if stats:
                for stat in stats.toArray():
                    pkg = stat.getPackageName()
                    app_key = package_map.get(pkg)
                    if app_key and app_key in self._usage_records:
                        total_ms = stat.getTotalTimeInForeground()
                        self._usage_records[app_key].total_seconds = (
                            total_ms / 1000.0
                        )
        except Exception:
            # Android API 不可用时静默失败
            pass

    def get_usage(self, app_key: str) -> Optional[UsageRecord]:
        """获取指定应用的使用记录"""
        return self._usage_records.get(app_key)

    def get_all_usage(self) -> Dict[str, UsageRecord]:
        """获取所有应用的使用记录"""
        return self._usage_records.copy()

    def is_over_limit(self, app_key: str, limit_minutes: int) -> bool:
        """检查指定应用是否超过使用时间限制"""
        record = self._usage_records.get(app_key)
        if record is None:
            return False
        return record.total_minutes >= limit_minutes

    def reset_all(self):
        """重置所有使用记录"""
        for record in self._usage_records.values():
            record.total_seconds = 0.0
            record.start_time = 0.0
            record.is_running = False

    def get_running_processes(self):
        """兼容接口"""
        return []

    def check_app_running(self, app_key: str) -> bool:
        """兼容接口"""
        record = self._usage_records.get(app_key)
        return record.is_running if record else False
