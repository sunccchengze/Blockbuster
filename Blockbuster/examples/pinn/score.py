# PINN · 分场景配乐 + 科技音效
import sys, os; sys.path.insert(0, os.path.expanduser('~')); from scorelib import *
T = 60.4; mus, sfx = buses(T)
SEG = [0.8, 12.48, 20.42, 32.13, 42.60, 48.01]
# 1 引入：标题钟琴重音 + 电子琶音 + 10 个数据点"哔"
add(mus, 0.2, bell(72, 0.8)); add(mus, 0.2, bell(79, 0.6)); add(mus, 0.2, timpani(36, 0.6))
chord_strings(0.2, 6.2, [45, 57, 60, 64], 0.45, 1.2, 0.6, 1.0); chord_strings(6.2, 12.48, [41, 57, 60, 65], 0.45, 0.8, 0.6, 1.0)
t = 1.0; i = 0
while t < 12.3:
    c = [Am, Am, F, F][(i // 8) % 4]; add(mus, t, pluck(c[1 + i % 3] + 12 + (12 if i % 8 >= 4 else 0), 0.5), pan=0.4 * math.sin(i)); t += 0.24; i += 1
for j in range(10): add(sfx, 9.3 + j * 0.25, blip(1047 + j * 110, 1.2))
# 2 普通神经网络：训练滴答 → 预测失控（故障音 + 不协和颤音 + 闷响）
for j in range(50): add(sfx, 12.8 + j * 0.08, tick(0.4, 3000))
chord_strings(12.48, 16.6, [45, 57, 64], 0.45, 0.6, 0.4, 0.9)
chord_strings(16.6, 20.42, [40, 46, 52, 53, 58], 0.6, 0.3, 0.6, 1.0, trem=9)
add(sfx, 16.8, glitch(2.2, 1.0)); add(sfx, 16.8, boom(0.5))
# 3 PINN 结构 / 自动微分：逐层节点钟琴 + 108bpm 律动
b = 60 / 108; t = 20.42; i = 0
while t < 31.9:
    c = [C, Am, F, Gm_][(i // 8) % 4]
    add(mus, t, kick(0.4)) if i % 4 == 0 else (add(mus, t, hat(0.8)) if i % 2 == 0 else None)
    add(mus, t, pluck(c[0] + 12, 0.6)); t += b / 2; i += 1
prog(20.42, 32.13, [C, Am, F, Gm_], lambda a, b_, c: chord_strings(a, b_, c[1:], 0.4, 0.6, 0.6, 1.0))
for j in range(8): add(mus, 21.0 + j * 1.3, bell([72, 76, 79, 83, 84, 79, 81, 86][j], 0.4), pan=(j % 3 - 1) * 0.5)
for tt in (24.5, 27.0, 29.3): add(sfx, tt, zap(0.7))
# 4 损失函数 + 训练：驱动节拍 + 上升 + 训练滴答
b = 0.5; t = 32.13; i = 0
while t < 42.5:
    add(mus, t, kick(0.55)) if i % 2 == 0 else add(mus, t, hat(1.0))
    if i % 4 == 2: add(mus, t, snare(0.3))
    add(mus, t, pluck([57, 60, 64, 69][i % 4] + 12, 0.45)); t += b / 2; i += 1
prog(32.13, 42.6, [Am, F, C, [43, 55, 59, 62]], lambda a, b_, c: chord_strings(a, b_, c, 0.45, 0.6, 0.6, 1.1))
for j in range(80): add(sfx, 34.0 + j * 0.105, tick(0.3, 2600 + (j % 4) * 300))
add(mus, 39.6, riser(3.0, 0.6))
# 5 结果：胜利大和弦
add(mus, 42.6, timpani(36, 1.1)); add(mus, 42.6, kick(0.9))
chord_strings(42.6, 48.0, [36, 48, 55, 60, 64, 67], 0.9, 0.1, 0.8, 1.3)
for m in [60, 64, 67, 72, 76]: add(mus, 42.6, piano(m, 0.7, 4))
# 6 反问题：神秘 → 参数被反推出来 → 终和弦
prog(48.01, 57.8, [Dm7, Bb, G6, A7], lambda a, b_, c: chord_strings(a, b_, c, 0.5, 0.8, 0.8, 1.0))
t = 48.3; i = 0
while t < 57.6: add(mus, t, pluck([62, 65, 69, 74][i % 4] + 12, 0.45), pan=0.4 * math.sin(i)); t += 0.3; i += 1
for j in range(60): add(sfx, 49.0 + j * 0.14, tick(0.3, 3200))
add(mus, 57.8, timpani(38, 0.9)); chord_strings(57.8, 60.0, [38, 50, 57, 62, 66, 69], 0.9, 0.1, 1.0, 1.2)
for m in [62, 66, 69, 74]: add(mus, 57.8, bell(m + 12, 0.5))
N = mus.shape[1]; v = load_voice(['narration/s%d.wav' % i for i in range(1, 7)], SEG, N)
finish(mus, sfx, v, 'mix.wav')
