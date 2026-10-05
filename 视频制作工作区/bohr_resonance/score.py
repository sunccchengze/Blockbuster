# 波尔共振 · 分场景配乐 + 与摆轮周期同步的音效
import sys, os; sys.path.insert(0, os.path.expanduser('~')); from scorelib import *
T = 60.4; mus, sfx = buses(T)
SEG = [0.8, 9.8, 21.78, 31.83, 41.78, 50.49]; T0 = 1.6
# 1 仪器结构：机械钟表滴答 + 低音弦乐悬念 + 扭转"吱"声
chord_strings(0.0, 9.8, [38, 50, 57, 62], 0.45, 1.5, 0.6, 0.8)
for j in range(16): add(sfx, 0.6 + j * 0.5, tick(0.6, 2000 if j % 2 else 2600))
for j, m in enumerate([62, 65, 69, 67, 65, 64]): add(mus, 1.0 + j * 1.2, bell(m + 12, 0.35))
add(sfx, 8.4, creak(1.3, 1.2))
# 2 阻尼振动：释放"咚"，每半周期一声摆动掠过，振幅衰减；钢琴按周期落音
def swings(t0, t1, decay, v0=0.7):
    k = 0
    while t0 + k * T0 / 2 < t1:
        a = v0 * math.exp(-decay * k * T0 / 2)
        if a < 0.05: break
        add(sfx, t0 + k * T0 / 2, whoosh(T0 / 2, 250, 250 + 2500 * a, a), pan=0.5 if k % 2 else -0.5); k += 1
add(sfx, 9.8, thud(0.9)); swings(9.8, 15.8, 0.25)
add(sfx, 15.8, creak(0.8, 0.8)); add(sfx, 16.6, thud(0.9)); swings(16.6, 21.4, 1.1)
k = 0
while 9.8 + k * T0 < 21.4:
    add(mus, 9.8 + k * T0, piano([57, 60, 64, 62, 65, 64, 60][k % 7], 0.55, 2.5)); k += 1
chord_strings(9.8, 15.8, Am7, 0.45, 0.8, 0.8, 0.9); chord_strings(15.8, 21.78, Dm7, 0.45, 0.8, 0.8, 0.9)
# 3 受迫振动：电机启动 + 以驱动周期(2.0s)为拍的律动
add(sfx, 21.8, tick(1.5, 1500)); add(sfx, 21.85, rumble(0.8, 0.1, 0.6, 400), g=0.25)
Td = T0 / 0.8; k = 0
while 21.8 + k * Td / 4 < 31.8:
    t = 21.8 + k * Td / 4; c = [Am, F, C, Gm_][(k // 8) % 4]
    add(mus, t, kick(0.4)) if k % 4 == 0 else (add(mus, t, hat(0.7)) if k % 2 == 0 else None)
    add(mus, t, pluck(c[1 + k % 3] + 12, 0.55)); k += 1
chord_strings(21.8, 31.8, [45, 57, 64, 69], 0.4, 1.0, 0.6, 1.0)
swings(23.5, 31.6, 0.0, 0.35)
# 4 共振：振幅增大 → 张力弦乐 crescendo + 每周期定音鼓 + 闪光灯快门
k = 0
while 31.83 + k * T0 < 41.5:
    t = 31.83 + k * T0; g = min(1, 0.3 + k * 0.12)
    add(mus, t, timpani(38, g)); add(sfx, t, whoosh(T0 / 2, 250, 800 + 2500 * g, 0.4 + 0.5 * g), pan=-0.5)
    add(sfx, t + T0 / 2, whoosh(T0 / 2, 250, 800 + 2500 * g, 0.4 + 0.5 * g), pan=0.5); k += 1
chord_strings(31.83, 35.8, [38, 50, 57, 62], 0.5, 1.5, 0.3, 0.9, trem=6)
chord_strings(35.8, 41.78, [38, 50, 54, 57, 62, 66], 0.9, 0.5, 1.0, 1.3, trem=4)
add(mus, 32.0, riser(3.8, 0.6))
t = 35.8
while t < 41.3: add(sfx, t, shutter(1.2)); t += T0
# 5 运动方程：安静的思辨钢琴
prog(41.78, 50.49, [Dm7, G6, Cmaj7, Am7], lambda a, b_, c: chord_strings(a, b_, c, 0.45, 0.8, 0.8, 0.9))
for j in range(13): add(mus, 42.0 + j * 0.64, piano([62, 65, 69, 72, 71, 67, 64][j % 7], 0.45, 2.5))
for tt in (42.6, 45.0, 47.6): add(sfx, tt, chalk(0.8))
# 6 幅频相频曲线：弦乐解决 + 画线闪光 + 终和弦
prog(50.49, 57.3, [F, C, [43, 55, 59, 62]], lambda a, b_, c: chord_strings(a, b_, c, 0.6, 0.8, 0.8, 1.1))
for j in range(3): add(mus, 50.8 + j * 1.8, whoosh(1.6, 400, 3500, 0.3))
for j in range(9): add(mus, 50.7 + j * 0.7, bell([72, 76, 79, 84, 79, 76, 81, 84, 88][j], 0.35), pan=(j % 3 - 1) * 0.4)
add(mus, 57.3, timpani(36, 0.9)); chord_strings(57.3, 59.8, [36, 48, 55, 60, 64, 67], 0.9, 0.2, 1.0, 1.2)
for m in [60, 64, 67, 72]: add(mus, 57.3, piano(m, 0.6, 3))
N = mus.shape[1]; v = load_voice(['narration/s%d.wav' % i for i in range(1, 7)], SEG, N)
finish(mus, sfx, v, 'mix.wav')
