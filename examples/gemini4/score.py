"""Gemini 4 新闻配乐：分段提示表见各段注释。"""
import os, sys, math
pi = math.pi
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
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


# ---------- 1 揭幕：体素飞入 → 氩原子钟琴 → 时间轴 → 三强追赶 ----------
k = 0; e = E(k); t0 = G(k, 0)
add(sfx, t0, riser(0.8, 0.4)); add(mus, t0 + 0.2, timpani(38, 1.0))
for i in range(19): add(sfx, t0 + 0.2 + i * 0.07 + 1.0, clink(0.45), pan=(i % 7 - 3) / 4)
chord_strings(t0 + 0.2, e[2], [38, 50, 57, 62, 66, 69], 0.8, 0.4, 1.0, 1.2)
for i, m in enumerate([62, 66, 69, 74]): add(mus, e[1] + i * 0.1, piano(m, 0.7, 3))
for i in range(18): add(mus, e[2] + 0.1 + i * 0.09, bell([74, 78, 81, 86][i % 4] + (12 if i >= 10 else 0), 0.35), pan=math.sin(i))
chord_strings(e[2], e[3], [43, 55, 62, 67, 71], 0.5, 0.4, 0.6, 1.1)
add(sfx, e[3], whoosh(0.8, 400, 3000, 0.35))
groove(e[3], e[6], 112, [D, Bb, G_, A7], 0.4, 0.6, snare_v=0.2)
add(mus, e[5] + 0.5, timpani(33, 0.7)); add(sfx, e[5] + 0.9, blip(220, 0.7))
add(sfx, e[6], whoosh(1.0, 300, 2500, 0.35))
groove(e[6], END(k) + 0.3, 128, [D, A7], 0.55, 0.8, snare_v=0.35)
add(sfx, END(k) - 1.2, riser(1.2, 0.45))

# ---------- 2 百万输出：长带脉冲 ----------
k = 1; e = E(k); t0 = G(k, 0)
add(mus, t0 + 0.1, timpani(38, 0.8))
b = 60 / 120; t = t0; i = 0
while t < END(k):
    add(sfx, t, tick(0.5, 3000), pan=0.3); i += 1; t += b / 2
