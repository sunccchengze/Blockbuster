#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec bash ../../tools/build_python_film.sh "${1:-devday_2026_news.mp4}"
