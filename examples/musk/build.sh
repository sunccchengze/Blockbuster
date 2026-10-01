#!/usr/bin/env bash
# 马斯克样例：渲染画面 → 配乐+旁白混音 → 封装并对齐 −14 LUFS → 质检
set -e; cd "$(dirname "$0")"; REPO=../..; OUT=${1:-$HOME/musk/musk_3min.mp4}
export PYTHONPATH=$REPO
python3 -m bb render film.py video.mp4 --jobs 2
python3 score.py
python3 -m bb remux video.mp4 mix.wav "$OUT"
rm -f video.mp4 mix.wav
python3 -m bb qc film.py "$OUT"
