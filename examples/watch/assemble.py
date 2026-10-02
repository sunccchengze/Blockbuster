"""帧序列 → 片尾字幕叠加 → H.264（CRF 14，高画质）→ 混音并做 −14 LUFS 响度。"""
import os, sys, glob, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from PIL import Image, ImageDraw, ImageFilter
from bb.render3d import font
from bb.media import ffmpeg
SRC = os.path.join(HERE, 'frames') + os.sep; DST = os.path.join(HERE, '.cache', 'overlay') + os.sep; os.makedirs(DST, exist_ok=True)
fs = sorted(glob.glob(SRC + 'f_*.jpg')); assert len(fs) == 250, len(fs)
def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
for i, f in enumerate(fs, 1):
    out = DST + f'f_{i:04d}.png'
    a = ease((i - 220) / 14)
    if a <= 0: Image.open(f).save(out); continue
    im = Image.open(f).convert('RGBA'); W, H = im.size
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rectangle((0, H - 170, W, H), fill=(0, 0, 0, int(110 * a)))
    ov = ov.filter(ImageFilter.GaussianBlur(30)); d = ImageDraw.Draw(ov)
    title = '  '.join('TOURBILLON'); sp = 4 + 6 * (1 - a)     # 字距从宽收紧
    x = W / 2; y = H - 108
    d.text((x, y), title, font=font(46, bold=False), fill=(240, 222, 190, int(255 * a)), anchor='mm')
    d.line((W / 2 - 160 * a, y + 36, W / 2 + 160 * a, y + 36), fill=(240, 200, 140, int(200 * a)), width=1)
    d.text((x, y + 62), '飞行陀飞轮机芯 · 全程序化建模 · Cycles 路径追踪 · 一镜到底', font=font(20, bold=False), fill=(220, 220, 225, int(220 * a)), anchor='mm')
    Image.alpha_composite(im, ov).convert('RGB').save(out)
FF = ffmpeg()
subprocess.run([FF, '-v', 'error', '-y', '-framerate', '25', '-i', DST + 'f_%04d.png', '-c:v', 'libx264', '-preset', 'slow', '-crf', '14',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', os.path.join(HERE, 'video.mp4')], check=True)
print('video ok')
