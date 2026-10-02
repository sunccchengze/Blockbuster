"""AI 早报 · 谷歌发布 Gemini 4 Argon（两分钟新闻播报）
信息截至 2026-10-01；来源见 README.md。基准分数均为谷歌公布或第三方早期数据。
渲染：python3 -m bb render film.py video.mp4 --jobs 2
"""
from bb.render3d import *
from bb.news import *
from bb.timeline import starts_from_durations
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
TM = json.load(open(os.path.join(HERE, 'timing.json')))
dur = TM['durs']
SEG = starts_from_durations(dur, first=0.6, gap=0.5)
SUBS = [[(a, b - 0.2 if i + 1 < len(s) else b, t) for i, (a, b, t) in enumerate(s)] for s in TM['subs']]
TOTAL = SEG[-1] + dur[-1] + 2.4
def ev(k, i): return SUBS[k][i][0]

GB, GR, GY, GG = (66, 133, 244), (234, 67, 53), (251, 188, 5), (52, 168, 83)
GCOL = [GB, GR, GY, GG]
ACC = GB; TAG = 'Google DeepMind · 9月30日发布'
ARGON = (90, 150, 255); OPUS = (220, 125, 90); ASTRA = (60, 200, 170); SOL = (255, 150, 50)
RED = (240, 80, 80); GREEN = (80, 220, 120); GOLD = (245, 190, 70); PURPLE = (160, 110, 255)

M_BOX = box(1, 1, 1, WHITE)
M_BALL = sphere(1, WHITE, 18, 10)
M_RING = torus(1, 0.05, WHITE, 56, 6)
M_RING_T = torus(1, 0.14, WHITE, 56, 8)
M_PANEL = panel(1, 1)
M_RACK = rack(led=(90, 160, 255))
M_SHIELD = shield()


def base(cam, lt, d, cuts=()):
    f = Fr(cam); f.dim = min(ease(lt / 0.3), 1 - ease((lt - d - 0.02) / 0.32), dip(lt, cuts)); return f
def cube(f, P, s, col, emis=0.15, alpha=255, R=I3):
    f.mesh(M_BOX, R=R @ np.diag(s if hasattr(s, '__len__') else [s, s, s]), T=P, col=col, emis=emis, alpha=alpha)
def bar(f, x, z, h, col, w=1.0, emis=0.25, y0=0.0):
    if h > 0.01: cube(f, (x, y0 + h / 2, z), (w, h, w), col, emis)
def ring(f, P, r, col, R=I3, thick=False, emis=0.6, alpha=255):
    f.mesh(M_RING_T if thick else M_RING, R=R, T=P, sc=r, col=col, emis=emis, alpha=alpha)
def slab(f, P, w, h, col, R=I3, emis=0.1, alpha=255):
    f.mesh(M_PANEL, R=R @ np.diag([w, h, 1]), T=P, col=col, emis=emis, alpha=alpha)
def floor(f, y=0.0, a=36):
    f.grid(y, 30, 3, (100, 150, 255, a)); f.layer()


# 体素数字 “4”（5×7）
FOUR = ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."]
VOX = [((c - 2) * 1.0, (3 - r) * 1.0) for r, row in enumerate(FOUR) for c, ch in enumerate(row) if ch == '#']


