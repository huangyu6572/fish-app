"""
摸鱼小助手 - 手机版 Kivy UI
使用 KivyMD Material Design 风格
"""

import os
import random
import threading
import time
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty, ListProperty
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import get_color_from_hex

from core.reminder_types import ReminderType, REMINDER_CONFIGS
from core.settings_manager import SettingsManager
from core.reminder_scheduler import ReminderScheduler
from core.image_manager import FunnyImageManager
from core.ui_helpers import (
    get_motivational_emoji,
    get_motivational_message,
)

# 手机版进程监控（简化版，手机端无法直接监控其他App进程）
from mobile.mobile_monitor import MobileMonitor


# ── 颜色定义 ──────────────────────────────────

COLORS = {
    "primary": "#FF6B35",
    "primary_dark": "#E85D26",
    "secondary": "#2EC4B6",
    "background": "#FFF8F0",
    "surface": "#FFFFFF",
    "text": "#1A1A1A",
    "text_light": "#666666",
    "water_blue": "#45B7D1",
    "kegel_pink": "#FF6B9D",
    "fish_green": "#4ECDC4",
    "warning": "#FFA62B",
    "danger": "#FF4757",
}


# ── 首页 ──────────────────────────────────────

class HomeScreen(Screen):
    """首页"""

    status_text = StringProperty("⏸️ 未开启监控")
    summary_text = StringProperty("还没有提醒记录~")
    wechat_time = StringProperty("0分钟 / 30分钟")
    douyin_time = StringProperty("0分钟 / 20分钟")
    wechat_progress = NumericProperty(0)
    douyin_progress = NumericProperty(0)
    monitor_active = BooleanProperty(False)

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        # 标题
        title = Label(
            text="🐟 摸鱼小助手",
            font_size=dp(28),
            size_hint_y=None, height=dp(50),
            color=get_color_from_hex(COLORS["primary"]),
            bold=True,
        )
        layout.add_widget(title)

        subtitle = Label(
            text="提肛喝水摸鱼，一个都不能少！",
            font_size=dp(14),
            size_hint_y=None, height=dp(30),
            color=get_color_from_hex(COLORS["text_light"]),
        )
        layout.add_widget(subtitle)

        # 监控状态
        status_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None, height=dp(50),
            spacing=dp(10),
        )
        self.status_label = Label(
            text=self.status_text,
            font_size=dp(15),
            halign='left',
            color=get_color_from_hex(COLORS["text"]),
        )
        status_box.add_widget(self.status_label)

        self.toggle_btn = ToggleButton(
            text="开启监控",
            size_hint_x=0.4,
            background_color=get_color_from_hex(COLORS["secondary"]),
            on_press=self.toggle_monitor,
        )
        status_box.add_widget(self.toggle_btn)
        layout.add_widget(status_box)

        # 使用时间显示
        usage_label = Label(
            text="📱 应用使用时间",
            font_size=dp(16),
            size_hint_y=None, height=dp(35),
            bold=True,
            halign='left',
            color=get_color_from_hex(COLORS["text"]),
        )
        usage_label.bind(size=usage_label.setter('text_size'))
        layout.add_widget(usage_label)

        self.wechat_label = Label(
            text="💬 微信: " + self.wechat_time,
            font_size=dp(14),
            size_hint_y=None, height=dp(30),
            halign='left',
            color=get_color_from_hex(COLORS["text"]),
        )
        self.wechat_label.bind(size=self.wechat_label.setter('text_size'))
        layout.add_widget(self.wechat_label)

        self.douyin_label = Label(
            text="🎵 抖音: " + self.douyin_time,
            font_size=dp(14),
            size_hint_y=None, height=dp(30),
            halign='left',
            color=get_color_from_hex(COLORS["text"]),
        )
        self.douyin_label.bind(size=self.douyin_label.setter('text_size'))
        layout.add_widget(self.douyin_label)

        # 测试按钮区域
        test_label = Label(
            text="🎮 测试提醒",
            font_size=dp(16),
            size_hint_y=None, height=dp(35),
            bold=True, halign='left',
            color=get_color_from_hex(COLORS["text"]),
        )
        test_label.bind(size=test_label.setter('text_size'))
        layout.add_widget(test_label)

        btn_row1 = BoxLayout(
            orientation='horizontal',
            size_hint_y=None, height=dp(45),
            spacing=dp(8),
        )
        btn_configs = [
            ("💧 喝水", ReminderType.DRINK_WATER, COLORS["water_blue"]),
            ("🍑 提肛", ReminderType.KEGEL, COLORS["kegel_pink"]),
            ("🐟 摸鱼", ReminderType.FISH_TOUCH, COLORS["fish_green"]),
        ]
        for text, rtype, color in btn_configs:
            btn = Button(
                text=text,
                background_color=get_color_from_hex(color),
                font_size=dp(14),
                on_press=partial(self.test_reminder, rtype),
            )
            btn_row1.add_widget(btn)
        layout.add_widget(btn_row1)

        btn_row2 = BoxLayout(
            orientation='horizontal',
            size_hint_y=None, height=dp(45),
            spacing=dp(8),
        )
        btn_configs2 = [
            ("👀 护眼", ReminderType.REST_EYES, COLORS["warning"]),
            ("🧘 伸展", ReminderType.STRETCH, COLORS["text_light"]),
            ("🎲 随机", None, COLORS["primary"]),
        ]
        for text, rtype, color in btn_configs2:
            btn = Button(
                text=text,
                background_color=get_color_from_hex(color),
                font_size=dp(14),
                on_press=partial(self.test_reminder, rtype),
            )
            btn_row2.add_widget(btn)
        layout.add_widget(btn_row2)

        # 今日小结
        self.summary_lbl = Label(
            text=self.summary_text,
            font_size=dp(14),
            size_hint_y=None, height=dp(60),
            halign='center',
            color=get_color_from_hex(COLORS["text"]),
        )
        self.summary_lbl.bind(size=self.summary_lbl.setter('text_size'))
        layout.add_widget(self.summary_lbl)

        # 填充剩余空间
        layout.add_widget(BoxLayout())

        return layout

    def toggle_monitor(self, instance):
        app = App.get_running_app()
        self.monitor_active = not self.monitor_active
        if self.monitor_active:
            app.start_monitor()
            self.status_label.text = "✅ 监控运行中..."
            self.status_label.color = get_color_from_hex("#27ae60")
            instance.text = "关闭监控"
        else:
            app.stop_monitor()
            self.status_label.text = "⏸️ 未开启监控"
            self.status_label.color = get_color_from_hex(COLORS["text"])
            instance.text = "开启监控"

    def test_reminder(self, rtype, instance):
        app = App.get_running_app()
        app.trigger_test_reminder(rtype)

    def update_data(self, settings, monitor):
        s = settings.settings
        wechat_usage = monitor.get_usage("wechat")
        douyin_usage = monitor.get_usage("douyin")

        wt = wechat_usage.format_time() if wechat_usage else "0分钟"
        dt = douyin_usage.format_time() if douyin_usage else "0分钟"

        self.wechat_label.text = f"💬 微信: {wt} / {s.wechat_limit}分钟"
        self.douyin_label.text = f"🎵 抖音: {dt} / {s.douyin_limit}分钟"

        total = s.today_drink_count + s.today_kegel_count + s.today_fish_count
        emoji = get_motivational_emoji(total)
        self.summary_lbl.text = (
            f"{emoji} 今日：喝水{s.today_drink_count}次 | "
            f"提肛{s.today_kegel_count}次 | "
            f"摸鱼提醒{s.today_fish_count}次"
        )


