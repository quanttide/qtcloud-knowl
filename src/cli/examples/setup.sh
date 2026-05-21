#!/usr/bin/env bash
# 下载示例项目的源文档
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

download() {
    local repo="$1"
    local name="$(basename "$repo" .git)"
    local target="$BASE_DIR/$name"

    if [ -d "$target" ]; then
        echo "✓ $name 已存在"
        return
    fi

    echo "下载 $name ..."
    git clone --depth 1 "$repo" "$target" 2>/dev/null
    echo "✓ $name 已下载到 $target"
}

download "https://github.com/quanttide/quanttide-bylaw-of-business-entity.git"
download "https://github.com/quanttide/quanttide-handbook-of-business-entity.git"
download "https://github.com/quanttide/quanttide-tutorial-of-business-entity.git"

