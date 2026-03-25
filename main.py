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

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

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


if __name__ == "__main__":
    main()
