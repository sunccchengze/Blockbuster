#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec "$(cd ../.. && pwd)/tools/build_node_film.sh" pinn_explained.mp4
