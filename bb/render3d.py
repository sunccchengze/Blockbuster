"""bb.render3d — 程序化 3D 渲染核心（numpy 透视投影 + 平面光照 + 画家算法 + 2× 超采样）

用法：在 film.py 里 `from bb.render3d import *`，写若干场景函数 scene(lt, dur) -> Fr，
最后构造 FILM = Film(...)。渲染/静帧/质检统一走 `python3 -m bb ...`。
"""
import numpy as np, math, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
W, H, FPS, SS = 1280, 720, 25, 2
W2, H2 = W * SS, H * SS
pi = math.pi
# ---------------- math ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x
def nrm(v): v = np.asarray(v, float); return v / (np.linalg.norm(v) + 1e-12)
def roty(a): c, s = math.cos(a), math.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def rotx(a): c, s = math.cos(a), math.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def rotz(a): c, s = math.cos(a), math.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
I3 = np.eye(3)
LIGHT = nrm([0.5, 0.8, 0.45])

class Cam:
    def __init__(s, pos, tgt, fov=45):
        s.p = np.array(pos, float); f = nrm(np.array(tgt, float) - s.p)
        r = nrm(np.cross(f, [0, 1, 0])); u = np.cross(r, f)
        s.f, s.r, s.u = f, r, u; s.foc = (H2 / 2) / math.tan(math.radians(fov / 2))
    def proj(s, P):
        d = np.asarray(P, float) - s.p; z = d @ s.f; zc = np.maximum(z, 1e-3)
        return np.stack([W2 / 2 + s.foc * (d @ s.r) / zc, H2 / 2 - s.foc * (d @ s.u) / zc], -1), z
def orbit(a, rad, h, tgt, fov=45):
    t = np.array(tgt, float); return Cam(t + [rad * math.sin(a), h, rad * math.cos(a)], t, fov)

# ---------------- meshes ----------------
class Mesh:
    def __init__(s, V, F, S, C): s.V, s.F, s.S, s.C = np.array(V, float), np.array(F, int), np.array(S, float), np.array(C, float)
def part(V, F, col, R=I3, T=(0,0,0)):
    V = np.array(V, float) @ R.T + np.array(T, float); F = np.array(F, int)
    n = np.cross(V[F[:,2]] - V[F[:,0]], V[F[:,3]] - V[F[:,1]]); fc = V[F].mean(1)
    S = np.sign(np.einsum('ij,ij->i', n, fc - V.mean(0))); S[S == 0] = 1
    return Mesh(V, F, S, np.tile(col, (len(F), 1)))
def merge(ms):
    V, F, S, C, o = [], [], [], [], 0
    for m in ms: V.append(m.V); F.append(m.F + o); S.append(m.S); C.append(m.C); o += len(m.V)
    return Mesh(np.vstack(V), np.vstack(F), np.concatenate(S), np.vstack(C))
def lathe(prof, n=24):
    V, F = [], []
    for r, y in prof:
        for j in range(n): a = 2 * pi * j / n; V.append([r * math.cos(a), y, r * math.sin(a)])
    for i in range(len(prof) - 1):
        for j in range(n): a = i * n + j; b = i * n + (j + 1) % n; F.append([a, b, b + n, a + n])
    return V, F
def box(sx, sy, sz, col, T=(0,0,0), R=I3, top=1.0):
    x, y, z = sx / 2, sy / 2, sz / 2; tx, tz = x * top, z * top
    V = [[-x,-y,-z],[x,-y,-z],[x,-y,z],[-x,-y,z],[-tx,y,-tz],[tx,y,-tz],[tx,y,tz],[-tx,y,tz]]
    F = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
    return part(V, F, col, R, T)
def sphere(r, col, n=28, m=14):
    prof = [(r * math.sin(pi * i / m), -r * math.cos(pi * i / m)) for i in range(m + 1)]
    V, F = lathe(prof, n); return part(V, F, col)
def disc(r, h, col): V, F = lathe([(0,0),(r,0),(r,h),(0,h)], 20); return part(V, F, col)

# ---------------- frame / drawing ----------------
def font(sz, bold=True, _c={}):
    k = (int(sz), bold)
    if k not in _c:
        from .fonts import cjk_font
        _c[k] = ImageFont.truetype(cjk_font(bold), int(sz))
    return _c[k]
