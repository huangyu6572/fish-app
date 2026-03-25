"""
UI辅助函数
"""
from .reminder_types import ReminderType


# 提醒类型的颜色映射
REMINDER_COLORS = {
    ReminderType.DRINK_WATER: "#45B7D1",   # 水蓝
    ReminderType.KEGEL: "#FF6B9D",          # 粉红
    ReminderType.FISH_TOUCH: "#4ECDC4",     # 青绿
    ReminderType.REST_EYES: "#96CEB4",      # 浅绿
    ReminderType.STRETCH: "#FFEAA7",        # 浅黄
}

# 提醒类型中文名
REMINDER_NAMES = {
    ReminderType.DRINK_WATER: "喝水",
    ReminderType.KEGEL: "提肛",
    ReminderType.FISH_TOUCH: "摸鱼",
    ReminderType.REST_EYES: "护眼",
    ReminderType.STRETCH: "伸展",
}


def get_motivational_emoji(total_reminders: int) -> str:
    """根据提醒次数返回激励Emoji"""
    if total_reminders == 0:
        return "😴"
    elif total_reminders < 3:
        return "🌱"
    elif total_reminders < 6:
        return "💪"
    elif total_reminders < 10:
        return "🔥"
    else:
        return "🏆"


def get_motivational_message(
    drink_count: int,
    kegel_count: int,
    fish_count: int,
    total: int,
) -> str:
    """根据统计数据返回激励文案"""
    if total == 0:
        return "还没有提醒记录，快开启监控吧！"
    elif drink_count >= 8:
        return f"🎉 喝水达标！已喝{drink_count}杯水，水润一整天！"
    elif kegel_count >= 5:
        return f"💪 提肛达人！已完成{kegel_count}次提肛训练！"
    elif fish_count >= 5:
        return f"🐟 摸鱼被抓{fish_count}次了！老板在看着你！"
    elif total >= 10:
        return f"🏆 今日超级积极！已响应{total}次提醒！"
    else:
        return f"✨ 今日已完成{total}次健康提醒，继续加油！"


def format_usage_progress(minutes: int, limit: int) -> float:
    """计算使用进度百分比（0.0 ~ 1.0）"""
    if limit <= 0:
        return 0.0
    return min(1.0, minutes / limit)


def get_usage_color(progress: float) -> str:
    """根据进度返回颜色"""
    if progress < 0.5:
        return "#2EC4B6"   # 绿色-安全
    elif progress < 0.8:
        return "#FFA62B"   # 橙色-警告
    else:
        return "#FF4757"   # 红色-危险
