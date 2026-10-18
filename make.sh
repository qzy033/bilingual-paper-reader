#!/usr/bin/env bash
# 一条龙：PDF -> 分节 -> 翻译 -> 术语表 -> 构建 -> 可选打包
# 用法: ./make.sh paper.pdf my-paper [--no-translate] [--package]
set -euo pipefail
cd "$(dirname "$0")"

PDF="${1:?用法: ./make.sh paper.pdf slug [--no-translate] [--package]}"
SLUG="${2:?缺少 slug}"
shift 2

NOTRANSLATE=0
PACKAGE=0
for a in "$@"; do
  case "$a" in
    --no-translate) NOTRANSLATE=1 ;;
    --package) PACKAGE=1 ;;
    *) echo "未知参数: $a"; exit 1 ;;
  esac
done

command -v python3 >/dev/null || { echo "需要 python3"; exit 1; }
python3 -c "import pymupdf" 2>/dev/null || python3 -m pip install --quiet pymupdf

echo "[1/4] 抽取 PDF 文本"
python3 tools/pdf_to_json.py "$PDF" "$SLUG"

if [ "$NOTRANSLATE" = "1" ]; then
  echo "[2/4] 跳过翻译"
else
  echo "[2/4] 翻译 + 术语表"
  if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "没有 OPENAI_API_KEY：只统计工作量。"
    python3 tools/translate.py --slug "$SLUG" --dry-run
    exit 2
  fi
  python3 tools/translate.py --slug "$SLUG" --with-terms
fi

echo "[3/4] 构建"
python3 build_paper.py

if [ "$PACKAGE" = "1" ]; then
  echo "[4/4] 打包"
  python3 tools/package.py
fi

echo "完成：打开 reader/index.html"
