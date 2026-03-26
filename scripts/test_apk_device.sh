#!/bin/bash
# ============================================================
# 摸鱼小助手 - ADB APK 真机/模拟器 自动化测试
#
# 适用于: 通过 USB 连接的 Android 手机 或 已启动的模拟器
# 前提: adb 已连接设备 (adb devices 能看到设备)
#
# 测试内容:
#   1. 安装 APK
#   2. 启动 App，等待并检查是否闪退
#   3. 抓取 logcat 日志，分析 Python/Kivy 错误
#   4. 截屏验证 UI
#   5. 生成测试报告
#
# 用法:
#   bash scripts/test_apk_device.sh [apk_path]
#
# 示例:
#   # 测试默认 APK（dist/ 目录）
#   bash scripts/test_apk_device.sh
#
#   # 测试指定 APK
#   bash scripts/test_apk_device.sh ~/my-build/fish.apk
# ============================================================

set -e

# ── 配置 ──
ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/.buildozer/android/platform/android-sdk}"
ADB="${ADB:-$ANDROID_SDK_ROOT/platform-tools/adb}"
PACKAGE_NAME="org.fishapp.fishassistant"
ACTIVITY="org.kivy.android.PythonActivity"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RESULTS_DIR="$PROJECT_DIR/test-results"
TIMEOUT_APP="${TIMEOUT_APP:-30}"

# 自动查找 APK
if [ -n "$1" ]; then
    APK_PATH="$1"
else
    APK_PATH=$(find "$PROJECT_DIR/dist" -name "*.apk" -type f 2>/dev/null | sort -r | head -1)
    if [ -z "$APK_PATH" ]; then
        APK_PATH=$(find "$HOME/fish-app-build/bin" -name "*.apk" -type f 2>/dev/null | sort -r | head -1)
    fi
fi

echo "🐟 ========================================="
echo "🐟  摸鱼小助手 - APK 设备测试"
echo "🐟 ========================================="
echo ""

# ── 前置检查 ──
ERRORS=0

if [ ! -f "$ADB" ]; then
    echo "❌ ADB 未找到: $ADB"
    echo "   设置环境变量: export ADB=/path/to/adb"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "$APK_PATH" ] || [ ! -f "$APK_PATH" ]; then
    echo "❌ APK 文件不存在: $APK_PATH"
    echo "   用法: bash scripts/test_apk_device.sh [apk_path]"
    ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -gt 0 ]; then
    exit 1
fi

# 检查设备连接
DEVICE_COUNT=$("$ADB" devices 2>/dev/null | grep -c -E "device$" || echo "0")
if [ "$DEVICE_COUNT" -eq 0 ]; then
    echo "❌ 没有检测到 ADB 设备"
    echo ""
    echo "   📱 真机连接方法:"
    echo "      1. 手机开启 USB 调试 (设置 → 开发者选项 → USB 调试)"
    echo "      2. USB 连接手机到电脑"
    echo "      3. 手机上点击「允许 USB 调试」"
    echo ""
    echo "   🖥️ 模拟器方法:"
    echo "      bash scripts/test_apk_emulator.sh"
    echo ""
    echo "   验证: $ADB devices"
    exit 1
fi

DEVICE_INFO=$("$ADB" shell getprop ro.product.model 2>/dev/null || echo "Unknown")
ANDROID_VER=$("$ADB" shell getprop ro.build.version.release 2>/dev/null || echo "?")
ABI=$("$ADB" shell getprop ro.product.cpu.abi 2>/dev/null || echo "?")

echo "✅ 检测到设备: $DEVICE_INFO (Android $ANDROID_VER, $ABI)"
echo "   APK: $(basename "$APK_PATH") ($(du -h "$APK_PATH" | cut -f1))"
echo ""

mkdir -p "$RESULTS_DIR"
TEST_START=$(date +%s)

# ── 1. 安装 APK ──
echo "📦 [1/5] 安装 APK..."
"$ADB" uninstall "$PACKAGE_NAME" 2>/dev/null || true
if "$ADB" install -r "$APK_PATH" 2>&1 | tee "$RESULTS_DIR/install.log"; then
    echo "✅ APK 安装成功"
else
    echo "❌ APK 安装失败 — 查看 $RESULTS_DIR/install.log"
    exit 1
fi

# ── 2. 清除日志并启动 App ──
echo ""
echo "🚀 [2/5] 启动 App..."
"$ADB" logcat -c 2>/dev/null

# 启动 App
"$ADB" shell am start -n "${PACKAGE_NAME}/${ACTIVITY}" 2>&1 | tee "$RESULTS_DIR/start.log"
echo "   等待 App 启动稳定（${TIMEOUT_APP}s）..."

