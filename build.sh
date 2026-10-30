#!/usr/bin/env bash
# 悬浮计时器 构建脚本
# 用法: ./build.sh
# 产物:
#   dist/floating_timer               静态二进制（PyInstaller onefile，自包含）
#   rpm/RPMS/x86_64/floating-timer-*.rpm   RPM 安装包（可在其他 EL8 兼容机器安装）
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-/usr/bin/python3.12}"
VENV=".venv"

echo "==> [1/4] 准备 Python 虚拟环境与 PyInstaller"
if [ ! -x "$VENV/bin/pyinstaller" ]; then
    "$PYTHON" -m venv "$VENV"
    "$VENV/bin/pip" install --upgrade pip >/dev/null
    "$VENV/bin/pip" install pyinstaller
fi

echo "==> [2/4] 编译静态二进制 (PyInstaller onefile)"
rm -rf build dist
"$VENV/bin/pyinstaller" --noconfirm --clean \
    --name floating_timer \
    --onefile \
    --windowed \
    src/floating_timer.py

echo "==> [3/4] 组装 RPM 源文件"
mkdir -p rpm/SOURCES rpm/SPECS rpm/BUILD rpm/BUILDROOT rpm/RPMS
cp dist/floating_timer rpm/SOURCES/
cp packaging/floating-timer.desktop rpm/SOURCES/
cp packaging/icon.png rpm/SOURCES/
cp packaging/floating-timer.spec rpm/SPECS/

echo "==> [4/4] 编译 RPM 包"
rpmbuild --define "_topdir $(pwd)/rpm" -bb rpm/SPECS/floating-timer.spec

echo ""
echo "==> 构建完成，产物如下:"
ls -lh dist/floating_timer
find rpm/RPMS -name "*.rpm" -exec ls -lh {} \;
