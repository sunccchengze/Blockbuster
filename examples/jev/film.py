"""深度讲解 · Jev：不会说话、只做决定的 System One 模型（约 4 分钟）
信息截至 2026-10-01；来源见 README.md。渲染：python3 -m bb render film.py video.mp4 --jobs 2
"""
from bb.explain import *
import os
HERE = os.path.dirname(os.path.abspath(__file__))
dur, SEG, SUBS, DISP, TOTAL = load_timing(HERE)
def ev(k, i): return SUBS[k][i][0]
def EV(k): return [ev(k, i) for i in range(len(SUBS[k]))]
ACC = TEAL; TAG = 'Jev · TypeSafe AI · 技术拆解'
FL = (90, 220, 200)


def jev_core(f, P, s, lt, glow=0.6):
    """Jev 本体：发光立方核心 + 外框环。"""
    P = np.array(P, float)
    cube(f, P, 1.0 * s, (30, 90, 90), 0.2, R=roty(lt * 0.4))
    cube(f, P, 0.62 * s, ACC, glow + 0.2 * math.sin(lt * 3), R=roty(-lt * 0.6) @ rotx(0.5))
    ring(f, P, 1.05 * s, ACC, 160, R=rotx(pi / 2) @ rotz(lt * 0.3))


def token_chain(f, P, n, col, s=0.42, gap=0.1, emis=0.4):
    for i in range(n): cube(f, (P[0] + i * (s + gap), P[1], P[2]), s, col, emis)


def state_panel(f, P, lines, a=1.0, w=3.2, col=(20, 32, 46)):
    P = np.array(P, float); h = 0.45 * len(lines) + 0.5
    slab(f, P, w, h, col, 0.25, 255 * a)
    for i, s in enumerate(lines):
        lab(f, P + [-w / 2 + 0.25, h / 2 - 0.45 - i * 0.45, 0.1], '', 1)
        f.label(P + [0, h / 2 - 0.5 - i * 0.45, 0.1], s, 16, (190, 235, 225), dx=0, dy=0, a=a, dot=False)


