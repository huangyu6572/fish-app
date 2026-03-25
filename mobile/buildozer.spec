[app]

# App 基本信息
title = 摸鱼小助手
package.name = fishassistant
package.domain = org.fishapp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = core/*.py,core/**/*.py
version = 1.0.0

# 入口
entrypoint = main.py

# 依赖
requirements = python3,kivy==2.3.0,pillow,pyjnius

# Android 配置
android.permissions = PACKAGE_USAGE_STATS,INTERNET,RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE
android.api = 34
android.minapi = 26
android.ndk_api = 21
android.archs = arm64-v8a

# 外观
orientation = portrait
fullscreen = 0

# Android 相关
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
