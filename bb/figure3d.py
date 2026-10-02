"""人物与道具模型（Dan Koe / Karpathy 共用）：带关节的风格化人物、合并网格的小人群、时间轴图标。
所有部件都按“外贴、不互插”的原则摆放；必须重叠处（头发/头）只做外壳。"""
import math
import numpy as np
from bb.explain import *

SKIN = (236, 200, 170); HAIR = (60, 44, 34); SHIRT = (52, 58, 72); PANTS = (70, 90, 130); SHOE = (30, 30, 34)


def figure(f, P, yaw=0.0, s=1.0, walk=None, la=0.15, ra=0.15, lo=0.08, ro=0.08, le=0.2, re=0.2,
           shirt=SHIRT, pants=PANTS, glow=0.12, alpha=255, glasses=True, nod=0.0):
    """风格化人物。la/ra 肩前摆角，lo/ro 外展角，le/re 肘弯角；walk = 步态相位（弧度）。"""
    P = np.array(P, float); Y = roty(yaw)
    def W(v): return P + Y @ (np.array(v, float) * s)
    sw = 0.5 * math.sin(walk) if walk is not None else 0.0
    bob = 0.03 * abs(math.cos(walk)) if walk is not None else 0.0
    hip = np.array([0, 0.92 + bob, 0])
    for side, a in ((-1, sw), (1, -sw)):
        Rl = rotx(a)
        top = hip + [side * 0.12, 0, 0]
        cube(f, W(top + Rl @ np.array([0, -0.43, 0])), (0.17 * s, 0.86 * s, 0.2 * s), pants, glow, alpha, R=Y @ Rl)
        cube(f, W(top + Rl @ np.array([0, -0.89, 0.06])), (0.18 * s, 0.08 * s, 0.32 * s), SHOE, glow, alpha, R=Y @ Rl)
    cube(f, W(hip + [0, 0.36, 0]), (0.5 * s, 0.68 * s, 0.27 * s), shirt, glow, alpha, R=Y)
    cube(f, W(hip + [0, 0.74, 0]), (0.1 * s, 0.08 * s, 0.1 * s), SKIN, glow, alpha, R=Y)
    H = hip + [0, 0.92, 0]; Rn = rotx(nod)
    f.mesh(M_BALL, R=Y @ Rn @ np.diag([0.16, 0.19, 0.17]) * s, T=W(H), col=SKIN, emis=glow, alpha=int(alpha))
    f.mesh(M_BALL, R=Y @ Rn @ np.diag([0.17, 0.1, 0.18]) * s, T=W(H + Rn @ np.array([0, 0.11, -0.02])), col=HAIR, emis=glow, alpha=int(alpha))
    if glasses:
        for gx in (-0.065, 0.065):
            cube(f, W(H + Rn @ np.array([gx, 0.02, 0.175])), (0.09 * s, 0.055 * s, 0.012 * s), (25, 25, 30), 0.1, alpha, R=Y @ Rn)
        cube(f, W(H + Rn @ np.array([0, 0.03, 0.178])), (0.05 * s, 0.012 * s, 0.01 * s), (25, 25, 30), 0.1, alpha, R=Y @ Rn)
    for side, fa, out, el in ((-1, la + (-sw * 0.8 if walk is not None else 0), lo, le), (1, ra + (sw * 0.8 if walk is not None else 0), ro, re)):
        sh = hip + [side * 0.31, 0.64, 0]
        Ru = rotz(side * out) @ rotx(-fa)
        cube(f, W(sh + Ru @ np.array([0, -0.17, 0])), (0.12 * s, 0.36 * s, 0.13 * s), shirt, glow, alpha, R=Y @ Ru)
        el_p = sh + Ru @ np.array([0, -0.34, 0])
        Rf = Ru @ rotx(-el)
        cube(f, W(el_p + Rf @ np.array([0, -0.15, 0])), (0.1 * s, 0.32 * s, 0.11 * s), SKIN, glow, alpha, R=Y @ Rf)
    return W(H)


def _mini(col):
    parts = [box(0.34, 0.5, 0.2, col, T=(0, 0.83, 0)), box(0.12, 0.58, 0.14, (70, 80, 100), T=(-0.09, 0.29, 0)),
             box(0.12, 0.58, 0.14, (70, 80, 100), T=(0.09, 0.29, 0))]
    hv = sphere(0.13, SKIN, 10, 6); hv.V = hv.V + np.array([0, 1.24, 0]); parts.append(hv)
    return merge(parts)
_MINI = {}
def mini(f, P, col, s=0.6, emis=0.15, yaw=0.0):
    k = tuple(col)
    if k not in _MINI: _MINI[k] = _mini(col)
    f.mesh(_MINI[k], R=roty(yaw), T=P, sc=s, emis=emis)


# ---------------- 时间轴图标 ----------------
def icon_book(f, P, s, col):
    P = np.array(P, float)
    cube(f, P, (0.9 * s, 0.14 * s, 0.65 * s), col, 0.3)
    cube(f, P + [0, 0.15 * s, 0], (0.82 * s, 0.14 * s, 0.6 * s), (230, 225, 210), 0.3)
    cube(f, P + [0, 0.3 * s, 0], (0.9 * s, 0.14 * s, 0.65 * s), (200, 60, 60), 0.3)


