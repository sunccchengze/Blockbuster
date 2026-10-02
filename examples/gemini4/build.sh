#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec bash ../../tools/build_python_film.sh "${1:-gemini4_argon_news.mp4}"
