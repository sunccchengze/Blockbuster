#!/usr/bin/env bash
# 在 examples/<name> 目录下调用。参数是该片的成片文件名。
# 配乐脚本自己混入旁白；旧的 music.js 已删除，不要再调用。
set -euo pipefail
OUT="${1:?需要成片文件名，例如 law_of_large_numbers.mp4}"
ROOT="$(cd ../.. && pwd)"
export PYTHONPATH="$ROOT"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  export PATH="$ROOT/.venv/bin:$PATH"
fi
if [[ ! -d "$ROOT/node_modules/@napi-rs/canvas" ]]; then
  (cd "$ROOT" && npm install --no-audit --no-fund)
fi
python3 score.py
node scene.js video
python3 -m bb remux "$OUT" mix.wav "$OUT"
rm -f mix.wav
echo "wrote $OUT"
