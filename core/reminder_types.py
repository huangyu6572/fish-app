"""
提醒类型定义 - 包含搞怪文案和Emoji Art
"""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ReminderType(Enum):
    """提醒类型枚举"""
    DRINK_WATER = "drink_water"
    KEGEL = "kegel"
    FISH_TOUCH = "fish_touch"
    REST_EYES = "rest_eyes"
    STRETCH = "stretch"


@dataclass
class ReminderConfig:
    """单个提醒类型的配置"""
    reminder_type: ReminderType
    title: str
    emoji: str
    description: str
    funny_messages: List[str] = field(default_factory=list)
    funny_arts: List[str] = field(default_factory=list)

    def get_random_message(self) -> str:
        return random.choice(self.funny_messages)

    def get_random_art(self) -> str:
        return random.choice(self.funny_arts)


# ============================================================
# 搞怪文案库
# ============================================================

DRINK_WATER_MESSAGES = [
    "💧 你已经刷了好久了！再不喝水，你就要变成咸鱼干了！",
    "💧 水是生命之源，快去倒杯水！别等渴了才喝！",
    "💧 你的身体正在发出SOS信号：需要水分补给！",
    "💧 据说多喝水能变美/帅，你还等什么？",
    "💧 老板都喝了三杯水了，你还没动！",
    "💧 八杯水任务进度：■□□□□□□□ 快去补进度！",
    "💧 你的小鱼缸都快干了，快加水！🐟",
    "💧 喝水不积极，思想有问题！",
]

KEGEL_MESSAGES = [
    "🍑 提肛时间到！偷偷提一提，谁也不知道~",
    "🍑 悄悄提肛，惊艳所有人！坚持就是胜利！",
    "🍑 你的菊花在呼唤你：该运动了！",
    "🍑 提肛小达人上线！来，跟我一起：提~放~提~放~",
    "🍑 据说提肛能延年益寿，你今天提了吗？",
    "🍑 办公室最隐蔽的健身方式，没有之一！",
    "🍑 三二一，提！保持5秒...放！做得好！👏",
    "🍑 提肛一时爽，一直提肛一直爽！",
]

FISH_TOUCH_MESSAGES = [
    "🐟 你已经摸鱼太久了！老板在你身后！快切屏！",
    "🐟 摸鱼指数已达危险水平！建议立即回到工作状态！",
    "🐟 据可靠消息，老板正在巡视，请注意！",
    "🐟 你的摸鱼技能已经满级了，该练练工作技能了！",
    "🐟 系统检测到您正在高强度摸鱼中...",
    "🐟 这条鱼你已经摸了很久了，换条鱼摸摸？",
    "🐟 摸鱼虽好，可不要贪杯哦~",
    "🐟 摸鱼一时爽，绩效火葬场！",
]

REST_EYES_MESSAGES = [
    "👀 你的眼睛需要休息了！远眺20秒，看看窗外！",
    "👀 20-20-20法则：每20分钟，看20英尺外，持续20秒！",
    "👀 你的眼睛快要罢工了！快给它们放个假！",
    "👀 眨眨眼，转转眼球，放松一下！",
    "👀 如果你能看清这行字，说明你的眼睛还有救！",
]

STRETCH_MESSAGES = [
    "🧘 你已经坐了好久了！站起来伸个懒腰吧！",
    "🧘 久坐等于慢性自杀！快站起来活动活动！",
    "🧘 你的脊椎在向你发出抗议！站起来！",
    "🧘 来，跟我做：伸手臂~转脖子~扭腰~",
    "🧘 运动使人快乐，站起来嗨一下！💃",
]

# ============================================================
# 搞怪 ASCII Art / Emoji Art
# ============================================================

DRINK_WATER_ARTS = [
    r"""
╔══════════════════════╗
║   💧💧💧💧💧💧💧   ║
║   🥤 喝水啦！ 🥤    ║
║   💧💧💧💧💧💧💧   ║
║                      ║
║    ┌──────────┐      ║
║    │  ~~~~~~  │      ║
║    │  ~~~~~~  │      ║
║    │  ~~~~~~  │      ║
║    └──────────┘      ║
║  再不喝水就干了！    ║
╚══════════════════════╝
""",
    r"""
🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊
🐟  鱼都快渴死了！  🐟
🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊

      ( ^ω^)つ🥤

    快！喝！水！
""",
    r"""
⚠️  紧急补水通知  ⚠️

╭━━━━━━━━━━━━━━╮
┃  水分不足！    ┃
┃  ████░░░░░░░  ┃
┃     40%       ┃
╰━━━━━━━━━━━━━━╯

  🚰 马上去倒水！
""",
]

