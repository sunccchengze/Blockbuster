"""DevDay 新闻播报配乐：场景提示表 → 代码。时间线取自 film.py（声画同源）。
1 开场：片头定音鼓+弦乐重音 → 时钟滴答（时差）→ 120bpm 新闻律动，卡片逐张叮 → 12亿上行+重音 → 6 件事钟琴
2 Dots：俏皮拨弦琶音 F 大调，出场钟琴；应用球 ping 群；共享记忆弦乐渐强；闸门：D 小调大提琴断奏，批准→大调和弦
3 Sol：温暖钢琴+弦乐 Bb；价格柱上行拨弦；缓存 ping；打平双音钟琴；成本方块叮当
4 Ultrafast：140bpm 鼓组+上升噪声+掠过声；价格 6 枚硬币；Pro 500 华丽弦乐+钢琴
5 Codex：112bpm A 小调科技脉冲；合盖闷响；语音 blip；多智能体 ping；扫描低频脉冲，发现漏洞低 blip，修复钟琴
6 平台：G 大调拨弦律动；插件落位叮；MCP 波纹 ping；三步钟琴；Space 弦乐+打字滴答
7 场外：E 小调低弦+心跳；上锁咔哒；抗议：城市氛围+行进小鼓；估值硬币+上行
8 收尾：转盘每项定音鼓；聊天→干活弦乐上行；翻日历掠过；Gemini 揭幕钟琴；同价重音；终止和弦
"""
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

# ---------- 1 开场 ----------
k = 0; e = E(k); t0 = G(k, 0)
add(mus, t0 + 0.15, timpani(36, 1.1)); add(mus, t0 + 0.15, kick(0.9))
chord_strings(t0 + 0.15, e[2], [36, 48, 55, 60, 64, 67, 72], 0.9, 0.12, 1.0, 1.3)
for i, m in enumerate([60, 64, 67, 72, 76]): add(mus, t0 + 0.15 + i * 0.09, piano(m, 0.8, 3))
add(sfx, t0, riser(0.6, 0.4))
for j in range(int((e[4] - e[2]) / 0.5)): add(sfx, e[2] + j * 0.5, tick(0.9, 2600 if j % 2 else 3400))   # 时钟滴答
chord_strings(e[2], e[4], [45, 57, 64, 69], 0.45, 0.8, 0.6, 0.9)
add(sfx, e[2] + 0.3, whoosh(1.3, 400, 3000, 0.4)); add(sfx, e[3] + 0.4, whoosh(1.6, 200, 1500, 0.35))
groove(e[4], e[7], 120, [C, Am, F, G_], 0.5, 0.7)
for i in range(22): add(sfx, e[4] + 0.25 + i * 0.05 + 0.8, clink(0.5), pan=(i % 11 - 5) / 6)
add(sfx, e[6] - 1.0, riser(1.1, 0.5)); add(mus, e[6] + 0.1, timpani(38, 0.9))
for i in range(6): add(mus, e[7] + 0.1 + i * 0.12, bell([72, 74, 76, 79, 81, 84][i], 0.6), pan=(i - 2.5) / 3)
chord_strings(e[7], END(k) + 0.3, [41, 53, 60, 65, 69], 0.6, 0.3, 0.6, 1.1)