# ── 统计页 ──────────────────────────────────────

class StatsScreen(Screen):
    """统计页面"""

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        title = Label(
            text="📊 今日统计",
            font_size=dp(24),
            size_hint_y=None, height=dp(45),
            bold=True,
            color=get_color_from_hex(COLORS["primary"]),
        )
        layout.add_widget(title)

        self.stat_labels = {}
        stats_config = [
            ("wechat_usage", "💬 微信使用", COLORS["primary"]),
            ("douyin_usage", "🎵 抖音使用", COLORS["danger"]),
            ("drink_count", "💧 喝水次数", COLORS["water_blue"]),
            ("kegel_count", "🍑 提肛次数", COLORS["kegel_pink"]),
            ("fish_count", "🐟 摸鱼提醒", COLORS["fish_green"]),
        ]
        for key, label_text, color in stats_config:
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None, height=dp(45),
            )
            name_lbl = Label(
                text=label_text,
                font_size=dp(16),
                halign='left',
                color=get_color_from_hex(COLORS["text"]),
            )
            name_lbl.bind(size=name_lbl.setter('text_size'))
            row.add_widget(name_lbl)

            val_lbl = Label(
                text="0",
                font_size=dp(20),
                bold=True,
                halign='right',
                color=get_color_from_hex(color),
            )
            val_lbl.bind(size=val_lbl.setter('text_size'))
            row.add_widget(val_lbl)
            self.stat_labels[key] = val_lbl
            layout.add_widget(row)

        # 激励区域
        self.motivation_emoji = Label(
            text="😴",
            font_size=dp(64),
            size_hint_y=None, height=dp(90),
        )
        layout.add_widget(self.motivation_emoji)

        self.motivation_text = Label(
            text="开启监控，开始健康之旅！",
            font_size=dp(14),
            size_hint_y=None, height=dp(40),
            halign='center',
            color=get_color_from_hex(COLORS["text"]),
        )
        self.motivation_text.bind(size=self.motivation_text.setter('text_size'))
        layout.add_widget(self.motivation_text)

        # 重置按钮
        reset_btn = Button(
            text="🔄 重置今日统计",
            size_hint_y=None, height=dp(45),
            background_color=get_color_from_hex(COLORS["danger"]),
            font_size=dp(14),
            on_press=self.reset_stats,
        )
        layout.add_widget(reset_btn)

        layout.add_widget(BoxLayout())
        return layout

    def reset_stats(self, instance):
        app = App.get_running_app()
        app.settings_manager.reset_daily_stats()
        app.mobile_monitor.reset_all()

    def update_data(self, settings, monitor):
        s = settings.settings
        wechat_usage = monitor.get_usage("wechat")
        douyin_usage = monitor.get_usage("douyin")

        self.stat_labels["wechat_usage"].text = (
            wechat_usage.format_time() if wechat_usage else "0分钟"
        )
        self.stat_labels["douyin_usage"].text = (
            douyin_usage.format_time() if douyin_usage else "0分钟"
        )
        self.stat_labels["drink_count"].text = str(s.today_drink_count)
        self.stat_labels["kegel_count"].text = str(s.today_kegel_count)
        self.stat_labels["fish_count"].text = str(s.today_fish_count)

        total = s.today_drink_count + s.today_kegel_count + s.today_fish_count
        self.motivation_emoji.text = get_motivational_emoji(total)
        self.motivation_text.text = get_motivational_message(
            s.today_drink_count, s.today_kegel_count, s.today_fish_count, total
        )


