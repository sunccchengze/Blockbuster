"""10 秒配乐：擒纵“嗒-嗒”（与画面每秒 4 拍严格同步）+ 大提琴断奏同速脉冲 + 弦乐渐强，
运镜甩动处 whoosh，8.6 s 拉远全景时定音鼓 + 大调和弦 + 钟琴收尾。"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import numpy as np
from bb.score import *
T = 10.4
mus, sfx = buses(T)
F = lambda fr: (fr - 1) / 25
# 擒纵声：每 0.25 s 一次，高低交替（tick / tock），全片贯穿；拉远后略退后
for k in range(int(T * 4)):
    t = k / 4; g = 0.55 if t < F(215) else 0.35
    add(sfx, t, tick(g, 3400 if k % 2 == 0 else 2600), pan=0.15 if k % 2 else -0.15)
    add(sfx, t + 0.004, clink(0.12 * g))
# 大提琴断奏：D 小调，与擒纵同速（8 分音符 = 0.25 s）
bass = [38, 38, 45, 38, 41, 38, 45, 43]
for k in range(int(F(215) * 4)):
    add(mus, k / 4, cello_stac(bass[k % 8] + (0 if k < 16 else 0), 0.2), g=0.35 + 0.25 * k / 34)
# 弦乐：Dm → Bb → Gm → A（渐强、渐亮）
for (t0, t1, ch) in [(0, 2.2, [50, 53, 57]), (2.2, 4.4, [46, 50, 53, 58]), (4.4, 6.4, [43, 50, 55, 58]), (6.4, F(215), [45, 49, 52, 57, 61])]:
    for m in ch: add(mus, t0, strings(m, t1 - t0 + 0.6, a=0.5, r=0.7, bright=0.6 + 0.08 * t0, trem=0.0 if t0 < 6 else 4.0), g=0.12 + 0.03 * t0)
# 运镜甩动：whoosh
for fr in (48, 92, 124, 152, 182):
    add(sfx, F(fr) - 0.35, whoosh(0.8, 300, 3200, 0.5), pan=0.4 if fr % 2 else -0.4)
# 摆轮/红宝石特写的钟琴点缀
for t, m in ((0.3, 86), (1.36, 89), (2.48, 93), (3.7, 91)):
    add(mus, t, bell(m, 0.25))
# 高潮：拉远全景
tr = F(215)
add(sfx, tr - 1.6, riser(1.6, 0.6))
add(mus, tr, timpani(38, 1.0)); add(sfx, tr, boom(0.8))
for m in (50, 54, 57, 62, 66, 69):
    add(mus, tr, strings(m, T - tr, a=0.15, r=1.0, bright=1.3), g=0.22)
for j, m in enumerate((74, 78, 81, 86, 90)):
    add(mus, tr + 0.15 + j * 0.12, bell(m, 0.35))
add(mus, tr + 0.05, piano(38, 0.7, 2.5)); add(mus, tr + 0.05, piano(50, 0.6, 2.5))
finish(mus, sfx, np.zeros(mus.shape[1], np.float32), os.path.join(HERE, 'mix.wav'), music_gain=1.0)
print('ok')
