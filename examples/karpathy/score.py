"""Karpathy 人物配乐：叙事型——钢琴 + 弦乐为主，履历段轻快，三个特质各有一个调性。"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import film as r3d
from bb.explain_score import *
Q = Cues(r3d); mus, sfx = Q.mus, Q.sfx
# 1 开场：温暖弦乐 → 名字出现钟琴 → 三个问号
k = 0; e = Q.E(k)
Q.pad(Q.G(k, 0), Q.end(k), [C, F], 0.5)
Q.sparkle(e[1], [72, 76, 79, 84], 0.45)
for j in range(3): add(mus, e[2] + 0.4 + j * 0.3, piano(67 + j * 2, 0.5, 2))
# 2 履历：轻快拨弦律动，每个里程碑一声钟琴
k = 1; e = Q.E(k)
Q.groove(Q.G(k, 0), Q.end(k), 108, [C, G_, Am, F], 0.35, 0.5, snare_v=0.12)
for i_, t in enumerate(e): add(mus, t + 0.1, bell(76 + [0, 2, 4, 5, 7, 9, 12][i_], 0.4))
add(mus, e[6] + 0.2, timpani(43, 0.6))
# 3 思想：钢琴分解 → vibe coding 俏皮拨弦 → 智能体工程 cello
k = 2; e = Q.E(k)
Q.piano_arp(Q.G(k, 0), e[3], 88, [Am, F, C, G_], 0.38)
for i_ in (1, 2): add(sfx, e[i_], whoosh(0.6, 400, 2500, 0.2))
for q in range(10): add(mus, e[3] + q * 0.22, pluck(72 + [0, 4, 7, 4, 9, 7, 4, 2, 0, 2][q], 0.4), pan=0.4 * math.sin(q))
add(sfx, e[4] + 0.1, beep(330, 0.2, 0.25))
Q.cello(e[4], Q.end(k), 116, [43, 36], 0.4); Q.pad(e[4], Q.end(k), [G_, C], 0.3)
# 4 作品：积木叠加 clink + 律动 → autoresearch 环形快速滴答 → 星星钟琴
k = 3; e = Q.E(k)
Q.groove(Q.G(k, 0), e[5], 112, [F, C, G_, Am], 0.4, 0.6, snare_v=0.18)
for i_ in range(1, 5):
    for q in range(5): add(sfx, e[i_] + q * 0.07, clink(0.25))
add(sfx, e[5], riser(0.7, 0.25))
Q.groove(e[5], Q.end(k), 128, [Dm, Bb, F, C], 0.45, 0.75, pl=False, snare_v=0.2)
for q in range(48): add(sfx, e[6] + q * 0.065, tick(0.22, 1800 + q * 30))
Q.sparkle(e[6] + 2.0, [84, 86, 88, 91, 93, 96], 0.35, 0.12)
# 5 特质一（青）：E 小调钢琴，搭积木 → 反向传播
k = 4; e = Q.E(k)
Q.piano_arp(Q.G(k, 0), Q.end(k), 90, [Em, C, G_, D], 0.38, 0.35)
for q in range(10): add(sfx, Q.G(k, 0.4) + q * 0.15, clink(0.25))
add(mus, e[4] + 0.1, timpani(40, 0.6)); Q.sparkle(e[4] + 0.2, [76, 79, 83], 0.4)
# 6 特质二（绿）：F 大调，弦乐展开 + 拨弦扩散
k = 5; e = Q.E(k)
Q.groove(Q.G(k, 0), Q.end(k), 100, [F, C, Dm, Bb], 0.3, 0.45, snare_v=0.1, strings_g=0.4)
add(mus, e[4] + 0.1, timpani(41, 0.6)); Q.sparkle(e[4] + 0.2, [77, 81, 84], 0.4)
# 7 特质三（紫）：D 大调上行进行 + 大提琴，台阶向上
k = 6; e = Q.E(k)
Q.cello(Q.G(k, 0), Q.end(k), 112, [38, 43, 45, 47], 0.42)
Q.pad(Q.G(k, 0), Q.end(k), [D, G_, A7, Em], 0.4)
for q in range(6): add(mus, Q.G(k, 1.0) + q * 2.0, bell(74 + q * 2, 0.35))
add(sfx, e[2] + 0.1, beep(330, 0.2, 0.25))
add(mus, e[4] + 0.1, timpani(38, 0.6))
# 8 总结 → 片尾
k = 7; e = Q.E(k)
Q.pad(Q.G(k, 0), e[5], [C, G_, Am, F], 0.5)
for i_ in (1, 2, 3): add(mus, e[i_] + 0.1, timpani(36 + 2 * i_, 0.6)); Q.sparkle(e[i_] + 0.2, [72 + 2 * i_, 76 + 2 * i_], 0.35)
Q.ending(e[4], [F, G_, C])
Q.finish(HERE)
