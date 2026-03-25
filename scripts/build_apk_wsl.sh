#!/bin/bash
# ============================================================
# 摸鱼小助手 - WSL Buildozer APK 编译脚本
# 在 Windows WSL (Ubuntu) 中运行
# ============================================================

set -e

echo "🐟 ========================================="
echo "🐟  摸鱼小助手 APK 编译脚本"
echo "🐟  提肛喝水摸鱼，一个都不能少！"
echo "🐟 ========================================="
echo ""

# ── 项目路径 ──
# WSL 挂载的 Windows 路径
WIN_PROJECT="/mnt/d/code/fish-app"
# WSL 工作目录（避免 Windows 文件系统性能问题）
BUILD_DIR="$HOME/fish-app-build"

echo "📁 Windows 项目路径: $WIN_PROJECT"
echo "📁 WSL 编译目录:     $BUILD_DIR"
echo ""

# ── 1. 安装系统依赖 ──
echo "📦 [1/6] 安装系统依赖..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3 python3-pip python3-venv \
    build-essential git \
    libffi-dev libssl-dev \
    zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
    libncurses5-dev libncursesw5-dev xz-utils tk-dev \
    autoconf libtool pkg-config \
    zip unzip openjdk-17-jdk \
    ccache cmake \
    2>/dev/null

echo "✅ 系统依赖安装完成"

# ── 2. 准备编译目录 ──
echo ""
echo "📂 [2/6] 准备编译目录..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# 复制 core 模块
cp -r "$WIN_PROJECT/core" "$BUILD_DIR/core"

# 复制 mobile 模块
cp -r "$WIN_PROJECT/mobile" "$BUILD_DIR/mobile"

# 把 core 和 mobile 中的内容展平到 BUILD_DIR（Buildozer 需要）
cp "$BUILD_DIR/mobile/main.py" "$BUILD_DIR/main.py"
cp "$BUILD_DIR/mobile/app.py" "$BUILD_DIR/app.py"
cp "$BUILD_DIR/mobile/mobile_monitor.py" "$BUILD_DIR/mobile_monitor.py"
cp "$BUILD_DIR/mobile/buildozer.spec" "$BUILD_DIR/buildozer.spec"

echo "✅ 文件复制完成"

# ── 3. 修复 import 路径（展平后 mobile.xxx → xxx）──
echo ""
echo "🔧 [3/6] 修复 import 路径..."

# main.py: 去掉 mobile.app → app
sed -i 's/from mobile\.app import/from app import/' "$BUILD_DIR/main.py"
sed -i 's/from mobile\.mobile_monitor import/from mobile_monitor import/' "$BUILD_DIR/main.py"

# app.py: mobile.mobile_monitor → mobile_monitor
sed -i 's/from mobile\.mobile_monitor import/from mobile_monitor import/' "$BUILD_DIR/app.py"

# buildozer.spec: source.dir 改为当前目录
sed -i 's|source.dir = .*|source.dir = .|' "$BUILD_DIR/buildozer.spec"

echo "✅ Import 路径修复完成"

# ── 4. 安装 Buildozer ──
echo ""
echo "🛠️ [4/6] 安装 Buildozer..."
cd "$BUILD_DIR"

python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate

pip install --upgrade pip setuptools wheel 2>/dev/null
# ⚠️ Cython 必须 <3.0，否则 pyjnius 编译报错 (undeclared name: long)
pip install buildozer 'cython<3.0' 2>/dev/null

echo "✅ Buildozer 安装完成"

# ── 5. 编译 APK ──
echo ""
echo "🔨 [5/6] 开始编译 APK（首次编译可能需要 10-30 分钟）..."
echo "   编译日志: $BUILD_DIR/buildozer.log"
echo ""

cd "$BUILD_DIR"
buildozer android debug 2>&1 | tee buildozer.log

# ── 6. 复制产物 ──
echo ""
echo "📦 [6/6] 复制 APK 到 Windows..."

APK_FILE=$(find "$BUILD_DIR/bin" -name "*.apk" 2>/dev/null | head -1)

if [ -n "$APK_FILE" ]; then
    mkdir -p "$WIN_PROJECT/dist"
    cp "$APK_FILE" "$WIN_PROJECT/dist/"
    APK_NAME=$(basename "$APK_FILE")
    echo ""
    echo "🎉 ========================================="
    echo "🎉  APK 编译成功！"
    echo "🎉  文件: dist/$APK_NAME"
    echo "🎉  路径: $WIN_PROJECT/dist/$APK_NAME"
    echo "🎉 ========================================="
    echo ""
    echo "📱 安装到手机："
    echo "   adb install dist/$APK_NAME"
    echo ""
else
    echo ""
    echo "❌ ========================================="
    echo "❌  APK 编译失败！"
    echo "❌  请查看日志: $BUILD_DIR/buildozer.log"
    echo "❌ ========================================="
    exit 1
fi
