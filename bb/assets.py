"""bb.assets — 可复用的低多边形模型（火箭、汽车等）。按需扩充。"""
from .render3d import *
STEEL = (190, 198, 210)
def starship():
    V, F = lathe([(0,0),(1,0),(1,9),(1.0,9.05),(1,17),(0.95,17.8),(0.8,18.6),(0.5,19.2),(0,19.6)], 20)
    ms = [part(V, F, STEEL)]
    for a in (0, pi / 2, pi, 1.5 * pi):
        R = roty(a); ms.append(box(0.12, 2.2, 1.0, (150,155,165), R=R, T=R @ [0, 16.4, 1.4]))
        ms.append(box(0.12, 1.6, 1.0, (150,155,165), R=R, T=R @ [0, 1.2, 1.3]))
    ms.append(box(2.02, 0.35, 2.02, (60,62,70), T=(0, 9.0, 0)))
    return merge(ms)
def falcon(h=14, r=0.36, white=(235,238,242)):
    V, F = lathe([(0,0),(r,0),(r,h * 0.7),(r * 1.001,h * 0.7),(r,h),(r * 0.7,h * 1.05),(0,h * 1.09)], 14)
    ms = [part(V, F, white), box(2 * r + 0.02, h * 0.06, 2 * r + 0.02, (30,30,34), T=(0, h * 0.72, 0))]
    return merge(ms)
def legs(r=0.36, spread=1.0):
    ms = []
    for a in (pi / 4, 3 * pi / 4, 5 * pi / 4, 7 * pi / 4):
        R = roty(a) @ rotx(0.5 * spread); ms.append(box(0.1, 2.2, 0.1, (40,40,45), R=R, T=roty(a) @ [0, 0.8, r + 0.45 * spread]))
    return merge(ms)
def car(col, cab=(20,26,36)):
    ms = [box(4.4, 0.7, 1.9, col, T=(0, 0.65, 0)), box(2.4, 0.6, 1.6, cab, T=(-0.2, 1.3, 0), top=0.75),
          box(0.9, 0.35, 1.7, col, T=(1.8, 0.95, 0), top=0.8)]
    V, F = lathe([(0,-0.2),(0.4,-0.2),(0.4,0.2),(0,0.2)], 12)
    for x in (-1.45, 1.45):
        for z in (-0.95, 0.95): ms.append(part(V, F, (25,25,28), R=rotx(pi / 2), T=(x, 0.4, z)))
    return merge(ms)
