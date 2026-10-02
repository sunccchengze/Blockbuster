"""讲解类 3D 短片的公共件：包装、镜头底板、常用几何（方块/标签/面板/概率柱/数据流）。
与 bb.news 配合使用：from bb.render3d import *; from bb.news import *; from bb.explain import *
"""
import math, json, os
import numpy as np
from bb.render3d import *
from bb.news import *
from bb.timeline import starts_from_durations

CYAN = (70, 200, 255); GREEN = (80, 220, 120); RED = (240, 80, 80); GOLD = (245, 190, 70)
PURPLE = (160, 110, 255); BLUE = (80, 140, 255); GREY = (120, 130, 150); ORANGE = (255, 140, 60)
STEEL = (200, 206, 216); DARK = (40, 46, 58); PINK = (255, 110, 170); TEAL = (60, 220, 200)

M_BOX = box(1, 1, 1, WHITE)
M_BALL = sphere(1, WHITE, 18, 10)
M_RING = torus(1, 0.05, WHITE, 48, 6)
M_PERSON = person((150, 160, 180))
M_COIN = coin(1.0)


def load_timing(here, first=0.6, gap=0.5, tail=2.6):
    TM = json.load(open(os.path.join(here, 'timing.json')))
    dur = TM['durs']; SEG = starts_from_durations(dur, first=first, gap=gap)
    SUBS = [[(a, b - 0.2 if i + 1 < len(s) else b, t) for i, (a, b, t) in enumerate(s)] for s in TM['subs']]
    def merge_short(s, m=0.8):
        out = []; i = 0
        while i < len(s):
            a, b, t = s[i]
            if b - a < m and i + 1 < len(s):
                a2, b2, t2 = s[i + 1]; out.append((a, b2, t + '，' + t2)); i += 2
            else: out.append((a, b, t)); i += 1
        return out
    DISP = [merge_short(s) for s in SUBS]
    return dur, SEG, SUBS, DISP, SEG[-1] + dur[-1] + tail


def base(cam, lt, d, cuts=()):
    f = Fr(cam); f.dim = min(ease(lt / 0.3), 1 - ease((lt - d - 0.02) / 0.32), dip(lt, cuts)); return f
def cube(f, P, s, col, emis=0.15, alpha=255, R=I3):
    f.mesh(M_BOX, R=R @ np.diag(s if hasattr(s, '__len__') else [s, s, s]), T=P, col=col, emis=emis, alpha=int(alpha))
def ball(f, P, r, col, emis=0.6, alpha=255):
    f.mesh(M_BALL, T=P, sc=r, col=col, emis=emis, alpha=int(alpha))
def ring(f, P, r, col, alpha=255, R=I3, emis=0.9):
    f.mesh(M_RING, R=R, T=P, sc=r, col=col, emis=emis, alpha=int(alpha))
def floor(f, col=(110, 170, 255), a=30, y=0.0):
    f.grid(y, 30, 3, (*col, a)); f.layer()
def lab(f, P, s, sz=20, col=WHITE, dy=-10, a=1.0):
    f.label(P, s, sz, col, dx=0, dy=dy, dot=False, a=a)
def flow(f, P0, P1, t, col, n=4, speed=0.8, r=0.08, a=230):
    P0 = np.asarray(P0, float); P1 = np.asarray(P1, float)
    for q in range(n):
        ph = (t * speed + q / n) % 1; f.dots([P0 + (P1 - P0) * ph], r, (*col, int(a)))
def beam(f, P0, P1, col, a=140, w=3):
    f.line([P0, P1], (*col, int(a)), w)
def slab(f, P, w, h, col, emis=0.25, alpha=255, d=0.12, R=I3):
    cube(f, P, (w, h, d), col, emis, alpha, R)
def bars(f, P, vals, cols, w=0.5, gap=0.15, hmax=3.0, g=1.0, emis=0.35):
    """沿 x 轴一排柱（概率分布），P 为中心底部。"""
    n = len(vals); x0 = P[0] - (n - 1) * (w + gap) / 2
    for i, v in enumerate(vals):
        h = max(v * hmax * g, 0.02)
        c = cols[i] if isinstance(cols, list) else cols
        cube(f, (x0 + i * (w + gap), P[1] + h / 2, P[2]), (w, h, w), c, emis)
    return [x0 + i * (w + gap) for i in range(n)]


def chrome_x(f, accent, tag, a=1.0, badge='深度讲解'):
    f.rect(28, 20, 146, 58, (*accent, int(240 * a)), r=8)
    f.text(87, 39, badge, 22, anc='mm', a=a)
    f.text(160, 31, '信息截至 2026年10月1日', 16, col=(225, 232, 244), bold=False, a=a)
    f.text(160, 51, tag, 15, col=tuple(int(c * 0.5 + 127) for c in accent), bold=False, a=a)


def note(f, x, y, s, a, sz=26, col=WHITE, w=None, accent=None):
    """屏幕下方居中提示条。"""
    if a < 0.02: return
    tw = font(sz).getlength(s) if w is None else w
    f.rect(x - tw / 2 - 18, y - sz * 0.8, x + tw / 2 + 18, y + sz * 0.8, (10, 14, 26, int(200 * a)), r=10,
           outline=(*accent, int(180 * a)) if accent else None, w=2)
    f.text(x, y, s, sz, col=col, anc='mm', a=a)


def stamp(f, x, y, s, a, col=RED, sz=28):
    if a < 0.02: return
    tw = font(sz).getlength(s)
    f.rect(x - tw / 2 - 16, y - sz * 0.75, x + tw / 2 + 16, y + sz * 0.75, (*col, int(60 * a)), r=6, outline=(*col, int(230 * a)), w=3)
    f.text(x, y, s, sz, col=col, anc='mm', a=a)
