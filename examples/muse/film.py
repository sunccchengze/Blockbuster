"""深度讲解 · Meta Muse：个人智能体的技术架构（约 3 分 50 秒）
信息截至 2026-10-01；来源见 README.md。渲染：python3 -m bb render film.py video.mp4 --jobs 4
"""
from bb.explain import *
import os
HERE = os.path.dirname(os.path.abspath(__file__))
dur, SEG, SUBS, DISP, TOTAL = load_timing(HERE)
def ev(k, i): return SUBS[k][i][0]
def EV(k): return [ev(k, i) for i in range(len(SUBS[k]))]
ACC = (60, 130, 255); TAG = 'Meta Muse · 个人智能体 · 技术拆解'
FL = (90, 140, 255); SENT = (255, 170, 60); MUSE = (120, 170, 255)


def muse_orb(f, P, s, lt, col=MUSE):
    P = np.array(P, float)
    ball(f, P, 0.55 * s, col, 0.6 + 0.2 * math.sin(lt * 3))
    ring(f, P, 0.85 * s, col, 170, R=rotx(1.2) @ rotz(lt * 0.8))
    ring(f, P, 0.95 * s, col, 120, R=rotz(0.7) @ rotx(lt * 0.5))


def spark_chip(f, P, s, lt):
    """芯片：封装基板 + 引脚 + 发光晶粒 + 晶粒网格；各部件上下堆叠，不相交。"""
    P = np.array(P, float); R = roty(lt * 0.25)
    def at(v): return P + R @ (np.array(v) * s)
    cube(f, at([0, 0, 0]), (2.4 * s, 0.24 * s, 2.4 * s), (34, 38, 52), 0.15, R=R)
    for q in range(8):
        u = -1.05 + q * 0.3
        for v in [(u, -1.28), (u, 1.28), (-1.28, u), (1.28, u)]:
            cube(f, at([v[0], -0.04, v[1]]), (0.12 * s, 0.06 * s, 0.16 * s) if abs(v[1]) > 1.2 else (0.16 * s, 0.06 * s, 0.12 * s), (200, 180, 120), 0.3, R=R)
    cube(f, at([0, 0.18, 0]), (1.5 * s, 0.12 * s, 1.5 * s), (70, 50, 140), 0.35, R=R)
    cube(f, at([0, 0.25, 0]), (1.3 * s, 0.02 * s, 1.3 * s), PURPLE, 0.7 + 0.2 * math.sin(lt * 3), R=R)
    for q in range(5):
        u = -0.52 + q * 0.26
        f.line([at([u, 0.27, -0.65]), at([u, 0.27, 0.65])], (220, 200, 255, 150), 1)
        f.line([at([-0.65, 0.27, u]), at([0.65, 0.27, u])], (220, 200, 255, 150), 1)
    for q in range(2):
        rr = ((lt * 0.7 + q / 2) % 1)
        ring(f, at([0, 0.3 + rr * 1.2, 0]), (0.9 + rr * 0.6) * s, PURPLE, int(160 * (1 - rr)), R=I3)


def sentinel(f, P, s, lt):
    P = np.array(P, float)
    f.mesh(shield(1.2 * s, 1.5 * s, SENT), T=P, R=roty(0.3 * math.sin(lt)), emis=0.45)


def phone(f, P, s=1.0, on=1.0, R=I3):
    P = np.array(P, float)
    cube(f, P, (1.1 * s, 2.1 * s, 0.12), (30, 34, 44), 0.15, R=R)
    cube(f, P + R @ np.array([0, 0, 0.07]), (0.95 * s, 1.85 * s, 0.02), lerp_col((10, 12, 18), (40, 80, 160), on), 0.6 * on, R=R)


def lerp_col(a, b, x): return tuple(int(lerp(a[i], b[i], x)) for i in range(3))


def vm_box(f, P, w, h, dd, col, a=90, label=None, lsz=20, fill=True):
    P = np.array(P, float)
    cube(f, P + [0, -h / 2, 0], (w, 0.08, dd), col, 0.5)
    for sx in (-1, 1):
        for sz in (-1, 1):
            cube(f, P + [sx * w / 2, 0, sz * dd / 2], (0.06, h, 0.06), col, 0.7)
    if a: cube(f, P + [0, h / 2, 0], (w, 0.04, dd), col, 0.5, alpha=a)
    if fill: cube(f, P, (w, h, dd), col, 0.1, alpha=40)
    if label: lab(f, P + [0, h / 2 + 0.35, 0], label, lsz, col)