rng = np.random.default_rng(7)
STARS = np.array([nrm(v) for v in rng.normal(size=(700, 3))]) * 600
STAR_B = rng.uniform(60, 230, 700)
BG = Image.new('RGB', (W2, H2)); _g = np.linspace(0, 1, H2)[:, None]
BG = Image.fromarray(np.broadcast_to(((1 - _g) * np.array([6, 9, 18]) + _g * np.array([14, 20, 36]))[:, None, :], (H2, W2, 3)).astype(np.uint8).copy())

class Fr:
    def __init__(s, cam): s.cam = cam; s.L = [[]]; s.ov = []; s.dim = 1.0; s.stars = True
    def layer(s): s.L.append([])
    def mesh(s, m, R=I3, T=(0,0,0), sc=1.0, alpha=255, cull=True, emis=0.0, col=None):
        V = m.V @ (R.T * sc) + np.array(T, float); Fi = m.F
        n = np.cross(V[Fi[:,2]] - V[Fi[:,0]], V[Fi[:,3]] - V[Fi[:,1]]); n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9); n *= m.S[:, None]
        fc = V[Fi].mean(1)
        vis = np.einsum('ij,ij->i', n, fc - s.cam.p) < 0 if cull else np.ones(len(Fi), bool)
        P2, z = s.cam.proj(V); zf = z[Fi].mean(1); ok = vis & (z[Fi].min(1) > 0.5)
        lam = np.clip(n @ LIGHT, 0, None) if cull else np.abs(n @ LIGHT)
        rim = np.clip(1 - np.abs(np.einsum('ij,ij->i', n, nrm(s.cam.p - fc) if False else (s.cam.p - fc) / (np.linalg.norm(s.cam.p - fc, axis=1, keepdims=True) + 1e-9))), 0, 1) ** 3
        base = m.C if col is None else np.array(col, float)[None, :]
        E = getattr(m, 'E', None); emv = emis + (E if E is not None else 0)
        c = np.clip(base * (0.25 + 0.75 * lam + emv)[:, None] + 70 * rim[:, None], 0, 255).astype(int)
        L = s.L[-1]
        for i in np.nonzero(ok)[0]: L.append((zf[i], 0, P2[Fi[i]].ravel().tolist(), (*c[i], alpha)))
    def line(s, pts, rgba, w=2):
        P2, z = s.cam.proj(np.asarray(pts, float)); L = s.L[-1]
        for i in range(len(pts) - 1):
            if z[i] > 0.5 and z[i + 1] > 0.5: L.append(((z[i] + z[i + 1]) / 2, 1, [*P2[i], *P2[i + 1]], rgba, w))
    def dots(s, pts, r, rgba, world=True):
        pts = np.asarray(pts, float).reshape(-1, 3); P2, z = s.cam.proj(pts); L = s.L[-1]
        for i in range(len(pts)):
            if z[i] > 0.5:
                rr = r * s.cam.foc / z[i] if world else r * SS
                L.append((z[i], 2, (P2[i][0], P2[i][1], max(rr, 0.8)), rgba if len(rgba) == 4 or isinstance(rgba[0], int) else rgba[i]))
    def pt(s, P):
        P2, z = s.cam.proj(np.asarray(P, float)[None]); return P2[0][0] / SS, P2[0][1] / SS, z[0]
    def text(s, x, y, t, sz, col=(255,255,255), anc='la', bold=True, stroke=0, a=1.0):
        if a > 0.01: s.ov.append((x, y, t, sz, col, anc, bold, stroke, a))
    def label(s, P, t, sz=26, col=(255,255,255), dx=30, dy=-40, a=1.0, dot=True):
        x, y, z = s.pt(P)
        if z > 0.5 and a > 0.01: s.ov.append(('lbl', x, y, dx, dy, t, sz, col, a, dot))
    def grid(s, y=0, ext=60, step=5, rgba=(90,160,255,40)):
        r = np.arange(-ext, ext + 0.1, step)
        for v in r:
            s.line([[v, y, u] for u in r], rgba, 2); s.line([[u, y, v] for u in r], rgba, 2)

