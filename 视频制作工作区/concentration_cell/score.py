# 浓差电池 · 分场景配乐 + 实验室音效（依赖 ~/scorelib.py）
import sys, os; sys.path.insert(0, os.path.expanduser('~')); from scorelib import *
T = 71.7; mus, sfx = buses(T)
SEG = [0.8, 9.6, 21.45, 33.27, 43.31, 57.43]
# 1 引入：好奇的钟琴动机 + 弦乐 + 玻璃轻碰 + 电压表
chord_strings(0.0, 4.8, Cmaj7, 0.55, 1.5, 0.8, 1.0); chord_strings(4.8, 9.6, Am7, 0.55, 0.8, 0.8, 1.0)
for i, m in enumerate([72, 76, 79, 83, 81, 79, 76, 74]): add(mus, 0.3 + i * 0.55, bell(m, 0.5), pan=(i % 3 - 1) * 0.4)
add(sfx, 1.0, clink(1.3), pan=-0.4); add(sfx, 1.6, clink(1.1), pan=0.4)
add(sfx, 6.8, beep(1760, 0.1)); add(sfx, 7.0, beep(2093, 0.14))
# 2 电极反应：神秘拨弦 ostinato + 溶解气泡 + 镀铜闪光
t = 9.6; i = 0
while t < 21.3:
    c = [Am, Am, F, Gm_][(i // 8) % 4]; add(mus, t, pluck(c[1 + i % 3] + (12 if i % 4 == 3 else 0), 0.7), pan=0.3 * math.sin(i)); t += 0.36; i += 1
chord_strings(9.6, 15.3, [45, 57, 64], 0.4, 0.8, 0.6, 0.8); chord_strings(15.3, 21.45, [41, 57, 60, 65], 0.45, 0.6, 0.6, 1.0)
add(sfx, 10.2, bubbles(5.0, 14, 1.0), pan=-0.4)
for j in range(10): add(sfx, 15.8 + j * 0.5, bell(88 + (j % 3) * 2, 0.25), pan=0.5)
# 3 电路与盐桥：96bpm 轻律动 + 电子"滋"声 + 离子掠过
b = 60 / 96; t = 21.45; i = 0
while t < 33.0:
    c = [C, Am, F, Gm_][(i // 8) % 4]
    if i % 2 == 0: add(mus, t, kick(0.45))
    add(mus, t + b / 4, hat(0.7), pan=0.3); add(mus, t, pluck(c[0] + 12, 0.7))
    if i % 8 == 0: chord_strings(t, t + 8 * b / 2, c[1:], 0.35, 0.3, 0.4, 1.0)
    t += b / 2; i += 1
for j in range(14): add(sfx, 22.3 + j * 0.55, zap(0.6), pan=-0.6 + (j % 5) * 0.3)
add(sfx, 26.8, whoosh(1.4, 300, 3000, 0.45), pan=-0.3); add(sfx, 28.4, whoosh(1.4, 300, 3000, 0.45), pan=0.3)
# 4 能斯特方程：思辨钢琴 + 弦乐 + 书写声
prog(33.27, 43.31, [Dm7, G6, Cmaj7, Am7], lambda a, b_, c: chord_strings(a, b_, c, 0.5, 0.8, 0.8, 0.9))
for j in range(16): add(mus, 33.4 + j * 0.62, piano([62, 65, 69, 72, 67, 71, 74, 71][j % 8], 0.5, 2.5), pan=-0.2)
for tt in (34.0, 36.6, 39.0, 41.2): add(sfx, tt, chalk(0.9, 1.0))
# 5 代入：上升 → 0.059 V 命中
add(mus, 43.31, riser(4.0, 0.6)); chord_strings(43.31, 47.8, [43, 55, 59, 62], 0.55, 1.0, 0.3, 1.0, trem=7)
add(mus, 47.8, timpani(36, 1.0)); add(mus, 47.8, kick(0.8)); chord_strings(47.8, 50.2, [36, 48, 55, 60, 64, 67], 0.9, 0.1, 1.0, 1.2)
for m in [72, 76, 79, 84]: add(mus, 47.8, bell(m, 0.5))
add(sfx, 47.9, beep(1760, 0.1)); add(sfx, 48.1, beep(2093, 0.14))
# 5b 真实溶液：转入思辨的小调钢琴 + 弦乐（理论值 → 实测值约一半）
prog(50.2, 57.6, [Am7, Dm7, Em7], lambda a, b_, c: chord_strings(a, b_, c, 0.5, 0.8, 0.8, 0.8))
for j in range(10): add(mus, 50.4 + j * 0.7, piano([69, 65, 64, 62, 64, 60, 62, 59, 60, 57][j], 0.45, 2.5), pan=-0.2)
for tt in (51.0, 53.6): add(sfx, tt, chalk(0.9, 1.0))
# 6 放电至平衡 → 结论
prog(57.43, 64.6, [Fmaj7, Em7, Dm7], lambda a, b_, c: chord_strings(a, b_, c, 0.55, 0.8, 0.8, 0.8))
for j in range(12): add(sfx, 57.9 + j * 0.55, tick(0.8 - j * 0.05, 2600 - j * 100))
for j in range(8): add(mus, 57.7 + j * 0.85, piano([69, 67, 65, 64, 62, 60, 59, 60][j], 0.5, 3))
add(mus, 65.6, timpani(36, 0.7)); chord_strings(65.6, 71.2, [36, 48, 55, 59, 64, 67], 0.85, 0.3, 1.6, 1.1)
for m in [60, 64, 67, 71, 76]: add(mus, 65.6, piano(m, 0.6, 3.5))
for m in [72, 76, 79]: add(mus, 66.4, bell(m, 0.45))
N = mus.shape[1]; v = load_voice(['narration/s%d.flac' % i for i in range(1, 7)], SEG, N)
finish(mus, sfx, v, 'mix.wav')
