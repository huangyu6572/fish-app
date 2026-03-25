# 🐟 摸鱼小助手 - 提肛喝水摸鱼小助手

> 提肛喝水摸鱼，一个都不能少！

定时提醒你喝水💧、提肛🍑、休息摸鱼🐟、护眼👀、伸展🧘，还能监控微信/抖音使用时间，超时弹出搞笑提醒！

## 📁 项目结构

```
fish-app/
├── core/                   # 🧠 核心逻辑（桌面版和手机版共享）
│   ├── reminder_types.py   #   提醒类型 & 搞笑文案 & ASCII Art
│   ├── process_monitor.py  #   进程监控（微信/抖音/QQ/B站）
│   ├── settings_manager.py #   设置管理（JSON持久化）
│   ├── reminder_scheduler.py # 提醒调度器（定时 + 超时检测）
│   ├── image_manager.py    #   搞怪图片管理
│   └── ui_helpers.py       #   UI辅助函数 & 激励文案
│
├── desktop/                # 🖥️ 桌面版（Tkinter + ttkbootstrap）
│   ├── app.py              #   主界面
│   └── main.py             #   启动入口
│
├── mobile/                 # 📱 手机版（Kivy → Buildozer APK）
│   ├── app.py              #   Kivy主界面
│   ├── main.py             #   启动入口
│   ├── mobile_monitor.py   #   手机端进程监控（Android UsageStats）
│   ├── buildozer.spec      #   APK打包配置
│   └── requirements.txt    #   手机版依赖
│
├── tests/                  # ✅ 单元测试（133个测试用例）
│   ├── test_reminder_types.py
│   ├── test_process_monitor.py
│   ├── test_settings_manager.py
│   ├── test_reminder_scheduler.py
│   ├── test_image_manager.py
│   └── test_ui_helpers.py
│
├── main.py                 # 🚀 统一启动入口
├── requirements.txt        # 依赖列表
├── build.spec              # PyInstaller打包配置
└── README.md
```

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动桌面版（默认）

```bash
python main.py
```

### 启动手机版（Kivy，需先安装kivy）

```bash
pip install kivy
python main.py --mobile
```

### 运行测试

```bash
python -m pytest tests/ -v
```

### 打包桌面版 EXE

```bash
python -m PyInstaller build.spec
```

### 打包手机版 APK（需要Linux/WSL + Buildozer）

```bash
cd mobile
buildozer -v android debug
```

## ✨ 功能特色

- 💧 **喝水提醒** - 定时提醒补水，附带搞笑ASCII Art
- 🍑 **提肛提醒** - 凯格尔运动提醒，趣味文案
- 🐟 **摸鱼提醒** - 适度摸鱼，有益身心
- 👀 **护眼提醒** - 20-20-20护眼法则
- 🧘 **伸展提醒** - 站起来活动活动
- 📱 **应用监控** - 微信/抖音/QQ/B站使用时间监控
- ⚠️ **超时提醒** - 超过设定时间弹出搞怪提醒
- 📊 **今日统计** - 记录每日健康行为

## 🧪 测试

133个单元测试，覆盖所有核心模块：

```
tests/test_reminder_types.py     → 提醒类型 & 文案测试
tests/test_process_monitor.py    → 进程监控测试
tests/test_settings_manager.py   → 设置管理测试
tests/test_reminder_scheduler.py → 调度器测试
tests/test_image_manager.py      → 图片管理测试
tests/test_ui_helpers.py         → UI辅助函数测试
```

## 📜 License

MIT