# =====================================================================
# 1 开场：手机里的 Muse → 免费榜第一
# =====================================================================
def sc1(lt, d):
    k = 0; e = EV(k)
    cam = orbit(0.3 + 0.05 * lt, lerp(7, 10, ease(lt / 6)), 2.0, (0, 1.6, 0), 45)
    f = base(cam, lt, d); floor(f, FL)
    phone(f, (-1.6, 1.8, 0), 1.3 * pop(lt, 0.2), on=ease((lt - 0.5) / 0.5), R=roty(0.25))
    muse_orb(f, (1.6, 2.0, 0), pop(lt, 0.8), lt)
    lab(f, (1.6, 3.2, 0), 'Muse', 40, MUSE, a=ease((lt - 1) / 0.4))
    card(f, 40, 160, 330, 100, 'Meta 超级智能实验室 · 9月8日', 'Muse 发布', '', ACC, a=ease((lt - 0.4) / 0.4), vsz=30, note='“第一个面向所有人的个人智能体”' if lt > e[1] else None)
    if lt > e[2]:
        rank = max(1, int(lerp(48, 1, ease((lt - e[2]) / 2.0))))
        card(f, 920, 160, 320, 100, '美区 App Store 免费榜 · 约一周后', f'#{rank}', '', GOLD, a=ease((lt - e[2]) / 0.4), vsz=40)
    if lt > e[3]: note(f, 640, 560, '今天只拆技术', ease((lt - e[3]) / 0.4), 26, accent=ACC)
    chrome_x(f, ACC, TAG, a=ease((lt - 0.3) / 0.5))
    return f


