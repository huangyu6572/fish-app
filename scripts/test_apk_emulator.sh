#!/bin/bash
# ============================================================
# 摸鱼小助手 - Android 模拟器自动化 APK 测试脚本
# 在 WSL2 (Ubuntu) 中运行，需要 KVM 支持
#
# 测试内容:
#   1. 启动 Android 模拟器
#   2. 安装 APK
#   3. 启动 App 检查是否闪退
#   4. 抓取 logcat 日志分析错误
#   5. 截屏验证 UI 渲染
#   6. 关闭模拟器
#
# 用法:
#   bash scripts/test_apk_emulator.sh [apk_path]
# ============================================================

set -e

# ── 配置 ──
ANDROID_SDK_ROOT="$HOME/.buildozer/android/platform/android-sdk"
ADB="$ANDROID_SDK_ROOT/platform-tools/adb"
EMULATOR="$ANDROID_SDK_ROOT/emulator/emulator"
AVD_NAME="fish_test"
PACKAGE_NAME="org.fishapp.fishassistant"
ACTIVITY="org.kivy.android.PythonActivity"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APK_PATH="${1:-$PROJECT_DIR/dist/fishassistant-1.0.0-arm64-v8a-debug.apk}"
RESULTS_DIR="$PROJECT_DIR/test-results"
TIMEOUT_BOOT=120    # 模拟器启动超时（秒）
TIMEOUT_APP=30      # App 启动等待（秒）

export ANDROID_SDK_ROOT

echo "🐟 ========================================="
echo "🐟  摸鱼小助手 - 模拟器 APK 自动化测试"
echo "🐟 ========================================="
echo ""

# ── 前置检查 ──
check_prerequisites() {
    local ok=true

    if [ ! -f "$EMULATOR" ]; then
        echo "❌ Android 模拟器未安装: $EMULATOR"
        echo "   运行: sdkmanager --install emulator 'system-images;android-34;google_apis;x86_64'"
        ok=false
    fi

    if [ ! -f "$ADB" ]; then
        echo "❌ ADB 未找到: $ADB"
        ok=false
    fi

    if [ ! -f "$APK_PATH" ]; then
        echo "❌ APK 文件不存在: $APK_PATH"
        echo "   先运行 buildozer 编译 APK"
        ok=false
    fi

    if [ ! -e /dev/kvm ]; then
        echo "❌ KVM 不可用，模拟器需要硬件加速"
        echo "   WSL2 中需要: 在 .wslconfig 中设置 nestedVirtualization=true"
        ok=false
    fi

    # 检查 AVD 是否存在
    if [ ! -d "$HOME/.android/avd/${AVD_NAME}.avd" ]; then
        echo "⚠️ AVD '$AVD_NAME' 不存在，正在创建..."
        echo "no" | "$ANDROID_SDK_ROOT/tools/bin/avdmanager" --clear-cache create avd \
            -n "$AVD_NAME" \
            -k "system-images;android-34;google_apis;x86_64" \
            --force 2>/dev/null
        echo "✅ AVD 创建完成"
    fi

    if [ "$ok" = false ]; then
        exit 1
    fi

    echo "✅ 前置检查通过"
    echo "   APK: $APK_PATH"
    echo "   AVD: $AVD_NAME"
    echo ""
}

# ── 启动模拟器 ──
start_emulator() {
    echo "📱 [1/6] 启动 Android 模拟器..."

    # 如果已有运行中的模拟器，先关闭
    "$ADB" devices 2>/dev/null | grep -q emulator && {
        echo "   检测到运行中的模拟器，正在关闭..."
        "$ADB" emu kill 2>/dev/null || true
        sleep 3
    }

    # 后台启动 headless 模拟器（无窗口，适合 CI/WSL）
    "$EMULATOR" -avd "$AVD_NAME" \
        -no-window \
        -no-audio \
        -no-snapshot \
        -gpu swiftshader_indirect \
        -memory 2048 \
        -partition-size 4096 \
        &>/dev/null &
    EMULATOR_PID=$!
    echo "   模拟器 PID: $EMULATOR_PID"

    # 等待模拟器启动完成
    echo "   等待模拟器启动（最多 ${TIMEOUT_BOOT}s）..."
    local waited=0
    while [ $waited -lt $TIMEOUT_BOOT ]; do
        if "$ADB" shell getprop sys.boot_completed 2>/dev/null | grep -q "1"; then
            echo "✅ 模拟器启动完成（${waited}s）"
            return 0
        fi
        sleep 5
        waited=$((waited + 5))
        echo "   等待中... ${waited}s"
    done

    echo "❌ 模拟器启动超时（${TIMEOUT_BOOT}s）"
    kill $EMULATOR_PID 2>/dev/null || true
    exit 1
}

# ── 安装 APK ──
install_apk() {
    echo ""
    echo "📦 [2/6] 安装 APK..."

    # 先卸载旧版本
    "$ADB" uninstall "$PACKAGE_NAME" 2>/dev/null || true

    # 安装新 APK
    if "$ADB" install -r "$APK_PATH" 2>&1; then
        echo "✅ APK 安装成功"
    else
        echo "❌ APK 安装失败"
        exit 1
    fi
}

