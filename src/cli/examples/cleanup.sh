#!/usr/bin/env bash
# 删除下载的示例源文档
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

for dir in "$BASE_DIR"/qtcloud-*/; do
    [ -d "$dir" ] || continue
    echo "删除 $dir"
    rm -rf "$dir"
done

echo "清理完成。"
