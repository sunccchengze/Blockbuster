"""深度讲解 · Andrej Karpathy：履历、思想、作品，以及三个可学习的特质（约 3 分 40 秒）
信息截至 2026-10-01。人物为风格化 3D 角色，不使用肖像。渲染：python3 -m bb render film.py video.mp4 --jobs 4
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from bb.explain import *
from bb.figure3d import *
dur, SEG, SUBS, DISP, TOTAL = load_timing(HERE)
def ev(k, i): return SUBS[k][i][0]
def EV(k): return [ev(k, i) for i in range(len(SUBS[k]))]
ACC = (255, 170, 60); TAG = 'Andrej Karpathy · 人物与方法'; FL = (255, 180, 110)
TR = [(CYAN, '亲手从零造一遍'), (GREEN, '用教学和公开分享逼自己想清楚'), (PURPLE, '不断更新自己，敢于承认落后')]
CH = lambda f, a=1.0: chrome_x(f, ACC, TAG, a=a, badge='人物讲解')


def net(f, C, layers, sp=(1.4, 0.8), col=CYAN, g=1.0, lt=0.0, s=0.16, fire=None):
    C = np.array(C, float); pos = []
    for i, n in enumerate(layers):
        x = (i - (len(layers) - 1) / 2) * sp[0]
        pos.append([C + [x, (j - (n - 1) / 2) * sp[1], 0] for j in range(n)])
    for i in range(len(pos) - 1):
        for a in pos[i]:
            for b in pos[i + 1]: f.line([a, b], (*col, int(60 * g)), 1)
    if fire is not None and g > 0.5:
        for i in range(len(pos) - 1):
            ph = (fire - i * 0.25) % 1.0
            for a, b in zip(pos[i][::2], pos[i + 1][::2]): f.dots([a + (b - a) * ph], 0.05, (*WHITE, 200))
    for i, L in enumerate(pos):
        for j, P in enumerate(L): ball(f, P, s * g, col, 0.4 + 0.4 * (math.sin(lt * 3 + i + j) > 0.5))
    return pos


def screen_panel(f, P, w, h, a=1.0, col=(16, 20, 30), frame=(80, 90, 110)):
    P = np.array(P, float)
    cube(f, P, (w + 0.1, h + 0.1, 0.06), frame, 0.2, 255 * a)
    cube(f, P + [0, 0, 0.035], (w, h, 0.01), col, 0.35, 255 * a)


def tag3d(f, P, s, col, sz=17, a=1.0, txt=WHITE):
    """3D 点上的 2D 标签牌（深底描边），在浅色物体上也清楚。"""
    x, y, z = f.pt(P)
    if z < 0.5 or a < 0.02: return
    w = font(sz).getlength(s) + 18
    f.rect(x - w / 2, y - sz * 0.75, x + w / 2, y + sz * 0.75, (12, 14, 24, int(215 * a)), r=6, outline=(*col, int(200 * a)), w=2)
    f.text(x, y, s, sz, col=txt, anc='mm', a=a)


def method(f, lt, t0, s, col):
    if lt > t0:
        A = ease((lt - t0) / 0.5)
        f.rect(240, 520, 1040, 594, (12, 16, 28, int(225 * A)), r=12, outline=(*col, int(220 * A)), w=3)
        f.text(270, 557, '马上能用', 20, col=col, a=A, anc='lm')
        f.text(380, 557, s, 24, a=A, anc='lm')


def trait_tag(f, lt, j):
    col, nm = TR[j]; headline(f, lt, col, str(j + 1), '特质' + '一二三'[j] + '：' + nm, None)


# =====================================================================
# 1 开场：阶梯教室，讲者在大屏前比划，观众逐排入座 → 三张待揭晓的卡
# =====================================================================
def sc1(lt, d):
    k = 0; e = EV(k)
    cam = orbit(0.22 + 0.03 * lt, lerp(13.5, 11, ease(lt / 7)), lerp(5.5, 4.2, ease(lt / 7)), (0, 1.9, 0.2), 45)
    f = base(cam, lt, d); floor(f, FL)
    screen_panel(f, (0, 2.6, -3.2), 4.4, 2.4)
    net(f, (0, 2.6, -3.12), [3, 4, 4, 2], (0.95, 0.55), ACC, 1.0, lt, 0.11, fire=lt * 0.8)
    cube(f, (0, 0.12, -1.5), (3.0, 0.24, 1.6), (70, 62, 54), 0.2)
    figure(f, (0, 0.24, -1.5), 0.15 * math.sin(lt * 0.5), 1.0, la=0.9 + 0.25 * math.sin(lt * 1.6), lo=0.25, le=0.9, ra=0.2, re=0.3)
    n = int(84 * ease(lt / 3.2))
    for i in range(n):
        r_, c = divmod(i, 14)
        x = (c - 6.5) * 0.85; z = 1.2 + r_ * 1.0; y = r_ * 0.28
        mini(f, (x, y, z), (120 + (i * 37) % 60, 130 + (i * 23) % 50, 160), 0.55, 0.15, yaw=pi)
    for r_ in range(6):
        cube(f, (0, r_ * 0.28 / 2 if r_ else 0.01, 1.2 + r_ * 1.0), (12.4, max(r_ * 0.28, 0.02), 0.95), (34, 38, 50), 0.1)
    lab(f, (0, 4.3, -3.2), 'Andrej Karpathy', 36, ACC, a=ease((lt - e[1]) / 0.4))
    if lt > e[2]:
        for j in range(3):
            g = pop(lt, e[2] + 0.4 + j * 0.3)
            f.rect(330 + j * 220, 512, 510 + j * 220, 582, (20, 24, 36, int(225 * g)), r=10, outline=(*TR[j][0], int(220 * g)), w=2)
            f.text(420 + j * 220, 547, f'特质 {j + 1}  ？', 24, a=g, anc='mm')
    CH(f, ease((lt - 0.3) / 0.5)); headline(f, lt, ACC, None, '顶尖研究者 · 无数人的启蒙老师')
    return f


# =====================================================================
# 2 履历：人物沿时间轴走过 8 个里程碑，每站一个图标
# =====================================================================
MILES = [('多伦多大学', '本科', (120, 160, 220)), ('斯坦福 · 李飞飞', '博士：图像 ↔ 语言', (200, 70, 70)), ('CS231n', '深度学习课程', (200, 70, 70)),
         ('OpenAI', '2015 · 创始成员', (120, 220, 200)), ('特斯拉', '2017–2022 · AI 总监', (230, 70, 70)), ('OpenAI', '2023 · 回归', (120, 220, 200)),
         ('Eureka Labs', '2024 · AI 教育', GOLD), ('Anthropic', '2026.5 · 预训练研究', (220, 140, 100))]
MAP = [0, 1, 2, 3, 4, 5, 7]
SP = 4.2
def mile_icon(f, i, P, lt):
    if i == 0: icon_book(f, P, 1.0, (60, 90, 160))
    elif i == 1:
        icon_cap(f, P + [-0.5, 0, 0], 0.9, lt)
        screen_panel(f, P + [0.7, 0.2, 0], 0.9, 0.6)
        cube(f, P + [0.55, 0.1, 0.05], (0.3, 0.2, 0.01), (90, 160, 90), 0.6); ball(f, P + [0.85, 0.3, 0.05], 0.06, GOLD, 0.9)
    elif i == 2: icon_screen(f, P + [0, 0.25, 0], 0.9, lt)
    elif i in (3, 5): icon_ring(f, P + [0, 0.3, 0], 1.0, lt, MILES[i][2])
    elif i == 4: icon_car(f, P + [0, -0.25, 0], 0.9, lt)
    elif i == 6: icon_bulb(f, P + [0, 0.1, 0], 1.0, lt)
    else: icon_star(f, P + [0, 0.3, 0], 1.0, lt)


def sc2(lt, d):
    k = 1; e = EV(k)
    keys = [(e[i] - 0.2, MAP[i]) for i in range(len(e))]; keys.insert(6, (e[5] + 2.2, 6))
    idx, t_cur, prev = 0, -9.0, 0
    for tk, ik in keys:
        if lt >= tk and ik != idx: prev, idx, t_cur = idx, ik, tk
    mv = ease((lt - t_cur) / 1.1)
    xs = [i * SP for i in range(8)]
    fx = lerp(xs[prev], xs[idx], mv)
    cam = orbit(0.42, 8.6, 2.6, (fx + 0.6, 1.3, 0), 45)
    f = base(cam, lt, d); floor(f, FL)
    cube(f, (14.7, 0.04, 1.2), (34, 0.08, 0.3), (110, 96, 80), 0.3)
    for i, (nm, sub, col) in enumerate(MILES):
        on = i <= idx; x = xs[i]
        if abs(x - fx) > 9: continue
        cube(f, (x, 0.15, 0), (1.9, 0.3, 1.6), col if on else DARK, 0.35 if i == idx else 0.15)
        cube(f, (x, 0.32, 0), (1.6, 0.04, 1.3), (30, 34, 44), 0.2)
        if on:
            mile_icon(f, i, np.array([x, 1.1, 0]), lt)
            a = 1.0 if i == idx else 0.55
            lab(f, (x, 2.3, 0), nm, 24 if i == idx else 18, WHITE, a=a); lab(f, (x, 2.3, 0), sub, 17, col, dy=16, a=a)
    walking = mv < 1 and lt > 0.3
    figure(f, (fx + 1.25, 0.0, 1.2), 0.5 if not walking else pi / 2, 0.85, walk=lt * 7 if walking else None, la=0.1, ra=0.1)
    CH(f); headline(f, lt, ACC, '1', '履历', None)
    return f


# =====================================================================
# 3 思想：软件 1.0 / 2.0 / 3.0 三块屏 → vibe coding 被划掉 → 智能体工程闭环
# =====================================================================
CODE = [(200, 120, 255), (120, 200, 255), (255, 200, 120), (150, 230, 150), (120, 200, 255), (255, 140, 140)]
def sc3(lt, d):
    k = 2; e = EV(k); cuts = [e[3]]
    if lt < e[3]:
        cam = orbit(0.08 * math.sin(lt * 0.3), 10.5, 2.4, (0, 1.9, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        g1 = ease(lt / 0.5); g2 = ease((lt - e[1]) / 0.6); g3 = ease((lt - e[2]) / 0.6)
        for j, (x, g) in enumerate([(-4.2, g1), (0, g2), (4.2, g3)]):
            if g > 0.01: screen_panel(f, (x, 2.0, 0), 3.4 * g, 2.3 * g)
        if g1 > 0.3:
            for q in range(7):
                w = [1.8, 1.2, 2.2, 0.9, 1.6, 2.0, 1.1][q]; ind = [0, 0.3, 0.3, 0.6, 0.3, 0, 0][q]
                cube(f, (-5.6 + ind + w / 2, 2.8 - q * 0.27, 0.05), (w, 0.12, 0.01), CODE[q % 6], 0.6, 255 * g1)
        lab(f, (-4.2, 0.6, 0), '软件 1.0 · 人写规则', 20, GREY, dy=20, a=g1)
        if g2 > 0.3: net(f, (0, 2.0, 0.08), [3, 4, 4, 2], (0.85, 0.5), CYAN, g2, lt, 0.11, fire=lt)
        lab(f, (0, 0.6, 0), '软件 2.0 · 权重就是代码', 20, CYAN, dy=20, a=g2)
        if g3 > 0.3:
            cube(f, (3.6, 2.5, 0.05), (1.8, 0.45, 0.01), (60, 70, 100), 0.5, 255 * g3)
            lab(f, (3.6, 2.5, 0.07), '“按月汇总这张表”', 15, WHITE, dy=0, a=g3)
            cube(f, (4.8, 1.75, 0.05), (1.6, 0.45, 0.01), (90, 70, 40), 0.5, 255 * g3)
            lab(f, (4.8, 1.75, 0.07), '好的，已完成 ✓', 15, WHITE, dy=0, a=g3)
        lab(f, (4.2, 0.6, 0), '软件 3.0 · 自然语言即编程', 20, ACC, dy=20, a=g3)
        for j, g in enumerate((g2, g3)):
            if g > 0: beam(f, (-2.4 + j * 4.2, 2.0, 0), (-1.8 + j * 4.2, 2.0, 0), ACC, 200 * g, 4)
        CH(f); headline(f, lt, ACC, '2', '擅长给时代命名', '软件 2.0（2017）· 软件 3.0')
        return f
    t = lt - e[3]
    cam = orbit(0.25 + 0.02 * t, 10, 2.4, (0, 2.0, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    figure(f, (-4.4, 0, 0.5), 0.6, 0.9, la=0.6 + 0.3 * math.sin(lt * 4), ra=0.6 + 0.3 * math.sin(lt * 4 + 1), le=1.2, re=1.2, nod=0.15 * math.sin(lt * 4))
    cube(f, (-4.4 + 0.5 * math.sin(0.6), 0.75, 0.5 + 0.5 * math.cos(0.6)), (0.9, 0.05, 0.6), (60, 64, 76), 0.3, R=roty(0.6))
    pts = [(-3.0 + q * 0.22, 2.6 + 0.35 * math.sin(q * 0.8 + lt * 2), 0) for q in range(16)]
    f.line(pts, (*PINK, 230), 5); lab(f, (-1.3, 3.4, 0), 'vibe coding · 2025', 24, PINK)
    if lt > e[4]:
        A = ease((lt - e[4]) / 0.5)
        cube(f, (-1.3, 2.65, 0.2), (3.8 * A, 0.09, 0.04), RED, 0.9)
        nodes = [('规划', (2.4, 2.9, 0)), ('执行', (4.4, 2.9, 0)), ('检查', (3.4, 1.3, 0))]
        for j, (nm, P) in enumerate(nodes):
            g = pop(lt, e[4] + 0.2 + j * 0.2)
            cube(f, P, (1.1 * g, 0.6 * g, 0.5 * g), GOLD, 0.45); tag3d(f, np.array(P) + [0, 0.65, 0], nm, GOLD, 18, g)
        for j in range(3):
            P0 = np.array(nodes[j][1]); P1 = np.array(nodes[(j + 1) % 3][1])
            beam(f, P0 + (P1 - P0) * 0.28, P0 + (P1 - P0) * 0.72, GOLD, 200 * A, 3)
            flow(f, P0 + (P1 - P0) * 0.28, P0 + (P1 - P0) * 0.72, lt, GOLD, 2, 0.8, 0.06)
        lab(f, (3.4, 3.8, 0), '智能体工程 · 2026', 24, GOLD, a=A)
    CH(f); headline(f, lt, ACC, '2', '连自己造的词也会更新', None)
    return f


# =====================================================================
# 4 作品：终端里 git clone → 五个仓库按“代码量”堆起 → autoresearch 实验环 + GPU
# =====================================================================
REPOS = [('micrograd', '≈150 行 · 自动求导', CYAN, 1, 3), ('nanoGPT', '最小 GPT 训练', BLUE, 2, 7), ('llm.c', '纯 C 训练 GPT', GREY, 2, 9),
         ('nanochat', '$100 的 ChatGPT', GREEN, 3, 11), ('MicroGPT', '243 行纯 Python', ACC, 4, 4)]
def sc4(lt, d):
    k = 3; e = EV(k); cuts = [e[5]]
    if lt < e[5]:
        cam = orbit(-0.22 + 0.025 * lt, 11, 3.2, (0, 1.7, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        if lt < e[1] + 0.5:
            A = 1 - ease((lt - e[1]) / 0.5)
            screen_panel(f, (0, 2.0, 0), 6.0, 2.6, A)
            s_ = '$ git clone github.com/karpathy/'
            nshow = int(len(s_) * clamp(lt / 1.8))
            f.label((0, 2.35, 0.08), s_[:nshow] + ('▌' if int(lt * 3) % 2 else ''), 26, GREEN, dx=0, dy=0, a=A, dot=False)
            f.label((0, 1.8, 0.08), '从零开始 · 尽量小 · 能读懂', 22, DIM, dx=0, dy=0, a=A * ease((lt - 1.0) / 0.4), dot=False)
        for j, (nm, sub, col, si, nlay) in enumerate(REPOS):
            g = pop(lt, e[si] + (0.5 if j == 2 else 0))
            if g < 0.01: continue
            x = (j - 2) * 2.7
            for q in range(nlay): cube(f, (x, 0.12 + q * 0.26 * g, 0), (1.7, 0.2, 1.1), col, 0.28 + 0.18 * (q % 2))
            top = 0.12 + nlay * 0.26 * g
            cube(f, (x, top + 0.02, 0), (1.2, 0.04, 0.8), (240, 240, 240), 0.5)
            lab(f, (x, top + 0.5, 0), nm, 22, WHITE, a=g); lab(f, (x, 0, 0.8), sub, 15, col, dy=34, a=g)
        if lt > e[1]: note(f, 640, 560, '共同点：从零开始 · 尽量小 · 能读懂', ease((lt - e[1]) / 0.4), 22, accent=ACC)
        CH(f); headline(f, lt, ACC, '3', '作品：一系列从零开始的开源代码', '堆叠层数 ≈ 代码量（示意）')
        return f
    t = lt - e[5]
    cam = orbit(0.3 + 0.06 * t, 10, 4.2, (0, 1.2, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    gpu(f, (0, 0.9, 0), 1.0, lt); tag3d(f, (0, 0.2, 0.9), '1 张 GPU', WHITE, 18)
    n = int(clamp((lt - e[6]) / 3.0) * 700) if lt > e[6] else int(t * 8)
    stages = [('改代码', ACC), ('训练', CYAN), ('评估', PURPLE), ('保留 / 丢弃', GREEN)]
    for j, (nm, col) in enumerate(stages):
        a_ = j / 4 * 2 * pi + pi / 4; P = np.array([3.8 * math.cos(a_), 0.9, 3.8 * math.sin(a_)])
        cube(f, P, (1.0, 0.5, 0.5), col, 0.4, R=roty(-a_)); tag3d(f, P + [0, 0.75, 0], nm, col, 16)
    for q in range(10):
        ph = (t * 0.6 + q / 10) % 1; a_ = ph * 2 * pi + pi / 4
        ball(f, (3.8 * math.cos(a_), 0.5, 3.8 * math.sin(a_)), 0.09, GREEN if q % 5 == 0 else WHITE, 0.8)
    stars = int(20 * n / 700)
    for q in range(stars): ball(f, ((q % 10 - 4.5) * 0.55, 3.4 + (q // 10) * 0.5, -1.5), 0.13, GOLD, 0.9)
    card(f, 40, 160, 330, 100, 'autoresearch · 2026年3月', f'{n}', '次实验', ACC, a=ease(t / 0.4), vsz=34, note='智能体自己改训练代码，两天跑完')
    if stars: card(f, 920, 160, 300, 92, '找到', f'{stars}', '项改进', GOLD, a=1, vsz=32)
    CH(f); headline(f, lt, ACC, '3', '让智能体自己做研究', None)
    return f


# =====================================================================
# 5 特质一：黑板上的费曼名言 → 从两个标量搭出计算图 → 梯度回流 → 长成网络
# =====================================================================
def sc5(lt, d):
    k = 4; e = EV(k); col = CYAN; cuts = [e[2]]
    if lt < e[2]:
        cam = orbit(0.25 + 0.02 * lt, 9, 2.2, (0, 1.9, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        cube(f, (0, 2.3, -1.2), (6.4, 2.8, 0.12), (110, 90, 60), 0.2)
        cube(f, (0, 2.3, -1.12), (6.0, 2.5, 0.02), (28, 52, 40), 0.3)
        A = ease((lt - e[1]) / 0.6)
        lab(f, (0, 2.8, -1.08), '“我造不出来的东西，', 26, (235, 235, 220), dy=0, a=A)
        lab(f, (0, 2.2, -1.08), '我就不理解。”', 26, (235, 235, 220), dy=0, a=ease((lt - e[1] - 0.6) / 0.6))
        lab(f, (1.6, 1.5, -1.08), '—— 费曼', 18, (200, 200, 190), dy=0, a=ease((lt - e[1] - 1.2) / 0.4))
        figure(f, (-3.6, 0, 0.2), 0.7, 1.0, la=1.3, lo=0.3, le=0.4, ra=0.15)
        CH(f); trait_tag(f, lt, 0)
        return f
    t = lt - e[2]
    cam = orbit(0.1 + 0.02 * t, 10, 2.4, (0, 2, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    ga = pop(t, 0.1); gb = pop(t, 0.4); gm = pop(t, 0.8); gn = pop(t, 1.3)
    ball(f, (-5, 2.8, 0), 0.32 * ga, GOLD, 0.6); ball(f, (-5, 1.2, 0), 0.32 * gb, GOLD, 0.6)
    lab(f, (-5, 3.35, 0), 'a = 2.0', 17, GOLD, a=ga); lab(f, (-5, 0.65, 0), 'b = −3.0', 17, GOLD, dy=20, a=gb)
    cube(f, (-3.4, 2.0, 0), 0.6 * gm, ORANGE, 0.5); lab(f, (-3.4, 2.0, 0.35), '×', 24, WHITE, dy=0, a=gm)
    if gm > 0.5: beam(f, (-4.7, 2.75, 0), (-3.7, 2.1, 0), GOLD); beam(f, (-4.7, 1.25, 0), (-3.7, 1.9, 0), GOLD)
    ball(f, (-1.8, 2.0, 0), 0.42 * gn, col, 0.7); lab(f, (-1.8, 2.75, 0), '神经元 tanh', 16, col, a=gn)
    if gn > 0.5:
        beam(f, (-3.1, 2.0, 0), (-2.25, 2.0, 0), col)
        lab(f, (-3.4, 3.2, 0), 'c = a × b = −6.0', 15, WHITE, a=ease((t - 1.6) / 0.4))
    if t > 2.2:
        flow(f, (-1.8, 2.0, 0), (-3.4, 2.0, 0), lt, RED, 2, 0.9, 0.07)
        flow(f, (-3.4, 2.0, 0), (-5, 2.8, 0), lt + 0.3, RED, 2, 0.9, 0.07)
        flow(f, (-3.4, 2.0, 0), (-5, 1.2, 0), lt + 0.6, RED, 2, 0.9, 0.07)
        lab(f, (-3.4, 0.4, 0), '反向传播：梯度沿计算图回流', 16, RED, dy=20, a=ease((t - 2.2) / 0.4))
    if lt > e[3] - 0.5:
        g = ease((lt - e[3] + 0.5) / 1.0)
        net(f, (2.8, 2.0, 0), [3, 5, 5, 2], (1.0, 0.6), col, g, lt, 0.15, fire=lt * 0.8)
        lab(f, (2.8, 0.2, 0), '最小 · 可读 · 完整', 20, col, dy=20, a=g)
    method(f, lt, e[4], '学新概念，别只会调用 → 自己写一个最小版本', col)
    CH(f); trait_tag(f, lt, 0)
    return f


# =====================================================================
# 6 特质二：讲者 + 视频屏 + 长文 → 光一圈圈传向越来越多的人
# =====================================================================
def sc6(lt, d):
    k = 5; e = EV(k); col = GREEN
    cam = orbit(0.5 + 0.03 * lt, lerp(8, 14, ease(lt / 10)), lerp(2.6, 6, ease(lt / 10)), (0, 1.2, 0), 45)
    f = base(cam, lt, d); floor(f, FL)
    figure(f, (0, 0, 0), 0.5, 1.0, la=0.7 + 0.3 * math.sin(lt * 1.5), lo=0.4, le=0.8, ra=0.6, ro=0.3, re=0.9)
    screen_panel(f, (-1.7, 2.2, -0.6), 1.9, 1.15)
    cube(f, (-1.7, 2.2, -0.55), (0.3, 0.3, 0.02), (240, 60, 60), 0.8); lab(f, (-1.7, 1.45, -0.55), '视频课', 15, WHITE, dy=0)
    cube(f, (1.7, 2.2, -0.6), (1.3, 1.6, 0.05), (235, 232, 222), 0.4)
    for q in range(6): cube(f, (1.7, 2.75 - q * 0.2, -0.56), (1.0 - 0.2 * (q % 3 == 2), 0.06, 0.01), (90, 90, 100), 0.3)
    lab(f, (1.7, 1.25, -0.55), '长文', 15, WHITE, dy=0)
    n = int(170 * ease((lt - e[1]) / 6))
    for i in range(n):
        a_ = i * 2.39996; r = 3.0 + 0.42 * math.sqrt(i)
        lit = ((lt * 1.2 - r * 0.25) % 2) < 0.45
        mini(f, (r * math.cos(a_), 0, r * math.sin(a_)), col if lit else (130, 140, 160), 0.5, 0.5 if lit else 0.12,
             yaw=math.atan2(-math.cos(a_), -math.sin(a_)))
    for q in range(3):
        r = ((lt * 0.6 + q / 3) % 1) * 9
        ring(f, (0, 0.05, 0), r, col, int(160 * (1 - r / 9)), R=I3)
    if e[2] < lt < e[4]: note(f, 640, 220, '“公开地做，而不是守着一个藏不住的秘密”', ease((lt - e[2]) / 0.4), 22, accent=col)
    if e[3] < lt < e[4]: note(f, 640, 470, '讲给别人听 = 最快的自我检验', ease((lt - e[3]) / 0.4), 24, accent=col)
    method(f, lt, e[4], '每学完一样东西 → 写一段笔记，或讲给一个人听', col)
    CH(f); trait_tag(f, lt, 1)
    return f


# =====================================================================
# 7 特质三：人物沿“技术台阶”向上走，vibe coding 被自己划掉，前方还有新台阶
# =====================================================================
STEPS = ['CNN', 'RNN', 'Transformer', 'LLM', 'vibe coding', '智能体工程', '下一个？']
def sc7(lt, d):
    k = 6; e = EV(k); col = PURPLE
    climb = clamp(lt / (e[4] + 0.3)) * 5.0
    j0 = min(int(climb), 5); fr = climb - j0
    cx = (j0 - 3) * 1.7 + fr * 1.7
    cam = orbit(0.55, 11.5, 3.6, (cx * 0.4 + 0.8, 2.0 + j0 * 0.2, 0), 45)
    f = base(cam, lt, d); floor(f, FL)
    for j, nm in enumerate(STEPS):
        x = (j - 3) * 1.7; h = 0.45 + j * 0.55
        last = j == 6
        cube(f, (x, (0.45 + 5 * 0.55) / 2 if last else h / 2, 0), (1.62, 0.45 + 5 * 0.55 if last else h, 2.0), (60, 50, 90) if last else lerp_c(col, (220, 200, 255), j / 6), 0.18 + 0.3 * (j == j0), alpha=120 if last else 255)
        tag3d(f, (x, h + 0.02, 1.0), nm, col if not last else GREY, 17 if j == j0 else 14, 1.0 if not last else 0.7)
        if j == 4 and lt > e[2]:
            sx, sy, _ = f.pt((x, h + 0.02, 1.0)); A2 = ease((lt - e[2]) / 0.4); f.rect(sx - 50 * A2, sy - 2, sx + 50 * A2, sy + 2, (*RED, 255))
    ny = 0.45 + j0 * 0.55 + 0.55 * ease(fr) if j0 < 6 else 0
    figure(f, ((j0 - 3) * 1.7 + fr * 1.7, ny, 0), pi / 2 if fr < 0.98 and lt < e[4] else 0.5, 0.75,
           walk=lt * 7 if lt < e[4] and fr < 0.98 else None)
    if e[1] < lt < e[3]: note(f, 640, 220, '“作为程序员，从来没有感觉这么落后过”', ease((lt - e[1]) / 0.4), 22, accent=col)
    method(f, lt, e[4], '新工具一出现 → 用它做个小项目，而不是只看评测', col)
    CH(f); trait_tag(f, lt, 2)
    return f


def lerp_c(a, b, x): return tuple(int(lerp(a[i], b[i], x)) for i in range(3))


# =====================================================================
# 8 总结：三根柱子依次升起，人物站在中间 → 片尾
# =====================================================================
def sc8(lt, d):
    k = 7; e = EV(k)
    cam = orbit(0.1 * math.sin(lt * 0.3), lerp(10, 11.5, ease(lt / 8)), 2.8, (0, 2, 0), 45)
    f = base(cam, lt, d); floor(f, FL)
    words = [('从零造一遍', '求真懂'), ('公开讲出来', '求想清楚'), ('持续更新', '求不落后')]
    for j in range(3):
        c = TR[j][0]; g = ease((lt - e[1 + j]) / 0.7)
        if g < 0.01: continue
        x = (j - 1) * 3.6; h = 3.0 * g
        cube(f, (x, h / 2, -0.6), (2.4, max(h, 0.02), 1.4), c, 0.4)
        lab(f, (x, h + 0.6, -0.6), words[j][0], 24, WHITE, a=g); lab(f, (x, h + 0.6, -0.6), words[j][1], 18, c, dy=14, a=g)
    figure(f, (4.6, 0, 1.4), -0.4, 0.9, ra=2.6 if lt > e[5] else 0.2, ro=0.3, re=0.3 + 0.4 * math.sin(lt * 6) if lt > e[5] else 0.2)
    if lt > e[4]: note(f, 640, 470, '不需要天赋 · 今天就能开始', ease((lt - e[4]) / 0.4), 26, accent=ACC)
    if lt > e[5]:
        A = ease((lt - e[5]) / 0.5)
        f.rect(390, 530, 890, 584, (*ACC, int(220 * A)), r=10); f.text(640, 557, '人物讲解 · 我们下期见', 26, anc='mm', a=A)
    CH(f); headline(f, lt, ACC, None, '总结')
    return f


FILM = Film(SEG, dur, [sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8], DISP,
            chapters=['开场', '履历', '思想', '作品', '特质一', '特质二', '特质三', '总结'], total=TOTAL, lead=0.15)
