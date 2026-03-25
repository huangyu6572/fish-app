"""
UI辅助函数 - 可爱搞怪风格 🐟
"""
import random
from .reminder_types import ReminderType


# 提醒类型的颜色映射（更鲜艳活泼）
REMINDER_COLORS = {
    ReminderType.DRINK_WATER: "#00B4D8",   # 清透蓝
    ReminderType.KEGEL: "#FF6B9D",          # 元气粉
    ReminderType.FISH_TOUCH: "#06D6A0",     # 摸鱼绿
    ReminderType.REST_EYES: "#8338EC",      # 梦幻紫
    ReminderType.STRETCH: "#FFB703",        # 活力橙
}

# 提醒类型中文名 + Emoji
REMINDER_NAMES = {
    ReminderType.DRINK_WATER: "💧 喝水",
    ReminderType.KEGEL: "🍑 提肛",
    ReminderType.FISH_TOUCH: "🐟 摸鱼",
    ReminderType.REST_EYES: "👀 护眼",
    ReminderType.STRETCH: "🧘 伸展",
}

# ── 可爱随机称呼 ──────────────────────────────
CUTE_NICKNAMES = [
    "小摸鱼的", "打工人", "卷王", "社畜宝宝", "摸鱼达人",
    "干饭人", "工位侠", "椅子长草星人", "咸鱼本鱼",
    "屏幕奴隶", "键盘侠", "格子间精灵", "PPT战士",
]

# ── 可爱加载语 ──────────────────────────────
CUTE_LOADING_MSGS = [
    "🐟 小鱼正在游过来...",
    "🍑 菊花正在热身...",
    "💧 水滴正在集合...",
    "🧘 关节正在抗议...",
    "👀 眼睛正在发出SOS...",
]

# ── 首页随机 slogan ──────────────────────────
HOME_SLOGANS = [
    "提肛喝水摸鱼，一个都不能少！",
    "今天你提肛了吗？(ノ>ω<)ノ",
    "摸鱼一时爽，一直摸鱼一直爽！",
    "多喝热水，包治百病 (˶‾᷄ ⁻̫ ‾᷅˵)",
    "每天提肛五分钟，快乐健康一辈子！",
    "偷偷提肛，惊艳所有人 ✧(≖ ◡ ≖✿)",
    "你已经坐了一万年了，站起来！",
    "老板走了，可以继续摸鱼了~",
    "喝水不积极，思想有问题！",
    "这是一个正经的健康提醒APP (才怪)",
]


def get_random_nickname() -> str:
    """随机可爱称呼"""
    return random.choice(CUTE_NICKNAMES)


def get_random_slogan() -> str:
    """随机首页标语"""
    return random.choice(HOME_SLOGANS)


def get_random_loading_msg() -> str:
    """随机加载提示"""
    return random.choice(CUTE_LOADING_MSGS)


def get_motivational_emoji(total_reminders: int) -> str:
    """根据提醒次数返回激励Emoji（更丰富）"""
    if total_reminders == 0:
        return "😴"
    elif total_reminders < 3:
        return random.choice(["🌱", "🐣", "🥚"])
    elif total_reminders < 6:
        return random.choice(["💪", "🔥", "⚡"])
    elif total_reminders < 10:
        return random.choice(["🏆", "🎉", "🌟"])
    elif total_reminders < 15:
        return random.choice(["�", "🦸", "💎"])
    else:
        return random.choice(["🐉", "🚀", "�"])


def get_motivational_message(
    drink_count: int,
    kegel_count: int,
    fish_count: int,
    total: int,
) -> str:
    """根据统计数据返回搞怪激励文案"""
    nickname = get_random_nickname()

    if total == 0:
        return f"嘿 {nickname}，还没有提醒记录\n快开启监控，开始摸鱼人生！🐟"
    elif drink_count >= 8:
        return f"🎉 {nickname}！喝水{drink_count}杯，你是行走的水库！💧"
    elif kegel_count >= 5:
        return f"💪 {nickname}提肛{kegel_count}次了！菊花都要冒烟了！🍑"
    elif fish_count >= 5:
        return f"🐟 {nickname}被抓摸鱼{fish_count}次！\n老板已经在磨刀了 🔪"
    elif total >= 15:
        return f"🚀 {nickname}今天响应{total}次提醒！你是全公司最健康的人！"
    elif total >= 10:
        return f"🏆 {nickname}今日{total}次提醒全部完成！\n升职加薪指日可待(才怪)！"
    else:
        return f"✨ {nickname}已完成{total}次健康提醒\n继续加油，今天也要元气满满！"


def get_daily_summary_text(drink: int, kegel: int, fish: int) -> str:
    """生成今日趣味小结"""
    total = drink + kegel + fish
    emoji = get_motivational_emoji(total)
    parts = []
    if drink > 0:
        parts.append(f"💧喝水{drink}杯")
    if kegel > 0:
        parts.append(f"🍑提肛{kegel}次")
    if fish > 0:
        parts.append(f"🐟摸鱼被抓{fish}次")

    if not parts:
        return f"{emoji} 今天还没有记录哦~\n快开启监控开始健康生活！"

    summary = " | ".join(parts)

    # 随机加个搞怪评价
    comments = [
        "继续保持！(ง •̀_•́)ง",
        "你是最棒的打工人！",
        "老板看了直呼内行！",
        "菊花感谢你的关爱！",
        "再接再厉，冲冲冲！",
        "今天也是元气满满的一天！",
        "摸鱼与健康两不误！",
    ]

    return f"{emoji} {summary}\n{random.choice(comments)}"


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


def get_usage_emoji(progress: float) -> str:
    """根据使用进度返回趣味Emoji"""
    if progress < 0.3:
        return "😊"
    elif progress < 0.5:
        return "🙂"
    elif progress < 0.7:
        return "😐"
    elif progress < 0.9:
        return "😰"
    else:
        return "🚨"