def icon_cap(f, P, s, lt):
    P = np.array(P, float); R = roty(0.4 + 0.2 * math.sin(lt))
    cube(f, P, (0.5 * s, 0.22 * s, 0.5 * s), (40, 40, 48), 0.25, R=R)
    cube(f, P + [0, 0.15 * s, 0], (0.95 * s, 0.05 * s, 0.95 * s), (30, 30, 38), 0.25, R=R @ roty(pi / 4))
    cube(f, P + R @ np.array([0.4, 0.0, 0.0]) * s, (0.03 * s, 0.3 * s, 0.03 * s), GOLD, 0.7, R=R)


def icon_screen(f, P, s, lt, col=CYAN):
    P = np.array(P, float)
    cube(f, P, (1.3 * s, 0.85 * s, 0.06 * s), (20, 24, 34), 0.3)
    for i in range(4):
        for j in range(3):
            on = (i + j + int(lt * 2)) % 3 == 0
            cube(f, P + [(-0.45 + i * 0.3) * s, (-0.25 + j * 0.25) * s, 0.04 * s], (0.22 * s, 0.18 * s, 0.01), col if on else (40, 70, 90), 0.8 if on else 0.3)
    cube(f, P + [0, -0.55 * s, 0], (0.08 * s, 0.3 * s, 0.08 * s), (80, 86, 100), 0.2)


def icon_ring(f, P, s, lt, col):
    P = np.array(P, float)
    for q in range(3):
        f.mesh(M_RING, R=roty(lt * 0.5 + q * pi / 3) @ rotx(pi / 2), T=P, sc=0.45 * s, col=col, emis=0.7)
    ball(f, P, 0.12 * s, col, 0.9)


def icon_car(f, P, s, lt):
    P = np.array(P, float)
    cube(f, P + [0, 0.22 * s, 0], (1.5 * s, 0.3 * s, 0.7 * s), (225, 60, 60), 0.3)
    cube(f, P + [-0.05 * s, 0.47 * s, 0], (0.8 * s, 0.22 * s, 0.62 * s), (40, 46, 60), 0.3)
    for wx in (-0.5, 0.5):
        for wz in (-0.36, 0.36):
            f.mesh(M_BALL, R=np.diag([0.17, 0.17, 0.05]) * s, T=P + [wx * s, 0.1 * s, wz * s * 1.02], col=(25, 25, 28), emis=0.2)
    cam = P + [0.35 * s, 0.6 * s, 0]
    for q in range(3):
        a = -0.35 + q * 0.35
        f.line([cam, cam + np.array([2.4 * math.cos(a), -0.15, 2.4 * math.sin(a)]) * s], (*CYAN, 120), 2)
    ph = (lt * 0.8) % 1
    f.dots([cam + np.array([2.4 * ph, -0.15 * ph, 0]) * s], 0.05, (*CYAN, 230))


def icon_bulb(f, P, s, lt):
    P = np.array(P, float)
    ball(f, P + [0, 0.25 * s, 0], 0.32 * s, GOLD, 0.8 + 0.15 * math.sin(lt * 3))
    cube(f, P + [0, -0.12 * s, 0], (0.2 * s, 0.2 * s, 0.2 * s), (150, 150, 160), 0.3)
    for q in range(8):
        a = q / 8 * 2 * pi; d = 0.5 + 0.06 * math.sin(lt * 3 + q)
        f.line([P + [0.38 * s * math.cos(a), 0.25 * s + 0.38 * s * math.sin(a), 0], P + [d * s * math.cos(a), 0.25 * s + d * s * math.sin(a), 0]], (*GOLD, 180), 2)


def icon_star(f, P, s, lt, col=(220, 140, 100)):
    P = np.array(P, float)
    for q in range(6):
        cube(f, P, (0.08 * s, 0.9 * s, 0.08 * s), col, 0.6, R=rotz(q * pi / 6 + lt * 0.3))
    ball(f, P, 0.1 * s, col, 0.9)


def gpu(f, P, s=1.0, lt=0.0):
    P = np.array(P, float)
    cube(f, P, (2.4 * s, 0.25 * s, 1.1 * s), (40, 44, 56), 0.25)
    cube(f, P + [0, -0.17 * s, 0], (2.3 * s, 0.08 * s, 1.0 * s), (30, 110, 70), 0.3)
    for fx in (-0.6, 0.6):
        f.mesh(M_BALL, R=np.diag([0.38, 0.02, 0.38]) * s, T=P + [fx * s, 0.135 * s, 0], col=(20, 20, 24), emis=0.2)
        for q in range(3):
            cube(f, P + [fx * s, 0.15 * s, 0], (0.6 * s, 0.01, 0.06 * s), (90, 96, 110), 0.3, R=roty(lt * 6 + q * pi / 3))
    cube(f, P + [-1.25 * s, 0, 0], (0.06 * s, 0.4 * s, 1.1 * s), (160, 166, 180), 0.3)