# =====================================================================
# 2 是什么：发消息 → 计划 → 浏览器填表 → 关掉手机仍在干活 → 记忆 → 价格
# =====================================================================
def sc2(lt, d):
    k = 1; e = EV(k); cuts = [e[3], e[5]]
    if lt < e[3]:
        cam = orbit(0.22 + 0.02 * lt, 9.5, 2.6, (-0.6, 2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        f.mesh(M_PERSON, T=(-5.5, 0, 0), sc=1.1, col=(180, 190, 210), emis=0.2)
        t1 = lt - e[1]
        if t1 > 0:
            ph = clamp(t1 / 1.2); P = np.array([lerp(-4.8, -3.6, ph), lerp(2.4, 3.3, ph), 0])
            slab(f, P, 1.6, 0.6, ACC, 0.5); lab(f, P + [0, 0, 0.1], '订周六两人餐厅', 14, WHITE, dy=0)
        muse_orb(f, (-1.5, 1.6, 0), 0.8, lt)
        steps = ['① 查评价', '② 比较时段', '③ 填预订表', '④ 发确认']
        ox, oy, _ = f.pt((-1.5, 1.6, 0))
        for j, s_ in enumerate(steps):
            g = ease((t1 - 1.2 - j * 0.4) / 0.3) * (1 - ease((lt - e[2]) / 0.5))
            if g > 0.01:
                y = oy - 150 + j * 40
                f.rect(ox + 70, y - 16, ox + 210, y + 16, (20, 30, 54, int(225 * g)), r=7, outline=(*ACC, int(160 * g)))
                f.text(ox + 82, y, s_, 16, col=(215, 228, 255), a=g, anc='lm')
        # 浏览器窗口：表单逐格填满
        tb = lt - e[2]
        slab(f, (2.6, 2.0, 0), 3.4, 2.6, (230, 234, 242), 0.35, 255 * ease(tb / 0.4) if tb > 0 else 0)
        if tb > 0:
            cube(f, (2.6, 3.15, 0.08), (3.4, 0.3, 0.04), (60, 70, 90), 0.3)
            for j in range(4):
                fill = clamp((tb - 0.6 - j * 0.6) / 0.5)
                cube(f, (2.6, 2.6 - j * 0.55, 0.08), (2.8, 0.34, 0.04), (200, 205, 215), 0.3)
                if fill > 0: cube(f, (1.2 + 1.4 * fill * 0.9, 2.6 - j * 0.55, 0.11), (2.8 * fill * 0.9, 0.2, 0.04), ACC, 0.5)
            lab(f, (2.6, 0.4, 0), '打开浏览器 · 填表 · 讨价还价', 18, ACC, dy=20)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '1', '不是聊天机器人，是会主动做事的智能体', None)
        return f
    if lt < e[5]:
        t = lt - e[3]
        cam = orbit(0.4 + 0.02 * t, 12, 3.5, (0, 2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        off = ease((t - 0.4) / 0.6); back = ease((t - 3.2) / 0.4)
        phone(f, (-3.5, 1.6, 0), 1.2, on=max(1 - off, back))
        lab(f, (-3.5, 0, 0), '应用已关闭' if back < 0.5 else '需要你批准', 20, GREY if back < 0.5 else GOLD, dy=30)
        # 云端继续干活
        vm_box(f, (2.5, 2.2, 0), 3.6, 2.6, 2.4, ACC, label='云端')
        muse_orb(f, (2.5, 2.2, 0), 0.7, lt)
        prog_ = clamp(t / 3.2)
        cube(f, (2.5, 0.5, 1.3), (3.0, 0.15, 0.1), DARK, 0.1); cube(f, (1.0 + 1.5 * prog_, 0.5, 1.35), (3.0 * prog_, 0.17, 0.1), GREEN, 0.6)
        if back > 0: flow(f, (1.0, 2.2, 0), (-2.8, 1.8, 0), t, GOLD, 3, 1.0, 0.1)
        if lt > e[4]:
            A = ease((lt - e[4]) / 0.4)
            for j, m in enumerate(['不吃香菜', '周六有空', '预算 ¥300']):
                f.label((2.5 + (j - 1) * 1.4, 4.4 + 0.15 * math.sin(lt + j), 0), m, 16, GOLD, dx=0, dy=0, a=A, dot=False)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '1', '关掉应用，它仍在后台工作', '还会记住你随口提过的细节')
        return f
    t = lt - e[5]
    cam = orbit(0.1 * math.sin(t * 0.3), 11, 2.5, (0, 1.6, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    for j, (nm, p, col) in enumerate([('免费版', 0, GREY), ('$20 / 月', 20, ACC), ('$100 / 月', 100, GOLD)]):
        x = (j - 1) * 3.2; g = pop(t, j * 0.25); h = 0.6 + p / 100 * 2.6
        cube(f, (x, h / 2 * g, 0), (2.2, h * g, 1.4), col, 0.35)
        lab(f, (x, h + 0.4, 0), nm, 24, WHITE, a=g)
    lab(f, (0, 0, 1.5), '无广告', 20, DIM, dy=30)
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '1', '三档订阅', None)
    return f


# =====================================================================
# 3 大脑：Muse Spark → 算力 1/10 → 100 万上下文 → 基准有胜有负 → 为 Muse 铺路
# =====================================================================
def sc3(lt, d):
    k = 2; e = EV(k); cuts = [e[2], e[3], e[5]]
    if lt < e[2]:
        cam = orbit(0.2 + 0.02 * lt, 11, 2.5, (0, 2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        spark_chip(f, (-3, 0.9, 0), 1.0, lt)
        lab(f, (-3, 3.6, 0), 'Muse Spark', 28, PURPLE)
        if lt > e[1]:
            g = ease((lt - e[1] - 0.5) / 1.0)
            cube(f, (1.6, 1.8 * g, 0), (1.3, 3.6 * g, 1.3), GREY, 0.25); lab(f, (1.6, 4.0, 0), 'Llama 4 Maverick', 16, GREY, a=g)
            cube(f, (3.6, 0.18 * g, 0), (1.3, 0.36 * g, 1.3), PURPLE, 0.6); lab(f, (3.6, 0.9, 0), '1/10', 26, PURPLE, a=g)
            lab(f, (2.6, 0, 1), '达到同等性能所需训练算力（Meta 自称）', 16, DIM, dy=36, a=g)
        card(f, 40, 160, 300, 96, '2026年4月', 'Spark 首发', '', PURPLE, a=ease(lt / 0.4), vsz=28, note='全新架构 · 非 Llama 衍生')
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '2', '大脑：Muse Spark 系列', None)
        return f
    if lt < e[3]:
        t = lt - e[2]
        cam = orbit(0.6 + 0.04 * t, 13, 3, (0, 1.2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        n = int(160 * ease(t / 2.5))
        for i in range(n):
            a_ = i * 0.16; r = 3.4; y = 0.3 + i * 0.026
            P = (r * math.cos(a_), y, r * math.sin(a_))
            cube(f, P, (0.5, 0.018, 0.34), lerp_col(ACC, PURPLE, i / 160), 0.45, R=roty(-a_))
        spark_chip(f, (0, 0.2, 0), 0.8, lt)
        if n: ball(f, (3.4 * math.cos((n - 1) * 0.16), 0.3 + (n - 1) * 0.026, 3.4 * math.sin((n - 1) * 0.16)), 0.12, WHITE, 1.0)
        card(f, 40, 160, 330, 100, '9月3日 · Spark 1.3', counter(t, 0, 2.5, 0, 1000000, '{:,.0f}'), 'token 上下文', PURPLE, a=ease(t / 0.4), vsz=30)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '2', '100 万 token 上下文', None)
        return f
    if lt < e[5]:
        t = lt - e[3]
        cam = orbit(-0.2 + 0.02 * t, 12, 3, (0, 2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        groups = [('DeepSWE 长程编程', [(75.4, PURPLE, 'Spark 1.3'), (74.0, ORANGE, 'Opus 5')], 0), ('OSWorld 2.0 电脑操作', [(66.9, PURPLE, 'Spark 1.3'), (68.3, ORANGE, 'Opus 5')], e[4] - e[3])]
        for gi, (nm, vs, t0) in enumerate(groups):
            gx = -3 + gi * 6; g = ease((t - t0) / 0.8)
            if g < 0.01: continue
            for j, (v, col, mn) in enumerate(vs):
                h = (v - 55) / 5 * g; x = gx + (j - 0.5) * 1.6
                cube(f, (x, h / 2, 0), (1.2, max(h, 0.02), 1.2), col, 0.4)
                lab(f, (x, h + 0.4, 0), f'{v}', 22, WHITE, a=g); lab(f, (x, 0, 0.8), mn, 15, col, dy=30, a=g)
            lab(f, (gx, 0, 0.8), nm, 18, WHITE, dy=58, a=g)
            if g > 0.9: lab(f, (gx, 0, 0.8), '领先' if gi == 0 else '落后', 22, GREEN if gi == 0 else RED, dy=86, a=1)
        lab(f, (-6.5, 0, 0), '纵轴从 55 起', 14, DIM, dy=20)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '2', '基准：编程领先，电脑操作仍落后', '数据来自 Meta 发布')
        return f
    t = lt - e[5]
    cam = orbit(0.3, 12, 3, (0, 1.5, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    pts = [(-5, 'Spark · 4月'), (-1.8, 'Glimmer · 8月'), (1.4, 'Spark 1.3 · 9月'), (4.8, 'Muse')]
    for j, (x, nm) in enumerate(pts):
        g = pop(t, j * 0.3)
        if j < 3: cube(f, (x, 1.2, 0), 1.0 * g, PURPLE, 0.45)
        else: muse_orb(f, (x, 1.4, 0), 1.0 * g, lt)
        lab(f, (x, 0, 0.8), nm, 18, WHITE, dy=30, a=g)
        if j: beam(f, (pts[j - 1][0] + 0.6, 1.2, 0), (x - 0.7, 1.2, 0), ACC, 160, 3)
    card(f, 40, 160, 330, 96, 'Alexandr Wang · 首席 AI 官', '“Spark 系列为 Muse 而建”', '', ACC, a=ease(t / 0.4), vsz=22)
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '2', '一路为 Muse 铺路', None)
    return f


# =====================================================================
# 4 Secure VM：专属云端虚拟机 → 里面装着 Muse、数据、凭证 → 与他人隔离 → 可见的浏览器
# =====================================================================
def sc4(lt, d):
    k = 3; e = EV(k); cuts = [e[3]]
    if lt < e[3]:
        cam = orbit(0.4 + 0.03 * lt, 10, 3.5, (0, 1.8, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        g = ease((lt - e[1]) / 0.8)
        vm_box(f, (0, 1.9 * max(g, 0.01), 0), 5.0 * max(g, 0.01), 3.4 * max(g, 0.01), 3.4 * max(g, 0.01), ACC, label='Secure VM · 你的专属' if g > 0.5 else None, lsz=22)
        if lt > e[2]:
            items = [('Muse', (-1.4, 1.8, 0)), ('你的数据', (0.4, 1.0, 0.6)), ('账号凭证', (1.5, 2.3, -0.4))]
            for j, (nm, P) in enumerate(items):
                gg = pop(lt, e[2] + j * 0.35)
                if j == 0: muse_orb(f, P, 0.7 * gg, lt)
                elif j == 1:
                    for q in range(3): cube(f, (P[0], P[1] + q * 0.32, P[2]), (0.8 * gg, 0.26, 0.8 * gg), CYAN, 0.4)
                else: cube(f, P, (0.9 * gg, 0.5 * gg, 0.2), GOLD, 0.6)
                lab(f, (P[0], P[1] - 0.8, P[2]), nm, 16, WHITE, a=gg)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '3', '安全架构 ①：每人一台云端虚拟机', None)
        return f
    t = lt - e[3]
    cam = orbit(0.55 + 0.03 * t, lerp(16, 12.5, ease((lt - e[4]) / 1.2)), lerp(9, 6.5, ease((lt - e[4]) / 1.2)), (0, 1.5, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    for i in range(9):
        r, c = divmod(i, 3); P = ((c - 1) * 5.2, 1.4, (r - 1) * 5.2)
        mine = i == 4
        vm_box(f, P, 3.4, 2.4, 3.4, ACC if mine else (60, 70, 88), a=90 if mine else 0, fill=mine)
        muse_orb(f, P, 0.5, lt + i, MUSE if mine else (120, 130, 150))
    if lt > e[4]:
        A = ease((lt - e[4] - 0.6) / 0.5)
        slab(f, (0, 1.6, 1.75), 2.6, 1.6, (230, 234, 242), 0.4, 255 * A)
        cube(f, (0, 2.3, 1.82), (2.6, 0.18, 0.03), (60, 70, 90), 0.3, alpha=255 * A)
        cube(f, (-0.3 + 0.6 * math.sin(lt * 2), 1.4, 1.84), (0.12, 0.12, 0.03), RED, 0.9, alpha=255 * A)
        lab(f, (0, 0.6, 1.8), '内置浏览器 · 每一步你都看得见', 18, ACC, dy=20, a=A)
    else: note(f, 640, 560, '与其他用户的智能体完全隔离', ease((t) / 0.4), 22, accent=ACC)
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '3', '彼此隔离 · 操作可见', None)
    return f


# =====================================================================
# 5 Sentinel：同机隔离的哨兵 → 动作包过闸（放行/拦截/问你）→ 弹窗绕过模型 → 权限矩阵 → 保险库
# =====================================================================
def sc5(lt, d):
    k = 4; e = EV(k); cuts = [e[5]]
    if lt < e[5]:
        cam = orbit(0.35 + 0.02 * lt, 13, 4, (0, 1.6, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        vm_box(f, (-1.5, 1.8, 0), 7, 3.2, 3.2, ACC, label='Secure VM')
        muse_orb(f, (-3.8, 1.8, 0), 0.8, lt); lab(f, (-3.8, 0.6, 0), 'Muse', 18, MUSE)
        g = pop(lt, 0.3)
        sentinel(f, (0.6, 1.8, 0), g, lt); lab(f, (0.6, 0.5, 0), 'Sentinel 哨兵', 18, SENT, a=g)
        if lt > e[1]: cube(f, (-1.6, 1.8, 0), (0.08, 3.0, 3.0), SENT, 0.6, alpha=110 * ease((lt - e[1]) / 0.4)); lab(f, (-1.6, 3.6, 0), '系统级隔离', 15, SENT, a=ease((lt - e[1]) / 0.4))
        outs = [('放行', GREEN, (5.2, 2.8, 0)), ('拦截', RED, (2.0, 1.8, 0)), ('问你', GOLD, (5.2, 0.8, 0))]
        if lt > e[2]:
            t = lt - e[2]
            for q in range(6):
                ph = (t * 0.45 + q / 6) % 1; kind = [0, 2, 0, 1, 0, 2][q]
                if ph < 0.5: P = np.array([lerp(-3.0, 0.2, ph * 2), 1.8, 0])
                else:
                    tgt = np.array(outs[kind][2]); s_ = (ph - 0.5) * 2
                    P = np.array([0.6, 1.8, 0]) + (tgt - [0.6, 1.8, 0]) * (s_ if kind != 1 else min(s_, 0.4))
                cube(f, P, 0.3, outs[kind][1] if ph > 0.5 else (200, 210, 230), 0.6)
            if lt > e[3]:
                for nm, col, P in outs: lab(f, P, nm, 18, col, dy=-24, a=ease((lt - e[3]) / 0.4))
        phone(f, (6.4, 0.9, 0.8), 0.6, on=1)
        if lt > e[4]:
            A = ease((lt - e[4]) / 0.4)
            f.line([(0.9, 2.2, 0), (2.5, 4.4, 0), (6.4, 4.4, 0.8), (6.4, 1.6, 0.8)], (*GOLD, int(220 * A)), 4)
            lab(f, (3.8, 4.4, 0), '确认弹窗直达你 · 不经过模型', 18, GOLD, a=A)
            stamp(f, 1050, 200, '防提示注入', A, GOLD, 22)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '4', '安全架构 ②：第二个智能体把关', None)
        return f
    t = lt - e[5]
    if lt < e[6]:
        cam = orbit(0.0, 11, 2.5, (0, 2.2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        rows = ['读', '写']; colsN = ['某个任务', '某个服务', '某笔交易', '某段时间']
        for i, rn in enumerate(rows):
            lab(f, (-4.8, 3.2 - i * 1.4, 0), rn, 26, ACC if i == 0 else SENT, dy=0)
            for j, cn in enumerate(colsN):
                g = pop(t, 0.2 + (i * 4 + j) * 0.08)
                on = (i, j) in [(0, 0), (0, 1), (0, 3), (1, 0)]
                cube(f, (-2.7 + j * 2.1, 3.2 - i * 1.4, 0), (1.8 * g, 1.0 * g, 0.3), GREEN if on else DARK, 0.5 if on else 0.15)
                if i == 0: lab(f, (-2.7 + j * 2.1, 4.1, 0), cn, 16, WHITE, a=g)
        lab(f, (0, 0.6, 0), '读写分离 · 按范围授权（示意）', 18, DIM)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '4', '细粒度权限', None)
        return f
    t = lt - e[6]
    cam = orbit(0.4 + 0.03 * t, 9, 2.5, (0, 1.6, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    cube(f, (1.5, 1.4, 0), 2.4, (70, 78, 92), 0.25)
    f.layer()
    ring(f, (1.5, 1.4, 1.22), 0.6, GOLD, 255, R=I3)
    cube(f, (1.5, 1.4, 1.25), (0.12, 0.9, 0.05), GOLD, 0.7, R=rotz(lt * 0.8))
    lab(f, (1.5, 3.0, 0), '加密保险库', 22, GOLD)
    muse_orb(f, (-3, 1.6, 0), 0.7, lt)
    flow(f, (1.0, 1.6, 0), (-2.4, 1.6, 0), t, GOLD, 3, 0.9, 0.08)
    lab(f, (-3, 0.4, 0), '密码：••••••••', 18, WHITE, dy=20)
    note(f, 640, 560, 'Muse 能用，但看不到', ease(t / 0.4), 26, accent=GOLD)
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '4', '凭证保险库', None)
    return f


# =====================================================================
# 6 支付与生态：一次性虚拟卡 → 连接器平台 → 与 MCP 的区别
# =====================================================================
APPS = [('Gmail', RED), ('Notion', WHITE), ('Slack', PURPLE), ('Asana', PINK), ('日历', CYAN), ('你的 API', GOLD)]
def sc6(lt, d):
    k = 5; e = EV(k); cuts = [e[2]]
    if lt < e[2]:
        cam = orbit(0.3 + 0.03 * lt, 10, 2.5, (0, 1.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        cube(f, (-4, 1.5, 0), (1.8, 1.1, 0.06), (40, 50, 80), 0.3, R=rotx(-0.2)); lab(f, (-4, 2.5, 0), '真实卡 •••• 4242', 16, WHITE)
        lab(f, (-4, 0.5, 0), '留在你手里', 16, GREEN, dy=20)
        muse_orb(f, (-0.8, 1.8, 0), 0.6, lt)
        n = int(lt / 1.5) + 1
        for q in range(min(n, 3)):
            ph = clamp((lt - q * 1.5) / 1.3)
            P = (lerp(-0.2, 3.0, ph), 1.5 + 0.25 * q, 0.6)
            cube(f, P, (1.2, 0.75, 0.04), lerp_col((99, 91, 255), GOLD, q / 3), 0.6, alpha=255 * (1 - 0.85 * ease((lt - q * 1.5 - 1.3) / 0.4)))
            if ph < 1: lab(f, P, f'一次性卡 #{q + 1}', 13, WHITE, dy=0)
        slab(f, (4.8, 1.6, 0), 1.6, 2.2, (230, 234, 242), 0.35); lab(f, (4.8, 3.0, 0), '商户网站', 16, WHITE)
        card(f, 40, 160, 320, 92, '支付', 'Stripe Link', '', (99, 91, 255), a=ease(lt / 0.4), vsz=28, note='首个享受 Link 购买保障的智能体')
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '5', '付款：每次一张一次性虚拟卡', None)
        return f
    t = lt - e[2]
    cam = orbit(0.2 + 0.05 * t, 12, 4, (0, 1.6, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    muse_orb(f, (0, 1.8, 0), 1.0, lt)
    for j, (nm, col) in enumerate(APPS):
        a_ = j / 6 * 2 * pi + t * 0.15; P = np.array([4.8 * math.cos(a_), 1.4, 4.8 * math.sin(a_)])
        g = pop(t, 0.3 + j * 0.2)
        cube(f, P, 0.7 * g, col, 0.4); lab(f, P + [0, 0.8, 0], nm, 16, col, a=g)
        if g > 0.5: beam(f, (0, 1.8, 0), P, col, 100, 2); flow(f, P, (0, 1.8, 0), t + j * 0.3, col, 2, 0.8, 0.06)
    card(f, 40, 160, 330, 96, '9月19日 · 连接器平台', '你带 API', '', ACC, a=ease(t / 0.4), vsz=28, note='Muse 带智能体、浏览器和上下文' if lt > e[3] else None)
    if lt > e[4]:
        A = ease((lt - e[4]) / 0.4)
        f.rect(900, 160, 1240, 280, (10, 16, 30, int(210 * A)), r=10)
        f.text(1070, 190, 'MCP：开放协议，各家通用', 17, col=GREEN, a=A, anc='mm')
        f.text(1070, 230, 'Muse 连接器：Meta 一家的平台', 17, col=GOLD, a=A, anc='mm')
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '5', '生态：连接器平台', None)
    return f


# =====================================================================
# 7 Confidential VM：Meta 能看 → TEE 外壳 + 用户持钥 → Moxie → 审计与透明日志
# =====================================================================
def eye(f, P, s, col, a=255):
    P = np.array(P, float)
    f.mesh(M_BALL, R=np.diag([1.4, 0.7, 0.5]), T=P, sc=s, col=(230, 230, 240), emis=0.4, alpha=int(a))
    ball(f, P + [0, 0, 0.3 * s], 0.32 * s, col, 0.8, a)


def sc7(lt, d):
    k = 6; e = EV(k); cuts = [e[2], e[5]]
    if lt < e[5]:
        cam = orbit(0.45 + 0.02 * lt, 11, 3.5, (0, 1.8, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        conf = lt > e[2]; gC = ease((lt - e[2]) / 0.8)
        vm_box(f, (0, 1.8, 0), 3.6, 2.8, 2.8, ACC if not conf else GREEN, label='Confidential VM' if conf else 'Secure VM（现在）')
        muse_orb(f, (0, 1.8, 0), 0.7, lt)
        if conf:
            cube(f, (0, 1.8, 0), (4.4 * gC, 3.6 * gC, 3.6 * gC), GREEN, 0.3, alpha=70)
            lab(f, (0, -0.1, 1.9), '可信执行环境 TEE', 18, GREEN, dy=24, a=gC)
        blocked = conf and lt > e[4]
        eye(f, (-4.6, 2.4, 0), 0.6, ACC)
        lab(f, (-4.6, 3.4, 0), 'Meta', 20, ACC)
        if not blocked:
            f.line([(-3.8, 2.4, 0), (-1.8, 2.0, 0)], (*ACC, 180), 3)
            if lt > e[1]: lab(f, (-4.6, 1.0, 0), '政策上不看 · 技术上能看', 16, GOLD, a=ease((lt - e[1]) / 0.4))
        else:
            f.line([(-3.8, 2.4, 0), (-2.5, 2.2, 0)], (*RED, 220), 3)
            cube(f, (-2.75, 2.25, 0), (0.1, 1.0, 1.0), RED, 0.8); lab(f, (-4.6, 1.0, 0), '连 Meta 也看不到', 18, RED)
        if lt > e[3]:
            A = ease((lt - e[3]) / 0.5)
            phone(f, (4.6, 1.6, 0), 0.8, on=1); f.mesh(M_RING, R=rotx(pi / 2), T=(4.6, 2.9, 0), sc=0.3, col=GOLD, emis=0.9, alpha=int(255 * A))
            cube(f, (4.6, 2.5, 0), (0.08, 0.5, 0.08), GOLD, 0.8, alpha=255 * A)
            lab(f, (4.6, 0.2, 0), '密钥只在你的设备', 18, GOLD, dy=20, a=A)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '6', '年底：Confidential VM', None)
        return f
    t = lt - e[5]
    cam = orbit(0.3 + 0.03 * t, 13, 3, (0, 1.6, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    if lt < e[6] + 0.6:
        A0 = 1 - ease((lt - e[6]) / 0.6)
        vm_box(f, (0, 1.6, 0), 3.0, 2.4, 2.4, GREEN, a=int(90 * A0), fill=A0 > 0.5, label='Confidential VM' if A0 > 0.5 else None)
        muse_orb(f, (0, 1.6, 0), 0.6 * max(A0, 0.01), lt)
        cube(f, (0, 1.6, 0), (3.6, 3.0, 3.0), GREEN, 0.3, alpha=60 * A0)
    card(f, 40, 160, 340, 96, '合作设计', 'Moxie Marlinspike', '', GREEN, a=ease(t / 0.4), vsz=26, note='Signal 创始人')
    if lt > e[6]:
        t2 = lt - e[6]
        cube(f, (-4.5, 1.4, 0), (1.4, 1.8, 0.2), (40, 60, 80), 0.3); lab(f, (-4.5, 2.6, 0), '源代码', 18, WHITE)
        for j in range(3):
            g = pop(t2, 0.3 + j * 0.2); f.mesh(M_PERSON, T=(-2.2, 0, -1.4 + j * 1.4), sc=0.6 * g, col=GREEN, emis=0.3)
        lab(f, (-2.2, 0, 1.4), '安全公司审计', 16, GREEN, dy=36)
        n = int(clamp((t2 - 0.8) / 2.0) * 6)
        for q in range(n):
            cube(f, (0.6 + q * 1.1, 1.0, 0), 0.8, GOLD, 0.45)
            if q: cube(f, (0.05 + q * 1.1, 1.0, 0), (0.3, 0.1, 0.1), GOLD, 0.8)
        lab(f, (3.3, 0, 0.6), '公开二进制 · 透明日志', 18, GOLD, dy=36, a=ease((t2 - 0.8) / 0.4))
    chrome_x(f, ACC, TAG); headline(f, lt, ACC, '6', '可验证：审计 + 透明日志', None)
    return f


# =====================================================================
# 8 Muse Charm 硬件 → 总结架构 → 片尾
# =====================================================================
def rrect_prism(W, H, D, r, col, n=6):
    pr = []
    for cx, cy, a0 in [(W/2-r, H/2-r, 0), (-W/2+r, H/2-r, pi/2), (-W/2+r, -H/2+r, pi), (W/2-r, -H/2+r, 3*pi/2)]:
        for i in range(n + 1):
            a = a0 + i / n * pi / 2; pr.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    m = len(pr); V = [[x, y, D / 2] for x, y in pr] + [[x, y, -D / 2] for x, y in pr] + [[0, 0, D / 2], [0, 0, -D / 2]]
    cf, cb = 2 * m, 2 * m + 1
    F = [[cf, i, (i + 1) % m, (i + 1) % m] for i in range(m)] + [[cb, m + (i + 1) % m, m + i, m + i] for i in range(m)]
    F += [[i, m + i, m + (i + 1) % m, (i + 1) % m] for i in range(m)]
    return part(V, F, col)
M_CHARM = rrect_prism(1.6, 2.0, 0.6, 0.26, (238, 232, 220))
def charm(f, P, s, lt, show=1.0):
    """圆角矩形机身（非相交拼装）+ 前屏 + 前摄 + 侧面指纹键 + 背面后摄。"""
    P = np.array(P, float)
    yaw = math.atan2(f.cam.p[0] - P[0], f.cam.p[2] - P[2]) + 0.55 * math.sin(lt * 0.5)
    R = roty(yaw); W, H, D, r = 1.6 * s, 2.0 * s, 0.6 * s, 0.22 * s
    body = (238, 232, 220)
    def at(v): return P + R @ np.array(v)
    f.mesh(M_CHARM, R=R, T=P, sc=s, emis=0.12, cull=False)
    f.layer()   # 机身先画，正面细节单独一层，避免逐面排序把屏幕压到机身后
    z = D / 2 + 0.012 * s
    cube(f, at([0, 0.1 * s, z]), (1.08 * s, 1.08 * s, 0.02 * s), (12, 16, 26), 0.2, R=R)
    cube(f, at([0, 0.1 * s, z + 0.012 * s]), (0.98 * s, 0.98 * s, 0.01 * s), (24, 52, 110), 0.55, R=R)
    f.layer()
    f.mesh(M_BALL, R=R @ np.diag([0.2 * s, 0.2 * s, 0.02 * s]), T=at([0, 0.22 * s, z + 0.06 * s]), col=MUSE, emis=0.9 + 0.1 * math.sin(lt * 3))
    for q in range(2): cube(f, at([0, (-0.18 - q * 0.16) * s, z + 0.025 * s]), ((0.6 - q * 0.2) * s, 0.06 * s, 0.005), (150, 180, 230), 0.6, R=R)
    f.mesh(M_BALL, R=R @ np.diag([0.06 * s, 0.06 * s, 0.02 * s]), T=at([0, 0.85 * s, D / 2 + 0.005]), col=(20, 20, 26), emis=0.3)
    if np.dot(R @ np.array([1, 0, 0]), f.cam.p - at([W / 2, 0, 0])) > 0: f.mesh(M_BALL, R=R @ np.diag([0.03 * s, 0.14 * s, 0.14 * s]), T=at([W / 2 + 0.005, 0.2 * s, 0]), col=GOLD, emis=0.6)
    return {'屏': at([-0.55 * s, 0.4 * s, z]), '前摄': at([0, 0.85 * s, D / 2]), '指纹': at([W / 2 + 0.03, 0.2 * s, 0]), '后摄': at([0.35 * s, 0.6 * s, -D / 2])}


def callout(f, P, Q, s_, a, col=WHITE):
    if a < 0.02: return
    f.line([P, Q], (*col, int(170 * a)), 2); f.dots([P], 0.04, (*col, int(230 * a)))
    lab(f, Q, s_, 18, col, dy=-12, a=a)


def sc8(lt, d):
    k = 7; e = EV(k); cuts = [e[3], e[5]]
    if lt < e[3]:
        cam = orbit(0.3 + 0.08 * lt, lerp(5, 6.5, ease(lt / 6)), 1.2, (0, 1.6, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        pts = charm(f, (0, 1.6, 0), 1.15 * pop(lt, 0.2), lt)
        lab(f, (0, 3.2, 0), 'Muse Charm', 30, GOLD, a=ease((lt - 0.5) / 0.4))
        if lt > e[1]:
            T0 = e[1]
            callout(f, pts['屏'], (-2.9, 2.4, 0), '2 英寸屏', ease((lt - T0) / 0.3))
            callout(f, (0.9, 2.9, 0), (2.4, 3.0, 0), '5G', ease((lt - T0 - 0.4) / 0.3), CYAN)
            callout(f, pts['前摄'], (2.4, 2.4, 0), '前后摄像头', ease((lt - T0 - 0.8) / 0.3))
            callout(f, pts['指纹'], (2.4, 1.0, 0), '指纹键：按住说话', ease((lt - T0 - 1.2) / 0.3), GOLD)
        if lt > e[2]: note(f, 640, 560, '目标 12 月前开售 · 价格未公布', ease((lt - e[2]) / 0.4), 22, accent=GOLD)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, '7', 'Connect 大会：专属硬件', None)
        return f
    if lt < e[5]:
        t = lt - e[3]
        cam = orbit(0.4 + 0.03 * t, 12, 4, (0, 1.6, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        vm_box(f, (0, 1.8, 0), 6, 3, 3, ACC, label='专属虚拟机')
        muse_orb(f, (-1.5, 1.8, 0), 0.7, lt); sentinel(f, (1.5, 1.8, 0), 0.8, lt)
        cube(f, (0, 1.8, 0), (0.06, 2.6, 2.6), SENT, 0.6, alpha=120)
        if lt > e[4]:
            A = ease((lt - e[4]) / 0.5)
            f.mesh(M_PERSON, T=(-5.5, 0, 1), sc=1.0, col=(200, 205, 220), emis=0.2)
            cube(f, (-4.2, 1.2, 1), (0.6 * A, 0.4 * A, 0.1), GOLD, 0.6)
            flow(f, (-4.2, 1.2, 1), (-1.5, 1.8, 0), t, GOLD, 2, 0.6, 0.08)
            note(f, 640, 560, '真正难题：让普通人敢把账号交给 AI', A, 24, accent=GOLD)
        chrome_x(f, ACC, TAG); headline(f, lt, ACC, None, '总结：专属虚拟机 + 双智能体隔离', None)
        return f
    t = lt - e[5]
    cam = orbit(0.2 + 0.05 * t, 8, 1.8, (0, 1.6, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    muse_orb(f, (0, 1.8, 0), 1.3, lt)
    A = ease(t / 0.5)
    f.rect(390, 540, 890, 600, (*ACC, int(220 * A)), r=10)
    f.text(640, 570, '深度讲解 · 我们下期见', 28, anc='mm', a=A)
    chrome_x(f, ACC, TAG)
    return f


FILM = Film(SEG, dur, [sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8], DISP,
            chapters=['开场', '是什么', '大脑', 'Secure VM', 'Sentinel', '支付与生态', 'Confidential VM', '硬件与总结'], total=TOTAL, lead=0.15)
