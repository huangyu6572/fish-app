"""
测试 - UiHelpers UI辅助函数
"""

import pytest
from core.ui_helpers import (
    get_motivational_emoji,
    get_motivational_message,
    format_usage_progress,
    get_usage_color,
    REMINDER_COLORS,
    REMINDER_NAMES,
)
from core.reminder_types import ReminderType


class TestMotivationalEmoji:
    """激励Emoji测试"""

    def test_zero_reminders(self):
        assert get_motivational_emoji(0) == "😴"

    def test_few_reminders(self):
        assert get_motivational_emoji(1) == "🌱"
        assert get_motivational_emoji(2) == "🌱"

    def test_moderate_reminders(self):
        assert get_motivational_emoji(3) == "💪"
        assert get_motivational_emoji(5) == "💪"

    def test_many_reminders(self):
        assert get_motivational_emoji(6) == "🔥"
        assert get_motivational_emoji(9) == "🔥"

    def test_lots_of_reminders(self):
        assert get_motivational_emoji(10) == "🏆"
        assert get_motivational_emoji(100) == "🏆"


class TestMotivationalMessage:
    """激励文案测试"""

    def test_zero_total(self):
        msg = get_motivational_message(0, 0, 0, 0)
        assert "开启监控" in msg or "没有" in msg

    def test_drink_champion(self):
        msg = get_motivational_message(8, 0, 0, 8)
        assert "喝水达标" in msg

    def test_kegel_champion(self):
        msg = get_motivational_message(0, 5, 0, 5)
        assert "提肛达人" in msg

    def test_fish_too_much(self):
        msg = get_motivational_message(0, 0, 5, 5)
        assert "摸鱼" in msg

    def test_super_active(self):
        msg = get_motivational_message(4, 3, 4, 11)
        assert "11" in msg or "积极" in msg or "提醒" in msg

    def test_normal_case(self):
        msg = get_motivational_message(2, 1, 1, 4)
        assert msg.strip()  # 不为空即可

    def test_returns_string(self):
        msg = get_motivational_message(1, 1, 1, 3)
        assert isinstance(msg, str)


class TestFormatUsageProgress:
    """使用进度计算测试"""

    def test_zero_usage(self):
        assert format_usage_progress(0, 30) == 0.0

    def test_half_usage(self):
        assert format_usage_progress(15, 30) == pytest.approx(0.5)

    def test_full_usage(self):
        assert format_usage_progress(30, 30) == pytest.approx(1.0)

    def test_over_limit(self):
        assert format_usage_progress(60, 30) == 1.0  # 不超过1.0

    def test_zero_limit(self):
        assert format_usage_progress(10, 0) == 0.0

    def test_negative_limit(self):
        assert format_usage_progress(10, -5) == 0.0


class TestGetUsageColor:
    """进度颜色测试"""

    def test_safe_color(self):
        color = get_usage_color(0.3)
        assert color == "#2EC4B6"

    def test_warning_color(self):
        color = get_usage_color(0.6)
        assert color == "#FFA62B"

    def test_danger_color(self):
        color = get_usage_color(0.9)
        assert color == "#FF4757"

    def test_zero_progress(self):
        color = get_usage_color(0.0)
        assert color == "#2EC4B6"

    def test_full_progress(self):
        color = get_usage_color(1.0)
        assert color == "#FF4757"


class TestReminderColors:
    """提醒颜色配置测试"""

    def test_all_types_have_colors(self):
        for t in ReminderType:
            assert t in REMINDER_COLORS

    def test_colors_are_hex(self):
        for color in REMINDER_COLORS.values():
            assert color.startswith("#")
            assert len(color) == 7


class TestReminderNames:
    """提醒中文名测试"""

    def test_all_types_have_names(self):
        for t in ReminderType:
            assert t in REMINDER_NAMES

    def test_names_are_non_empty(self):
        for name in REMINDER_NAMES.values():
            assert name.strip()