M_GLOBE = sphere(10, (22,52,110), 36, 18)   # draw_globe 默认地球网格
def draw_globe(f, center, R, rot, tilt=0.0, col=None, gridcol=(80,170,255,70), m=None):
    Rm = rotx(tilt) @ roty(rot)
    f.mesh(m or M_GLOBE, R=Rm, T=center, sc=R / 10 if m is None else 1, col=col)
    f.layer(); c = np.array(center, float)
    def seg(pts):
        pts = np.array(pts) @ Rm.T * R * 1.003 + c
        face = np.einsum('ij,ij->i', pts - c, f.cam.p - pts) > 0
        for i in range(len(pts) - 1):
            if face[i] and face[i + 1]: f.line(pts[i:i + 2], gridcol, 2)
    for lat in range(-60, 61, 30):
        la = math.radians(lat); seg([[math.cos(la) * math.cos(t), math.sin(la), math.cos(la) * math.sin(t)] for t in np.linspace(0, 2 * pi, 49)])
    for lon in range(0, 360, 30):
        lo = math.radians(lon); seg([[math.cos(t) * math.cos(lo), math.sin(t), math.cos(t) * math.sin(lo)] for t in np.linspace(-pi / 2, pi / 2, 25)])
    return Rm
def ll(lat, lon): la, lo = math.radians(lat), math.radians(lon); return np.array([math.cos(la) * math.cos(lo), math.sin(la), math.cos(la) * math.sin(lo)])
def facing(f, P, c): return np.dot(P - c, f.cam.p - P) > 0
def occluded(f, P, c, R):
    d = P - f.cam.p; L = np.linalg.norm(d); d /= L; oc = f.cam.p - c; b = np.dot(oc, d); cc = np.dot(oc, oc) - R * R; disc_ = b * b - cc
    if disc_ < 0: return False
    t0 = -b - math.sqrt(disc_); return 0 < t0 < L - 0.05

def exhaust(f, nozzle_at, t, rate=60, life=1.2, spread=2.0, down=(0, -1, 0), ground=None, scale=1.0, t0=0.0):
    pts, cols = [], []
    for j in range(int(max(0, t - t0) * rate) - int(life * rate), int(max(0, t - t0) * rate)):
        if j < 0: continue
        b = t0 + j / rate; age = t - b
        if age < 0 or age > life: continue
        h = (j * 2654435761) % 1000 / 1000.0; h2 = (j * 40503) % 997 / 997.0
        p = np.array(nozzle_at(b), float); v = np.array(down) * (14 * scale) + np.array([math.cos(h * 6.28), 0, math.sin(h * 6.28)]) * spread * h2 * scale
        q = p + v * age
        if ground is not None and q[1] < ground: q[1] = ground; r = (ground - (p[1] + v[1] * age)) * 0.8; q[0] += math.cos(h * 6.28) * r; q[2] += math.sin(h * 6.28) * r
        x = age / life; pts.append(q)
        cols.append((255, int(lerp(240, 90, x)), int(lerp(170, 30, x)), int(220 * (1 - x))))
    if pts: f.dots(pts, 0.35 * scale, cols)


# ---------------- film ----------------
class Film:
    """一部片子 = 若干段 (start, dur) + 每段一个场景函数 + 每段字幕 + 章节名。"""
    def __init__(s, starts, durs, scenes, subs, chapters=None, total=None, lead=0.4, tail_fade=1.2,
                 sub_size=36, chip=True):
        s.starts, s.durs, s.scenes, s.subs = list(starts), list(durs), list(scenes), subs
        s.chapters = chapters or [''] * len(scenes); s.total = total or (starts[-1] + durs[-1] + 1.5)
        s.lead, s.tail_fade, s.sub_size, s.chip = lead, tail_fade, sub_size, chip
    @property
    def nframes(s): return int(s.total * FPS)
    def all_text(s):
        """所有会上屏的字符串（字幕 + 章节）；场景内文字由 qc 在渲染时收集。"""
        out = [t for seg in s.subs for _, _, t in seg] + list(s.chapters); return out

TEXT_LOG = set()   # qc 用：记录渲染过程中出现的全部文字
BOX_LOG = []       # qc 用：当前帧所有可见文字的包围盒 (x0,y0,x1,y1,text)

