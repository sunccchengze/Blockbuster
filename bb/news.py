"""bb.news — 新闻播报类片子的包装和通用模型。

包装：chrome()（左上台标 + 日期 + 栏目标签）、headline()（第 N 件 + 标题条，滑入）、
      card()（2D 数据卡片）、counter()（数字滚动）、dip()（段内分镜之间的快速压暗）。
模型：torus()、avatar()（带眼睛的 Dot 小精灵）、rack()（服务器机柜，灯带自发光）、
      panel()（浮空屏幕）、laptop()、person()（不画真人：胶囊小人）、coin()、shield()。
"""
from .render3d import *

WHITE = (255, 255, 255)
DIM = (170, 182, 200)


# ---------------- 动画小工具 ----------------
def win(t, a, b, fi=0.35, fo=0.35):
    """t 在 [a, b] 内为 1，两端淡入淡出。"""
    return clamp((t - a) / fi) * (1 - clamp((t - (b - fo)) / fo)) if b > a else 0.0


def pop(t, a, d=0.45):
    """弹出：0→1 带一点过冲。"""
    x = clamp((t - a) / d)
    return 1 + 2.2 * (x - 1) ** 3 + 1.2 * (x - 1) ** 2 if x < 1 else 1.0


def dip(t, cuts, w=0.22):
    """分镜切换点 cuts 附近整体压暗，返回 dim 值。"""
    m = 1.0
    for c in cuts: m = min(m, clamp(abs(t - c) / w))
    return 0.25 + 0.75 * m


def counter(t, a, b, v0, v1, fmt='{:.0f}'):
    return fmt.format(lerp(v0, v1, ease((t - a) / max(b - a, 1e-6))))


# ---------------- 2D 包装 ----------------
def chrome(f, accent, tag, date='10月1日 周四', a=1.0):
    f.rect(28, 20, 146, 58, (*accent, int(240 * a)), r=8)
    f.text(87, 39, 'AI 早报', 23, anc='mm', a=a)
    f.text(160, 31, date, 18, col=(225, 232, 244), bold=False, a=a)
    f.text(160, 51, tag, 15, col=tuple(int(c * 0.5 + 127) for c in accent), bold=False, a=a)


def headline(f, lt, accent, num, title, sub=None, t0=0.15):
    """第 num 件 + 标题，从左侧滑入。"""
    x = ease((lt - t0) / 0.5); off = (1 - x) * -60; a = x
    if a < 0.02: return
    y = 80
    if num:
        f.rect(28 + off, y, 76 + off, y + 44, (*accent, int(235 * a)), r=6)
        f.text(52 + off, y + 22, num, 26, anc='mm', a=a)
        tx = 88
    else:
        tx = 28
    f.text(tx + off, y + 22, title, 32, anc='lm', a=a, stroke=2)
    if sub: f.text(tx + off, y + 62, sub, 20, col=DIM, anc='lm', bold=False, a=a)


def card(f, x, y, w, h, title, value, unit='', accent=(80, 170, 255), a=1.0, vsz=40, note=None):
    if a < 0.02: return
    f.rect(x, y, x + w, y + h, (10, 16, 30, int(200 * a)), r=10, outline=(*accent, int(160 * a)), w=2)
    f.rect(x, y, x + 6, y + h, (*accent, int(255 * a)), r=3)
    f.text(x + 20, y + 22, title, 18, col=DIM, anc='lm', bold=False, a=a)
    f.text(x + 20, y + 22 + 16 + vsz * 0.6, value, vsz, anc='lm', a=a)
    if unit:
        vw = font(vsz).getlength(value)
        f.text(x + 26 + vw, y + 22 + 16 + vsz * 0.6 + vsz * 0.18, unit, 20, col=DIM, anc='lm', bold=False, a=a)
    if note: f.text(x + 20, y + h - 18, note, 15, col=DIM, anc='lm', bold=False, a=a)


# ---------------- 模型 ----------------
def torus(R, r, col, n=40, m=10, arc=2 * pi):
    V, F = [], []
    closed = abs(arc - 2 * pi) < 1e-6; na = n if closed else n + 1
    for i in range(na):
        a = arc * i / n
        for j in range(m):
            b = 2 * pi * j / m; V.append([(R + r * math.cos(b)) * math.cos(a), r * math.sin(b), (R + r * math.cos(b)) * math.sin(a)])
    for i in range(n):
        i2 = (i + 1) % na if closed else i + 1
        for j in range(m):
            j2 = (j + 1) % m; F.append([i * m + j, i * m + j2, i2 * m + j2, i2 * m + j])
    V = np.array(V, float); F = np.array(F, int)
    nrm_ = np.cross(V[F[:, 2]] - V[F[:, 0]], V[F[:, 3]] - V[F[:, 1]]); fc = V[F].mean(1)
    ang = np.arctan2(fc[:, 2], fc[:, 0]); tc = np.stack([R * np.cos(ang), np.zeros_like(ang), R * np.sin(ang)], 1)
    S = np.sign(np.einsum('ij,ij->i', nrm_, fc - tc)); S[S == 0] = 1
    return Mesh(V, F, S, np.tile(col, (len(F), 1)))