for i in range(24): add(mus, e[2] + i * 0.09, pluck(50 + [0, 4, 7, 12, 16, 19][i % 6] + 12 * (i // 12), 0.45), pan=(i % 6 - 2.5) / 3)
chord_strings(t0, e[4], D, 0.45, 0.6, 0.7, 1.0)
chord_strings(e[4], END(k) + 0.2, [43, 55, 62, 66, 71], 0.55, 1.2, 0.7, 1.0)
add(sfx, e[4], whoosh(2.0, 200, 2000, 0.3))
add(mus, e[5] + 0.5, bell(86, 0.6)); add(mus, e[5] + 0.6, bell(90, 0.5))

# ---------- 3 成绩单 ----------
k = 2; e = E(k); t0 = G(k, 0)
groove(t0, e[6] - 0.1, 116, [G_, D, Em, C], 0.45, 0.6, snare_v=0.25)
for j in (1, 4, 5):
    for q in range(3): add(sfx, e[j] + 0.1 + q * 0.12, clink(0.5), pan=q - 1)
    add(mus, e[j] + 0.6, bell(83, 0.5))
add(sfx, e[6] - 0.1, whoosh(0.7, 2500, 300, 0.3))
chord_strings(e[6] - 0.1, END(k) + 0.3, [40, 52, 59, 64, 67], 0.55, 0.5, 0.8, 0.9)
for j in (6, 7): add(mus, e[j] + 0.6, piano(52, 0.6, 2)); add(mus, e[j] + 0.6, piano(55, 0.5, 2))

# ---------- 4 第三方 ----------
k = 3; e = E(k); t0 = G(k, 0)
prog(t0, END(k) + 0.2, [C, Am, F, G_], lambda a, b_, c: chord_strings(a, b_, c, 0.4, 0.5, 0.6, 1.0))
for j in range(4):
    for q in range(4): add(sfx, e[1] + j * 0.15 + q * 0.06, clink(0.4))
add(mus, e[2] + 0.1, bell(79, 0.5)); add(mus, e[2] + 0.1, bell(79, 0.5))
for q in range(10): add(sfx, e[4] + q * 0.14, tick(0.6, 2000 - q * 100))
add(mus, e[4] + 1.5, piano(72, 0.6, 3)); add(mus, e[4] + 1.5, piano(76, 0.6, 3))

# ---------- 5 安全首发 ----------
k = 4; e = E(k); t0 = G(k, 0)
chord_strings(t0, e[5], [38, 50, 57, 62], 0.5, 0.8, 0.8, 0.9)
for j, tt in enumerate([e[2], e[2] + 1.6, e[2] + 2.6]): add(mus, G(k, 0) + (tt - t0), bell([74, 69, 62][j], 0.5))
b = 60 / 70; t = e[5]
while t < e[6]: add(mus, t, kick(0.3)); add(mus, t + 0.25, kick(0.18)); t += b
add(sfx, e[5] + 1.6, blip(330, 0.8)); add(sfx, e[5] + 1.75, blip(330, 0.6))
chord_strings(e[5], e[6], [40, 52, 55, 59], 0.45, 0.6, 0.6, 0.8)
groove(e[6], END(k) + 0.3, 108, [Em, C, D, Em], 0.45, 0.6, snare_v=0.3)
for q in range(14): add(sfx, e[6] + 0.3 + q * 0.4, blip(900 + 60 * (q % 3), 0.25), pan=math.sin(q))

# ---------- 6 价格 → 内部应用 → 未定日期 → 片尾 ----------
k = 5; e = E(k); t0 = G(k, 0)
groove(t0, e[4], 118, [F, C, Dm, Bb], 0.45, 0.6, snare_v=0.25)
add(mus, e[2] + 0.1, timpani(41, 0.6)); add(sfx, e[3] + 0.6, riser(0.6, 0.35))
for q in range(6): add(sfx, e[3] + 0.6 + q * 0.07, clink(0.6))
add(sfx, e[4], whoosh(0.8, 300, 2500, 0.3))
prog(e[4], e[6], [Am, F, C, G_], lambda a, b_, c: chord_strings(a, b_, c, 0.45, 0.5, 0.6, 1.0))
for q in range(30): add(sfx, e[5] + q * 0.055, clink(0.35), pan=(q % 9 - 4) / 5)
chord_strings(e[6], e[8], [38, 50, 57, 64], 0.45, 0.6, 0.6, 0.9)
add(mus, e[6] + 0.4, piano(64, 0.6, 3)); add(mus, e[7] + 0.4, piano(62, 0.6, 3))
add(mus, e[8] + 0.05, timpani(36, 1.0)); add(mus, e[8] + 0.05, kick(0.8))
for j, m in enumerate([72, 76, 79, 84, 88]): add(mus, e[8] + j * 0.08, bell(m, 0.5), pan=(j - 2) / 3)
tend = r3d.TOTAL - 0.3
prog(e[8], tend - 2.2, [F, G_], lambda a, b_, c: chord_strings(a, b_, [c[0] - 12] + c + [c[-1] + 12], 0.8, 0.5, 1.0, 1.2))
chord_strings(tend - 2.2, tend, [36, 48, 55, 60, 64, 67, 72], 0.9, 0.2, 1.6, 1.1)
for m in [60, 64, 67, 72, 76]: add(mus, tend - 2.2, piano(m, 0.7, 4))
add(mus, tend - 2.2, timpani(36, 0.9))

voice = load_voice([os.path.join(HERE, f'narration/s{i}.flac') for i in range(1, 7)], S, mus.shape[1])
finish(mus, sfx, voice, os.path.join(HERE, 'mix.wav'))
print('mix.wav ok', T)
