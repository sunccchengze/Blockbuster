#!/usr/bin/env bash
# 在 examples/<name> 内调用；JOBS 可覆盖默认的两个渲染进程。
set -euo pipefail
OUT="${1:?需要成片文件名}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  export PATH="$ROOT/.venv/bin:$PATH"
fi
python3 -m bb render film.py video.mp4 --jobs "${JOBS:-2}"
python3 score.py
python3 -m bb remux video.mp4 mix.wav "$OUT"
if [[ ! "$OUT" -ef video.mp4 ]]; then
  rm -f video.mp4
fi
rm -f mix.wav
python3 -m bb qc film.py "$OUT"