# =====================================================================
# 1 揭幕：四色体素拼出 “4” → 氩原子 → 时间轴（2 月以来首发，3.5 Pro 被跳过）→ 三强追赶
# =====================================================================
def sc1(lt, d):
    k = 0; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[2], e[3], e[6]]
    if lt < e[2]:
        cam = orbit(0.35 * math.sin(lt * 0.35) + 0.2, lerp(30, 19, ease(lt / 3)), 1.5, (0, 0.5, 0), 45)
        f = base(cam, lt, d, cuts)
        for i, (x, y) in enumerate(VOX):
            h = (i * 2654435761 % 1000) / 1000
            src = np.array([math.cos(h * 6.28) * 18, math.sin(h * 9) * 9, math.sin(h * 6.28) * 18 - 6])
            g = ease((lt - 0.2 - i * 0.07) / 1.1)
            P = src + (np.array([x, y + 0.5, 0]) - src) * g
            cube(f, P, 0.92, GCOL[i % 4], 0.45 + 0.4 * (1 - g), R=roty((1 - g) * 4) @ rotx((1 - g) * 3))
        for j in range(4):
            a = lt * 1.3 + j * pi / 2; P = np.array([7.5 * math.cos(a), 0.5 + 1.8 * math.sin(a * 2), 7.5 * math.sin(a)])
            f.mesh(M_BALL, T=P, sc=0.35, col=GCOL[j], emis=0.8)
        f.text(640, 560, 'Gemini 4', 46, a=ease((lt - e[1]) / 0.5), anc='mm', stroke=3)
        chrome(f, ACC, TAG, a=ease((lt - 0.3) / 0.5))
        return f
    if lt < e[3]:                                        # 氩原子：18 个电子 2-8-8
        t = lt - e[2]
        cam = orbit(0.3 + 0.12 * t, 21, 3, (0, 1.6, 0), 45)
        f = base(cam, lt, d, cuts)
        C = np.array([0, 1.0, 0])
        for j in range(10): f.mesh(M_BALL, T=C + nrm([math.sin(j * 2.4), math.cos(j * 1.7), math.sin(j * 3.1)]) * 0.45, sc=0.38, col=GR if j % 2 else (220, 220, 230), emis=0.4)
        for s_, (r, n) in enumerate([(2.0, 2), (3.6, 8), (5.2, 8)]):
            R = rotx(0.5 + s_ * 0.6) @ rotz(s_ * 1.1)
            ring(f, C, r, (120, 170, 255), R=R, emis=0.8, alpha=150)
            for q in range(n):
                a = lt * (1.6 - s_ * 0.4) + q * 2 * pi / n
                f.mesh(M_BALL, T=C + R @ np.array([r * math.cos(a), 0, r * math.sin(a)]), sc=0.2, col=GY, emis=0.9)

        f.label(C + [5.4, 1.5, 0], 'Argon = 氩，第 18 号元素', 20, DIM, dx=20, dy=-20, a=ease((t - 0.4) / 0.4))
        chrome(f, ACC, TAG)
        return f
    if lt < e[6]:                                        # 时间轴
        t = lt - e[3]
        cam = orbit(-0.25 + 0.03 * t, 17, 5, (1.0, 0.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, -0.5, 30)
        f.mesh(M_BOX, R=np.diag([18, 0.12, 0.12]), T=(0, 0, 0), col=(120, 140, 180), emis=0.4)
        marks = [(-7.5, '2025年11月', 'Gemini 3', (120, 140, 180)), (-3.0, '2026年2月', '上一款重要模型', (120, 140, 180)), (7.0, '2026年9月30日', 'Gemini 4 Argon', GB)]
        for j, (x, d1, d2, col) in enumerate(marks):
            g = ease((t - j * 0.4) / 0.4)
            f.mesh(M_BALL, T=(x, 0, 0), sc=0.35 * g + 0.01, col=col, emis=0.7)
            f.label((x, 0, 0), d1, 18, DIM, dx=0, dy=44, dot=False, a=g)
            f.label((x, 0.6, 0), d2, 20, WHITE if j < 2 else (150, 190, 255), dx=0, dy=-34, dot=False, a=g)
        g = ease((t - 1.2) / 1.2)
        if g > 0: cube(f, (-3.0 + 5.0 * g, 0.25, 0), (10 * g, 0.1, 0.3), GOLD, 0.6)
        f.label((2.0, 0.3, 0), '7 个多月', 22, GOLD, dx=0, dy=40, dot=False, a=ease((t - 2.2) / 0.4) * (1 - ease((lt - e[5]) / 0.3)))
        if lt > e[5]:                                    # 3.5 Pro：被跳过
            g = ease((lt - e[5]) / 0.5)
            P = np.array([2.0, 3.4 - 0.6 * g, 0])
            slab(f, P, 3.2, 1.3, (70, 80, 100), emis=0.2, alpha=int(255 * (1 - 0.4 * g)))
            f.label(P, 'Gemini 3.5 Pro', 20, (200, 205, 215), dx=0, dy=8, dot=False, a=1 - 0.3 * g)
            if g > 0.5:
                for s_ in (1, -1): cube(f, P + [0, 0, 0.2], (3.8 * ease((g - 0.5) * 2), 0.18, 0.08), RED, 0.8, R=rotz(0.38 * s_))
            f.label(P + [0, 1.0, 0], '原定 6 月发布，最终跳过', 18, RED, dx=0, dy=-30, dot=False, a=ease((lt - e[5] - 0.6) / 0.4))
        chrome(f, ACC, TAG); headline(f, lt, ACC, None, '谷歌今年第一款旗舰')
        return f
    t = lt - e[6]                                        # 追赶：三条跑道
    cam = orbit(0.6 + 0.04 * t, 17, 7, (2.0, 0, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, -0.3, 28)
    for j, (nm, col, x0, x1) in enumerate([('OpenAI', ASTRA, 4.5, 6.5), ('Anthropic', OPUS, 4.0, 6.3), ('Google', GB, -1.0, 6.0)]):
        z = (j - 1) * 2.6
        cube(f, (1.5, -0.25, z), (16, 0.08, 1.6), (40, 48, 64), 0.1)
        x = lerp(x0, x1, ease(t / 2.4))
        f.mesh(M_BALL, T=(x, 0.5, z), sc=0.55, col=col, emis=0.6)
        for q in range(6): f.dots([(x - 0.6 - q * 0.45, 0.5, z)], 0.18 - q * 0.025, (*col, 200 - q * 30))
        f.label((-6.0, 0.3, z), nm, 20, col, dx=0, dy=-10, dot=False, a=ease((t - j * 0.2) / 0.4))
    chrome(f, ACC, TAG); headline(f, lt, ACC, None, '目标：追上 OpenAI 与 Anthropic')
    return f


# =====================================================================
# 2 一百万 token 输出：64K 短带 vs 1M 长带（1 : 15.6）→ 沿长带飞行 → 一次完成
# =====================================================================
def sc2(lt, d):
    k = 1; e = [ev(k, i) for i in range(len(SUBS[k]))]
    L = 31.2; L0 = L * 64 / 1000
    fly = ease((lt - e[4]) / (d - e[4]))
    tgt = np.array([lerp(-8, 14, fly) if lt > e[4] else -6 + 6 * ease((lt - e[2]) / 1.5), 0.5, 0])
    cam = Cam(tgt + np.array([-6 + 3 * fly, 6 - 2 * fly, 13 - 4 * fly]), tgt, 48)
    f = base(cam, lt, d)
    floor(f, -0.4, 30)
    x0 = -16
    g0 = ease((lt - e[1]) / 0.6)
    cube(f, (x0 + L0 * g0 / 2, 0.3, 1.6), (L0 * g0 + 0.01, 0.5, 0.9), (150, 160, 180), 0.25)
    f.label((x0 + L0 / 2, 0.6, 1.6), '6.4万', 22, DIM, dx=0, dy=-30, dot=False, a=g0 * (1 - fly))
    g1 = ease((lt - e[2]) / 2.2)
    n = int(g1 * 120)
    for i in range(n):
        x = x0 + (i + 0.5) * L / 120
        cube(f, (x, 0.3 + 0.08 * math.sin(i * 0.5 + lt * 3), -0.6), (L / 120 * 0.85, 0.5, 0.9), GCOL[(i // 30) % 4], 0.45)
    if n: f.label((x0 + n * L / 120, 0.6, -0.6), counter(lt, e[2], e[2] + 2.2, 6.4, 100, '{:.0f}万'), 24, WHITE, dx=10, dy=-30, dot=False, a=1 - fly * 0.6)
    card(f, 40, 160, 300, 112, '单次最大输出（token）', '64K → 1M', '', ACC, a=ease((lt - 0.2) / 0.4), vsz=36,
         note='约 15.6 倍' if lt > e[3] else None)
    if lt > e[5] + 0.5:
        A = ease((lt - e[5] - 0.5) / 0.4)
        f.label((x0 + L + 0.8, 1.2, -0.6), '✓ 一次完成', 24, GREEN, dx=10, dy=-30, dot=False, a=A)
    chrome(f, ACC, TAG); headline(f, lt, ACC, '1', '输出上限：64K → 100 万', '更长的推理轨迹，难题一次写完')
    return f


# =====================================================================
# 3 成绩单：每个测试一组三柱（Argon / Opus 5.5 / Astra），先赢后输
# =====================================================================
BENCH = [  # (名称, Argon, Opus 5.5, Astra, 从第几句开始)
    ('DeepSWE v1.1 · 长程软件工程', 77.9, 74.2, 74.1, 1),
    ('AutomationBench · 业务自动化', 51.3, 42.5, 41.4, 4),
    ('法律 · 金融 · 长视频', None, None, None, 5),
    ('Terminal-Bench 4.0 · 终端编程', 57.4, 66.4, 58.2, 6),
    ('FrontierSWE v2', 55.0, 62.3, 65.5, 7),
]
TRIO = [('Harvey 法律', 19.6, 3.8, 5.4), ('金融智能体 v2', 65.4, 58.6, 53.5), ('LVBench 长视频', 91.7, 83.7, 87.5)]


def sc3(lt, d):
    k = 2; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cur = 0
    for j, b in enumerate(BENCH):
        if lt >= e[b[4]] - 0.1: cur = j
    cuts = [e[b[4]] - 0.1 for b in BENCH[1:]]
    t0 = e[BENCH[cur][4]] - 0.1 if lt > e[1] - 0.1 else 0
    cam = orbit(-0.25 + 0.04 * (lt - t0), 18, 4.5, (0, 2.8, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, 0, 32)
    names = [('Gemini 4 Argon', ARGON), ('Claude Opus 5.5', OPUS), ('GPT-6 Astra', ASTRA)]
    lose = cur >= 3
    if lt < e[1] - 0.1:                                   # 开场：三家模型代表色
        for j, (nm, col) in enumerate(names):
            x = (j - 1) * 4.5; f.mesh(M_BALL, T=(x, 2.5, 0), sc=1.0 * pop(lt, 0.1 + j * 0.2), col=col, emis=0.6)
            f.label((x, 1.2, 0), nm, 22, col, dx=0, dy=40, dot=False, a=ease((lt - 0.2 - j * 0.2) / 0.3))
        f.text(640, 560, '数据来自谷歌官方公布', 22, col=DIM, anc='mm', bold=False, a=ease((lt - 0.6) / 0.4))
    elif BENCH[cur][1] is None:                           # 三连小组
        for g_, (nm, *vals) in enumerate(TRIO):
            gx = (g_ - 1) * 6.2
            for j, v in enumerate(vals):
                h = v * 0.07 * ease((lt - t0 - g_ * 0.2) / 0.8)
                bar(f, gx + (j - 1) * 1.5, 0, h, names[j][1], 1.2, 0.35)
                if j == 0: f.label((gx - 1.5, h + 0.4, 0), f'{v}%', 20, WHITE, dx=0, dy=-10, dot=False, a=ease((lt - t0 - 0.6) / 0.3))
            f.label((gx, 0, 0.8), nm, 20, DIM, dx=0, dy=36, dot=False, a=ease((lt - t0) / 0.3))
    else:
        nm, *vals, _ = BENCH[cur]
        for j, v in enumerate(vals):
            x = (j - 1) * 4.0; h = v * 0.062 * ease((lt - t0 - j * 0.12) / 0.9)
            best = v == max(vals)
            bar(f, x, 0, h, names[j][1], 2.4, 0.5 if best else 0.25)
            f.label((x, h + 0.5, 0), f'{v}%', 26, GOLD if best else WHITE, dx=0, dy=-10, dot=False, a=ease((lt - t0 - 0.5) / 0.3))
            f.label((x, 0, 1.4), names[j][0], 18, names[j][1], dx=0, dy=40, dot=False, a=ease((lt - t0) / 0.3))
        f.text(40, 178, nm, 24, col=RED if lose else (180, 210, 255), anc='lm', a=ease((lt - t0) / 0.3), stroke=2)
    if lose: f.text(40, 214, 'Argon 落后', 22, col=RED, anc='lm', a=ease((lt - e[6]) / 0.3), stroke=2)
    chrome(f, ACC, TAG); headline(f, lt, ACC, '2', '成绩单：多数领先，并非全胜', '谷歌公布数据，尚无独立复现')
    return f


# =====================================================================
# 4 第三方：Artificial Analysis 智能指数 → 幻觉率仪表
# =====================================================================
M_GAUGE = torus(3.0, 0.18, (60, 70, 90), 60, 8, arc=pi)


def sc4(lt, d):
    k = 3; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[4]]
    if lt < e[4]:
        cam = orbit(0.2 - 0.03 * lt, 18, 4, (0, 3.2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 32)
        rows = [('Claude Opus 5.5', 58, OPUS), ('Gemini 4 Argon', 53, ARGON), ('GPT-6 Astra', 53, ASTRA), ('GPT-6.1 Sol', 52, SOL)]
        for j, (nm, v, col) in enumerate(rows):
            x = (j - 1.5) * 3.4; g = ease((lt - e[1] - j * 0.15) / 0.9)
            h = (v - 40) * 0.3 * g
            bar(f, x, 0, h, col, 2.0, 0.5 if j in (1, 2) and lt > e[2] else 0.25)
            f.label((x, h + 0.5, 0), f'{v}', 28, WHITE, dx=0, dy=-10, dot=False, a=g)
            f.label((x, 0, 1.3), nm, 18, col, dx=0, dy=40, dot=False, a=ease((lt - 0.2 - j * 0.1) / 0.3))
        if lt > e[2]: f.label((-1.7, 5.0, 0), '持平', 24, GOLD, dx=0, dy=-30, dot=False, a=ease((lt - e[2]) / 0.3))
        card(f, 40, 160, 330, 104, 'Artificial Analysis 智能指数', '53', '分', ACC, a=ease((lt - e[1]) / 0.4))
        chrome(f, ACC, TAG); headline(f, lt, ACC, '3', '第三方评测：更冷静', None)
        return f
    t = lt - e[4]
    cam = orbit(0.08 * math.sin(t * 0.5), 12, 1.5, (0, 1.6, 0), 45)
    f = base(cam, lt, d, cuts)
    C = np.array([0, 0.6, 0])
    f.mesh(M_GAUGE, R=rotx(-pi / 2), T=C, emis=0.1)
    v = lerp(60, 15, ease(t / 1.4))
    arc = torus(3.0, 0.22, GREEN if v < 25 else GOLD, 60, 8, arc=pi * v / 60 + 0.01)
    f.mesh(arc, R=rotx(-pi / 2), T=C + [0, 0, 0.05], emis=0.8)
    a = pi * v / 60
    f.mesh(M_BOX, R=rotz(a - pi / 2) @ np.diag([0.12, 2.6, 0.12]), T=C + rotz(a - pi / 2) @ np.array([0, 1.3, 0.2]), col=WHITE, emis=0.6)
    f.label(C + [0, -0.4, 0], f'{v:.0f}%', 44, WHITE, dx=0, dy=40, dot=False)
    f.label(C + [0, -1.2, 0], '幻觉率 · 主流模型中最低', 22, GREEN, dx=0, dy=60, dot=False, a=ease((t - 1.0) / 0.4))
    chrome(f, ACC, TAG); headline(f, lt, ACC, '3', '第三方评测：幻觉率最低', '数据：Artificial Analysis')
    return f


# =====================================================================
# 5 安全首发：Fairwind 同心圈 → 内部激活监控 → 提示注入攻防
# =====================================================================
NET = [(x, y) for x in range(-3, 4) for y in range(-2, 3)]


def sc5(lt, d):
    k = 4; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[5], e[6]]
    if lt < e[5]:
        cam = orbit(0.2 + 0.03 * lt, 18, 9, (0, 0, 0), 45)
        f = base(cam, lt, d, cuts)
        rings = [(2.6, '网络安全防御者（Fairwind 计划）', GREEN, e[2]), (5.2, 'AI Ultra 会员 + 付费 API（未定日期）', GOLD, e[2] + 1.6), (7.8, '所有用户', (130, 140, 160), e[2] + 2.6)]
        f.mesh(M_BALL, T=(0, 0.8, 0), sc=1.0, col=GB, emis=0.7)
        f.mesh(M_SHIELD, R=I3, T=(0, 3.0, 0), sc=0.4 * ease((lt - e[1]) / 0.5), col=GREEN, emis=0.5)
        for j, (r, nm, col, ta) in enumerate(rings):
            g = ease((lt - ta) / 0.5); lit = j == 0
            ring(f, (0, 0, 0), r, col if lit else tuple(int(c * 0.6) for c in col), thick=True, emis=0.9 if lit else 0.3, alpha=int(255 * g))
            f.label((r * 0.71, 0, r * 0.71), nm, 20, col, dx=30, dy=20, a=g)
        if lt > e[4]:
            for j, nm in enumerate(['政府', '医疗', '电信', '能源', '金融']):
                a = j * 2 * pi / 5 + 0.3 + lt * 0.15; P = np.array([1.8 * math.cos(a), 0.3, 1.8 * math.sin(a)])
                cube(f, P, 0.5 * ease((lt - e[4] - j * 0.1) / 0.3), GREEN, 0.6)
        chrome(f, ACC, TAG); headline(f, lt, ACC, '4', '安全优先：先给网络防御者', '经美国政府自愿性发布前审查流程')
        return f
    if lt < e[6]:
        t = lt - e[5]
        cam = orbit(-0.2 + 0.04 * t, 14, 3, (0, 0.5, 0), 45)
        f = base(cam, lt, d, cuts)
        sweep = lerp(-4, 4, clamp(t / 2.6)); bad = (1, 0)
        for (x, y) in NET:
            for (x2, y2) in ((x + 1, y), (x, y + 1)):
                if (x2, y2) in NET: f.line([(x * 1.4, y * 1.2, 0), (x2 * 1.4, y2 * 1.2, 0)], (90, 130, 200, 90), 2)
        for (x, y) in NET:
            hit = (x, y) == bad and x * 1.4 < sweep
            f.mesh(M_BALL, T=(x * 1.4, y * 1.2, 0), sc=0.32 if not hit else 0.42, col=RED if hit else (120, 160, 230), emis=0.8 if hit else 0.4)
        f.layer(); slab(f, (sweep, 0, 0.5), 0.08, 6.0, (120, 255, 200), emis=0.9, alpha=110)
        if sweep > 1.4: f.label((1.4, 0, 0), '异常激活：疑似滥用', 20, RED, dx=40, dy=-40, a=ease((t - 1.6) / 0.3))
        chrome(f, ACC, TAG); headline(f, lt, ACC, '4', '监控模型“内部激活”', '实时发现网络攻击、生化核风险等滥用')
        return f
    t = lt - e[6]
    cam = orbit(0.35 - 0.04 * t, 17, 4, (0, 2.5, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, 0, 30)
    for j, (x, col, rate, nm) in enumerate([(-4.0, ARGON, 0.7, 'Gemini 4 Argon'), (4.0, ASTRA, 8.5, 'GPT-6 Astra')]):
        f.mesh(M_SHIELD, R=I3, T=(x, 3.2, 0), sc=0.8, col=col, emis=0.35, alpha=220)
        for q in range(10):
            ph = ((lt - e[6]) * 0.9 + q / 10) % 1; P = np.array([x + lerp(-6, 0, ph) * (1 if j else -1) * -1, 3.2 + math.sin(q) * 1.2, 4.5 * (1 - ph) + 0.4])
            leak = (q < 1 if j == 1 else False) and ph > 0.9
            cube(f, P, 0.22, RED if not leak else (255, 160, 160), 0.8)
        g = ease((lt - e[7] - j * 0.6) / 0.8)
        h = rate * 0.45 * g
        bar(f, x, 0, max(h, 0.05 * g), RED, 1.4, 0.5, y0=0)
        f.label((x, h + 0.5, 0), f'{rate}%', 26, WHITE, dx=0, dy=-10, dot=False, a=g)
        f.label((x, 0, 1.2), nm, 18, col, dx=0, dy=40, dot=False, a=ease(t / 0.4))
    card(f, 40, 160, 320, 104, '间接提示注入（越低越好）', '攻击成功率', '', RED, a=ease(t / 0.4), vsz=30, note='Gray Swan IPI 测试')
    chrome(f, ACC, TAG); headline(f, lt, ACC, '4', '抗提示注入：谷歌最强一代', None)
    return f


# =====================================================================
# 6 价格战：同价标签 → 涨价 → 数据中心省出 300TB → 何时可用？ → 片尾
# =====================================================================
def sc6(lt, d):
    k = 5; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[4], e[6], e[8]]
    if lt < e[4]:
        cam = orbit(-0.1 + 0.03 * lt, 15, 3, (0, 2.6, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30)
        for j, (x, col, nm) in enumerate([(-3.8, ARGON, 'Gemini 4 Argon'), (3.8, SOL, 'GPT-6.1 Sol')]):
            s = pop(lt, 0.2 + j * 0.3)
            slab(f, (x, 3.0, 0), 4.6 * s, 3.0 * s, (20, 26, 40), emis=0.15, R=roty(0.25 * (1 if j else -1)))
            cube(f, (x, 4.3 * s, 0.1), (4.6 * s, 0.4 * s, 0.05), col, 0.6)
            f.label((x, 4.4, 0.1), nm, 20, WHITE, dx=0, dy=-24, dot=False, a=s)
            up = j == 0 and lt > e[3]
            price = '$4 / $20' if up and lt > e[3] + 0.6 else '$2 / $10'
            f.label((x, 2.9, 0.1), price, 36, GOLD if up and lt > e[3] + 0.6 else WHITE, dx=0, dy=14, dot=False, a=ease((lt - e[1]) / 0.4))
            f.label((x, 1.7, 0.1), '输入 / 输出 · 每百万 token', 16, DIM, dx=0, dy=20, dot=False, a=ease((lt - e[1]) / 0.4))
        if e[2] < lt < e[3] + 0.4: f.label((0, 3.0, 0), '=', 54, GOLD, dx=0, dy=20, dot=False, a=win(lt, e[2], e[3] + 0.4))
        if lt > e[3]:
            g = ease((lt - e[3]) / 0.6)
            cube(f, (-0.9, 2.6 + 0.5 * g, 0.3), (0.3, 1.2 * g, 0.1), RED, 0.7)
            cube(f, (-0.9, 3.3 + 0.6 * g, 0.3), (0.7 * g, 0.7 * g, 0.1), RED, 0.7, R=rotz(pi / 4))
            f.label((-3.8, 0.4, 0), '推广期结束后翻倍', 20, RED, dx=0, dy=30, dot=False, a=ease((lt - e[3] - 0.4) / 0.4))
        f.label((3.8, 0.4, 0), '前一天刚发布', 18, DIM, dx=0, dy=30, dot=False, a=ease((lt - e[2]) / 0.4))
        chrome(f, ACC, TAG); headline(f, lt, ACC, '5', '价格：与 OpenAI 针锋相对', '缓存输入一律 95% 折扣')
        return f
    if lt < e[6]:
        t = lt - e[4]
        cam = orbit(0.5 + 0.06 * t, 20, 7, (0, 1.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30)
        for r in range(3):
            for c in range(7):
                f.mesh(M_RACK, T=((c - 3) * 2.3, 2.0, (r - 1) * 3.4), sc=1.0, emis=0.05)
        g = ease((lt - e[5]) / 1.6)
        for q in range(int(g * 30)):
            h = (q * 7919) % 1000 / 1000
            P = np.array([(h - 0.5) * 14, 4.3 + ((lt * 1.5 + h * 7) % 4), ((q * 31) % 7 - 3) * 1.4])
            cube(f, P, 0.35, GREEN, 0.8, alpha=200)
        card(f, 40, 160, 300, 104, '谷歌内部：智能体优化内存', counter(lt, e[5], e[5] + 1.6, 0, 300) + '+' if lt > e[5] else '0', 'TB 已释放', GREEN, a=ease(t / 0.4))
        chrome(f, ACC, TAG); headline(f, lt, ACC, '5', '已在谷歌内部干活', '数据中心内存优化 · 视频解码器改写成 Rust')
        return f
    if lt < e[8]:
        t = lt - e[6]
        cam = orbit(0.1 * math.sin(t), 12, 2.5, (0, 2.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 28)
        slab(f, (0, 2.8, 0), 4.0, 4.0, (240, 240, 245), emis=0.3)
        cube(f, (0, 4.6, 0.08), (4.0, 0.7, 0.05), GB, 0.5)
        f.label((0, 2.6, 0.1), '?', 80, (40, 50, 70), dx=0, dy=30, dot=False, a=ease(t / 0.4))
        for j, nm in enumerate(['付费 API', 'AI Ultra 会员']):
            f.label(((j - 0.5) * 6.5, 1.0, 0.5), nm, 22, GOLD, dx=0, dy=-10, dot=False, a=ease((t - 0.3 - j * 0.3) / 0.4))
        chrome(f, ACC, TAG); headline(f, lt, ACC, '5', '何时能用？谷歌未给日期', None)
        return f
    t = lt - e[8]                                          # 片尾
    cam = orbit(lt * 0.15, lerp(18, 24, ease(t / 3)), 2.0, (0, 0.5, 0), 45)
    f = base(cam, lt, d, cuts)
    for i, (x, y) in enumerate(VOX):
        cube(f, (x, y + 0.5, 0), 0.92, GCOL[i % 4], 0.5)
    for j in range(6):
        a = lt * 0.8 + j * pi / 3; ring(f, (0, 0.5, 0), 6 + j * 0.1, GCOL[j % 4], R=rotx(1.2 + 0.2 * j) @ rotz(a * 0.3), emis=0.7, alpha=140)
    f.rect(390, 548, 890, 600, (*ACC, int(225 * ease(t / 0.5))), r=10)
    f.text(640, 574, 'AI 早报 · 我们明天见', 28, anc='mm', a=ease(t / 0.5))
    chrome(f, ACC, TAG)
    return f


FILM = Film(SEG, dur, [sc1, sc2, sc3, sc4, sc5, sc6], SUBS,
            chapters=['揭幕', '百万输出', '成绩单', '第三方', '安全首发', '价格'], total=TOTAL, lead=0.15)
