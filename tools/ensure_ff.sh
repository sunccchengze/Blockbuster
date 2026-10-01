#!/usr/bin/env bash
# 用法: source tools/ensure_ff.sh
# 在仓库根的 .venv 里安装 Python 依赖，并把 imageio-ffmpeg 放进 PATH。
# 中文字体不在这里安装：需要系统包 fonts-noto-cjk，或设置 BB_FONT_DIR。
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "请用 source 运行，这样 PATH 才会留在当前 shell：source tools/ensure_ff.sh" >&2
  exit 1
fi
if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  python3 -m venv "$ROOT/.venv"
fi
"$ROOT/.venv/bin/pip" install -q -r "$ROOT/requirements.txt"
FF="$("$ROOT/.venv/bin/python" -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')"
mkdir -p "$ROOT/.bin"
ln -sfn "$FF" "$ROOT/.bin/ffmpeg"
export PATH="$ROOT/.bin:$ROOT/.venv/bin:$PATH"
export VIRTUAL_ENV="$ROOT/.venv"
hash -r 2>/dev/null || true
echo "已就绪：python=$ROOT/.venv/bin/python  ffmpeg=$ROOT/.bin/ffmpeg"
