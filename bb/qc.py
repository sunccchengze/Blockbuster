"""bb.qc — 内容质检（不是只看技术参数）：
1. 字形覆盖：所有上屏文字（字幕、章节、场景内标签——渲染抽样时收集）必须在字体里有字形，否则会显示成方框；
2. 版面：每个抽样帧检测文字出画、文字互相重叠（>15% 面积）；
2b. 字幕长度：单条字幕像素宽度不得超过画面 90%；
3. 字幕时长：每条 ≥ 0.8 s，且字速 ≤ 7 字/秒；
4. 抽样静帧 + 接触单：交给 Agent 看图，检查重叠/裁切/穿模/声画同步；
5. 成片：响度 −14±1 LUFS、峰值 ≤ −1 dBFS。
"""
import os
from fontTools.ttLib import TTCollection
from PIL import ImageFont
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
_cmap = None
def cmap():
    global _cmap
    if _cmap is None: _cmap = set(TTCollection(FONT).fonts[0].getBestCmap().keys())
    return _cmap

def missing_glyphs(texts):
    cm = cmap(); bad = {}
    for t in texts:
        for ch in t:
            if ord(ch) not in cm and not ch.isspace(): bad.setdefault(ch, t)
    return bad

def check_film(film, sample_every=1.0, out_dir=None):
    from . import render3d as R
    issues = []
    R.TEXT_LOG.clear()
    n = 0; t = 0.0; stills = []
    while t < film.total:
        img = R.render_frame(film, int(t * R.FPS))
        B = list(R.BOX_LOG)
        for x0, y0, x1, y1, tx in B:
            if x0 < 0 or y0 < 0 or x1 > R.W or y1 > R.H: issues.append(f'{t:6.1f}s 文字出画：「{tx}」')
        for i in range(len(B)):
            for j in range(i + 1, len(B)):
                a, b = B[i], B[j]; ix = min(a[2], b[2]) - max(a[0], b[0]); iy = min(a[3], b[3]) - max(a[1], b[1])
                if ix > 0 and iy > 0:
                    small = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
                    if ix * iy > 0.15 * small: issues.append(f'{t:6.1f}s 文字重叠：「{a[4]}」×「{b[4]}」')
        if out_dir and abs((t / 10) - round(t / 10)) < 1e-6: p = os.path.join(out_dir, 'qc_%05.1f.png' % t); img.save(p); stills.append(p)
        t += sample_every; n += 1
    texts = set(film.all_text()) | R.TEXT_LOG
    for ch, ctx in missing_glyphs(texts).items(): issues.append(f'缺字形 {ch!r} (U+{ord(ch):04X}) 出现在：{ctx}')
    f = ImageFont.truetype(FONT, film.sub_size)
    for k, seg in enumerate(film.subs):
        for a, b, s in seg:
            w = f.getlength(s)
            if w > R.W * 0.9: issues.append(f'字幕过长 {w:.0f}px：第{k+1}段「{s}」')
            if b - a < 0.8: issues.append(f'字幕过短 {b-a:.2f}s：第{k+1}段「{s}」')
            if len(s) / max(b - a, 1e-3) > 7: issues.append(f'字速过快 {len(s)/(b-a):.1f}字/s：第{k+1}段「{s}」')
    seen = set(); issues = [x for x in issues if not (x[7:] in seen or seen.add(x[7:]))]   # 同一问题只报首次
    return issues, stills

def check_video(path):
    from .media import loudness
    I, P = loudness(path); issues = []
    if abs(I + 14) > 1: issues.append(f'响度 {I} LUFS（目标 −14±1）')
    if P > -1: issues.append(f'峰值 {P} dBFS（应 ≤ −1）')
    return (I, P), issues