# =====================================================================
# 1 开场：Jev 核心出现 → 候补名单人群涌入 → 文字流熄灭、决策灯亮起
# =====================================================================
def sc1(lt, d):
    k = 0; e = EV(k); cuts = [e[3]]
    if lt < e[3]:
        cam = orbit(0.4 + 0.05 * lt, lerp(9, 12, ease(lt / 8)), 2.5, (0, 1.6, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        jev_core(f, (0, 2.0, 0), pop(lt, 0.3) * 1.2, lt)
        lab(f, (0, 3.6, 0), 'Jev', 40, ACC, a=ease((lt - 0.6) / 0.4))
        card(f, 40, 160, 300, 100, 'TypeSafe AI · 旧金山', '9月15日 发布', '', ACC, a=ease((lt - 0.5) / 0.4), vsz=28, note='9月16日 开发者圈刷屏')
        n = int(140 * ease((lt - e[2]) / 2.2)) if lt > e[2] else 0
        for i in range(n):
            a_ = i * 2.39996; r = 3.2 + 0.18 * math.sqrt(i) * 1.6
            f.mesh(M_PERSON, T=(r * math.cos(a_), 0, r * math.sin(a_)), sc=0.42, col=(150, 175, 185), emis=0.15)
        if lt > e[2]:
            card(f, 900, 160, 340, 100, '36 小时 · 候补名单放行', counter(lt, e[2], e[2] + 2.2, 0, 140000, '{:,.0f}'), '人', ACC, a=ease((lt - e[2]) / 0.4), vsz=32,
                 note='每个小人 ≈ 1000 人')
        chrome_x(f, ACC, TAG, a=ease((lt - 0.3) / 0.5))
        return f
    t = lt - e[3]
    cam = orbit(0.15 * math.sin(t * 0.3), 13, 2.8, (0, 1.6, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    # 左：大模型吐字（被划掉）  右：Jev 一次点亮一个决定
    off = ease((t - 1.6) / 0.6)
    slab(f, (-4, 2, 0), 4.6, 2.6, (26, 30, 44), 0.2)
    m = min(int(t * 6), 18)
    for i in range(m): cube(f, (-5.9 + (i % 9) * 0.48, 2.8 - (i // 9) * 0.6, 0.12), 0.34, (150, 160, 190), 0.3, alpha=255 * (1 - 0.7 * off))
    if off > 0: cube(f, (-4, 2, 0.25), (5.0 * off, 0.12, 0.05), RED, 0.9)
    lab(f, (-4, 0.4, 0), '生成文字', 22, GREY, dy=20)
    jev_core(f, (3.6, 2.2, 0), 0.9, lt)
    for j, (nm, on) in enumerate([('批准', 1), ('拒绝', 0), ('转人工', 0)]):
        g = ease((t - 1.0) / 0.4)
        x = 2.4 + j * 1.2; lit = on and t > 1.8
        cube(f, (x, 0.6, 0.8), (0.9, 0.35, 0.35), GREEN if lit else DARK, 0.9 if lit else 0.15, alpha=255 * g)
        lab(f, (x, 0.6, 0.8), nm, 16, WHITE if lit else DIM, dy=30, a=g)
    lab(f, (3.6, 0, 0.8), '只做决定', 22, ACC, dy=60)
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, None, '不会说话，只会做决定')
    if lt > e[4]: note(f, 640, 560, '今天不谈热度 · 只拆技术', ease((lt - e[4]) / 0.4), 26, accent=ACC)
    return f


# =====================================================================
# 2 System One：快脑（脉冲球）vs 慢脑（token 链）→ Jev 归位 → 杰文斯悖论
# =====================================================================
def sc2(lt, d):
    k = 1; e = EV(k); cuts = [e[5]]
    if lt < e[5]:
        cam = orbit(0.1 * math.sin(lt * 0.25), 13, 3.2, (0, 2.0, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        g1 = ease((lt - e[2]) / 0.5)
        # 系统 1：一闪即答
        P1 = np.array([-3.6, 2.2, 0])
        ball(f, P1, 0.9 * max(g1, 0.3), GOLD, 0.5 + 0.4 * (math.sin(lt * 8) > 0.6))
        for q in range(3):
            r = ((lt * 1.5 + q / 3) % 1) * 2.4
            ring(f, P1, 0.9 + r, GOLD, int(200 * (1 - r / 2.4) * g1), R=I3)
        lab(f, P1 + [0, -1.8, 0], '系统 1 · 快 · 直觉', 22, GOLD, a=g1)
        # 系统 2：逐字推理
        n = int(clamp((lt - e[2]) / 6) * 12) if lt > e[2] else 0
        for i in range(n):
            cube(f, (1.0 + (i % 6) * 0.65, 3.0 - (i // 6) * 0.75, 0), 0.5, PURPLE if lt > e[3] else BLUE, 0.35)
        lab(f, (2.6, 0.8, 0), '系统 2 · 慢 · 推理', 22, PURPLE, a=g1)
        if lt > e[3]: lab(f, (2.6, 4.2, 0), '大语言模型：一个 token 接一个', 18, WHITE, a=ease((lt - e[3]) / 0.4))
        if lt > e[4]:
            A = ease((lt - e[4]) / 0.5)
            jev_core(f, P1 + [0, 0, 1.6], 0.55 * A, lt)
            lab(f, P1 + [0, 1.6, 1.6], 'Jev', 26, ACC, a=A)
        card(f, 40, 160, 300, 96, '类别名', 'System One 模型', '', ACC, a=ease(lt / 0.4), vsz=26, note='典出卡尼曼《思考，快与慢》' if lt > e[1] else None)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '1', '它在做哪一种“思考”', None)
        return f
    t = lt - e[5]
    cam = orbit(-0.2 + 0.03 * t, 12, 3, (0, 2, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    g = ease(t / 1.6)
    f.mesh(M_COIN, R=rotx(pi / 2), T=(-3, 2.2, 0), sc=lerp(1.4, 0.4, g), col=GOLD, emis=0.4)
    lab(f, (-3, 0.4, 0), '单次成本 ↓', 22, GOLD, dy=20)
    for i in range(6):
        h = 0.4 + i * 0.55 * g
        bar_x = 1.0 + i * 0.75
        cube(f, (bar_x, h / 2, 0), (0.55, h, 0.55), ACC, 0.4)
    lab(f, (2.9, 0.0, 0.8), '调用总量 ↑', 22, ACC, dy=40)
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '1', '名字：杰文斯悖论', '越便宜，用得越多')
    return f


# =====================================================================
# 3 接口：state + 类型化问题 → 三种原语 → 并行作答 → 延迟几乎不变
# =====================================================================
QS = [('Choice', '意图是哪一类？', CYAN), ('Score', '客户情绪 1–5', GOLD), ('Noul', '需要退款吗？', GREEN), ('Noul', '有攻击性吗？', GREEN)]
def sc3(lt, d):
    k = 2; e = EV(k); cuts = [e[4], e[7]]
    if lt < e[4]:
        cam = orbit(0.25 + 0.02 * lt, 12, 2.8, (0, 2.2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        A = ease((lt - e[1]) / 0.5)
        state_panel(f, (-3.4, 2.4, 0), ['{ "ticket": 8812,', '  "msg": "收到的杯子碎了",', '  "order": "已签收",', '  "vip": true }'], a=A)
        lab(f, (-3.4, 0.4, 0), '状态 state · 文本 / JSON', 20, ACC, dy=20, a=A)
        for j, (ty, q, col) in enumerate(QS):
            g = pop(lt, e[2] + j * 0.25)
            P = (3.2, 3.8 - j * 0.95, 0)
            slab(f, P, 3.4 * g, 0.7 * g, (24, 30, 46), 0.25)
            cube(f, (1.7, P[1], 0.1), (0.3 * g, 0.7 * g, 0.1), col, 0.8)
            lab(f, (3.3, P[1], 0.15), f'{ty}：{q}', 16, WHITE, dy=0, a=g)
        if lt > e[3]: note(f, 640, 560, '问题只有三种原语', ease((lt - e[3]) / 0.4), 24, accent=ACC)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '2', '接口：一段状态 + 一组带类型的问题', None)
        return f
    if lt < e[7]:
        t = lt - e[4]
        cam = orbit(0.1 * math.sin(t * 0.3), 13, 3.5, (0, 2.0, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        # Choice：最多 255 个选项的分布（展示 24 根）
        gC = ease(t / 0.6)
        vals = [0.05 + 0.04 * ((i * 7) % 5) for i in range(24)]; vals[9] = 0.95
        bars(f, (-4.4, 0.3, 0), vals, [CYAN if i == 9 else (60, 90, 120) for i in range(24)], w=0.12, gap=0.04, hmax=2.6, g=gC)
        lab(f, (-4.4, 0, 0.6), 'Choice · ≤255 选项', 20, CYAN, dy=36, a=gC)
        # Score：10 级量表，加权平均指针
        gS = ease((lt - e[5]) / 0.6)
        pS = [0.02, 0.04, 0.08, 0.16, 0.3, 0.24, 0.1, 0.04, 0.01, 0.01]
        xs = bars(f, (0, 0.3, 0), pS, GOLD, w=0.25, gap=0.07, hmax=6, g=gS)
        mean = sum((i + 1) * p for i, p in enumerate(pS)); xm = lerp(xs[0], xs[-1], (mean - 1) / 9)
        if gS > 0.5: cube(f, (xm, 2.6, 0), (0.05, 0.6, 0.05), WHITE, 0.9); lab(f, (xm, 3.0, 0), f'加权平均 {mean:.1f}', 16, GOLD, a=gS)
        lab(f, (0, 0, 0.6), 'Score · 2–10 级', 20, GOLD, dy=36, a=gS)
        # Noul：是的概率
        gN = ease((lt - e[6]) / 0.6)
        cube(f, (4.4, 1.5, 0), (0.7, 2.4, 0.7), DARK, 0.1, alpha=255 * gN)
        hY = 2.4 * 0.81 * gN; cube(f, (4.4, 0.3 + hY / 2, 0.05), (0.72, hY, 0.72), GREEN, 0.5)
        lab(f, (4.4, 3.1, 0), 'P(是) = 0.81', 18, GREEN, a=gN)
        lab(f, (4.4, 0, 0.6), 'Noul · 是/否', 20, GREEN, dy=36, a=gN)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '2', '三种原语', '返回的都是概率，不是一段文字')
        return f
    t = lt - e[7]
    cam = orbit(0.35 + 0.03 * t, 13, 3, (0, 2.2, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    S = np.array([-4.2, 2.2, 0]); slab(f, S, 2, 2.6, (20, 32, 46), 0.3); lab(f, S + [0, 1.7, 0], 'state', 20, ACC)
    nq = 8
    for j in range(nq):
        P = np.array([2.0, 4.0 - j * 0.55, 0])
        cube(f, P, (1.6, 0.4, 0.3), QS[j % 4][2], 0.3 + 0.4 * (((t * 2) % 1) < 0.5))
        beam(f, S + [1, 0, 0], P - [0.8, 0, 0], ACC, 90, 2); flow(f, S + [1, 0, 0], P - [0.8, 0, 0], t, ACC, 2, 1.2, 0.06)
    lab(f, (2.0, 0.0, 0), '彼此隔离 · 同时作答', 20, WHITE, dy=20)
    if lt > e[8]:
        A = ease((lt - e[8]) / 0.4)
        f.rect(880, 380, 1240, 560, (10, 14, 26, int(210 * A)), r=10)
        f.text(1060, 400, '问题数 → 延迟（示意）', 17, a=A, anc='mm')
        for i in range(8):
            h_j = 18 + 2 * i; h_l = 18 + 16 * i
            x = 910 + i * 40
            f.rect(x, 540 - h_l * A, x + 14, 540, (*PURPLE, int(170 * A)), r=2)
            f.rect(x + 16, 540 - h_j * A, x + 30, 540, (*ACC, int(240 * A)), r=2)
        f.text(915, 425, '■ Jev', 15, col=ACC, a=A, bold=False); f.text(1000, 425, '■ 逐个问大模型', 15, col=PURPLE, a=A, bold=False)
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '2', '并行：多问几个，延迟几乎不变', None)
    return f


# =====================================================================
# 4 出答案的方式：逐 token 生成 vs 一次给出分布 → 价格 → 赛跑
# =====================================================================
def sc4(lt, d):
    k = 3; e = EV(k); cuts = [e[3], e[6]]
    if lt < e[3]:
        cam = orbit(0.1 * math.sin(lt * 0.3), 13, 3.2, (0, 2.2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        # 上排：大模型逐 token
        tL = lt - e[1]
        n = int(clamp(tL / 4.5) * 10) if tL > 0 else 0
        cube(f, (-6, 3.4, 0), 1.0, (90, 100, 140), 0.3)
        lab(f, (-6, 4.2, 0), '大模型', 18, GREY)
        token_chain(f, (-5, 3.4, 0), n, BLUE, 0.42, 0.12)
        if n >= 10: cube(f, (1.2, 3.4, 0), (0.9, 0.9, 0.9), (200, 140, 60), 0.5); lab(f, (1.2, 4.2, 0), '解析 JSON', 16, GOLD)
        lab(f, (-2.5, 2.5, 0), '{ "intent": "退款", ... } 一个 token 一个 token', 16, DIM, a=ease(tL / 0.4))
        # 下排：Jev 一次出完整分布
        tR = lt - e[2]
        jev_core(f, (-6, 0.9, 0), 0.5, lt)
        if tR > 0:
            g = pop(tR, 0, 0.4)
            ring(f, (-6, 0.9, 0), 0.6 + tR * 3 if tR < 0.6 else 0.6, ACC, int(255 * clamp(1 - tR / 0.6)))
            bars(f, (-2.6, 0.2, 0), [0.08, 0.72, 0.12, 0.05, 0.03], [DARK, ACC, DARK, DARK, DARK], w=0.6, gap=0.2, hmax=2, g=g)
            lab(f, (-2.6, 0, 0.6), '一次计算 → 整个概率分布', 18, ACC, dy=30, a=g)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '3', '关键区别：怎么出答案', None)
        return f
    if lt < e[6]:
        t = lt - e[3]
        cam = orbit(0.3 + 0.03 * t, 11, 2.5, (0, 1.8, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        for j in range(5):
            f.mesh(M_COIN, R=rotx(pi / 2) @ rotz(0), T=(-3.5, 0.3 + j * 0.2, 0), sc=0.6, col=GOLD, emis=0.3)
        lab(f, (-3.5, 2, 0), '输入', 22, GOLD)
        jev_core(f, (0, 1.8, 0), 0.6, lt)
        flow(f, (-3.0, 1.0, 0), (-0.6, 1.8, 0), t, GOLD, 3, 0.8, 0.1)
        flow(f, (0.6, 1.8, 0), (3.5, 1.0, 0), t, ACC, 3, 0.8, 0.1)
        lab(f, (3.5, 1.6, 0), '输出：$0', 26, GREEN, a=ease(t / 0.4))
        card(f, 40, 160, 320, 100, '输入价格', '$0.042', '/ 百万 token', GOLD, a=ease((lt - e[4]) / 0.4), vsz=34)
        card(f, 920, 160, 320, 100, '端到端延迟', '70–500', '毫秒', ACC, a=ease((lt - e[5]) / 0.4), vsz=34)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '3', '不逐字生成 → 输出不收费', None)
        return f
    t = lt - e[6]
    cam = orbit(0.55, 14, 4.5, (0, 0.5, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    # 赛跑：同一问题。时间压缩：动画 1 秒 = 2 秒
    clock = t * 2.0
    for j, (nm, tt, col, z) in enumerate([('Jev', 0.114, ACC, -1.2), ('GPT-5.6 Terra', 8.566, PURPLE, 1.2)]):
        prog_ = clamp(clock / tt)
        cube(f, (0, 0.05, z), (12, 0.1, 1.2), DARK, 0.1)
        x = -6 + 12 * prog_
        cube(f, (x, 0.5, z), 0.8, col, 0.6)
        lab(f, (-6.5, 0.3, z), nm, 20, col, dy=0)
        if prog_ >= 1: lab(f, (6.6, 1.2, z), f'{tt:.3f} 秒' if tt < 1 else f'{tt:.1f} 秒', 24, col)
    f.text(1180, 160, f'{min(clock, 9.0):.1f} s', 30, anc='rm', a=1)
    note(f, 640, 560, '官方演示 · 同一个问题', 0.9, 22, accent=ACC)
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '3', '0.11 秒 vs 8.6 秒', '数据来自 TypeSafe 官方演示')
    return f


# =====================================================================
# 5 RLCD：三条训练路线 → 校准曲线 → 分布形状 = 置信度 → 三档闸门
# =====================================================================
def sc5(lt, d):
    k = 4; e = EV(k); cuts = [e[2], e[3], e[5]]
    if lt < e[2]:
        cam = orbit(0.2 * math.sin(lt * 0.2), 13, 3, (0, 2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        for j, (nm, out, col, t0) in enumerate([('RLHF', '聊天机器人', BLUE, e[1]), ('RLVR', '推理模型', PURPLE, e[1] + 1.2), ('RLCD', '校准决策', ACC, 0.3)]):
            x = (j - 1) * 4.2; g = pop(lt, t0)
            cube(f, (x, 1.2 * g, 0), (2.6, 2.4 * g, 1.2), col, 0.35 + 0.25 * (j == 2))
            lab(f, (x, 1.4, 0.7), nm, 30, WHITE, a=g)
            lab(f, (x, 0, 0.7), '→ ' + out, 20, col, dy=40, a=g)
        card(f, 40, 160, 330, 96, '训练方法', 'RLCD', '', ACC, a=ease(lt / 0.4), vsz=32, note='Reinforcement Learning for Calibrated Decisions')
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '4', '第三条训练路线', None)
        return f
    if lt < e[3]:
        t = lt - e[2]
        cam = orbit(0.0, 11, 2.0, (0, 2.6, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        # 校准图：x = 模型给的概率，y = 实际正确率
        O = np.array([-3, 0.4, 0]); L = 5.2
        f.line([O, O + [L, 0, 0]], (*WHITE, 200), 3); f.line([O, O + [0, L, 0]], (*WHITE, 200), 3)
        f.line([O, O + [L, L, 0]], (*ACC, 120), 2)
        g = ease(t / 2.5)
        for i in range(10):
            p = (i + 0.5) / 10; q = p + 0.03 * math.sin(i * 2.1)
            if i / 10 < g: ball(f, O + [L * p, L * q, 0], 0.14, ACC, 0.8)
        pt = O + [L * 0.8, L * 0.8, 0]
        if t > 1.5:
            A = ease((t - 1.5) / 0.4)
            f.line([O + [L * 0.8, 0, 0], pt], (*GOLD, int(200 * A)), 2); f.line([O + [0, L * 0.8, 0], pt], (*GOLD, int(200 * A)), 2)
            lab(f, pt + [0.4, 0.4, 0], '说 80% → 真的 8 成正确', 20, GOLD, a=A)
        lab(f, O + [L / 2, 0, 0], '模型给出的概率', 18, DIM, dy=30); lab(f, O + [-0.3, L + 0.3, 0], '实际正确率', 18, DIM)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '4', '目标：校准', None)
        return f
    if lt < e[5]:
        t = lt - e[3]
        cam = orbit(0.2 + 0.02 * t, 12, 3, (0, 2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        g = ease(t / 0.6)
        bars(f, (-3.4, 0.2, 0), [0.03, 0.06, 0.82, 0.06, 0.03], [DARK, DARK, ACC, DARK, DARK], w=0.5, gap=0.15, hmax=3, g=g)
        bars(f, (3.4, 0.2, 0), [0.22, 0.18, 0.24, 0.2, 0.16], [GREY] * 5, w=0.5, gap=0.15, hmax=3, g=g)
        g2 = ease((lt - e[4]) / 0.5)
        lab(f, (-3.4, 3.4, 0), '集中 → 置信度高 0.91', 22, GREEN, a=g2); lab(f, (3.4, 3.4, 0), '平坦 → 置信度低 0.12', 22, RED, a=g2)
        note(f, 640, 560, '置信度 = 从分布形状计算，不是模型“自报”', ease(t / 0.4), 22, accent=ACC)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '4', '置信度从哪来', None)
        return f
    t = lt - e[5]
    cam = orbit(0.45 + 0.02 * t, 14, 5, (0, 0.8, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    jev_core(f, (-5, 1.2, 0), 0.6, lt)
    lanes = [('高置信 → 自动执行', GREEN, -2.2), ('中间 → 请人确认', GOLD, 0), ('低置信 → 交给人 / 推理模型', RED, 2.2)]
    for j, (nm, col, z) in enumerate(lanes):
        cube(f, (2, 0.05, z), (8, 0.1, 1.4), col, 0.25, alpha=200)
        lab(f, (6.5, 0.3, z), nm, 18, col, dy=-20)
    for q in range(9):
        ph = (t * 0.35 + q / 9) % 1; lane = [0, 0, 1, 0, 2, 0, 1, 0, 0][q]; z = lanes[lane][2]
        x = lerp(-4.2, 6, ph); zz = lerp(0, z, ease((x + 4.2) / 3))
        ball(f, (x, 0.45, zz), 0.25, lanes[lane][1], 0.6)
    if lt > e[6]: stamp(f, 1040, 190, '尚无公开论文 · 细节无法核实', ease((lt - e[6]) / 0.4), GOLD, 22)
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '4', '按置信度分流', None)
    return f


# =====================================================================
# 6 “零幻觉”：答案一定落在类型槽里，但可能落错 → 准确率柱 → 时间对比 → 性价比前沿
# =====================================================================
MODELS = [('Jev', 67.8, 0.4, 0.0004, ACC), ('GPT-5.6 Terra', 67.9, 10.1, 0.0304, PURPLE), ('Claude Sonnet 5', 67.8, 78.1, 0.1174, ORANGE), ('GPT-5.6 Sol', 74.1, 23.3, 0.0836, BLUE)]
def sc6(lt, d):
    k = 5; e = EV(k); cuts = [e[3], e[6], e[8]]
    if lt < e[3]:
        cam = orbit(0.3 + 0.02 * lt, 11, 4, (0, 1.2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        slots = [('退款', -2.4), ('换货', 0), ('转人工', 2.4)]
        for nm, x in slots:
            cube(f, (x, 0.2, 0), (1.8, 0.4, 1.8), (40, 60, 70), 0.2); lab(f, (x, 0, 1.2), nm, 20, WHITE, dy=30)
        t = lt - e[1]
        if t > 0:
            ph = clamp(t / 1.2); P = np.array([lerp(0, 2.4, ph), 4 - 3.4 * ease(ph), 0])
            wrong = lt > e[2]
            ball(f, P, 0.35, RED if wrong else GREEN, 0.7)
            if ph >= 1: lab(f, (2.4, 1.6, 0), '格式永远正确 ✓', 20, GREEN, a=1)
            if wrong: lab(f, (2.4, 2.4, 0), '但正确答案其实是“退款”', 20, RED, a=ease((lt - e[2]) / 0.4)); ring(f, (-2.4, 0.5, 0), 1.2, GREEN, 200, R=rotx(pi / 2))
        stamp(f, 1050, 190, '“零幻觉”', ease(lt / 0.4), GOLD, 28)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '5', '“零幻觉”的真实含义', '只保证类型正确，不保证答对')
        return f
    if lt < e[6]:
        t = lt - e[3]
        cam = orbit(-0.25 + 0.02 * t, 13, 3.5, (0, 2.2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        for j, (nm, acc, _, _, col) in enumerate(MODELS):
            t0 = 0 if j == 0 else (e[4] if j < 3 else e[5]) - e[3]
            g = ease((t - t0) / 0.8); x = (j - 1.5) * 2.8; h = (acc - 50) / 5 * g
            cube(f, (x, h / 2, 0), (1.8, max(h, 0.02), 1.4), col, 0.5 if j == 0 else 0.3)
            lab(f, (x, h + 0.4, 0), f'{acc:.1f}%', 22, WHITE, a=g); lab(f, (x, 0, 1), nm, 17, col, dy=36, a=g)
        lab(f, (-6, 0, 0), '纵轴从 50% 起', 14, DIM, dy=20)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '5', '官方四个工作流评测 · 平均准确率', '参考标签由 GPT-6 Astra 与 Claude Fable 5.1 给出')
        return f
    if lt < e[8]:
        t = lt - e[6]
        cam = orbit(0.4, 14, 4.5, (0, 0.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        clock = t * 12   # 动画 1 秒 = 12 秒
        for j, (nm, _, tt, cost, col) in enumerate([MODELS[0], MODELS[2]]):
            z = -1.2 + j * 2.4; p = clamp(clock / tt)
            cube(f, (0, 0.05, z), (12, 0.1, 1.2), DARK, 0.1); cube(f, (-6 + 12 * p, 0.5, z), 0.8, col, 0.6)
            lab(f, (-6.5, 0.3, z), nm, 20, col, dy=0)
            if p >= 1: lab(f, (6.4, 1.3, z), f'{tt} 秒 · ${cost}', 22, col)
        f.text(1180, 160, f'{min(clock, 80):.0f} s', 30, anc='rm')
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '5', '同样准确率：0.4 秒 vs 78 秒', '每个案例 · 时间轴已加速')
        return f
    t = lt - e[8]
    cam = orbit(0.0, 11, 2.0, (0, 2.6, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    O = np.array([-4, 0.4, 0]); W, H = 8, 4.4
    f.line([O, O + [W, 0, 0]], (*WHITE, 200), 3); f.line([O, O + [0, H, 0]], (*WHITE, 200), 3)
    for j, (nm, acc, _, cost, col) in enumerate(MODELS):
        x = (math.log10(cost) + 4) / 3.2 * W; y = (acc - 60) / 16 * H
        g = pop(t, j * 0.15); ball(f, O + [x, y, 0], 0.25 * g, col, 0.7); lab(f, O + [x, y + 0.5, 0], nm, 16, col, a=g)
    lab(f, O + [W / 2, 0, 0], '每案例成本（对数）→', 17, DIM, dy=30); lab(f, O + [0, H + 0.3, 0], '准确率 ↑', 17, DIM)
    note(f, 640, 560, '卖点是性价比，不是最准', ease(t / 0.4), 26, accent=ACC)
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '5', '性价比前沿', None)
    return f


# =====================================================================
# 7 参差能力：起伏的能力地形 + 弱项坑 → 退款 0.72 / 不退款 0.47
# =====================================================================
WEAK = [('数数', 1), ('算术 · 日期', 1), ('双重否定', 2), ('上下文腐烂', 3), ('提示注入', 4)]
def sc7(lt, d):
    k = 6; e = EV(k); cuts = [e[5]]
    if lt < e[5]:
        cam = orbit(0.35 + 0.02 * lt, 14, 5, (0, 1.2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        hs = [3.2, 0.7, 3.0, 2.8, 0.8, 3.4, 1.0, 2.9, 0.9, 3.1, 0.6, 3.3]
        lows = {1: 1, 4: 2, 6: 3, 8: 4, 10: 5}   # 柱索引 → 第几句出现
        for i, h in enumerate(hs):
            x = (i - 5.5) * 1.05
            weak = i in lows; show = (not weak) or lt > e[lows[i]] - 0.2
            hh = h if show else 2.9
            col = RED if weak and show else ACC
            cube(f, (x, hh / 2, 0), (0.9, hh, 0.9), col, 0.45 if weak and show else 0.3)
        for (i, si), (nm, _) in zip(lows.items(), WEAK):
            if lt > e[si]: lab(f, ((i - 5.5) * 1.05, hs[i] + 0.4, 0), nm, 18, RED, a=ease((lt - e[si]) / 0.4))
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '6', '官方公开的“参差能力”清单', '强项和弱项交错（示意）')
        return f
    t = lt - e[5]
    cam = orbit(0.1 * math.sin(t * 0.4), 11, 2.5, (0, 2.0, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    for j, (q, p, col) in enumerate([('想要退款？', 0.72, GREEN), ('不想要退款？', 0.47, ORANGE)]):
        x = -2.4 + j * 4.8; g = ease((lt - e[6] - j * 0.5) / 0.7) if lt > e[6] else 0
        cube(f, (x, 1.8, 0), (1.2, 3.2, 1.2), DARK, 0.1, alpha=200)
        h = 3.2 * p * g; cube(f, (x, 0.2 + h / 2, 0.05), (1.22, h, 1.22), col, 0.5)
        lab(f, (x, 3.8, 0), f'{q}  {p * g:.2f}', 22, col, a=ease(t / 0.4))
    if lt > e[6] + 1.4:
        A = ease((lt - e[6] - 1.4) / 0.4)
        note(f, 640, 560, '0.72 + 0.47 = 1.19 > 1  → 互相矛盾', A, 26, RED, accent=RED)
    lab(f, (0, 0, 1.5), '同一张工单', 20, DIM, dy=30)
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '6', '逻辑相关的问题可能不一致', None)
    return f


# =====================================================================
# 8 定位：大模型旁边的“聪明 if” → pi-warden 守卫编程智能体 → 片尾
# =====================================================================
WQ = ['不可逆？', '跑题？', '改动文件？', '影响范围？']
def sc8(lt, d):
    k = 7; e = EV(k); cuts = [e[1], e[4]]
    if lt < e[1]:
        cam = orbit(0.3 + 0.03 * lt, 12, 3.5, (0, 1.6, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        cube(f, (-3, 2.0, 0), 2.6, (90, 100, 150), 0.25, R=roty(0.3)); lab(f, (-3, 3.8, 0), '大模型', 24, (170, 180, 230))
        jev_core(f, (1.6, 1.2, 0), 0.7, lt); lab(f, (1.6, 2.5, 0), 'if (Jev …)', 24, ACC)
        flow(f, (-1.4, 2.0, 0), (1.0, 1.2, 0), lt, BLUE, 3, 0.9, 0.1)
        for j, col in enumerate([GREEN, GOLD, RED]):
            P = (5, 2.4 - j * 1.0, 0); beam(f, (2.3, 1.2, 0), P, col, 120); cube(f, P, 0.5, col, 0.6)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, None, '定位：大模型旁边的“聪明 if 语句”', '路由 · 守卫 · 打分')
        return f
    if lt < e[4]:
        t = lt - e[1]
        cam = orbit(0.45 + 0.02 * t, 13, 4, (0, 1.2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        cube(f, (-5, 1.2, 0), 1.6, (90, 100, 150), 0.3); lab(f, (-5, 2.4, 0), '编程智能体', 20, (170, 180, 230))
        cube(f, (0, 1.5, 0), (0.3, 3, 3), ACC, 0.4, alpha=150); lab(f, (0, 3.4, 0), 'pi-warden', 22, ACC)
        cmds = ['ls src/', 'npm test', 'rm -rf /', 'git diff']
        for q in range(4):
            ph = (t * 0.3 + q / 4) % 1; bad = cmds[q].startswith('rm')
            x = lerp(-4, 5, ph) if not bad else lerp(-4, -0.4, min(ph * 2, 1))
            cube(f, (x, 0.6, -1 + q * 0.6), (1.4, 0.35, 0.35), RED if bad and ph > 0.45 else (150, 180, 200), 0.5)
            lab(f, (x, 0.6, -1 + q * 0.6), cmds[q], 14, WHITE, dy=-18)
        for j, q in enumerate(WQ):
            g = ease((lt - e[2] - j * 0.3) / 0.3)
            f.rect(900, 170 + j * 50, 1240, 210 + j * 50, (10, 16, 30, int(210 * g)), r=8, outline=(*ACC, int(150 * g)))
            f.text(920, 190 + j * 50, f'Q{j + 1}  {q}', 18, a=g, anc='lm')
        if lt > e[3]: card(f, 900, 390, 340, 92, '4 个问题并行', '≈ 250', '毫秒 决定拦不拦', ACC, a=ease((lt - e[3]) / 0.4), vsz=30)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, None, '例子：给编程智能体装闸门', None)
        return f
    t = lt - e[4]
    cam = orbit(0.2 + 0.05 * t, lerp(8, 10, ease(t / 6)), 2, (0, 1.6, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    jev_core(f, (0, 1.8, 0), 1.0, lt)
    stamp(f, 640, 200, '多为官方自测 · 尚无独立复现', ease(t / 0.4), GOLD, 22)
    if lt > e[5]:
        A = ease((lt - e[5]) / 0.5)
        f.rect(340, 540, 940, 600, (*ACC, int(220 * A)), r=10)
        f.text(640, 570, '让模型少说话，多做决定', 30, anc='mm', a=A)
    chrome_x(f, ACC, TAG)
    return f


FILM = Film(SEG, dur, [sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8], DISP,
            chapters=['开场', 'System One', '接口', '速度与价格', 'RLCD', '准确率', '局限', '定位'], total=TOTAL, lead=0.15)
