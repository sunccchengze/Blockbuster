// 旧版 node 场景共用：canvas、中文字体、ffmpeg。路径相对仓库根目录，不写死家目录。
const path = require('path');
const fs = require('fs');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');

function canvas() {
  if (process.env.BB_CANVAS) return require(process.env.BB_CANVAS);
  return require(path.join(ROOT, 'node_modules', '@napi-rs', 'canvas'));
}

const BOLD = ['NotoSansCJK-Bold.ttc', 'NotoSansCJK-Bold.otf', 'NotoSansCJKsc-Bold.otf', 'NotoSansSC-Bold.otf'];
const REG = ['NotoSansCJK-Regular.ttc', 'NotoSansCJK-Regular.otf', 'NotoSansCJKsc-Regular.otf', 'NotoSansSC-Regular.otf'];
const DIRS = [
  '/usr/share/fonts/opentype/noto',
  '/usr/share/fonts/opentype/noto-cjk',
  '/usr/share/fonts/noto-cjk',
  '/usr/share/fonts/truetype/noto',
  '/usr/share/fonts/truetype/noto-cjk',
];

function fontFile(bold) {
  const key = bold ? 'BB_FONT_BOLD' : 'BB_FONT_REGULAR';
  const env = process.env[key];
  if (env) {
    if (fs.existsSync(env)) return env;
    throw new Error(key + ' 指向的文件不存在：' + env);
  }
  const names = bold ? BOLD : REG;
  const dirs = [];
  if (process.env.BB_FONT_DIR) dirs.push(process.env.BB_FONT_DIR);
  dirs.push(...DIRS);
  for (const d of dirs) {
    for (const name of names) {
      const p = path.join(d, name);
      if (fs.existsSync(p)) return p;
    }
  }
  throw new Error('找不到中文字体（Noto Sans CJK）。安装 fonts-noto-cjk，或设置 BB_FONT_DIR / BB_FONT_BOLD / BB_FONT_REGULAR。');
}

function ffmpegBin() {
  if (process.env.BB_FFMPEG && fs.existsSync(process.env.BB_FFMPEG)) return process.env.BB_FFMPEG;
  const which = spawnSync('which', ['ffmpeg'], { encoding: 'utf8' });
  if (which.status === 0 && which.stdout.trim()) return which.stdout.trim();
  const py = spawnSync('python3', ['-c', 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'], { encoding: 'utf8' });
  if (py.status === 0 && py.stdout.trim() && fs.existsSync(py.stdout.trim())) return py.stdout.trim();
  const local = path.join(ROOT, 'node_modules', '@ffmpeg-installer', 'linux-x64', 'ffmpeg');
  if (fs.existsSync(local)) return local;
  throw new Error('找不到 ffmpeg。安装系统 ffmpeg，或 pip install imageio-ffmpeg，或设置 BB_FFMPEG。');
}

module.exports = { ROOT, canvas, fontFile, ffmpegBin };
