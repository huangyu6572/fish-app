"""
测试 - ReminderType 提醒类型和文案
"""

import pytest
from core.reminder_types import (
    ReminderType,
    ReminderConfig,
    REMINDER_CONFIGS,
    build_reminder_configs,
    DRINK_WATER_MESSAGES,
    KEGEL_MESSAGES,
    FISH_TOUCH_MESSAGES,
    REST_EYES_MESSAGES,
    STRETCH_MESSAGES,
    DRINK_WATER_ARTS,
    KEGEL_ARTS,
    FISH_TOUCH_ARTS,
    REST_EYES_ARTS,
    STRETCH_ARTS,
)


class TestReminderType:
    """提醒类型枚举测试"""

    def test_has_five_types(self):
        assert len(ReminderType) == 5

    def test_type_values_are_unique(self):
        values = [t.value for t in ReminderType]
        assert len(values) == len(set(values))

    def test_drink_water_value(self):
        assert ReminderType.DRINK_WATER.value == "drink_water"

    def test_kegel_value(self):
        assert ReminderType.KEGEL.value == "kegel"

    def test_fish_touch_value(self):
        assert ReminderType.FISH_TOUCH.value == "fish_touch"

    def test_rest_eyes_value(self):
        assert ReminderType.REST_EYES.value == "rest_eyes"

    def test_stretch_value(self):
        assert ReminderType.STRETCH.value == "stretch"


class TestReminderConfig:
    """提醒配置测试"""

    def test_config_creation(self):
        config = ReminderConfig(
            reminder_type=ReminderType.DRINK_WATER,
            title="Test",
            emoji="💧",
            description="test desc",
            funny_messages=["msg1", "msg2"],
            funny_arts=["art1", "art2"],
        )
        assert config.title == "Test"
        assert config.emoji == "💧"

    def test_get_random_message_returns_from_list(self):
        messages = ["msg1", "msg2", "msg3"]
        config = ReminderConfig(
            reminder_type=ReminderType.KEGEL,
            title="T",
            emoji="🍑",
            description="d",
            funny_messages=messages,
            funny_arts=["a"],
        )
        for _ in range(20):
            assert config.get_random_message() in messages

    def test_get_random_art_returns_from_list(self):
        arts = ["art1", "art2"]
        config = ReminderConfig(
            reminder_type=ReminderType.STRETCH,
            title="T",
            emoji="🧘",
            description="d",
            funny_messages=["m"],
            funny_arts=arts,
        )
        for _ in range(20):
            assert config.get_random_art() in arts


class TestReminderMessages:
    """搞怪文案测试"""

    def test_drink_water_messages_not_empty(self):
        assert len(DRINK_WATER_MESSAGES) >= 5

    def test_kegel_messages_not_empty(self):
        assert len(KEGEL_MESSAGES) >= 5

    def test_fish_touch_messages_not_empty(self):
        assert len(FISH_TOUCH_MESSAGES) >= 5

    def test_rest_eyes_messages_not_empty(self):
        assert len(REST_EYES_MESSAGES) >= 3

    def test_stretch_messages_not_empty(self):
        assert len(STRETCH_MESSAGES) >= 3

    def test_all_messages_are_non_blank(self):
        all_messages = (
            DRINK_WATER_MESSAGES
            + KEGEL_MESSAGES
            + FISH_TOUCH_MESSAGES
            + REST_EYES_MESSAGES
            + STRETCH_MESSAGES
        )
        for msg in all_messages:
            assert msg.strip(), f"Message should not be blank: '{msg}'"

    def test_no_duplicate_messages_within_type(self):
        for msgs in [
            DRINK_WATER_MESSAGES,
            KEGEL_MESSAGES,
            FISH_TOUCH_MESSAGES,
            REST_EYES_MESSAGES,
            STRETCH_MESSAGES,
        ]:
            assert len(msgs) == len(set(msgs)), "Messages should be unique"


class TestReminderArts:
    """搞怪Emoji Art测试"""

    def test_drink_water_arts_not_empty(self):
        assert len(DRINK_WATER_ARTS) >= 3

    def test_kegel_arts_not_empty(self):
        assert len(KEGEL_ARTS) >= 3

    def test_fish_touch_arts_not_empty(self):
        assert len(FISH_TOUCH_ARTS) >= 3

    def test_rest_eyes_arts_not_empty(self):
        assert len(REST_EYES_ARTS) >= 2

    def test_stretch_arts_not_empty(self):
        assert len(STRETCH_ARTS) >= 2

    def test_arts_are_multiline(self):
        all_arts = (
            DRINK_WATER_ARTS
            + KEGEL_ARTS
            + FISH_TOUCH_ARTS
            + REST_EYES_ARTS
            + STRETCH_ARTS
        )
        for art in all_arts:
            lines = [l for l in art.strip().split('\n') if l.strip()]
            assert len(lines) >= 3, f"Art should have at least 3 non-empty lines"

    def test_arts_are_non_blank(self):
        all_arts = (
            DRINK_WATER_ARTS
            + KEGEL_ARTS
            + FISH_TOUCH_ARTS
            + REST_EYES_ARTS
            + STRETCH_ARTS
        )
        for art in all_arts:
            assert art.strip(), "Art should not be blank"


class TestReminderConfigs:
    """全局配置字典测试"""

    def test_configs_has_all_types(self):
        for t in ReminderType:
            assert t in REMINDER_CONFIGS

    def test_each_config_has_title(self):
        for config in REMINDER_CONFIGS.values():
            assert config.title.strip()

    def test_each_config_has_emoji(self):
        for config in REMINDER_CONFIGS.values():
            assert config.emoji.strip()

    def test_each_config_has_messages(self):
        for config in REMINDER_CONFIGS.values():
            assert len(config.funny_messages) >= 2

    def test_each_config_has_arts(self):
        for config in REMINDER_CONFIGS.values():
            assert len(config.funny_arts) >= 2

    def test_build_reminder_configs_returns_dict(self):
        configs = build_reminder_configs()
        assert isinstance(configs, dict)
        assert len(configs) == 5