KEGEL_ARTS = [
    r"""
╔══════════════════════╗
║  🍑  提肛时间  🍑   ║
╠══════════════════════╣
║                      ║
║      ↑ 提！          ║
║      ↓ 放！          ║
║      ↑ 提！          ║
║      ↓ 放！          ║
║                      ║
║  坚持5组，加油！     ║
╚══════════════════════╝
""",
    r"""
🍑🍑🍑🍑🍑🍑🍑🍑🍑🍑

   提肛小课堂：

   1️⃣ 收紧 (3秒)
   2️⃣ 保持 (5秒)
   3️⃣ 放松 (3秒)
   4️⃣ 重复 5次

 没人知道你在做什么 😏
🍑🍑🍑🍑🍑🍑🍑🍑🍑🍑
""",
    r"""
┌─────────────────────┐
│   悄悄提肛           │
│   惊艳所有人         │
│                      │
│   (˶‾᷄ ⁻̫ ‾᷅˵)       │
│                      │
│   偷偷练，棒棒哒！   │
└─────────────────────┘
""",
]

FISH_TOUCH_ARTS = [
    r"""
🚨🚨🚨  警报！！  🚨🚨🚨

╔══════════════════════════╗
║  老板出现在走廊上！      ║
║                          ║
║    👔 ← 老板             ║
║    ↓                     ║
║   你的工位 → 🖥️💤       ║
║                          ║
║    快！切！屏！          ║
╚══════════════════════════╝
""",
    r"""
╭━━━━━━━━━━━━━━━━━━╮
┃  🐟  摸鱼指数     ┃
┃                    ┃
┃  ████████████████  ┃
┃      99.9%  ⚠️     ┃
┃                    ┃
┃  危险！即将被发现  ┃
╰━━━━━━━━━━━━━━━━━━╯
""",
    r"""
📡 摸鱼雷达扫描中...

        . · .
      ·  🐟  ·
    ·    |      ·
   ·   --|---    ·
    ·   YOU    ·
      ·      ·
        · ·

  检测到高级摸鱼行为！
""",
]

REST_EYES_ARTS = [
    r"""
╔══════════════════════╗
║  👁️ 护眼时间  👁️    ║
╠══════════════════════╣
║                      ║
║  (◉_◉) →  (—_—)     ║
║   睁眼      闭眼     ║
║                      ║
║  看看远处20秒        ║
║  转转眼球            ║
║  眨眨眼              ║
╚══════════════════════╝
""",
    r"""
⚠️ 视力保护模式激活 ⚠️

  你的用眼时间：
  ████████████  120%

    🔴 已超标！

 快看看窗外吧~ 🌳🌤️
""",
]

STRETCH_ARTS = [
    r"""
╔══════════════════════╗
║  🧘  伸展时间  🧘   ║
╠══════════════════════╣
║                      ║
║     \(^o^)/          ║
║       |  |           ║
║      / \             ║
║                      ║
║  站起来动一动！      ║
╚══════════════════════╝
""",
    r"""
💪 久坐预警 💪

你已连续坐了好久！

 脊椎：救救我！
 腰椎：我也是！
 颈椎：算我一个！

快站起来活动一下！🏃
""",
]


def build_reminder_configs() -> dict:
    """构建所有提醒配置"""
    return {
        ReminderType.DRINK_WATER: ReminderConfig(
            reminder_type=ReminderType.DRINK_WATER,
            title="喝水警告 ⚠️",
            emoji="💧",
            description="该喝水啦",
            funny_messages=DRINK_WATER_MESSAGES,
            funny_arts=DRINK_WATER_ARTS,
        ),
        ReminderType.KEGEL: ReminderConfig(
            reminder_type=ReminderType.KEGEL,
            title="提肛预警 🚨",
            emoji="🍑",
            description="提肛时间到",
            funny_messages=KEGEL_MESSAGES,
            funny_arts=KEGEL_ARTS,
        ),
        ReminderType.FISH_TOUCH: ReminderConfig(
            reminder_type=ReminderType.FISH_TOUCH,
            title="摸鱼雷达 📡",
            emoji="🐟",
            description="摸鱼提醒",
            funny_messages=FISH_TOUCH_MESSAGES,
            funny_arts=FISH_TOUCH_ARTS,
        ),
        ReminderType.REST_EYES: ReminderConfig(
            reminder_type=ReminderType.REST_EYES,
            title="护眼行动 🛡️",
            emoji="👀",
            description="休息眼睛",
            funny_messages=REST_EYES_MESSAGES,
            funny_arts=REST_EYES_ARTS,
        ),
        ReminderType.STRETCH: ReminderConfig(
            reminder_type=ReminderType.STRETCH,
            title="伸展运动 💪",
            emoji="🧘",
            description="站起来活动",
            funny_messages=STRETCH_MESSAGES,
            funny_arts=STRETCH_ARTS,
        ),
    }


REMINDER_CONFIGS = build_reminder_configs()