# ── 启动 App 并检测闪退 ──
test_app_launch() {
    echo ""
    echo "🚀 [3/6] 启动 App 并检测闪退..."

    mkdir -p "$RESULTS_DIR"

    # 清除旧日志
    "$ADB" logcat -c 2>/dev/null

    # 启动 App
    "$ADB" shell am start -n "${PACKAGE_NAME}/${ACTIVITY}" 2>&1
    echo "   等待 App 启动（${TIMEOUT_APP}s）..."
    sleep "$TIMEOUT_APP"

    # 检查 App 是否还在运行
    local running
    running=$("$ADB" shell pidof "$PACKAGE_NAME" 2>/dev/null || echo "")

    if [ -n "$running" ]; then
        echo "✅ App 正在运行 (PID: $running) — 未闪退！"
        APP_CRASHED=false
    else
        echo "❌ App 未在运行 — 可能闪退了！"
        APP_CRASHED=true
    fi
}

# ── 抓取日志 ──
capture_logs() {
    echo ""
    echo "📋 [4/6] 抓取 logcat 日志..."

    # 抓取完整的 Python/Kivy 相关日志
    "$ADB" logcat -d -s "python:*" "PythonActivity:*" "SDL:*" "AndroidRuntime:*" \
        > "$RESULTS_DIR/logcat_filtered.txt" 2>/dev/null

    # 抓取所有日志（用于调试）
    "$ADB" logcat -d > "$RESULTS_DIR/logcat_full.txt" 2>/dev/null

    # 提取关键错误
    echo ""
    echo "   === Python 错误日志 ==="
    grep -i "error\|exception\|traceback\|crash\|FATAL" "$RESULTS_DIR/logcat_filtered.txt" 2>/dev/null | head -30 || echo "   （无 Python 错误）"

    echo ""
    echo "   === AndroidRuntime 错误 ==="
    grep "AndroidRuntime\|FATAL" "$RESULTS_DIR/logcat_full.txt" 2>/dev/null | tail -20 || echo "   （无 Runtime 错误）"

    echo ""
    echo "   日志保存到: $RESULTS_DIR/logcat_filtered.txt"
    echo "   完整日志:   $RESULTS_DIR/logcat_full.txt"
}

# ── 截屏 ──
capture_screenshot() {
    echo ""
    echo "📸 [5/6] 截屏..."

    if [ "$APP_CRASHED" = false ]; then
        "$ADB" shell screencap -p /sdcard/fish_test_screenshot.png 2>/dev/null
        "$ADB" pull /sdcard/fish_test_screenshot.png "$RESULTS_DIR/screenshot.png" 2>/dev/null
        if [ -f "$RESULTS_DIR/screenshot.png" ]; then
            echo "✅ 截屏保存: $RESULTS_DIR/screenshot.png"
        else
            echo "⚠️ 截屏失败"
        fi
    else
        echo "   ⏭️ App 已闪退，跳过截屏"
    fi
}

# ── 关闭模拟器 ──
cleanup() {
    echo ""
    echo "🧹 [6/6] 关闭模拟器..."
    "$ADB" emu kill 2>/dev/null || true
    sleep 2
    kill $EMULATOR_PID 2>/dev/null || true
    echo "✅ 模拟器已关闭"
}

# ── 输出测试报告 ──
report() {
    echo ""
    echo "📊 ========================================="
    echo "📊  测试报告"
    echo "📊 ========================================="
    echo ""
    echo "  APK:        $(basename "$APK_PATH")"
    echo "  APK 大小:   $(du -h "$APK_PATH" | cut -f1)"
    echo "  模拟器:     $AVD_NAME (Android 14, x86_64)"
    echo "  测试时间:   $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    if [ "$APP_CRASHED" = false ]; then
        echo "  ✅ 结果: App 启动成功，未闪退"
    else
        echo "  ❌ 结果: App 闪退！"
        echo ""
        echo "  🔍 排查建议:"
        echo "     1. 查看日志: cat $RESULTS_DIR/logcat_filtered.txt"
        echo "     2. 搜索 Python 错误: grep -i 'error\|import' $RESULTS_DIR/logcat_filtered.txt"
        echo "     3. 搜索 crash: grep -i 'fatal\|crash' $RESULTS_DIR/logcat_full.txt"
    fi
    echo ""
    echo "  📁 测试产物: $RESULTS_DIR/"
    ls -la "$RESULTS_DIR/" 2>/dev/null | grep -v "^total" | grep -v "^\." | sed 's/^/     /'
    echo ""
}

# ── 主流程 ──
main() {
    check_prerequisites
    start_emulator
    install_apk
    test_app_launch
    capture_logs
    capture_screenshot
    cleanup
    report

    if [ "$APP_CRASHED" = true ]; then
        exit 1
    fi
}

# 确保退出时清理模拟器
trap 'kill $EMULATOR_PID 2>/dev/null || true' EXIT

main
