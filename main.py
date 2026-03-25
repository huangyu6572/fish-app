"""
摸鱼小助手 - 启动入口
支持双版本：桌面版(Tkinter) / 手机版(Kivy)

用法:
    python main.py              → 启动桌面版
    python main.py --mobile     → 启动手机版(Kivy)
    python main.py --help       → 显示帮助
"""

import sys
import os
import logging
import traceback
from pathlib import Path
from datetime import datetime

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _setup_crash_log():
    """配置全局崩溃日志"""
    log_dir = Path.home() / ".fish_assistant" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"fish_{datetime.now().strftime('%Y%m%d')}.log"
    return log_file


def main():
    log_file = _setup_crash_log()

    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    try:
        if "--mobile" in args:
            # 手机版 / Kivy
            from mobile.app import FishAssistantMobileApp
            app = FishAssistantMobileApp()
            app.run()
        else:
            # 桌面版 / Tkinter (默认)
            from desktop.app import FishAssistantApp
            app = FishAssistantApp()
            app.run()
    except Exception as e:
        error_msg = traceback.format_exc()
        # 写入崩溃日志
        with open(str(log_file), "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"CRASH at {datetime.now().isoformat()}\n")
            f.write(f"{'='*60}\n")
            f.write(error_msg)
            f.write(f"\n{'='*60}\n")

        # 尝试弹窗显示错误
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "摸鱼小助手 - 启动失败",
                f"程序出错了！😱\n\n{e}\n\n"
                f"详细日志已保存到:\n{log_file}",
            )
            root.destroy()
        except Exception:
            print(f"FATAL ERROR: {error_msg}", file=sys.stderr)

        sys.exit(1)


if __name__ == "__main__":
    main()
