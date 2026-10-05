"""具身智能播报配乐：每段注释即提示表。"""
import os, sys, math
pi = math.pi
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import film as r3d
from bb.score import *
T = r3d.TOTAL; mus, sfx = buses(T); S = r3d.SEG
def G(k, lt): return S[k] + lt
def E(k): return [G(k, r3d.ev(k, i)) for i in range(len(r3d.SUBS[k]))]
def END(k): return S[k] + r3d.dur[k]
C = [48, 55, 60, 64]; Am = [45, 57, 60, 64]; F = [41, 57, 60, 65]; G_ = [43, 55, 59, 62]; Dm = [38, 53, 57, 62]
Bb = [46, 53, 58, 62]; Eb = [39, 55, 58, 63]; Em = [40, 55, 59, 64]; D = [38, 54, 57, 62]; A7 = [45, 55, 61, 64]
def groove(t0, t1, bpm, chords, kick_v=0.5, hat_v=0.8, pl=True, snare_v=0.3, bar_beats=4):
    b = 60 / bpm; i = 0; t = t0
    while t < t1 - 0.05:
        c = chords[(i // (bar_beats * 2)) % len(chords)]
        if i % 2 == 0: add(mus, t, kick(kick_v if (i // 2) % 2 == 0 else kick_v * 0.6))
        add(mus, t, hat(hat_v * (1 if i % 2 else 0.5)), pan=0.3)
        if i % 4 == 2 and snare_v: add(mus, t, snare(snare_v))
        if pl: add(mus, t, pluck(c[1 + (i % 3)] + 12, 0.45), pan=0.35 * math.sin(i))
        if i % (bar_beats * 2) == 0: chord_strings(t, min(t1, t + bar_beats * b), c, 0.32, 0.4, 0.5, 1.0)
        t += b / 2; i += 1



def sec_end(k): return END(k) + 0.3
# 1 开场：低弦 + 脚步声（机器人走来）→ 光球入头：钟琴上行 + 定音鼓 → 三站 → 五章节 ping
k = 0; e = E(k); t0 = G(k, 0)
chord_strings(t0, e[2], [36, 48, 55, 60], 0.55, 1.2, 0.8, 0.9)
for j in range(int(4.5 / 0.42)): add(sfx, t0 + j * 0.42, kick(0.25), pan=0.2 * (1 if j % 2 else -1))
for i, m in enumerate([67, 72, 76, 79, 84]): add(mus, e[2] + 1.0 + i * 0.1, bell(m, 0.5), pan=(i - 2) / 3)
add(mus, e[2] + 1.4, timpani(36, 0.9)); add(sfx, e[2] - 0.2, riser(1.4, 0.4))
groove(e[3], sec_end(k), 112, [C, G_, Am, F], 0.45, 0.6, snare_v=0.2)
add(sfx, e[3], whoosh(0.8, 400, 3000, 0.3))
for j in range(5): add(mus, e[4] + 0.15 + j * 0.18, bell([72, 74, 76, 79, 81][j], 0.5), pan=(j - 2) / 3)
# 2 规模：计数滴答 + 律动 → 中国红色：大调弦乐 → 排名：定音鼓
k = 1; e = E(k); t0 = G(k, 0)
groove(t0, sec_end(k), 118, [F, C, Dm, Bb], 0.5, 0.7, snare_v=0.25)
for j in range(40): add(sfx, e[2] + j * 0.05, tick(0.35, 2400 + j * 30))
add(sfx, e[4], whoosh(0.7, 300, 2500, 0.3)); chord_strings(e[4], e[5], [41, 53, 60, 65, 69], 0.4, 0.4, 0.6, 1.0)
add(mus, e[5] + 0.1, timpani(41, 0.7)); add(mus, e[6] + 0.2, timpani(43, 0.8))
for j, m in enumerate([77, 81, 84]): add(mus, e[6] + 0.2 + j * 0.1, bell(m, 0.5))
# 3 大脑：A 小调科技脉冲 → 全身点亮钟琴 → 任务红绿 blip → 技能拼合 → 房子点亮
k = 2; e = E(k); t0 = G(k, 0)
groove(t0, e[3], 108, [Am, F, C, G_], 0.4, 0.6, snare_v=0.2)
for q in range(12): add(sfx, e[2] - 0.5 + q * 0.25, blip(880 + 110 * (q % 4), 0.25), pan=math.sin(q))
add(sfx, e[3], whoosh(0.8, 300, 3000, 0.3))
prog(e[3], e[6], [Em, C, D, Em], lambda a, b_, c: chord_strings(a, b_, c, 0.45, 0.6, 0.7, 1.0))
for j in range(5): add(mus, e[4] + j * 0.4, bell(76 + [0, 3, 7, 10, 12][j], 0.5))
for j in range(5): add(sfx, e[5] + 0.3 + j * 0.15, blip(1200 if j < 2 else 300, 0.5))
add(sfx, e[6], whoosh(0.8, 400, 2500, 0.3))
groove(e[6], e[8], 100, [D, G_], 0.35, 0.5, snare_v=0.15)
for j in range(4): add(sfx, e[7] + j * 0.3, clink(0.5))
add(mus, e[7] + 1.2, bell(86, 0.5))
add(sfx, e[8], whoosh(0.8, 300, 2500, 0.3))
prog(e[8], sec_end(k), [C, Am, F, G_], lambda a, b_, c: chord_strings(a, b_, c, 0.5, 0.5, 0.7, 1.0))
for j in range(17): add(mus, e[9] + j * 0.09, bell([72, 76, 79, 84][j % 4], 0.3), pan=(j % 5 - 2) / 3)
# 4 数据：低沉 → 算力硬币 → 三种来源律动 → 英伟达
k = 3; e = E(k); t0 = G(k, 0)
chord_strings(t0, e[3], [38, 50, 57, 62], 0.5, 0.8, 0.7, 0.9)
for q in range(24): add(sfx, e[1] + q * 0.06, clink(0.25))
add(sfx, e[3], whoosh(0.7, 300, 2500, 0.3))
for q in range(35): add(sfx, e[3] + q * 0.04, clink(0.4), pan=0.6)
groove(e[4], sec_end(k), 116, [G_, D, Em, C], 0.45, 0.6, snare_v=0.25)
add(mus, e[6] + 0.1, timpani(43, 0.7)); add(mus, e[6] + 0.3, bell(83, 0.5))
# 5 量产：机械节奏 → Atlas 进行曲 → 产线
k = 4; e = E(k); t0 = G(k, 0)
groove(t0, e[4], 124, [Em, C, D, Em], 0.55, 0.8, snare_v=0.3)
for q in range(int((e[4] - t0) / 0.48)): add(sfx, t0 + q * 0.48, tick(0.4, 1500), pan=-0.4)
add(mus, e[1] + 0.5, timpani(33, 0.6))
add(sfx, e[4], whoosh(0.8, 300, 2500, 0.3))
groove(e[4], e[8], 116, [D, Bb, G_, A7], 0.5, 0.6, snare_v=0.3)
add(mus, e[7] + 0.1, timpani(38, 0.8))
add(sfx, e[8], whoosh(0.8, 300, 2500, 0.3))
groove(e[8], sec_end(k), 128, [Am, F, C, G_], 0.55, 0.8, snare_v=0.3)
# 6 家庭：温暖钢琴 + 拨弦
k = 5; e = E(k); t0 = G(k, 0)
b = 60 / 92; t = t0; i = 0
while t < sec_end(k) - 0.1:
    c = [F, C, Dm, Bb][(i // 8) % 4]
    add(mus, t, pluck(c[1 + i % 3] + 12, 0.45), pan=0.4 * math.sin(i * 0.7))
    if i % 8 == 0: chord_strings(t, t + 4 * b, c, 0.35, 0.6, 0.6, 1.0); add(mus, t, piano(c[0] + 12, 0.5, 3))
    t += b / 2; i += 1
for q in range(8): add(sfx, e[4] + q * 0.2, blip(1000 + q * 40, 0.2))
# 7 资本：悬疑 → 硬币 → 闸门 → 泡沫
k = 6; e = E(k); t0 = G(k, 0)
chord_strings(t0, e[3], [40, 52, 55, 59, 64], 0.5, 0.8, 0.7, 0.9)
add(mus, e[1] + 0.1, timpani(40, 0.7))
groove(e[3], e[5], 116, [C, G_, Am, F], 0.45, 0.6, snare_v=0.25)
for tt in (e[3], e[4]):
    for q in range(10): add(sfx, tt + 0.3 + q * 0.1, clink(0.45))
add(sfx, e[5], whoosh(0.8, 2500, 300, 0.3))
chord_strings(e[5], sec_end(k), [38, 50, 53, 57, 62], 0.5, 0.6, 0.8, 0.9)
for j in range(3): add(mus, e[6] + j * 0.3, piano(50 + j * 3, 0.6, 2))
add(sfx, e[7], riser(2.0, 0.3))
# 8 总结 + 片尾
k = 7; e = E(k); t0 = G(k, 0)
prog(t0, e[5], [C, G_, Am, F], lambda a, b_, c: chord_strings(a, b_, c, 0.55, 0.6, 0.8, 1.1))
groove(t0, e[5], 112, [C, G_, Am, F], 0.4, 0.6, pl=False, snare_v=0.2)
add(sfx, e[4] - 1.0, riser(1.1, 0.4)); add(mus, e[4] + 0.1, timpani(36, 0.8))
add(mus, e[5] + 0.05, timpani(36, 1.0)); add(mus, e[5] + 0.05, kick(0.8))
for j, m in enumerate([72, 76, 79, 84, 88]): add(mus, e[5] + j * 0.08, bell(m, 0.5), pan=(j - 2) / 3)
tend = r3d.TOTAL - 0.3
prog(e[5], tend - 2.2, [F, G_], lambda a, b_, c: chord_strings(a, b_, [c[0] - 12] + c + [c[-1] + 12], 0.8, 0.5, 1.0, 1.2))
chord_strings(tend - 2.2, tend, [36, 48, 55, 60, 64, 67, 72], 0.9, 0.2, 1.6, 1.1)
for m in [60, 64, 67, 72, 76]: add(mus, tend - 2.2, piano(m, 0.7, 4))
add(mus, tend - 2.2, timpani(36, 0.9))

voice = load_voice([os.path.join(HERE, f'narration/s{i}.flac') for i in range(1, 9)], S, mus.shape[1])
finish(mus, sfx, voice, os.path.join(HERE, 'mix.wav'))
print('mix.wav ok', T)
