# 大数定律 · 分场景配乐 + 同步音效
import sys, os; sys.path.insert(0, os.path.expanduser('~')); from scorelib import *
T = 60.4; mus, sfx = buses(T)
SEG = [0.8, 10.47, 18.97, 33.20, 42.99, 48.10]
FIRST10 = [1, 0, 1, 1, 0, 1, 1, 1, 0, 1]
# 1 抛硬币：俏皮拨弦 + 每次抛掷 "嗖—叮"
t = 0.4; i = 0
while t < 9.9:
    c = [C, Am, F, Gm_][(i // 8) % 4]; add(mus, t, pluck(c[1 + i % 3] + 12, 0.55), pan=0.3 * ((i % 2) * 2 - 1))
    if i % 4 == 0: add(mus, t, pluck(c[0], 0.8))
    t += 0.41; i += 1
chord_strings(0.0, 10.4, [48, 60, 64, 67], 0.3, 1.0, 0.6, 1.0)
for k in range(10):
    t0 = 1.4 + k * 0.82; add(sfx, t0, whoosh(0.4, 800, 5000, 0.35), pan=-0.3 + k * 0.06)
    add(sfx, t0 + 0.75, clink(1.2)); add(mus, t0 + 0.75, bell(79 if FIRST10[k] else 72, 0.3), pan=-0.6 + k * 0.13)
add(mus, 8.9, strings(70, 1.4, 0.2, 0.5), g=0.5)  # 疑问尾音
# 2 频率稳定：琶音由慢到快（n 增大），最后收在稳定和弦
t = 10.47; i = 0
while t < 17.6:
    p = (t - 10.47) / 7.1; step = 0.45 * (1 - p) + 0.09; c = [Am, F, C, Gm_][min(3, int(p * 4))]
    add(mus, t, pluck(c[1 + i % 3] + 12 + (12 if i % 6 >= 3 else 0), 0.45 + 0.3 * p), pan=0.5 * math.sin(i * 0.7)); t += step; i += 1
chord_strings(10.47, 14.5, [45, 57, 64], 0.4, 0.8, 0.5, 0.8, trem=6); chord_strings(14.5, 19.0, [48, 55, 60, 64, 67], 0.55, 1.2, 0.8, 1.1)
# 3 大数定律：定音鼓宣告 + 宏大弦乐渐强 + 扫描线
add(mus, 19.0, timpani(36, 1.1)); add(mus, 19.0, kick(0.8))
prog(19.0, 33.2, [C, Am, F, [43, 55, 59, 62, 67]], lambda a, b_, c: chord_strings(a, b_, [c[0] - 12] + c, 0.55 + 0.1 * (a - 19) / 14, 0.8, 0.8, 1.1))
t = 19.0; i = 0
while t < 33.0:
    if i % 4 == 0: add(mus, t, timpani(36 + (7 if i % 8 == 4 else 0), 0.35))
    add(mus, t, cello_stac(36 + [0, 12, 7, 12][i % 4], 0.2), g=0.5); t += 0.45; i += 1
add(sfx, 27.8, whoosh(3.5, 200, 2200, 0.4))
for j in range(20): add(sfx, 28.2 + j * 0.2, tick(0.6))
# 4 切比雪夫：思辨钢琴 + 400 次实验的快速滴答
prog(33.2, 42.99, [Dm7, G6, Em7, Am7], lambda a, b_, c: chord_strings(a, b_, c, 0.45, 0.8, 0.8, 0.9))
for j in range(15): add(mus, 33.4 + j * 0.64, piano([62, 65, 69, 67, 71, 74, 72, 76][j % 8], 0.5, 2.5))
for j in range(60): add(sfx, 36.5 + j * 0.07, tick(0.35, rng.choice([2400, 3000, 3600])), pan=rng.uniform(-.6, .6))
# 5 骰子：明快鼓组 + 骰子翻滚
b = 0.31; t = 42.99; i = 0
while t < 47.9:
    add(mus, t, kick(0.55)) if i % 2 == 0 else add(mus, t, hat(1.0)); 
    if i % 4 == 2: add(mus, t, snare(0.3))
    add(mus, t, pluck([60, 64, 67, 72][i % 4] + 12, 0.45)); t += b; i += 1
chord_strings(42.99, 48.1, [48, 60, 64, 67], 0.5, 0.3, 0.5, 1.2)
for d in range(2):
    for k in range(8): add(sfx, 43.0 + d * 0.3 + k * 0.62, rattle(0.45, 0.8), pan=-0.4 + d * 0.8)
# 6 稀释 + 蒙特卡洛：闪烁撒点 + 终章
prog(48.1, 57.4, [F, C, [43, 55, 59, 62], Am], lambda a, b_, c: chord_strings(a, b_, c, 0.5, 0.8, 0.8, 1.0))
for j in range(10): add(mus, 48.3 + j * 0.9, piano([65, 69, 72, 67, 71, 74, 72, 76, 79, 84][j], 0.45, 2.5))
for j in range(70): add(sfx, rng.uniform(52.0, 57.0), ping(rng.choice([2093, 2349, 2637, 3136, 3520]), 0.35), pan=rng.uniform(-.8, .8))
add(mus, 57.4, timpani(36, 0.9)); chord_strings(57.4, 59.8, [36, 48, 55, 60, 64, 67, 72], 0.9, 0.2, 1.0, 1.2)
for m in [60, 64, 67, 72, 76]: add(mus, 57.4, piano(m, 0.6, 3))
N = mus.shape[1]; v = load_voice(['narration/s%d.wav' % i for i in range(1, 7)], SEG, N)
finish(mus, sfx, v, 'mix.wav')