def draw_overlay(img, f, film, k, lt, fade):
    d = ImageDraw.Draw(img, 'RGBA'); BOX_LOG.clear()
    def hit(bx):
        return any(min(bx[2], o[2]) - max(bx[0], o[0]) > 0 and min(bx[3], o[3]) - max(bx[1], o[1]) > 0 for o in BOX_LOG)
    # 1) 普通文字（标题/数字/说明）先画并登记
    for o in f.ov:
        if o[0] == 'lbl': continue
        x, y, t, sz, col, anc, bold, st, a = o; TEXT_LOG.add(t)
        if sz < 6: continue
        if a * fade > 0.5: bb_ = d.textbbox((x, y), t, font=font(sz, bold), anchor=anc); BOX_LOG.append((*bb_, t))
        d.text((x, y), t, font=font(sz, bold), fill=(*col, int(255 * a * fade)), anchor=anc, stroke_width=st, stroke_fill=(0, 0, 0, int(200 * a * fade)))
    # 2) 3D 标签：自动收进画面 + 与已有文字碰撞时向上/向下避让
    for o in f.ov:
        if o[0] != 'lbl': continue
        _, x, y, dx, dy, t, sz, col, a, dt = o; A = int(255 * a * fade); TEXT_LOG.add(t)
        fo = font(sz); tw = d.textlength(t, font=fo); tx = x + dx if dx >= 0 else x + dx - tw
        if dx == 0: tx = x - tw / 2
        tx = min(max(tx, 24), W - 24 - tw); ty = y + dy
        hgt = sz * 1.3 + 6
        for step in [0, -1, 1, -2, 2, -3, 3]:
            yy = min(max(y + dy + step * hgt, sz + 12), H - 100)
            box = (tx - 10, yy - sz * 0.75, tx + tw + 10, yy + sz * 0.55, t)
            if not hit(box): ty = yy; break
        else: ty = min(max(y + dy, sz + 12), H - 100)
        box = (tx - 10, ty - sz * 0.75, tx + tw + 10, ty + sz * 0.55, t)
        if A > 128: BOX_LOG.append(box)
        if dt:
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(*col, A)); d.line([x, y, tx if dx >= 0 else tx + tw, ty - sz * 0.2], fill=(*col, int(A * 0.7)), width=2)
        d.rounded_rectangle(box[:4], 8, fill=(8, 12, 22, int(A * 0.7)))
        d.text((tx, ty), t, font=fo, fill=(*col, A), anchor='ls')
    n = len(film.scenes)
    if film.chip:
        d.text((W - 40, 36), "%02d  %s" % (k + 1, film.chapters[k]), font=font(22), fill=(255, 255, 255, int(170 * fade)), anchor='rm')
        for i in range(n):
            cx = W - 40 - (n - 1 - i) * 34 - 20; c = (255, 200, 80, 230) if i == k else (160, 170, 190, 110)
            d.ellipse([cx - 4, 56, cx + 4, 64], fill=c)
    for a, b, t in film.subs[k]:
        if a <= lt < b + 0.15:
            d.text((W / 2, H - 52), t, font=font(film.sub_size), fill=(255, 255, 255, 255), anchor='mm', stroke_width=3, stroke_fill=(0, 0, 0, 230))

def render_frame(film, n):
    t = n / FPS; k = 0
    for i in range(len(film.starts)):
        if t >= film.starts[i] - film.lead: k = i
    lt = t - film.starts[k]
    f = film.scenes[k](max(lt, 0), film.durs[k])
    img = BG.copy(); d = ImageDraw.Draw(img, 'RGBA')
    if f.stars:
        P2, z = f.cam.proj(STARS)
        for i in np.nonzero(z > 1)[0]:
            b = int(STAR_B[i]); x, y = P2[i]
            if 0 <= x < W2 and 0 <= y < H2: d.rectangle([x, y, x + 2, y + 2], fill=(b, b, min(255, b + 20)))
    for L in f.L:
        L.sort(key=lambda it: -it[0])
        for it in L:
            if it[1] == 0: d.polygon(it[2], fill=it[3])
            elif it[1] == 1: d.line(it[2], fill=it[3], width=it[4] * SS // 2 + 1)
            else:
                x, y, r = it[2]; d.ellipse([x - r, y - r, x + r, y + r], fill=it[3])
    img = img.reduce(SS)
    endfade = 1 - ease((t - (film.total - film.tail_fade)) / 1.0)
    fade = clamp(f.dim) * endfade
    draw_overlay(img, f, film, k, lt, clamp(f.dim))
    if fade < 0.999 and (k != 0 or lt > 0): img = Image.blend(Image.new('RGB', (W, H)), img, fade)
    return img

def encode(film, a, b, out, ffmpeg='ffmpeg'):
    p = subprocess.Popen([ffmpeg, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for n in range(a, b): p.stdin.write(render_frame(film, n).tobytes())
    p.stdin.close(); p.wait()