# 逐秒检查 App 是否存活
APP_CRASHED=false
CRASH_TIME=""
for i in $(seq 1 "$TIMEOUT_APP"); do
    sleep 1
    PID=$("$ADB" shell pidof "$PACKAGE_NAME" 2>/dev/null || echo "")
    if [ -z "$PID" ] && [ $i -gt 3 ]; then
        # App 启动 3 秒后消失 = 闪退
        APP_CRASHED=true
        CRASH_TIME="${i}s"
        echo "   ❌ App 在第 ${i}s 闪退 (PID 消失)"
        break
    fi
    if [ $((i % 5)) -eq 0 ]; then
        echo "   ⏳ ${i}s - App 运行中 (PID: $PID)"
    fi
done

if [ "$APP_CRASHED" = false ]; then
    FINAL_PID=$("$ADB" shell pidof "$PACKAGE_NAME" 2>/dev/null || echo "")
    if [ -n "$FINAL_PID" ]; then
        echo "✅ App 运行稳定 (PID: $FINAL_PID, 持续 ${TIMEOUT_APP}s)"
    else
        APP_CRASHED=true
        CRASH_TIME="after ${TIMEOUT_APP}s"
        echo "❌ App 在等待结束时已退出"
    fi
fi

# ── 3. 抓取日志 ──
echo ""
echo "📋 [3/5] 抓取诊断日志..."

# Python/Kivy 相关
"$ADB" logcat -d -s "python:*" "PythonActivity:*" "SDL:*" "AndroidRuntime:*" "ActivityManager:*" \
    > "$RESULTS_DIR/logcat_app.txt" 2>/dev/null

# 完整日志
"$ADB" logcat -d > "$RESULTS_DIR/logcat_full.txt" 2>/dev/null

# 提取关键信息
echo ""
echo "   ── Python 层日志 ──"
grep -i "python\|kivy\|Exception\|Error\|Traceback\|import" "$RESULTS_DIR/logcat_app.txt" 2>/dev/null \
    | grep -v "DEBUG" | head -30 || echo "   （无 Python 日志）"

echo ""
echo "   ── 崩溃信息 ──"
grep -A5 "FATAL\|AndroidRuntime.*E\|Process.*died\|crash" "$RESULTS_DIR/logcat_full.txt" 2>/dev/null \
    | head -20 || echo "   （无崩溃信息）"

echo ""
echo "   ── ImportError / ModuleNotFoundError ──"
grep -i "ImportError\|ModuleNotFound\|No module named" "$RESULTS_DIR/logcat_full.txt" 2>/dev/null \
    | head -10 || echo "   （无 import 错误 ✅）"

# ── 4. 截屏 ──
echo ""
echo "📸 [4/5] 截屏..."
if [ "$APP_CRASHED" = false ]; then
    "$ADB" shell screencap -p /sdcard/fish_test.png 2>/dev/null
    "$ADB" pull /sdcard/fish_test.png "$RESULTS_DIR/screenshot.png" 2>/dev/null
    "$ADB" shell rm /sdcard/fish_test.png 2>/dev/null
    if [ -f "$RESULTS_DIR/screenshot.png" ]; then
        echo "   ✅ 截屏: $RESULTS_DIR/screenshot.png"
    else
        echo "   ⚠️ 截屏失败"
    fi
else
    echo "   ⏭️ App 已闪退，跳过截屏"
fi

# ── 5. 清理 ──
echo ""
echo "🧹 [5/5] 清理..."
"$ADB" shell am force-stop "$PACKAGE_NAME" 2>/dev/null || true
echo "   ✅ App 已停止"

# ── 测试报告 ──
TEST_END=$(date +%s)
DURATION=$((TEST_END - TEST_START))

echo ""
echo "📊 ========================================="
echo "📊  测试报告"
echo "📊 ========================================="
echo ""
echo "  设备:       $DEVICE_INFO (Android $ANDROID_VER, $ABI)"
echo "  APK:        $(basename "$APK_PATH")"
echo "  APK 大小:   $(du -h "$APK_PATH" | cut -f1)"
echo "  测试耗时:   ${DURATION}s"
echo "  测试时间:   $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

if [ "$APP_CRASHED" = false ]; then
    echo "  ✅ 结果: PASS — App 启动成功，运行 ${TIMEOUT_APP}s 无闪退"
else
    echo "  ❌ 结果: FAIL — App 闪退 ($CRASH_TIME)"
    echo ""
    echo "  🔍 排查步骤:"
    echo "     1. 查看 Python 日志: cat $RESULTS_DIR/logcat_app.txt"
    echo "     2. 搜索 import 错误: grep -i 'import' $RESULTS_DIR/logcat_full.txt"
    echo "     3. 搜索崩溃:       grep -i 'fatal\\|crash' $RESULTS_DIR/logcat_full.txt"
    echo "     4. 搜索异常:       grep -i 'exception' $RESULTS_DIR/logcat_full.txt"
fi

echo ""
echo "  📁 测试产物:"
ls -lh "$RESULTS_DIR/"* 2>/dev/null | awk '{print "     " $5 " " $9}'
echo ""

if [ "$APP_CRASHED" = true ]; then
    exit 1
fi
