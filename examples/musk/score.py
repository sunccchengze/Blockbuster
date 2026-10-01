# 分场景配乐 + 同步音效（弦乐 / 钢琴 / 定音鼓 / 鼓组 / 氛围音效），跟随 r3d.py 的时间线
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(os.path.dirname(HERE))); sys.path.insert(0, HERE)
import film as r3d                      # 时间线（段落起点、字幕锚点）直接取自 film.py，声画同源
ASSETS = os.environ.get('MUSK_ASSETS', os.path.expanduser('~/musk'))   # 旁白 narration/s1–s8.flac 所在目录
from bb.score import *
T = r3d.TOTAL
mus, sfx = buses(T)
S = r3d.SEG
def G(k, lt): return S[k] + lt
def ev(k, i): return G(k, r3d.ev(k, i))

# 和弦 (midi)
Am = [45, 57, 60, 64]; F = [41, 57, 60, 65]; C = [48, 55, 60, 64]; Gm_ = [43, 55, 59, 62]; Em = [40, 55, 59, 64]
Dm = [38, 53, 57, 62]; Bb = [46, 53, 58, 62]; A7 = [45, 55, 61, 64]; Gm = [43, 55, 58, 62]; D = [38, 54, 57, 62]

# ============ 1 序章：发射 → 轨道 → 标题 ============
k = 0
add(sfx, G(k, 0.2), rumble(6.8, 1.2, 1.0, 160), g=0.9)                     # 发动机轰鸣
add(sfx, G(k, 1.0), rumble(5.9, 2.0, 0.6, 900), g=0.25)                   # 高频嘶啸
add(mus, G(k, 0.0), timpani(33, 0.8)); add(mus, G(k, 1.0), timpani(33, 1.0))
chord_strings(G(k, 0.0), G(k, 3.6), [33, 45, 52, 57], 0.9, 1.5, 0.6, 0.8)
chord_strings(G(k, 3.6), G(k, 7.2), [29, 41, 53, 57, 60], 1.0, 0.8, 0.6, 1.0)
add(mus, G(k, 5.0), riser(2.2, 0.8))
for i in range(8): add(mus, G(k, 3.6 + i * 0.45), timpani(33 + (i % 2) * 7, 0.35 + i * 0.07))
add(sfx, G(k, 7.05), whoosh(0.9, 200, 2500, 0.6))
# 轨道：空灵 + 26 颗卫星逐颗"叮"
chord_strings(G(k, 7.2), G(k, 13.0), [48, 60, 64, 67, 71], 0.55, 1.2, 1.2, 1.3)
pent = [72, 74, 76, 79, 81, 84, 86, 88]
for i in range(26): add(mus, G(k, 7.2 + 0.8 + 0.14 * i), bell(pent[(i * 3) % 8], 0.45), pan=((i % 5) - 2) / 3)
# 标题：大和弦重音
add(mus, G(k, 13.0), timpani(36, 1.2)); add(mus, G(k, 13.0), kick(0.9))
chord_strings(G(k, 13.0), G(k, 18.6), [36, 48, 55, 60, 64, 67], 1.1, 0.15, 1.5, 1.2)
for i, m in enumerate([60, 64, 67, 72]): add(mus, G(k, 13.0 + i * 0.12), piano(m, 0.9, 4))

# ============ 2 少年：温暖钢琴 + 轻弦乐 + 8-bit 游戏音 ============
k = 1; t0, t1 = G(k, 0), G(k, 22.1)
chords = [C, Am, F, Gm_] * 3; step = (t1 - t0) / len(chords)
for i, c in enumerate(chords):
    a = t0 + i * step
    chord_strings(a, a + step, [c[0] + 12] + c[1:], 0.45, 0.9, 1.0, 0.7)
    for j in range(8):
        m = c[1:][j % 3] + (12 if j >= 4 else 0) + 12
        add(mus, a + j * step / 8, piano(m, 0.55 + 0.2 * (j == 0), 2.5), pan=(j % 3 - 1) * 0.3)
g0 = ev(k, 1)
for i, f in enumerate([523, 659, 784, 1047, 784, 1047, 1319]): add(sfx, g0 + 0.8 + i * 0.11, blip(f, 1.0))
for c in range(1, 4): add(sfx, ev(k, [0, 2, 3, 4][c]) + 0.2, whoosh(1.4, 400, 3500, 0.35))   # 地球转向