# ── 设置页 ──────────────────────────────────────

class SettingsScreen(Screen):
    """设置页面"""

    def build(self):
        scroll = ScrollView()
        layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
        )
        layout.bind(minimum_height=layout.setter('height'))

        title = Label(
            text="⚙️ 设置",
            font_size=dp(24),
            size_hint_y=None, height=dp(45),
            bold=True,
            color=get_color_from_hex(COLORS["primary"]),
        )
        layout.add_widget(title)

        # 时间限制
        layout.add_widget(self._section_label("⏱️ 使用时间限制"))

        app = App.get_running_app()
        s = app.settings_manager.settings

        self.wechat_slider = self._slider_row(
            "💬 微信上限", s.wechat_limit, 5, 120, "wechat_limit", layout
        )
        self.douyin_slider = self._slider_row(
            "🎵 抖音上限", s.douyin_limit, 5, 120, "douyin_limit", layout
        )
        self.interval_slider = self._slider_row(
            "⏰ 提醒间隔", s.remind_interval, 1, 60, "remind_interval", layout
        )

        # 提醒类型
        layout.add_widget(self._section_label("🔔 提醒类型"))

        self.toggle_configs = [
            ("💧 喝水提醒", "drink_water_enabled", s.drink_water_enabled),
            ("🍑 提肛提醒", "kegel_enabled", s.kegel_enabled),
            ("🐟 摸鱼提醒", "fish_touch_enabled", s.fish_touch_enabled),
            ("👀 护眼提醒", "rest_eyes_enabled", s.rest_eyes_enabled),
            ("🧘 伸展提醒", "stretch_enabled", s.stretch_enabled),
            ("🔊 提示音", "sound_enabled", s.sound_enabled),
        ]
        self.toggles = {}
        for label_text, key, default in self.toggle_configs:
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None, height=dp(45),
            )
            lbl = Label(
                text=label_text,
                font_size=dp(15),
                halign='left',
                color=get_color_from_hex(COLORS["text"]),
            )
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(lbl)

            toggle = ToggleButton(
                text="开" if default else "关",
                state='down' if default else 'normal',
                size_hint_x=0.25,
                font_size=dp(14),
                on_press=partial(self._on_toggle, key),
            )
            self.toggles[key] = toggle
            row.add_widget(toggle)
            layout.add_widget(row)

        # 版本信息
        ver_label = Label(
            text="摸鱼小助手 v1.0.0 | Python Kivy 手机版",
            font_size=dp(11),
            size_hint_y=None, height=dp(30),
            color=get_color_from_hex(COLORS["text_light"]),
        )
        layout.add_widget(ver_label)

        scroll.add_widget(layout)
        return scroll

    def _section_label(self, text):
        lbl = Label(
            text=text,
            font_size=dp(16),
            size_hint_y=None, height=dp(35),
            bold=True, halign='left',
            color=get_color_from_hex(COLORS["text"]),
        )
        lbl.bind(size=lbl.setter('text_size'))
        return lbl

    def _slider_row(self, label_text, value, min_val, max_val, setting_key, parent):
        row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None, height=dp(45),
            spacing=dp(5),
        )
        lbl = Label(
            text=label_text,
            font_size=dp(14),
            size_hint_x=0.35,
            halign='left',
            color=get_color_from_hex(COLORS["text"]),
        )
        lbl.bind(size=lbl.setter('text_size'))
        row.add_widget(lbl)

        slider = Slider(
            min=min_val, max=max_val, value=value, step=1,
            size_hint_x=0.45,
        )
        row.add_widget(slider)

        val_lbl = Label(
            text=f"{int(value)}分钟",
            font_size=dp(13),
            size_hint_x=0.2,
            halign='right',
            color=get_color_from_hex(COLORS["primary"]),
        )
        val_lbl.bind(size=val_lbl.setter('text_size'))
        row.add_widget(val_lbl)

        slider.bind(value=partial(self._on_slider, setting_key, val_lbl))
        parent.add_widget(row)
        return slider

    def _on_slider(self, setting_key, val_lbl, instance, value):
        val_lbl.text = f"{int(value)}分钟"
        app = App.get_running_app()
        setattr(app.settings_manager.settings, setting_key, int(value))
        app.settings_manager.save()

    def _on_toggle(self, setting_key, instance):
        is_on = instance.state == 'down'
        instance.text = "开" if is_on else "关"
        app = App.get_running_app()
        setattr(app.settings_manager.settings, setting_key, is_on)
        app.settings_manager.save()


