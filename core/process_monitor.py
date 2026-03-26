"""
进程监控模块 - 监控微信、抖音等应用的使用时间
跨平台支持 Windows / macOS / Linux
"""

import time
import platform
from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    import psutil
except ImportError:
    psutil = None  # Android 环境无 psutil


@dataclass
class AppInfo:
    """应用信息"""
    name: str
    process_names: List[str]  # 不同平台可能名称不同
    display_name: str
    icon_emoji: str


@dataclass
class UsageRecord:
    """使用时间记录"""
    app_name: str
    start_time: float = 0.0
    total_seconds: float = 0.0
    is_running: bool = False

    @property
    def total_minutes(self) -> int:
        return int(self.total_seconds / 60)

    def format_time(self) -> str:
        """格式化显示时间"""
        minutes = self.total_minutes
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0:
            return f"{hours}小时{mins}分钟"
        return f"{mins}分钟"


# 监控的应用列表 - 跨平台兼容
MONITORED_APPS: Dict[str, AppInfo] = {
    "wechat": AppInfo(
        name="wechat",
        process_names=["WeChat.exe", "WeChat", "wechat", "com.tencent.mm"],
        display_name="微信",
        icon_emoji="💬",
    ),
    "douyin": AppInfo(
        name="douyin",
        process_names=[
            "Douyin.exe", "douyin", "抖音.exe",
            # 抖音PC版 / 网页版浏览器进程中无法精确匹配，此处列出常见名
            "DouYin.exe", "com.ss.android.ugc.aweme",
        ],
        display_name="抖音",
        icon_emoji="🎵",
    ),
    "bilibili": AppInfo(
        name="bilibili",
        process_names=["bili_app.exe", "bilibili", "Bilibili.exe"],
        display_name="哔哩哔哩",
        icon_emoji="📺",
    ),
    "qq": AppInfo(
        name="qq",
        process_names=["QQ.exe", "qq", "QQ"],
        display_name="QQ",
        icon_emoji="🐧",
    ),
}


class ProcessMonitor:
    """
    进程监控器
    定期扫描运行中的进程，统计各应用使用时间
    """

    def __init__(self):
        self._usage_records: Dict[str, UsageRecord] = {}
        self._last_check_time: float = time.time()
        self._system = platform.system()

        # 初始化所有监控应用的记录
        for app_key, app_info in MONITORED_APPS.items():
            self._usage_records[app_key] = UsageRecord(app_name=app_info.display_name)

    def get_running_processes(self) -> List[str]:
        """获取当前运行中的进程名列表"""
        if psutil is None:
            return []
        process_names = []
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info.get('name', '')
                    if name:
                        process_names.append(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception:
            pass
        return process_names

    def check_app_running(self, app_key: str) -> bool:
        """检查指定应用是否在运行"""
        if app_key not in MONITORED_APPS:
            return False

        app_info = MONITORED_APPS[app_key]
        running_processes = self.get_running_processes()

        for proc_name in app_info.process_names:
            if proc_name in running_processes:
                return True
        return False

    def update(self):
        """
        更新使用时间统计
        应定期调用此方法（建议每10-30秒一次）
        """
        current_time = time.time()
        elapsed = current_time - self._last_check_time
        self._last_check_time = current_time

        running_processes = self.get_running_processes()

        for app_key, app_info in MONITORED_APPS.items():
            record = self._usage_records[app_key]
            is_running = any(p in running_processes for p in app_info.process_names)

            if is_running:
                if not record.is_running:
                    # 刚开始运行
                    record.start_time = current_time
                record.total_seconds += elapsed
                record.is_running = True
            else:
                record.is_running = False

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
        """重置所有使用记录（每日重置）"""
        for record in self._usage_records.values():
            record.total_seconds = 0.0
            record.start_time = 0.0
            record.is_running = False

    def reset_app(self, app_key: str):
        """重置指定应用的使用记录"""
        if app_key in self._usage_records:
            record = self._usage_records[app_key]
            record.total_seconds = 0.0
            record.start_time = 0.0
            record.is_running = False
