"""
摸鱼小助手 - 手机版 (Kivy)
支持通过 Buildozer 打包为 Android APK

用法:
  运行:    python mobile/main.py
  打包APK: cd mobile && buildozer android debug
"""

import sys
import os

# 确保项目根目录在路径中
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from mobile.app import FishAssistantMobileApp


def main():
    FishAssistantMobileApp().run()


if __name__ == "__main__":
    main()