# ── 主App ──────────────────────────────────────

class FishAssistantMobileApp(App):
    """摸鱼小助手 手机版"""

    title = "摸鱼小助手"

    def build(self):
        # 设置窗口背景色（桌面调试用）
        Window.clearcolor = get_color_from_hex(COLORS["background"])

        # 初始化核心组件
        self.settings_manager = SettingsManager()
        self.mobile_monitor = MobileMonitor()
        self.image_manager = FunnyImageManager()
        self.scheduler = ReminderScheduler(
            settings_manager=self.settings_manager,
            process_monitor=self.mobile_monitor,
            on_reminder=self._on_reminder,
        )

        # 构建标签页
        tab_panel = TabbedPanel(
            do_default_tab=False,
            tab_width=Window.width / 3 if Window.width > 0 else dp(120),
        )

        # 首页
        self.home_screen = HomeScreen(name='home')
        home_tab = TabbedPanelItem(text="🏠 首页")
        home_content = self.home_screen.build()
        home_tab.add_widget(home_content)
        tab_panel.add_widget(home_tab)

        # 统计
        self.stats_screen = StatsScreen(name='stats')
        stats_tab = TabbedPanelItem(text="📊 统计")
        stats_content = self.stats_screen.build()
        stats_tab.add_widget(stats_content)
        tab_panel.add_widget(stats_tab)

        # 设置
        self.settings_screen = SettingsScreen(name='settings')
        settings_tab = TabbedPanelItem(text="⚙️ 设置")
        settings_content = self.settings_screen.build()
        settings_tab.add_widget(settings_content)
        tab_panel.add_widget(settings_tab)

        # 定时更新UI
        Clock.schedule_interval(self._update_ui, 5)

        # 恢复监控状态
        if self.settings_manager.settings.monitor_enabled:
            self.start_monitor()
            self.home_screen.monitor_active = True

        return tab_panel

    def start_monitor(self):
        self.settings_manager.settings.monitor_enabled = True
        self.settings_manager.save()
        self.scheduler.start()

    def stop_monitor(self):
        self.settings_manager.settings.monitor_enabled = False
        self.settings_manager.save()
        self.scheduler.stop()

    def trigger_test_reminder(self, rtype=None):
        self.scheduler.trigger_test_reminder(rtype)

    def _on_reminder(self, reminder_type, title, message, art):
        """提醒回调 - 在主线程显示弹窗"""
        Clock.schedule_once(
            partial(self._show_popup, reminder_type, title, message, art), 0
        )

    def _show_popup(self, reminder_type, title, message, art, dt=None):
        """显示搞怪提醒弹窗 - 表情包图片 + ASCII Art"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # 表情包图片
        type_key = reminder_type.value if hasattr(reminder_type, 'value') else str(reminder_type)
        meme_path = self.image_manager.generate_meme_image(type_key, size=(300, 300))
        if meme_path and os.path.exists(meme_path):
            meme_img = KivyImage(
                source=meme_path,
                size_hint_y=0.4,
                allow_stretch=True,
                keep_ratio=True,
            )
            content.add_widget(meme_img)

        # 搞怪Art
        art_label = Label(
            text=art,
            font_size=dp(10),
            halign='center',
            valign='middle',
            font_name='RobotoMono' if os.path.exists('/system') else 'Consolas',
            size_hint_y=0.35,
        )
        art_label.bind(size=art_label.setter('text_size'))
        content.add_widget(art_label)

        # 提醒文案
        msg_label = Label(
            text=message,
            font_size=dp(14),
            halign='center',
            size_hint_y=0.2,
            color=get_color_from_hex(COLORS["text"]),
        )
        msg_label.bind(size=msg_label.setter('text_size'))
        content.add_widget(msg_label)

        # 按钮
        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.15,
            spacing=dp(10),
        )
        ok_btn = Button(
            text="✅ 知道了！",
            background_color=get_color_from_hex(COLORS["secondary"]),
            font_size=dp(14),
        )
        refresh_btn = Button(
            text="🔄 换一个",
            background_color=get_color_from_hex(COLORS["primary"]),
            font_size=dp(14),
        )
        btn_row.add_widget(ok_btn)
        btn_row.add_widget(refresh_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.9, 0.75),
            auto_dismiss=True,
        )
        ok_btn.bind(on_press=popup.dismiss)
        refresh_btn.bind(
            on_press=partial(self._refresh_popup_art, reminder_type, art_label)
        )
        popup.open()

    def _refresh_popup_art(self, reminder_type, art_label, instance):
        config = REMINDER_CONFIGS[reminder_type]
        art_label.text = config.get_random_art()

    def _update_ui(self, dt=None):
        """定时更新UI数据"""
        self.home_screen.update_data(self.settings_manager, self.mobile_monitor)
        self.stats_screen.update_data(self.settings_manager, self.mobile_monitor)

    def on_stop(self):
        """App退出时保存"""
        self.scheduler.stop()
        self.settings_manager.save()