# ============ 3 第一桶金：110bpm 轻快律动 → ALL IN ============
k = 2; bpm = 110; b = 60 / bpm; t0, t1 = G(k, 0), G(k, 20.5); c4 = ev(k, 4)
ch3 = [F, C, Gm_, Am]
nb = int((c4 - t0) / b)
for i in range(nb):
    t = t0 + i * b; c = ch3[(i // 4) % 4]
    add(mus, t, kick(0.55 if i % 2 == 0 else 0.0)); add(mus, t + b / 2, hat(0.8), pan=0.3)
    if i % 4 == 2: add(mus, t, snare(0.35))
    add(mus, t, pluck(c[0] + 12, 0.9)); add(mus, t + b / 2, pluck(c[0] + 24, 0.5))
    if i % 4 == 0: chord_strings(t, t + 4 * b, c[1:], 0.35, 0.3, 0.4, 1.1)
    if i % 2 == 0: add(mus, t, piano(c[1 + (i // 2) % 3] + 12, 0.45, 1.5), pan=-0.3)
add(sfx, G(k, 0.4), riser(1.8, 0.35)); add(sfx, ev(k, 2) - 0.1, riser(2.3, 0.5))
for i in range(6): add(sfx, ev(k, 2) + 0.3 + i * 0.3, clink(1.0), pan=rng.uniform(-.5, .5))
add(sfx, ev(k, 1) + 2.0, kick(0.5))                                          # 两块合并
# ALL IN：音乐停顿 → 两次砸落 → 大和弦
for i in range(2): add(sfx, c4 + 0.3 + i * 0.8 + 0.95, boom(0.55)); add(mus, c4 + 0.3 + i * 0.8 + 0.95, timpani(38 - i * 2, 0.9))
chord_strings(c4 + 2.0, t1 + 0.4, [41, 53, 57, 60, 65], 1.0, 0.1, 0.8, 1.2)
add(mus, c4 + 2.0, kick(0.9))

# ============ 4 SpaceX：D 小调紧张断奏 → 胜利 → 回收 → 星链 ============
k = 3; e = [ev(k, i) for i in range(8)]; b = 60 / 124
t = G(k, 0); i = 0
while t < e[3]:
    c = [Dm, Dm, Bb, A7][(i // 8) % 4]; add(mus, t, cello_stac(c[0] + 12 + (7 if i % 4 == 3 else 0), 0.2), pan=-0.3)
    if i % 2 == 0: add(mus, t, cello_stac(c[2], 0.2), pan=0.3)
    t += b / 2; i += 1
chord_strings(G(k, 0), e[3], [50, 57, 62], 0.35, 1.0, 0.5, 0.8, trem=6)
for j in range(3):
    tf = e[2] + j * 0.8 + 0.25
    add(sfx, tf, boom(0.8), pan=-0.5 + j * 0.3); add(mus, tf, timpani(38 - j, 0.7))
add(sfx, e[3], rumble(e[4] - e[3], 0.3, 0.8, 200), g=0.6)
# 成功：D 大调
chord_strings(e[3] + 0.4, e[4], [38, 50, 54, 57, 62, 66], 1.0, 0.3, 0.8, 1.3)
for m in [62, 66, 69, 74]: add(mus, e[3] + 0.4, piano(m, 0.7, 3))
add(mus, e[3] + 0.4, timpani(38, 1.0))
# 回收：下降轰鸣 + 张力弦乐 → 着陆
add(sfx, e[4], rumble(e[5] - e[4] - 0.6, 0.4, 0.6, 220), g=0.55)
chord_strings(e[4], e[5], [38, 50, 57, 64], 0.5, 0.6, 0.6, 0.9, trem=8)
add(sfx, e[5] - 0.6, boom(0.4)); add(mus, e[5] - 0.6, timpani(38, 0.6))
# 龙飞船：失重感
chord_strings(e[5], e[6], [50, 57, 62, 69, 74], 0.45, 0.8, 1.0, 1.2)
add(sfx, e[5], whoosh(e[6] - e[5], 150, 1200, 0.3)); add(sfx, e[6] - 0.5, clink(1.5))
# 星链：闪烁高音弦乐 + 数据 ping
chord_strings(e[6], G(k, 23.3), [50, 62, 66, 69, 74, 78], 0.6, 1.0, 1.0, 1.3)
for j in range(40):
    add(sfx, e[6] + 0.1 * j * (1 + j * 0.02), ping(rng.choice([2093, 2349, 2637, 3136]), 0.5), pan=rng.uniform(-.8, .8))

# ============ 5 特斯拉：120bpm 驱动 → 破产警报 → 明亮 → 金币 → 城市 ============
k = 4; e = [ev(k, i) for i in range(len(r3d.SUBS[k]))]; b = 0.5
t = G(k, 0); i = 0
while t < e[3]:
    c = [Am, F, C, Gm_][(i // 8) % 4]
    add(mus, t, kick(0.55)) if i % 2 == 0 else add(mus, t, hat(0.9), pan=0.3)
    add(mus, t, pluck(c[0] + 12, 0.8)); t += b / 2; i += 1
chord_strings(G(k, 0), e[3], Am[1:] + [69], 0.35, 0.6, 0.5)
# 濒临破产：音乐骤停，警报 + 不协和颤音 + 心跳
add(sfx, e[3], alarm(e[4] - e[3] - 0.2))
chord_strings(e[3], e[4], [40, 46, 52, 53], 0.6, 0.2, 0.6, 1.0, trem=9)
for j in range(int((e[4] - e[3]) / 0.8)): add(sfx, e[3] + j * 0.8, heartbeat(1.0))
# Model S/3/Y：明亮大调 + 驶入 whoosh
chord_strings(e[4], e[5], [48, 60, 64, 67, 72], 0.7, 0.3, 0.6, 1.3)
t = e[4]; i = 0
while t < e[5]:
    add(mus, t, kick(0.5)) if i % 2 == 0 else add(mus, t, hat(1.0)); add(mus, t, pluck([60, 64, 67, 72][i % 4] + 12, 0.5)); t += 0.25; i += 1
for j in range(3): add(sfx, e[4] + j * 0.9 + 0.1, whoosh(0.9, 250, 2500, 0.6), pan=-0.6 + j * 0.6)
# 薪酬：金币叮当 + 上行
n_c = 40
for j in range(n_c): add(sfx, e[5] + 3.2 * math.sqrt(j / n_c) * 1.0, clink(0.8), pan=rng.uniform(-.4, .4))
chord_strings(e[5], e[7], [41, 53, 57, 60, 65], 0.55, 0.5, 0.6, 1.1)
add(sfx, e[5] + 1.0, riser(e[7] - e[5] - 1.0, 0.4))
# Cybercab：城市氛围 + 电子琶音
add(sfx, e[7], city(G(k, 28.8) - e[7]), g=0.8)
t = e[7]; i = 0
while t < G(k, 28.6):
    c = [Am, F, C, Gm_][(i // 16) % 4]; add(mus, t, pluck(c[1 + i % 3] + 12 + (12 if i % 8 >= 4 else 0), 0.55), pan=0.4 * math.sin(i))
    if i % 4 == 0: add(mus, t, kick(0.45))
    t += 0.2; i += 1
chord_strings(e[7], G(k, 28.8), [45, 57, 64, 69], 0.4, 0.8, 0.8)

# ============ 6 版图：每出现一个公司叠加一层 → 合并大重音 ============
k = 5; e = [ev(k, i) for i in range(len(r3d.SUBS[k]))]; t0, t1 = G(k, 0), G(k, 26.7)
layers = [(t0, 38), (e[1], 50), (e[2], 57), (e[4], 62), (e[5], 69)]
for j, (ts, m) in enumerate(layers):
    add(mus, ts, strings(m, e[6] - ts, 0.6, 0.8, 0.9 + 0.1 * j), pan=(j - 2) * 0.3, g=0.7)
    add(mus, ts, bell(m + 24, 0.6), pan=(j - 2) * 0.3); add(sfx, ts, whoosh(0.7, 500, 3000, 0.3))
t = t0; i = 0
while t < e[6]:
    add(mus, t, timpani(38, 0.25 + 0.3 * (t - t0) / (e[6] - t0))) if i % 4 == 0 else None
    add(mus, t, cello_stac(38 + [0, 12, 7, 12][i % 4], 0.2), g=0.6); t += 0.5 * 0.5; i += 1
add(mus, e[6] + 0.3 - 1.8, riser(2.0, 0.7))
add(sfx, e[6] + 0.3, whoosh(1.8, 200, 4000, 0.6))
add(mus, e[6] + 2.1, timpani(38, 1.2)); add(mus, e[6] + 2.1, kick(1.0))
chord_strings(e[6] + 2.1, t1, [38, 50, 57, 62, 66, 69], 1.0, 0.1, 1.0, 1.3)
for m in [62, 66, 69, 74, 78]: add(mus, e[6] + 2.1, piano(m, 0.6, 4))

# ============ 7 争议：低音大提琴脉冲 + 心跳 + 卡片掠过 ============
k = 6; e = [ev(k, i) for i in range(len(r3d.SUBS[k]))]; t0, t1 = G(k, 0), G(k, 22.6)
prog(t0, t1, [Em, Em, [36, 52, 55, 60], [35, 51, 54, 59]] * 2, lambda a, b_, c: chord_strings(a, b_, [c[0] - 12] + c, 0.55, 1.0, 1.0, 0.6))
t = t0; i = 0
while t < t1:
    add(mus, t, cello_stac(28 + (3 if i % 8 >= 6 else 0), 0.3), g=1.0)
    if i % 4 == 0: add(sfx, t, heartbeat(0.9))
    t += 0.4; i += 1
for i in range(1, 8): add(sfx, e[i] - 0.1, whoosh(0.8, 300, 2500, 0.45), pan=0.5 if i % 2 else -0.5)
add(sfx, e[7] + 0.2, boom(0.45))

# ============ 8 现在：上涨 → 金币雨 → 白宫 → 正反面 → 火星终章 ============
k = 7; e = [ev(k, i) for i in range(8)]; tend = r3d.TOTAL - 0.2
add(sfx, G(k, 0), riser(3.6, 0.6))
chord_strings(G(k, 0), e[2], [43, 55, 59, 62, 67], 0.7, 1.5, 0.6, 1.1)
b = 0.48; t = G(k, 0); i = 0
while t < e[3]:
    add(mus, t, kick(0.5)) if i % 2 == 0 else add(mus, t, hat(0.9)); t += b / 2; i += 1
add(mus, e[2], timpani(36, 1.1)); add(mus, e[2], kick(1.0))
chord_strings(e[2], e[3], [36, 48, 55, 60, 64, 67], 1.0, 0.1, 0.6, 1.3)
for j in range(30): add(sfx, e[2] + rng.uniform(0, 2.5), clink(0.9), pan=rng.uniform(-.7, .7))
# 白宫：庄重稀疏
chord_strings(e[3], e[5], [41, 53, 57, 60], 0.55, 1.0, 0.8, 0.8)
for j, m in enumerate([65, 69, 72, 69, 77, 72]): add(mus, e[3] + 0.4 + j * 0.9, piano(m, 0.5, 3))
# 硬币翻面：悬念
chord_strings(e[5], e[6], [45, 57, 60, 64], 0.6, 0.6, 0.4, 1.0)
chord_strings(e[6], e[7], [44, 56, 59, 62], 0.6, 0.3, 0.6, 1.0, trem=7)
add(sfx, e[6] - 0.3, whoosh(1.0, 400, 5000, 0.6)); add(sfx, e[6] + 0.7, clink(2.0))
# 火星终章：宏大弦乐 + 钢琴解决 + 飞船掠过
add(sfx, e[7], whoosh(3.4, 150, 2500, 0.45))
prog(e[7], tend - 2.0, [F, C, [43, 55, 59, 62, 67], [45, 57, 60, 64, 69]], lambda a, b_, c: chord_strings(a, b_, [c[0] - 12] + c + [c[-1] + 12], 0.95, 0.8, 1.0, 1.2))
chord_strings(tend - 2.0, tend - 0.2, [36, 48, 55, 60, 64, 67, 72], 0.9, 0.3, 1.5, 1.1)
for j in range(12): add(mus, e[7] + j * 0.33, piano([65, 69, 72, 77, 72, 69][j % 6] + 12, 0.45, 2.5), pan=0.3 * math.sin(j))
add(mus, tend - 2.0, timpani(36, 0.9))
for m in [60, 64, 67, 72, 76]: add(mus, tend - 2.0, piano(m, 0.7, 4))

# 转场淡入淡出由场景本身承担：此处不再加刺耳转场音
# ---------- 混响 + 人声闪避 → mix.wav ----------
voice = load_voice([os.path.join(ASSETS, f'narration/s{i}.flac') for i in range(1, 9)], S, mus.shape[1])
finish(mus, sfx, voice, 'mix.wav')
print('mix.wav ok', T)
