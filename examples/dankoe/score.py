"""Dan Koe 人物配乐：钢琴 + 弦乐叙事；起点段拨弦律动，写作系统段打字般的滴答，价值阶梯上行，AI 段转为大提琴与 pad。"""
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
# 1 开场：温暖弦乐 + 卡片钢琴音 → 光点钟琴
k = 0; e = Q.E(k)
Q.pad(Q.G(k, 0), Q.end(k), [C, Am, F, G_], 0.5)
for j, t in enumerate((0.5, 1.9, e[1])): add(mus, t, piano(67 + j * 2, 0.5, 2))
Q.sparkle(e[2], [72, 76, 79, 84, 88], 0.4, 0.15)
add(mus, e[3], timpani(36, 0.5)); Q.sparkle(e[3] + 0.1, [79, 84], 0.45)
# 2 起点：小调拨弦律动，每次尝试一声低音钢琴 → 自由职业转大调 → 天花板定音鼓
k = 1; e = Q.E(k)
Q.groove(Q.G(k, 0), e[2], 100, [Am, F, C, G_], 0.32, 0.45, snare_v=0.1)
for j in range(4): add(mus, e[1] + j * 1.1 + 1.0, piano(45 - j, 0.35, 1.5))
Q.piano_arp(e[2], Q.end(k), 96, [C, G_, Am, F], 0.36)
for q in range(14): add(sfx, e[3] + q / 2.2, tick(0.12, 2200))
add(mus, e[4] + 0.5, timpani(38, 0.6)); add(sfx, e[4] + 1.6, beep(300, 0.25, 0.2))
# 3 核心观点：弦乐展开 → 反愿景小调 cello → 兴趣汇合钟琴
k = 2; e = Q.E(k)
Q.groove(Q.G(k, 0), e[2], 104, [F, C, Dm, Bb], 0.3, 0.45, snare_v=0.08, strings_g=0.4)
add(sfx, Q.G(k, 0.5), riser(0.9, 0.2))
Q.cello(e[2], e[4], 100, [40, 45, 36, 43], 0.4); Q.pad(e[2], e[4], [Em, Am, C, D], 0.35)
Q.sparkle(e[3], [76, 79, 83], 0.35)
Q.piano_arp(e[4], Q.end(k), 92, [G_, D, Em, C], 0.36)
for j in range(5): add(mus, e[4] + j * 0.25, bell(76 + [0, 2, 4, 7, 9][j], 0.3))
# 4 写作系统：律动 + 键盘滴答 → 分发段更饱满 → 一亿浏览上行钟琴
k = 3; e = Q.E(k)
Q.groove(Q.G(k, 0), e[4], 112, [C, G_, Am, F], 0.38, 0.55, snare_v=0.15)
for q in range(40): add(sfx, e[2] + q * 0.11, tick(0.14, 1800 + (q % 5) * 200))
for j in range(3): add(sfx, e[3] + j * 0.6, whoosh(0.5, 500, 2600, 0.15))
add(sfx, e[4], riser(0.7, 0.22))
Q.groove(e[4], Q.end(k), 120, [F, G_, Em, Am], 0.42, 0.7, snare_v=0.18, strings_g=0.45)
Q.sparkle(e[6] + 0.3, [84, 86, 88, 91, 96], 0.35, 0.12)
# 5 价值阶梯：每级一声上行钢琴 → Kortex 碎裂（低音 + 碎声）→ Eden 重组温暖 pad
k = 4; e = Q.E(k)
Q.pad(Q.G(k, 0), e[5], [D, G_, A7, D], 0.4); Q.cello(Q.G(k, 0), e[5], 100, [38, 43, 45, 38], 0.35)
for j, t in enumerate((e[1], e[2], e[2] + 0.8, e[4])): add(mus, t + 0.1, piano(62 + j * 3, 0.5, 2)); add(sfx, t + 0.1, clink(0.2))
add(mus, e[6] + 0.8, timpani(33, 0.7))
for q in range(10): add(sfx, e[6] + 0.85 + q * 0.06, clink(0.18))
Q.piano_arp(e[6] + 2.6, Q.end(k), 90, [F, C, Dm, Bb], 0.36)
Q.sparkle(e[6] + 4.6, [77, 81, 84], 0.35)
for j in range(3): add(sfx, e[7] + j * 0.35, beep(660 + 110 * j, 0.12, 0.15))
# 6 AI：神秘 pad + 拨弦 → 70 亿光点钟琴 → 复制人群的小调 → 护城河弦乐升起
k = 5; e = Q.E(k)
Q.pad(Q.G(k, 0), e[3], [Am, F, C, G_], 0.4)
for q in range(12): add(mus, e[2] + q * 0.3, pluck(72 + [0, 3, 7, 10][q % 4], 0.35), pan=0.4 * math.sin(q))
Q.sparkle(e[3], [84, 88, 91, 96, 100], 0.35, 0.15)
Q.cello(e[4], e[7], 104, [45, 41, 43, 40], 0.4); Q.pad(e[4], e[7], [Am, F, G_, Em], 0.35)
add(sfx, e[7] - 0.8, riser(0.9, 0.22)); add(mus, e[7], timpani(36, 0.7))
Q.groove(e[7], Q.end(k), 96, [C, G_], 0.35, 0.4, pl=False, snare_v=0.0, strings_g=0.55)
# 7 三点借鉴 → 片尾
k = 6; e = Q.E(k)
Q.pad(Q.G(k, 0), e[4], [C, G_, Am, F], 0.5)
for i_ in (1, 2, 3): add(mus, e[i_] + 0.1, timpani(36 + 2 * i_, 0.6)); Q.sparkle(e[i_] + 0.2, [72 + 2 * i_, 76 + 2 * i_], 0.35)
Q.ending(e[4], [F, G_, C])
Q.finish(HERE)
