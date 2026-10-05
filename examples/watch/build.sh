#!/usr/bin/env bash
# Blender 本体不随工程入库；BB_BLENDER 可指定可执行文件。
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  export PATH="$ROOT/.venv/bin:$PATH"
fi
BLENDER="${BB_BLENDER:-blender}"
if ! command -v "$BLENDER" >/dev/null 2>&1; then
  echo "需要 Blender 4.2；安装后设置 BB_BLENDER=/path/to/blender。" >&2
  exit 1
fi
"$BLENDER" -b --factory-startup -P scene.py -- render 1 250
python3 assemble.py
python3 score.py
OUT="${1:-watch.mp4}"
python3 -m bb remux video.mp4 mix.wav "$OUT"
if [[ ! "$OUT" -ef video.mp4 ]]; then
  rm -f video.mp4
fi
rm -f mix.wav
# 保留 frames/ 以便检查或断点续渲；它已被 .gitignore 排除。
