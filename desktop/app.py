"""
摸鱼小助手 - 主界面
使用 ttkbootstrap 美化的 Tkinter GUI
"""

import sys
import os
import logging
import traceback
import threading
import platform
from datetime import date, datetime
from pathlib import Path

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import Text, END, Toplevel, StringVar, IntVar, BooleanVar

# ── 日志配置 ──────────────────────────────────────────
def _setup_logging():
    """配置日志，写入文件 + 控制台"""
    log_dir = Path.home() / ".fish_assistant" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"fish_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(str(log_file), encoding="utf-8"),
            logging.StreamHandler(sys.stderr),
        ],
    )
    return logging.getLogger("fish_assistant")

logger = _setup_logging()

try:
    from tkinter import PhotoImage as TkPhotoImage
    from PIL import Image as PILImage, ImageTk
    HAS_PIL = True
    logger.info("PIL/Pillow loaded successfully")
except ImportError as e:
    HAS_PIL = False
    logger.warning(f"PIL not available: {e}")

from core.reminder_types import ReminderType, REMINDER_CONFIGS
from core.process_monitor import ProcessMonitor, MONITORED_APPS
from core.settings_manager import SettingsManager
from core.reminder_scheduler import ReminderScheduler
from core.image_manager import FunnyImageManager
from core.ui_helpers import (
    REMINDER_COLORS,
    REMINDER_NAMES,
    get_motivational_emoji,
    get_motivational_message,
    get_daily_summary_text,
    get_random_slogan,
    get_random_nickname,
    get_usage_emoji,
    format_usage_progress,
    get_usage_color,
)

logger.info("All modules imported successfully")


def _make_labelframe(parent, text, pad=10):
    """创建 LabelFrame 并安全设置 padding（兼容不同 ttkbootstrap 版本）"""
    try:
        frame = ttk.LabelFrame(parent, text=text, padding=pad)
    except Exception:
        frame = ttk.LabelFrame(parent, text=text)
        # 用内层 Frame 模拟 padding
        inner = ttk.Frame(frame, padding=pad)
        inner.pack(fill=BOTH, expand=True)
    return frame