# ---------- 2 Dots ----------
k = 1; e = E(k); t0 = G(k, 0)
add(mus, t0 + 0.25, bell(84, 0.8)); add(sfx, t0 + 0.25, blip(1320, 1.0))
b = 60 / 104; t = t0; i = 0
while t < e[6] - 0.1:
    c = [F, C, Dm, Bb][(i // 8) % 4]
    add(mus, t, pluck(c[1 + i % 3] + 12 + (12 if i % 8 >= 4 else 0), 0.5), pan=0.4 * math.sin(i * 0.7))
    if i % 4 == 0: add(mus, t, kick(0.35))
    if i % 4 == 2: add(mus, t, hat(0.6))
    if i % 8 == 0: chord_strings(t, t + 4 * b, c, 0.3, 0.5, 0.6, 1.0)
    t += b / 2; i += 1
add(mus, e[2], piano(53, 0.7, 3)); add(mus, e[2], piano(60, 0.6, 3))
add(sfx, e[3], whoosh(0.8, 500, 3000, 0.3))
for j in range(36): add(sfx, e[4] + 2.0 * math.sqrt(j / 36), ping(rng.choice([2093, 2349, 2637, 3136, 3520]), 0.35), pan=rng.uniform(-.8, .8))
chord_strings(e[5], e[6], [53, 60, 65, 69, 72], 0.5, 1.0, 0.5, 1.2)
b = 60 / 120; t = e[6]; i = 0
while t < e[9] - 0.1:
    add(mus, t, cello_stac(38 + (7 if i % 4 == 3 else 0), 0.2), pan=-0.3)
    if i % 2 == 0: add(mus, t, cello_stac(50, 0.2), g=0.6, pan=0.3)
    t += b / 2; i += 1
chord_strings(e[6], e[8] + 1.2, [50, 57, 62], 0.35, 0.8, 0.4, 0.8, trem=6)
for j in range(2): add(sfx, e[7] + j * 0.5 + 1.0, blip(440, 1.2))
add(mus, e[8] + 1.2, bell(81, 0.7)); add(mus, e[8] + 1.2, timpani(38, 0.6))
chord_strings(e[8] + 1.2, e[9], [38, 50, 54, 57, 62, 66], 0.7, 0.2, 0.5, 1.2)
for j in range(3): add(mus, e[9] + 0.1 + j * 0.25, bell([74, 78, 81][j], 0.6))
groove(e[9], END(k) + 0.2, 104, [D, G_], 0.35, 0.6, snare_v=0)

# ---------- 3 Sol ----------
k = 2; e = E(k); t0 = G(k, 0)
prog(t0, e[5], [Bb, F, [43, 55, 58, 62], Eb] * 2, lambda a, b_, c: chord_strings(a, b_, c, 0.45, 0.8, 0.8, 1.0))
t = t0; i = 0
while t < e[5]:
    c = [Bb, F, [43, 55, 58, 62], Eb][int((t - t0) / ((e[5] - t0) / 8)) % 4]
    add(mus, t, piano(c[1 + i % 3] + 12, 0.45, 2.0), pan=(i % 3 - 1) * 0.3); t += 0.42; i += 1
add(mus, t0 + 0.15, bell(82, 0.5)); add(mus, t0 + 0.45, bell(86, 0.5))
for j in range(8): add(mus, e[2] + j * 0.12, pluck(58 + [0, 2, 4, 5, 7, 9, 11, 12][j], 0.6))
for j in range(8): add(mus, e[3] - 0.3 + j * 0.12, pluck(53 + [0, 2, 4, 5, 7, 9, 11, 12][j], 0.6))
add(sfx, e[4] + 0.2, ping(3000, 0.8))
add(mus, e[5], timpani(41, 0.6))
add(mus, e[5] + 0.3, bell(77, 0.7), pan=-0.4); add(mus, e[5] + 0.3, bell(77, 0.7), pan=0.4)
groove(e[5], END(k) + 0.2, 116, [Bb, F, Eb, F], 0.45, 0.6)
for j in range(7): add(sfx, e[7] + j * 0.08, clink(0.8), pan=-0.5)
add(sfx, e[7], clink(1.2), pan=0.5)

# ---------- 4 Ultrafast ----------
k = 3; e = E(k); t0 = G(k, 0)
add(sfx, t0, riser(e[1] - t0, 0.5))
b = 60 / 140; t = t0; i = 0
while t < e[5] - 0.1:
    dens = 1 if t > e[1] else 0
    add(mus, t, kick(0.6)) if i % 2 == 0 else None
    add(mus, t, hat(0.9), pan=0.3)
    if dens: add(mus, t + b / 4, hat(0.5), pan=-0.3)
    if i % 4 == 2: add(mus, t, snare(0.4))
    add(mus, t, cello_stac([45, 45, 52, 48][(i // 2) % 4], 0.15), g=0.7)
    t += b / 2; i += 1
chord_strings(t0, e[5], [45, 57, 64, 69, 76], 0.35, 0.6, 0.5, 1.2, trem=10)
for j in range(10): add(sfx, t0 + 0.5 + j * (e[5] - t0) / 10, whoosh(0.7, 300, 5000, 0.35), pan=(-1) ** j * 0.6)
add(mus, e[2], timpani(45, 0.8))
for j in range(6): add(sfx, e[3] + 0.1 + j * 0.15, clink(1.0), pan=rng.uniform(-.4, .4))
add(mus, e[4], bell(81, 0.6))
add(mus, e[5], timpani(41, 0.9))
prog(e[5], END(k) + 0.3, [[41, 53, 57, 60, 65], [43, 55, 59, 62, 67], [45, 57, 60, 64, 69]], lambda a, b_, c: chord_strings(a, b_, c, 0.75, 0.4, 0.8, 1.3))
for j in range(14): add(mus, e[5] + j * 0.6, piano([65, 69, 72, 77, 72, 69, 67][j % 7] + 12, 0.45, 2.5), pan=0.3 * math.sin(j))
for j in range(25): add(sfx, e[6] + j * 0.03, tick(0.6, 3000 + j * 40))

# ---------- 5 Codex ----------
k = 4; e = E(k); t0 = G(k, 0)
b = 60 / 112; t = t0; i = 0
while t < END(k):
    c = [Am, F, C, G_][(i // 8) % 4]
    if i % 2 == 0: add(mus, t, kick(0.45))
    add(mus, t, pluck(c[0] + 24 + (7 if i % 4 == 3 else 0), 0.4), pan=0.3)
    if i % 4 == 2: add(mus, t, hat(0.7))
    if i % 8 == 0: chord_strings(t, t + 4 * b, c, 0.28, 0.5, 0.6, 0.9)
    t += b / 2; i += 1
add(sfx, e[1], whoosh(1.0, 300, 3000, 0.4)); add(sfx, e[2] + 0.85, kick(0.7))
for j in range(10): add(sfx, e[3] + 0.2 + j * 0.13, blip(800 + 200 * (j % 4), 0.6))
for j in range(4): add(sfx, e[4] + 0.6 + j * 0.15, ping([2093, 2637, 3136, 3520][j], 0.7))
for j in range(int((e[6] - e[5]) / 0.5)): add(mus, e[5] + j * 0.5, cello_stac(33, 0.3), g=0.9)
add(sfx, e[5], whoosh(e[6] - e[5], 200, 1200, 0.35))
for j in range(5): add(sfx, e[5] + 0.6 + j * 0.7, blip(330, 1.0))
for j, m in enumerate([72, 76, 79, 84]): add(mus, e[6] + 0.6 + j * 0.1, bell(m, 0.6))
for j in range(8): add(sfx, e[7] + 0.9 * (j + 1) - 0.1, tick(0.9, 2200))
for j in range(3): add(sfx, e[8] + 0.8 + j * 0.15, blip([1047, 784, 659][j], 0.8))
for j in range(3): add(sfx, e[9] + j * 0.7, whoosh(0.8, 400, 2500, 0.3), pan=-0.5 + j * 0.5)
add(mus, e[10], bell(81, 0.5))

# ---------- 6 平台 ----------
k = 5; e = E(k); t0 = G(k, 0)
groove(t0, e[5], 108, [G_, Em, C, D], 0.45, 0.7)
add(mus, t0 + 0.2, timpani(43, 0.6))
for j in range(8): add(sfx, e[1] + j * 0.18 + 0.45, clink(0.9), pan=math.cos(j * pi / 4) * 0.6)
add(sfx, e[2], whoosh(0.7, 500, 2500, 0.3))
for j in range(5): add(sfx, e[3] + 0.6 + j * 1.5, ping(1760, 0.6))
for j in range(3): add(mus, e[4] + j * 0.6, bell([79, 83, 86][j], 0.6))
chord_strings(e[5], END(k) + 0.3, [43, 55, 59, 62, 67, 71], 0.6, 1.0, 0.8, 1.1)
t = e[5]; i = 0
while t < END(k):
    add(mus, t, piano([67, 71, 74, 79, 74, 71][i % 6], 0.4, 2), pan=0.3 * math.sin(i)); t += 0.45; i += 1
for j in range(30): add(sfx, e[8] + j * 0.08 + rng.uniform(0, 0.03), tick(0.5, rng.uniform(1800, 2600)), pan=rng.uniform(-.5, .5))
add(sfx, e[9], whoosh(0.9, 400, 3000, 0.35))

# ---------- 7 场外 ----------
k = 6; e = E(k); t0 = G(k, 0)
chord_strings(t0, e[4], [28, 40, 52, 55, 59], 0.55, 1.0, 0.6, 0.6)
for j in range(int((e[4] - t0) / 1.6)): add(sfx, t0 + j * 1.6, heartbeat(0.7))
add(sfx, e[3] + 0.4, clink(1.5)); add(mus, e[3] + 0.4, timpani(40, 0.7))
add(sfx, e[4], city(e[5] - e[4] + 0.6), g=0.9)
for j in range(int((e[5] - e[4]) / 0.25)): add(mus, e[4] + j * 0.25, snare(0.25 if j % 4 else 0.45))
chord_strings(e[5], END(k) + 0.3, [40, 52, 59, 64, 67], 0.5, 0.6, 0.6, 1.0)
add(sfx, e[6] - 0.5, riser(2.5, 0.4))
for j in range(28): add(sfx, e[6] - 0.5 + 2.0 * (j / 28) ** 0.7, clink(0.6), pan=-0.3)
for j in range(7): add(sfx, e[7] + j * 0.14, clink(0.8), pan=0.4)

# ---------- 8 收尾 ----------
k = 7; e = E(k); t0 = G(k, 0)
for i in range(5): add(mus, e[i], timpani(36 + [0, 2, 4, 5, 7][i], 0.6)); add(sfx, e[i] + 0.05, whoosh(0.6, 400, 2500, 0.25))
prog(t0, e[5], [C, G_, Am, F], lambda a, b_, c: chord_strings(a, b_, c, 0.55, 0.6, 0.8, 1.1))
groove(t0, e[5], 116, [C, G_, Am, F], 0.4, 0.6, pl=False, snare_v=0.25)
chord_strings(e[5], e[7], [41, 53, 57, 60, 65], 0.5, 1.5, 0.6, 1.0)
add(sfx, e[6] - 0.5, riser(1.6, 0.4)); add(mus, e[6] + 0.9, timpani(41, 0.7))
add(sfx, e[7] + 0.3, whoosh(0.7, 600, 4000, 0.4))
chord_strings(e[7], e[9], [45, 57, 64, 69, 72], 0.5, 0.6, 0.8, 1.2)
for j, m in enumerate([76, 79, 83, 88, 91]): add(mus, e[8] - 0.2 + j * 0.08, bell(m, 0.55), pan=(j - 2) / 3)
add(mus, e[9] + 0.05, timpani(36, 1.0)); add(mus, e[9] + 0.05, kick(0.8))
tend = r3d.TOTAL - 0.3
prog(e[9], tend - 2.2, [F, G_], lambda a, b_, c: chord_strings(a, b_, [c[0] - 12] + c + [c[-1] + 12], 0.85, 0.5, 1.0, 1.2))
chord_strings(tend - 2.2, tend, [36, 48, 55, 60, 64, 67, 72], 0.9, 0.2, 1.6, 1.1)
for m in [60, 64, 67, 72, 76]: add(mus, tend - 2.2, piano(m, 0.7, 4))
add(mus, tend - 2.2, timpani(36, 0.9))

voice = load_voice([os.path.join(HERE, f'narration/s{i}.flac') for i in range(1, 9)], S, mus.shape[1])
finish(mus, sfx, voice, os.path.join(HERE, 'mix.wav'))
print('mix.wav ok', T)
