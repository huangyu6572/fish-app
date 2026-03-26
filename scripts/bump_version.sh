#!/bin/bash
# ============================================================
# 摸鱼小助手 - 版本自动更新脚本
# 用法: bash scripts/bump_version.sh <新版本号>
# 示例: bash scripts/bump_version.sh 1.2.0
# ============================================================

set -e

NEW_VERSION="$1"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ -z "$NEW_VERSION" ]; then
    CURRENT=$(grep '__version__' "$PROJECT_DIR/core/__init__.py" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    echo "当前版本: $CURRENT"
    echo "用法: bash scripts/bump_version.sh <新版本号>"
    echo "示例: bash scripts/bump_version.sh 1.2.0"
    exit 1
fi

# 验证版本格式
if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "❌ 版本格式错误，必须是 x.y.z（如 1.2.0）"
    exit 1
fi

CURRENT=$(grep '__version__' "$PROJECT_DIR/core/__init__.py" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
echo "🔖 版本更新: $CURRENT → $NEW_VERSION"

# 1. core/__init__.py（单一真值来源）
sed -i "s/__version__ = \"$CURRENT\"/__version__ = \"$NEW_VERSION\"/" \
    "$PROJECT_DIR/core/__init__.py"
echo "   ✅ core/__init__.py"

# 2. mobile/buildozer.spec
sed -i "s/^version = .*/version = $NEW_VERSION/" \
    "$PROJECT_DIR/mobile/buildozer.spec"
echo "   ✅ mobile/buildozer.spec"

# 3. $HOME/fish-app-build/buildozer.spec（构建目录同步）
if [ -f "$HOME/fish-app-build/buildozer.spec" ]; then
    sed -i "s/^version = .*/version = $NEW_VERSION/" \
        "$HOME/fish-app-build/buildozer.spec"
    echo "   ✅ ~/fish-app-build/buildozer.spec"
fi

echo ""
echo "✅ 版本已更新至 $NEW_VERSION"
echo "   下一步: bash scripts/build_apk_wsl.sh"