class FishAssistantApp:
    """摸鱼小助手主应用"""

    def __init__(self):
        logger.info("FishAssistantApp initializing...")
        try:
            # 初始化组件
            self.settings_manager = SettingsManager()
            self.process_monitor = ProcessMonitor()
            self.image_manager = FunnyImageManager()
            self.scheduler = ReminderScheduler(
                settings_manager=self.settings_manager,
                process_monitor=self.process_monitor,
                on_reminder=self._on_reminder_callback,
            )
            logger.info("Core components initialized")

            # 创建主窗口
            self.root = ttk.Window(
                title="🐟 摸鱼小助手 - 提肛喝水摸鱼提醒",
                themename=self.settings_manager.settings.theme,
                size=(520, 720),
                resizable=(True, True),
            )
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)
            logger.info("Main window created")

            # 设置窗口图标（跨平台）
            try:
                if platform.system() == "Windows":
                    self.root.iconbitmap(default="")
            except Exception:
                pass

            # Tkinter 变量
            self._init_vars()

            # 构建界面
            self._build_ui()
            logger.info("UI built successfully")

            # 启动定时更新
            self._start_ui_update()
            logger.info("FishAssistantApp ready!")

        except Exception as e:
            logger.error(f"Init failed: {e}\n{traceback.format_exc()}")
            raise

    def _init_vars(self):
        """初始化界面变量"""
        s = self.settings_manager.settings
        self.monitor_var = BooleanVar(value=s.monitor_enabled)
        self.sound_var = BooleanVar(value=s.sound_enabled)
        self.wechat_limit_var = IntVar(value=s.wechat_limit)
        self.douyin_limit_var = IntVar(value=s.douyin_limit)
        self.interval_var = IntVar(value=s.remind_interval)
        self.drink_var = BooleanVar(value=s.drink_water_enabled)
        self.kegel_var = BooleanVar(value=s.kegel_enabled)
        self.fish_var = BooleanVar(value=s.fish_touch_enabled)
        self.eyes_var = BooleanVar(value=s.rest_eyes_enabled)
        self.stretch_var = BooleanVar(value=s.stretch_enabled)

    def _build_ui(self):
        """构建主界面"""
        # 创建Notebook（标签页）
        notebook = ttk.Notebook(self.root, bootstyle="info")
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 首页
        home_frame = ttk.Frame(notebook, padding=10)
        notebook.add(home_frame, text="🏠 首页")
        self._build_home_tab(home_frame)

        # 统计页
        stats_frame = ttk.Frame(notebook, padding=10)
        notebook.add(stats_frame, text="📊 统计")
        self._build_stats_tab(stats_frame)

        # 设置页
        settings_frame = ttk.Frame(notebook, padding=10)
        notebook.add(settings_frame, text="⚙️ 设置")
        self._build_settings_tab(settings_frame)

    # ── 首页 ──────────────────────────────────────────

    def _build_home_tab(self, parent):
        """构建首页 - 可爱搞怪风格"""
        # 标题区域
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(
            title_frame,
            text="🐟 摸鱼小助手 🐟",
            font=("", 22, "bold"),
            bootstyle="inverse-info",
            anchor="center",
        ).pack(fill=X, ipady=10)

        # 随机搞笑 slogan
        self.slogan_label = ttk.Label(
            title_frame,
            text=get_random_slogan(),
            font=("", 11),
            anchor="center",
            cursor="hand2",
        )
        self.slogan_label.pack(fill=X, pady=5)
        # 点击 slogan 换一条
        self.slogan_label.bind("<Button-1>", lambda e: self.slogan_label.configure(
            text=get_random_slogan()
        ))

        # 监控开关 - 更可爱的文案
        switch_frame = _make_labelframe(parent, "🎮 监控状态")
        switch_frame.pack(fill=X, pady=5)

        self.status_label = ttk.Label(
            switch_frame, text="😴 摸鱼小助手在打盹...", font=("", 13)
        )
        self.status_label.pack(side=LEFT, padx=10)

        ttk.Checkbutton(
            switch_frame,
            text="唤醒小助手",
            variable=self.monitor_var,
            command=self._toggle_monitor,
            bootstyle="success-round-toggle",
        ).pack(side=RIGHT, padx=10)

        # 应用使用时间 - 更生动
        usage_frame = _make_labelframe(parent, "📱 摸鱼时间监控")
        usage_frame.pack(fill=X, pady=5)

        self.usage_bars = {}
        app_display = {
            "wechat": ("💬", "微信摸鱼"),
            "douyin": ("🎵", "抖音沉迷"),
        }
        for app_key in ["wechat", "douyin"]:
            app_info = MONITORED_APPS[app_key]
            emoji, label_text = app_display[app_key]
            row = ttk.Frame(usage_frame)
            row.pack(fill=X, pady=3)

            ttk.Label(
                row,
                text=f"{emoji} {label_text}",
                font=("", 11),
                width=10,
            ).pack(side=LEFT)

            bar = ttk.Progressbar(
                row, length=200, mode="determinate", bootstyle="info-striped"
            )
            bar.pack(side=LEFT, padx=10, expand=True, fill=X)

            time_label = ttk.Label(row, text="0分钟", font=("", 10), width=12)
            time_label.pack(side=RIGHT)

            self.usage_bars[app_key] = (bar, time_label)

        # 测试提醒按钮 - 更搞怪
        test_frame = _make_labelframe(parent, "� 戳一下试试")
        test_frame.pack(fill=X, pady=5)

        btn_row1 = ttk.Frame(test_frame)
        btn_row1.pack(fill=X, pady=2)
        btn_row2 = ttk.Frame(test_frame)
        btn_row2.pack(fill=X, pady=2)

        buttons = [
            ("💧 喝水!", ReminderType.DRINK_WATER, "info", btn_row1),
            ("🍑 提肛!", ReminderType.KEGEL, "danger", btn_row1),
            ("🐟 摸鱼!", ReminderType.FISH_TOUCH, "success", btn_row1),
            ("👀 护眼!", ReminderType.REST_EYES, "warning", btn_row2),
            ("🧘 伸展!", ReminderType.STRETCH, "secondary", btn_row2),
            ("� 随机!", None, "primary", btn_row2),
        ]

        for text, rtype, style, parent_row in buttons:
            ttk.Button(
                parent_row,
                text=text,
                bootstyle=style,
                command=lambda t=rtype: self._test_reminder(t),
                width=8,
            ).pack(side=LEFT, padx=3, expand=True, fill=X)

        # 今日小结 - 更有趣
        summary_frame = _make_labelframe(parent, "📝 今日战报")
        summary_frame.pack(fill=BOTH, expand=True, pady=5)

        self.summary_label = ttk.Label(
            summary_frame,
            text="😴 还没有记录哦~\n快唤醒小助手开始健康生活！",
            font=("", 11),
            wraplength=450,
        )
        self.summary_label.pack(fill=BOTH, expand=True)

    # ── 统计页 ──────────────────────────────────────────

    def _build_stats_tab(self, parent):
        """构建统计页面 - 搞怪风格"""
        ttk.Label(
            parent,
            text="📊 今日战绩",
            font=("", 18, "bold"),
            anchor="center",
        ).pack(fill=X, pady=(0, 15))

        # 统计卡片 - 更有趣的描述
        self.stat_labels = {}

        stats_config = [
            ("wechat_usage", "💬 微信摸鱼时长", "info"),
            ("douyin_usage", "🎵 抖音沉迷时长", "danger"),
            ("drink_count", "💧 补水次数", "primary"),
            ("kegel_count", "🍑 提肛修炼", "warning"),
            ("fish_count", "🐟 摸鱼被抓", "success"),
        ]

        for key, label_text, style in stats_config:
            card = ttk.Frame(parent, padding=10)
            card.pack(fill=X, pady=3)

            ttk.Label(
                card, text=label_text, font=("", 13), width=14, anchor="w"
            ).pack(side=LEFT)

            value_label = ttk.Label(
                card,
                text="0",
                font=("", 16, "bold"),
                bootstyle=style,
                anchor="e",
            )
            value_label.pack(side=RIGHT, padx=10)
            self.stat_labels[key] = value_label

        # 激励区域
        ttk.Separator(parent).pack(fill=X, pady=15)

        self.motivation_emoji_label = ttk.Label(
            parent, text="😴", font=("", 48), anchor="center"
        )
        self.motivation_emoji_label.pack()

        self.motivation_text_label = ttk.Label(
            parent,
            text="嘿打工人，快开启监控吧！🐟",
            font=("", 12),
            wraplength=400,
            anchor="center",
        )
        self.motivation_text_label.pack(pady=10)

        # 重置按钮
        ttk.Button(
            parent,
            text="�️ 清空今日战绩",
            bootstyle="outline-danger",
            command=self._reset_stats,
        ).pack(pady=10)

    # ── 设置页 ──────────────────────────────────────────

    def _build_settings_tab(self, parent):
        """构建设置页面 - 轻松风格"""
        ttk.Label(
            parent,
            text="⚙️ 调教小助手",
            font=("", 18, "bold"),
            anchor="center",
        ).pack(fill=X, pady=(0, 15))

        # 时间限制设置
        limit_frame = _make_labelframe(parent, "⏱️ 摸鱼时限 (分钟)")
        limit_frame.pack(fill=X, pady=5)

        limit_items = [
            ("💬 微信上限", self.wechat_limit_var),
            ("🎵 抖音上限", self.douyin_limit_var),
            ("⏰ 提醒间隔", self.interval_var),
        ]
        for label_text, var in limit_items:
            row = ttk.Frame(limit_frame)
            row.pack(fill=X, pady=3)
            ttk.Label(row, text=label_text, font=("", 11), width=12).pack(side=LEFT)
            ttk.Spinbox(
                row,
                from_=1,
                to=480,
                textvariable=var,
                width=6,
                font=("", 11),
                command=self._save_settings,
            ).pack(side=RIGHT, padx=10)

        # 提醒类型开关 - 更有趣的描述
        type_frame = _make_labelframe(parent, "🔔 被骚扰方式")
        type_frame.pack(fill=X, pady=5)

        type_items = [
            ("💧 喝水提醒 (成为水人)", self.drink_var),
            ("🍑 提肛提醒 (菊花宝典)", self.kegel_var),
            ("🐟 摸鱼提醒 (防老板)", self.fish_var),
            ("👀 护眼提醒 (拯救近视)", self.eyes_var),
            ("🧘 伸展提醒 (告别腰突)", self.stretch_var),
        ]
        for label_text, var in type_items:
            ttk.Checkbutton(
                type_frame,
                text=label_text,
                variable=var,
                command=self._save_settings,
                bootstyle="success-round-toggle",
            ).pack(anchor=W, pady=2)

        # 其他设置
        other_frame = _make_labelframe(parent, "🛠️ 其他")
        other_frame.pack(fill=X, pady=5)

        ttk.Checkbutton(
            other_frame,
            text="🔊 提示音",
            variable=self.sound_var,
            command=self._save_settings,
            bootstyle="info-round-toggle",
        ).pack(anchor=W, pady=2)

        # 主题选择
        theme_row = ttk.Frame(other_frame)
        theme_row.pack(fill=X, pady=5)
        ttk.Label(theme_row, text="🎨 主题", font=("", 11)).pack(side=LEFT)

        themes = ["cosmo", "flatly", "journal", "darkly", "solar", "superhero", "cyborg"]
        self.theme_var = StringVar(value=self.settings_manager.settings.theme)
        theme_combo = ttk.Combobox(
            theme_row,
            textvariable=self.theme_var,
            values=themes,
            state="readonly",
            width=12,
        )
        theme_combo.pack(side=RIGHT, padx=10)
        theme_combo.bind("<<ComboboxSelected>>", self._change_theme)

        # 版本信息
        ttk.Label(
            parent,
            text="🐟 摸鱼小助手 v1.1.0  |  一个不正经的健康提醒APP",
            font=("", 9),
            anchor="center",
            bootstyle="secondary",
        ).pack(side=BOTTOM, pady=10)

    # ── 事件处理 ──────────────────────────────────────

    def _toggle_monitor(self):
        """切换监控状态"""
        enabled = self.monitor_var.get()
        self.settings_manager.settings.monitor_enabled = enabled
        self.settings_manager.save()

        if enabled:
            self.scheduler.start()
            self.status_label.configure(
                text="🐟 小助手已上线！盯着你呢~", bootstyle="success"
            )
        else:
            self.scheduler.stop()
            self.status_label.configure(
                text="😴 摸鱼小助手在打盹...", bootstyle=""
            )

    def _test_reminder(self, reminder_type=None):
        """测试提醒"""
        self.scheduler.trigger_test_reminder(reminder_type)

    def _save_settings(self, *_):
        """保存设置"""
        s = self.settings_manager.settings
        s.wechat_limit = self.wechat_limit_var.get()
        s.douyin_limit = self.douyin_limit_var.get()
        s.remind_interval = max(1, self.interval_var.get())
        s.sound_enabled = self.sound_var.get()
        s.drink_water_enabled = self.drink_var.get()
        s.kegel_enabled = self.kegel_var.get()
        s.fish_touch_enabled = self.fish_var.get()
        s.rest_eyes_enabled = self.eyes_var.get()
        s.stretch_enabled = self.stretch_var.get()
        self.settings_manager.save()

    def _change_theme(self, event=None):
        """切换主题"""
        new_theme = self.theme_var.get()
        self.settings_manager.settings.theme = new_theme
        self.settings_manager.save()
        self.root.style.theme_use(new_theme)

    def _reset_stats(self):
        """重置每日统计"""
        if Messagebox.yesno("确认重置今日所有统计数据吗？", title="重置统计") == "Yes":
            self.settings_manager.reset_daily_stats()
            self.process_monitor.reset_all()

    def _on_close(self):
        """关闭窗口"""
        self.scheduler.stop()
        self.settings_manager.save()
        self.root.destroy()

    # ── 提醒弹窗 ──────────────────────────────────────

    def _on_reminder_callback(self, reminder_type, title, message, art):
        """
        提醒回调 - 在主线程显示弹窗
        从调度器线程调用，需要通过after切到主线程
        """
        self.root.after(0, lambda: self._show_reminder_popup(
            reminder_type, title, message, art
        ))

    def _show_reminder_popup(self, reminder_type, title, message, art):
        """显示搞怪提醒弹窗 - 可爱娱乐风格"""
        popup = Toplevel(self.root)
        popup.title(f"🐟 {title}")
        popup.geometry("460x620")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)

        # 尝试抢占焦点
        popup.lift()
        popup.focus_force()

        bg_color = REMINDER_COLORS.get(reminder_type, "#FF6B35")

        # 标题 - 更搞怪
        header = ttk.Frame(popup)
        header.pack(fill=X)

        cute_titles = {
            ReminderType.DRINK_WATER: "💧 水分警报！！",
            ReminderType.KEGEL: "🍑 菊花召唤令！",
            ReminderType.FISH_TOUCH: "🚨 摸鱼被抓现行！",
            ReminderType.REST_EYES: "👀 眼睛快瞎了！",
            ReminderType.STRETCH: "🧘 你的身体在哭泣！",
        }
        display_title = cute_titles.get(reminder_type, title)

        ttk.Label(
            header,
            text=display_title,
            font=("", 18, "bold"),
            anchor="center",
            bootstyle="inverse-danger" if reminder_type == ReminderType.FISH_TOUCH else "inverse-info",
        ).pack(fill=X, ipady=8)

        # 表情包图片区域
        meme_frame = ttk.Frame(popup, padding=5)
        meme_frame.pack(fill=X)

        meme_label = ttk.Label(meme_frame, anchor="center")
        meme_label.pack(fill=X)
        self._load_meme_into_label(
            reminder_type, meme_label, popup, size=(240, 240)
        )

        # 搞怪 Art
        art_frame = ttk.Frame(popup, padding=5)
        art_frame.pack(fill=BOTH, expand=True)

        art_text = Text(
            art_frame,
            wrap="word",
            font=("Consolas", 10) if platform.system() == "Windows" else ("Menlo", 10),
            height=8,
            relief="flat",
            bg="#2d2d44" if "dark" in self.settings_manager.settings.theme else "#FFF8F0",
            fg="#FFFFFF" if "dark" in self.settings_manager.settings.theme else "#1A1A1A",
        )
        art_text.insert(END, art)
        art_text.configure(state="disabled")
        art_text.pack(fill=BOTH, expand=True)

        # 提醒文案
        ttk.Label(
            popup,
            text=message,
            font=("", 12),
            wraplength=420,
            anchor="center",
        ).pack(fill=X, padx=10, pady=5)

        # 按钮 - 搞怪文案
        btn_frame = ttk.Frame(popup, padding=10)
        btn_frame.pack(fill=X)

        dismiss_texts = [
            "✅ 知道了知道了！", "✅ 好的好的！", "✅ 收到收到！",
            "✅ 马上行动！", "✅ 遵命！",
        ]
        import random as _rnd
        ttk.Button(
            btn_frame,
            text=_rnd.choice(dismiss_texts),
            bootstyle="success",
            command=popup.destroy,
            width=15,
        ).pack(side=LEFT, expand=True, padx=5)

        ttk.Button(
            btn_frame,
            text="🎰 再来一个！",
            bootstyle="info-outline",
            command=lambda: self._refresh_popup(popup, reminder_type, art_text),
            width=15,
        ).pack(side=RIGHT, expand=True, padx=5)

        # 提示音
        if self.settings_manager.settings.sound_enabled:
            try:
                popup.bell()
            except Exception:
                pass

    def _refresh_popup(self, popup, reminder_type, art_text):
        """刷新弹窗内容（ASCII Art + 表情包）"""
        config = REMINDER_CONFIGS[reminder_type]
        new_art = config.get_random_art()
        art_text.configure(state="normal")
        art_text.delete("1.0", END)
        art_text.insert(END, new_art)
        art_text.configure(state="disabled")

        # 同时刷新表情包图片 - 找到弹窗中的meme label
        for child in popup.winfo_children():
            for sub in child.winfo_children():
                if isinstance(sub, ttk.Label) and hasattr(sub, '_meme_type'):
                    self._load_meme_into_label(
                        reminder_type, sub, popup, size=(240, 240)
                    )
                    break

    def _load_meme_into_label(self, reminder_type, label, popup, size=(240, 240)):
        """加载表情包图片到 Label 中"""
        if not HAS_PIL:
            label.configure(text="(表情包需要 Pillow)")
            return

        type_key = reminder_type.value if hasattr(reminder_type, 'value') else str(reminder_type)
        meme_path = self.image_manager.generate_meme_image(type_key, size=size)
        if meme_path:
            try:
                pil_img = PILImage.open(meme_path)
                pil_img = pil_img.resize(size, PILImage.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)
                label.configure(image=tk_img)
                label._tk_img = tk_img  # 防止垃圾回收
                label._meme_type = type_key
            except Exception:
                label.configure(text="😂 表情包加载失败")
        else:
            label.configure(text="😂 表情包生成失败")

    # ── 定时更新UI ──────────────────────────────────

    def _start_ui_update(self):
        """启动定时UI更新"""
        self._update_ui()
        self.root.after(5000, self._start_ui_update)  # 每5秒更新一次

    def _update_ui(self):
        """更新界面数据"""
        # 更新使用时间进度条
        for app_key in ["wechat", "douyin"]:
            usage = self.process_monitor.get_usage(app_key)
            limit = self.settings_manager.get_app_limit(app_key)
            if usage and app_key in self.usage_bars:
                bar, label = self.usage_bars[app_key]
                progress = format_usage_progress(usage.total_minutes, limit)
                bar["value"] = progress * 100

                status_emoji = get_usage_emoji(progress)
                label.configure(
                    text=f"{status_emoji} {usage.format_time()} / {limit}分钟"
                )

        # 更新统计数据
        s = self.settings_manager.settings
        if hasattr(self, 'stat_labels'):
            wechat_usage = self.process_monitor.get_usage("wechat")
            douyin_usage = self.process_monitor.get_usage("douyin")

            self.stat_labels["wechat_usage"].configure(
                text=wechat_usage.format_time() if wechat_usage else "0分钟"
            )
            self.stat_labels["douyin_usage"].configure(
                text=douyin_usage.format_time() if douyin_usage else "0分钟"
            )
            self.stat_labels["drink_count"].configure(
                text=f"{s.today_drink_count} 杯 💧"
            )
            self.stat_labels["kegel_count"].configure(
                text=f"{s.today_kegel_count} 次 🍑"
            )
            self.stat_labels["fish_count"].configure(
                text=f"{s.today_fish_count} 次 🐟"
            )

            # 更新激励
            total = s.today_drink_count + s.today_kegel_count + s.today_fish_count
            self.motivation_emoji_label.configure(
                text=get_motivational_emoji(total)
            )
            self.motivation_text_label.configure(
                text=get_motivational_message(
                    s.today_drink_count, s.today_kegel_count,
                    s.today_fish_count, total
                )
            )

        # 更新首页战报
        if hasattr(self, 'summary_label'):
            self.summary_label.configure(
                text=get_daily_summary_text(
                    s.today_drink_count,
                    s.today_kegel_count,
                    s.today_fish_count,
                )
            )

    def run(self):
        """启动应用"""
        logger.info("Starting application mainloop")
        # 如果上次开着监控，自动恢复
        if self.settings_manager.settings.monitor_enabled:
            self.scheduler.start()
            self.status_label.configure(
                text="🐟 小助手已上线！盯着你呢~", bootstyle="success"
            )
            logger.info("Monitor auto-resumed from previous session")

        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Mainloop error: {e}\n{traceback.format_exc()}")
            raise
        finally:
            logger.info("Application exited")