def tube(pts, r, col, m=8):
    """沿折线的圆管（连线、线缆）。"""
    pts = np.asarray(pts, float); V, F = [], []
    for i, p in enumerate(pts):
        t = nrm(pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]); u = nrm(np.cross(t, [0, 1, 0]) if abs(t[1]) < 0.9 else np.cross(t, [1, 0, 0])); v = np.cross(t, u)
        for j in range(m): b = 2 * pi * j / m; V.append(p + r * (math.cos(b) * u + math.sin(b) * v))
    for i in range(len(pts) - 1):
        for j in range(m): F.append([i * m + j, i * m + (j + 1) % m, (i + 1) * m + (j + 1) % m, (i + 1) * m + j])
    V = np.array(V); F = np.array(F)
    nrm_ = np.cross(V[F[:, 2]] - V[F[:, 0]], V[F[:, 3]] - V[F[:, 1]]); fc = V[F].mean(1)
    ctr = np.array([pts[i] for i in range(len(pts) - 1) for _ in range(m)]) * 0.5 + np.array([pts[i + 1] for i in range(len(pts) - 1) for _ in range(m)]) * 0.5
    S = np.sign(np.einsum('ij,ij->i', nrm_, fc - ctr)); S[S == 0] = 1
    return Mesh(V, F, S, np.tile(col, (len(F), 1)))


def emissive(m, e):
    m.E = np.full(len(m.F), float(e)); return m


def glow_merge(parts):
    """parts = [(mesh, emis)] → 带逐面自发光的合并网格。"""
    M = merge([p for p, _ in parts]); M.E = np.concatenate([np.full(len(p.F), e) for p, e in parts]); return M


M_EYE = sphere(1, (250, 250, 255), 14, 8)
M_PUPIL = sphere(1, (15, 20, 30), 12, 6)


def avatar(f, P, col, r=1.0, yaw=None, blink=0.0, alpha=255, emis=0.25):
    """Dot 小精灵：球身 + 一对会眨的眼睛，自动朝向相机（yaw 可覆盖）。"""
    P = np.array(P, float)
    if yaw is None: d = f.cam.p - P; yaw = math.atan2(d[0], d[2])
    R = roty(yaw)
    f.mesh(_body(col), T=P, sc=r, alpha=alpha, emis=emis)
    ey = 1 - 0.9 * blink
    for s in (-1, 1):
        e = P + R @ np.array([0.36 * s, 0.18, 0.86]) * r
        f.mesh(M_EYE, R=R @ np.diag([1, ey, 1]), T=e, sc=0.2 * r, alpha=alpha)
        f.mesh(M_PUPIL, R=R @ np.diag([1, ey, 1]), T=e + R @ np.array([0, 0, 0.12]) * r, sc=0.11 * r, alpha=alpha)


_BODIES = {}


def _body(col):
    k = tuple(col)
    if k not in _BODIES: _BODIES[k] = sphere(1, col, 30, 16)
    return _BODIES[k]


def rack(w=2.0, h=4.0, d=1.6, col=(36, 44, 60), led=(80, 220, 160), rows=8):
    ps = [(box(w, h, d, col), 0.0)]
    for i in range(rows):
        y = -h / 2 + (i + 0.6) * h / rows
        ps.append((box(w * 0.86, h / rows * 0.55, 0.05, (22, 26, 36), T=(0, y, d / 2 + 0.01)), 0.0))
        ps.append((box(w * 0.22, 0.07, 0.06, led, T=(-w * 0.26, y, d / 2 + 0.03)), 0.9))
        ps.append((box(0.07, 0.07, 0.06, (255, 180, 80) if i % 3 == 0 else led, T=(w * 0.32, y, d / 2 + 0.03)), 0.9))
    return glow_merge(ps)


def panel(w, h, col=(18, 26, 44), frame=(90, 110, 140), d=0.08):
    return merge([box(w, h, d, col), box(w + 0.12, 0.08, d + 0.02, frame, T=(0, h / 2, 0)), box(w + 0.12, 0.08, d + 0.02, frame, T=(0, -h / 2, 0)),
                  box(0.08, h, d + 0.02, frame, T=(-w / 2, 0, 0)), box(0.08, h, d + 0.02, frame, T=(w / 2, 0, 0))])


def person(col=(200, 210, 225), h=1.8):
    V, F = lathe([(0, 0), (0.28, 0.02), (0.3, 0.9), (0.24, 1.2), (0, 1.25)], 12)
    return merge([part(V, F, col), part(*lathe([(0, 0), (0.17, 0.05), (0.2, 0.2), (0.17, 0.35), (0, 0.4)], 12), (235, 210, 190), T=(0, 1.3, 0))])


def coin(r=1.0, col=(235, 185, 60)): return disc(r, 0.18 * r, col)


def shield(w=3.0, h=3.6, col=(60, 160, 255)):
    prof = [(-w / 2, h / 2), (w / 2, h / 2), (w / 2, 0), (0.0, -h / 2), (-w / 2, 0)]
    V = [[x, y, 0.15] for x, y in prof] + [[x, y, -0.15] for x, y in prof]
    F = [[0, 1, 2, 4], [2, 3, 4, 4], [5, 9, 7, 6], [7, 9, 8, 8]] + [[i, (i + 1) % 5, (i + 1) % 5 + 5, i + 5] for i in range(5)]
    return part(V, F, col)
