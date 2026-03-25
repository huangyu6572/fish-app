"""
摸鱼小助手 - 桌面版启动入口
Tkinter + ttkbootstrap
"""

import sys
import os

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop.app import FishAssistantApp


def main():
    app = FishAssistantApp()
    app.run()


if __name__ == "__main__":
    main()
