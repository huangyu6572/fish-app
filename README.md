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
# 运行全部单元测试
python -m pytest tests/ -v

# 仅运行手机端 APK 启动链测试（模拟无 psutil 的 Android 环境）
python -m pytest tests/test_mobile_app.py -v
```

### APK 真机/模拟器测试

```bash
# 真机测试（USB 连接手机，需开启 USB 调试）
bash scripts/test_apk_device.sh

# 模拟器测试（需要 KVM 支持，WSL2 需开启嵌套虚拟化）
bash scripts/test_apk_emulator.sh
```

测试脚本会自动完成：安装 APK → 启动 App → 检测闪退 → 抓取 logcat 日志 → 截屏 → 生成报告。
测试产物保存在 `test-results/` 目录。

### 打包桌面版 EXE

```bash
python -m PyInstaller build.spec
```

### 打包手机版 APK（需要 Linux/WSL + Buildozer）

#### 环境要求

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.8+ | 编译宿主环境 |
| Cython | <3.0 (推荐 0.29.x) | ⚠️ Cython 3.x 与 pyjnius 不兼容 |
| Buildozer | 1.5+ | Kivy 官方打包工具 |
| Java JDK | 17 | OpenJDK 17 推荐 |
| Android SDK | API 34 | 自动下载 |
| Android NDK | r25b | 自动下载 |
| 系统依赖 | - | build-essential, libffi-dev, libssl-dev, zlib1g-dev, autoconf, libtool, pkg-config, zip, unzip, ccache, cmake |

#### 方式一：使用编译脚本（推荐，WSL 环境）

```bash
bash scripts/build_apk_wsl.sh
```

#### 方式二：手动编译

```bash
# 1. 创建虚拟环境
python3 -m venv .buildenv
source .buildenv/bin/activate

# 2. 安装 Buildozer（⚠️ Cython 必须 <3.0）
pip install buildozer 'cython<3.0'

# 3. 准备编译目录（展平文件结构）
BUILD_DIR="$HOME/fish-app-build"
mkdir -p "$BUILD_DIR"
cp -r core "$BUILD_DIR/core"
cp mobile/main.py mobile/app.py mobile/mobile_monitor.py mobile/buildozer.spec "$BUILD_DIR/"

# 4. 修复 import 路径
sed -i 's/from mobile\.app import/from app import/' "$BUILD_DIR/main.py"
sed -i 's/from mobile\.mobile_monitor import/from mobile_monitor import/' "$BUILD_DIR/main.py"
sed -i 's/from mobile\.mobile_monitor import/from mobile_monitor import/' "$BUILD_DIR/app.py"

# 5. 编译 APK
cd "$BUILD_DIR"
buildozer android debug
```

#### ⚠️ 常见问题

1. **Cython 3.x 报错 `undeclared name not builtin: long`**
   - 原因：Cython 3.x 移除了 Python 2 的 `long` 类型，与 pyjnius 不兼容
   - 解决：`pip install 'cython<3.0'`

2. **`minsdk` 与 `ndk_api` 不匹配**
   - 原因：`android.minapi` 与 `android.ndk_api` 必须一致或使用 `--allow-minsdk-ndkapi-mismatch`
   - 解决：在 `buildozer.spec` 中设置 `android.minapi = 21`，与 `android.ndk_api = 21` 保持一致

3. **首次编译耗时长（10-30分钟）**
   - 首次编译需要下载 Android SDK、NDK 以及编译 Python 3、SDL2、Kivy 等原生库
   - 后续编译会使用缓存，速度更快

### 安装 APK 到手机

```bash
# 使用 ADB 安装（需开启 USB 调试）
adb install dist/fishassistant-1.0.0-arm64-v8a-debug.apk

# 或将 dist/ 目录下的 APK 文件传输到手机，手动安装
```

> 📱 **注意**：安装前需在手机上开启「允许安装未知来源应用」。应用需要「应用使用情况访问」权限才能监控其他 App 使用时间。

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

164 个单元测试，覆盖所有核心模块 + 手机端启动链：

```
tests/test_reminder_types.py     → 提醒类型 & 文案测试
tests/test_process_monitor.py    → 进程监控测试
tests/test_settings_manager.py   → 设置管理测试
tests/test_reminder_scheduler.py → 调度器测试
tests/test_image_manager.py      → 图片管理测试
tests/test_ui_helpers.py         → UI辅助函数测试
tests/test_mobile_app.py         → 手机版 APK 启动链 & 兼容性测试（31个）
```

### 手机端测试覆盖

| 测试类 | 说明 |
|-------|------|
| `TestImportSafetyNoPsutil` | 模拟 Android 无 psutil 环境，验证所有 core 模块安全导入 |
| `TestMobileMonitor` | MobileMonitor 完整接口 + 无 psutil/jnius 降级 |
| `TestSchedulerWithMobileMonitor` | 调度器与手机监控器集成 |
| `TestSettingsAndroidPath` | 设置管理在自定义路径下的读写 |
| `TestImageManagerAndroid` | 图片管理器在无 PIL 环境的降级 |
| `TestAPKBootChain` | 模拟 APK 展平后的完整 import 启动链 |

## 📜 License

MIT
