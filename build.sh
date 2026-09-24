#!/bin/sh
# JupyterLite サイトをビルドする（教員用）。
# 使い方: sh build.sh [出力先]   既定の出力先は Claude ジョブの tmp。Drive にはビルド成果物を置かない。
# サイト内のフォルダ構成を notebooks/ と data/ に保つため、いったん stage/ に集めてから --contents stage を渡す
# （--contents にフォルダを直接渡すと中身が平坦化され、ノートブックの ../data/ が壊れる）。
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-/Users/kenichi.shibata/.claude/jobs/fdb81dd8/tmp/jl_output}"
VENV="${JL_VENV:-/Users/kenichi.shibata/.claude/jobs/fdb81dd8/tmp/jlvenv}"
STAGE="$(mktemp -d)"
. "$VENV/bin/activate"
cd "$HERE"
mkdir -p "$STAGE/notebooks" "$STAGE/data"
cp notebooks/*.ipynb "$STAGE/notebooks/"
cp data/*.csv data/*.ttf data/SOURCES.md data/OFL_*.txt "$STAGE/data/"
rm -rf "$OUT" .jupyterlite.doit.db
jupyter lite build --contents "$STAGE" --output-dir "$OUT"
rm -rf "$STAGE" .jupyterlite.doit.db
echo "built: $OUT"
echo "test:  cd \"$OUT\" && python -m http.server 8765   → http://localhost:8765/"
