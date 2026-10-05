"""AI 早报 · OpenAI DevDay 2026 全部重点（三分钟新闻播报）
信息截至 2026-10-01；来源见 README.md。
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
SUBS = [[(a, b - 0.2 if i + 1 < len(s) else b, t) for i, (a, b, t) in enumerate(s)] for s in TM['subs']]   # 句尾留 0.2 s，避免与引擎 0.15 s 余显叠字
TOTAL = SEG[-1] + dur[-1] + 2.2
def ev(k, i): return SUBS[k][i][0]

ACC = (16, 163, 127)            # 栏目主色（青绿）
TEAL = (40, 210, 170); BLUE = (70, 150, 255); GOLD = (245, 190, 70); ORANGE = (255, 140, 60); RED = (240, 80, 80)
PURPLE = (160, 110, 255); GREEN = (80, 220, 120)
TAG = 'OpenAI DevDay 2026 · 旧金山'

M_BOX = box(1, 1, 1, WHITE)
M_BALL = sphere(1, WHITE, 18, 10)
M_RING = torus(1, 0.06, WHITE, 48, 6)
M_RING_T = torus(1, 0.14, WHITE, 48, 8)
M_PANEL = panel(1, 1)
M_RACK = rack()
M_PERSON = person()
M_COIN = coin()
M_SHIELD = shield()
M_GLOBE6 = sphere(10, (20, 46, 100), 40, 20)


def base(cam, lt, d, cuts=()):
    f = Fr(cam)
    f.dim = min(ease(lt / 0.3), 1 - ease((lt - d - 0.02) / 0.32), dip(lt, cuts))
    return f


def cube(f, P, s, col, emis=0.15, alpha=255, R=I3):
    f.mesh(M_BOX, R=R @ np.diag(s if hasattr(s, '__len__') else [s, s, s]), T=P, col=col, emis=emis, alpha=alpha)


def bar(f, x, z, h, col, w=1.0, emis=0.2, y0=0.0):
    if h > 0.01: cube(f, (x, y0 + h / 2, z), (w, h, w), col, emis)


def ring(f, P, r, col, R=I3, thick=False, emis=0.6, alpha=255):
    f.mesh(M_RING_T if thick else M_RING, R=R, T=P, sc=r, col=col, emis=emis, alpha=alpha)


def slab(f, P, w, h, col, R=I3, emis=0.1, alpha=255):
    f.mesh(M_PANEL, R=R @ np.diag([w, h, 1]), T=P, col=col, emis=emis, alpha=alpha)


def fib(n, r):
    i = np.arange(n) + 0.5; phi = np.arccos(1 - 2 * i / n); th = pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.cos(phi), np.sin(th) * np.sin(phi)], 1) * r


def floor(f, y=0.0, ext=30, step=3, a=40):
    f.grid(y, ext, step, (90, 200, 180, a)); f.layer()


# =====================================================================
# 1 开场：片头 → 时差地球 → 主题演讲台 + 20 多项发布 → 12 亿 → 6 件事
# =====================================================================
BLOSSOM = [(roty(k * pi / 3) @ rotx(pi / 2.6), roty(k * pi / 3) @ np.array([1.25, 0, 0])) for k in range(6)]


def sc1(lt, d):
    k = 0; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[2], e[4], e[7]]
    if lt < e[2]:                                        # 片头：花形环结 + 光环隧道
        a = 0.6 + lt * 0.25
        cam = Cam([0, 0.6, 30], [0, 0.6, 0], 45)
        f = base(cam, lt, d, cuts)
        for j in range(12):
            z = ((j * 6 + lt * 7) % 72) - 50
            ring(f, (0, 0, z), 13, (30, 120, 110), R=rotx(pi / 2), emis=0.7, alpha=90)
        f.layer()
        C = np.array([0, 6.2, 0])
        for R, T in BLOSSOM:
            ring(f, C + rotz(lt * 0.4) @ T * 0.8, 1.6, TEAL, R=roty(lt * 0.5) @ rotz(lt * 0.4) @ R, thick=True, emis=0.6)
        A = win(lt, 0.2, e[2] - 0.1, 0.4, 0.3)
        f.text(640, 400, 'AI 早报', 88, a=A * pop(lt, 0.2), anc='mm', stroke=3)
        f.text(640, 480, 'OpenAI 开发者大会 · 特别报道', 30, col=(190, 235, 225), a=A * ease((lt - 0.8) / 0.5), anc='mm')
        chrome(f, ACC, TAG, a=ease((lt - e[1]) / 0.6))
        return f
    if lt < e[4]:                                        # 时差：旧金山 9/29 10:00 → 北京 9/30 01:00
        t = lt - e[2]
        sf, bj = ll(37.8, -122.4), ll(39.9, 116.4)
        mid = nrm(sf + bj); rot = 0.05 * t
        Rm = roty(rot)
        zoom = ease((lt - e[3] - 0.5) / 1.6)
        cpos = Rm @ (mid * lerp(21, 13, zoom) + np.array([0, 1.5, 0]))
        tgt = Rm @ (lerp(0, 1, zoom) * sf * 6 * 0.6)
        cam = Cam(cpos, tgt, 45)
        f = base(cam, lt, d, cuts)
        draw_globe(f, (0, 0, 0), 6, rot, m=None)
        f.layer()
        pts = []
        for s in np.linspace(0, 1, 60):
            w = math.sin(pi * s); p = nrm(sf * (1 - s) + bj * s) * (6 + 1.6 * w); pts.append(Rm @ p)
        n = int(60 * ease((t - 0.3) / 1.2))
        if n > 1: f.line(pts[:n], (255, 210, 120, 230), 4)
        P_sf, P_bj = Rm @ sf * 6.02, Rm @ bj * 6.02
        f.dots([P_sf], 0.18, (255, 120, 90, 255)); f.dots([P_bj], 0.18, (255, 220, 120, 255))
        f.label(P_sf, '旧金山 · 9月29日 上午10点', 22, (255, 190, 170), dx=-30, dy=-50, a=ease((t - 0.2) / 0.4))
        f.label(P_bj, '北京 · 9月30日 凌晨1点', 22, (255, 225, 160), dx=30, dy=-50, a=ease((t - 1.2) / 0.4) * (1 - zoom))
        if lt > e[3]:
            pin = P_sf + Rm @ sf * 0.9
            f.mesh(M_BALL, T=pin, sc=0.22 + 0.04 * math.sin(lt * 6), col=(255, 110, 90), emis=0.6)
            card(f, 40, 160, 330, 118, '主题演讲', 'DevDay 2026', '', ACC, a=ease((lt - e[3]) / 0.5), vsz=30, note='Fort Mason · 旧金山')
        chrome(f, ACC, TAG)
        return f
    if lt < e[7]:                                        # 演讲台 → 20 多项发布 → 12 亿
        t = lt - e[4]
        a = -0.35 + 0.05 * t
        cam = orbit(a, 27, 5.5, (0, 6.0, 0), 45)
        f = base(cam, lt, d, cuts)
        floor(f, 0, 30, 3, 35)
        cube(f, (0, 0.4, 2), (18, 0.8, 7), (28, 34, 46), 0.05)                     # 舞台
        slab(f, (0, 6.5, -1.5), 17, 8.2, (12, 40, 44), emis=0.35)                     # 大屏
        f.mesh(M_PERSON, T=(0, 0.8, 3), sc=1.0, col=(200, 210, 225))
        f.label((0, 3.1, 3), '主讲：山姆·奥特曼', 20, DIM, dx=40, dy=10, a=ease(t / 0.5) * (1 - ease((lt - e[5]) / 0.4)))
        # 20 多张发布卡片从大屏飞出，排成弧形
        if lt < e[5] + 0.6:
            cols = [TEAL, BLUE, PURPLE, GOLD, ORANGE]
            for i in range(22):
                gx, gy = i % 11, i // 11
                dst = np.array([(gx - 5) * 1.9, 11.6 + gy * 1.6, 1.0])
                src = np.array([0, 6.5, -1.4]); x = ease((t - 0.25 - i * 0.05) / 0.8)
                P = src + (dst - src) * x + np.array([0, math.sin(pi * x) * 2.0, math.sin(pi * x) * 3])
                al = int(255 * min(1, x * 3) * (1 - ease((lt - e[5]) / 0.5)))
                if al > 5: slab(f, P, 1.6, 1.1, cols[i % 5], R=roty(0.0), emis=0.4, alpha=al)
            A = ease((t - 0.6) / 0.4) * (1 - ease((lt - e[5]) / 0.4))
            card(f, 980, 520, 260, 104, '本届发布', '20+', '项', ACC, a=A)
        if lt > e[5] - 0.2:                                                         # 周活跃用户
            x1 = ease((lt - e[6] + 0.2) / 1.6)
            for j, (lab, v, col) in enumerate([('2026年7月', 10, (90, 120, 160)), ('9月29日', lerp(10, 12, x1) if lt > e[6] else 10 * ease((lt - e[5]) / 1.0), TEAL)]):
                x = -3.2 + j * 6.4; h = v * 0.62
                bar(f, x, 3.2, h, col, 2.6, 0.35, 0.8)
                f.label((x, 0.8 + h + 0.4, 3.2), f'{v:.1f}亿' if j else '10亿', 26, WHITE, dx=0, dy=-14, dot=False, a=ease((lt - e[5]) / 0.5))
                f.label((x, 0.9, 4.6), lab, 20, DIM, dx=0, dy=34, dot=False, a=ease((lt - e[5]) / 0.5))
            card(f, 40, 160, 300, 104, 'ChatGPT 周活跃用户', counter(lt, e[6], e[6] + 1.6, 10, 12, '{:.1f}') if lt > e[6] else '10.0', '亿', ACC, a=ease((lt - e[5]) / 0.4))
        chrome(f, ACC, TAG)
        return f
    t = lt - e[7]                                        # 六件事：弧形排开
    cam = orbit(0.08 * math.sin(t * 0.6), 19, 2.5, (0, 1.4, 0), 45)
    f = base(cam, lt, d, cuts)
    floor(f, -1.5, 30, 3, 30)
    names = ['Dots', 'GPT-6.1 Sol', 'Ultrafast', 'Codex 与 API', 'ChatGPT 平台', '场外背景']
    cols = [BLUE, ORANGE, TEAL, PURPLE, GREEN, GOLD]
    for i in range(6):
        x = (i - 2.5) * 2.6; P = np.array([x, 1.2 + 0.2 * math.sin(lt * 2 + i), 0.0])
        s = pop(t, 0.1 + i * 0.12)
        slab(f, P, 2.1 * s, 2.1 * s, cols[i], emis=0.35)
        f.label(P + [0, -1.5, 0], names[i], 18, WHITE, dx=0, dy=8, dot=False, a=ease((t - 0.2 - i * 0.12) / 0.3))
        f.label(P, f'{i + 1}', 40, WHITE, dx=0, dy=14, dot=False, a=ease((t - 0.2 - i * 0.12) / 0.3))
    chrome(f, ACC, TAG)
    return f


# =====================================================================
# 2 Dots：小精灵 → 24/7 → Astra 芯片 → 云端电脑+浏览器 → 4000 应用 → 共享记忆 → 审核闸门 → 开放范围
# =====================================================================
APPS = fib(260, 6.0)
APP_COL = [BLUE, TEAL, ORANGE, PURPLE, GOLD, GREEN, RED, (230, 230, 240)]


def sc2(lt, d):
    k = 1; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[6], e[9]]
    DOT = (60, 140, 255)
    blink = max(0, 1 - abs(((lt * 0.7) % 3.1) - 0.1) / 0.1)
    if lt < e[6]:
        a = 0.2 + 0.07 * lt
        rad = 12 if lt < e[4] else lerp(12, 22, ease((lt - e[4]) / 1.5))
        cam = orbit(a, rad, 2.5 + (2.5 if lt > e[4] else 0) * ease((lt - e[4]) / 1.5), (0, 1.5, 0), 45)
        f = base(cam, lt, d, cuts)
        P = np.array([0, 1.6 + 0.15 * math.sin(lt * 2.2), 0])
        s = pop(lt, 0.25, 0.6)
        if s > 0.02: avatar(f, P, DOT, 1.3 * s, blink=blink)
        f.layer()
        # 24/7 光环
        A1 = ease((lt - e[1]) / 0.5)
        if A1 > 0.01:
            arc = torus(2.3, 0.07, TEAL, 40, 6, arc=2 * pi * ((lt - e[1]) * 0.35 % 1) + 0.01)
            f.mesh(arc, R=rotx(pi / 2 - 0.25), T=P, emis=0.8, alpha=int(255 * A1))
            f.label(P + [2.4, 0.6, 0], '永远在线 · 24/7', 22, TEAL, dx=30, dy=-30, a=A1 * (1 - ease((lt - e[3]) / 0.4)))
        # GPT-6 Astra 芯片
        A2 = ease((lt - e[2]) / 0.5)
        if A2 > 0.01:
            chip = np.array([0, -1.2, 0])
            cube(f, chip, (2.0, 0.35, 2.0), (40, 34, 70), 0.2); cube(f, chip + [0, 0.2, 0], (1.3, 0.08, 1.3), PURPLE, 0.8)
            f.line([chip + [0, 0.25, 0], P - [0, 1.2, 0]], (170, 130, 255, int(200 * A2)), 3)
            f.label(chip, 'GPT-6 Astra 驱动', 22, (200, 170, 255), dx=40, dy=30, a=A2 * (1 - ease((lt - e[4]) / 0.4)))
        # 云端电脑 + 浏览器
        A3 = ease((lt - e[3]) / 0.6)
        if A3 > 0.01:
            rp = np.array([-4.8, 1.6, -1.0]); f.mesh(M_RACK, T=rp, sc=0.9 * A3, emis=0.05)
            bp = np.array([4.8, 2.2, -1.0])
            slab(f, bp, 3.6 * A3, 2.6 * A3, (24, 32, 52), emis=0.1)
            cube(f, bp + [0, 1.05 * A3, 0.06], (3.4 * A3, 0.28 * A3, 0.04), (70, 80, 100), 0.3)
            for j in range(4): cube(f, bp + [(-1.0 + j * 0.0) * A3, (0.5 - j * 0.45) * A3, 0.07], ((2.6 - j * 0.4) * A3, 0.14 * A3, 0.03), (90, 140, 210) if j == 0 else (70, 90, 120), 0.4)
            for q in (rp, bp): f.line([P, q], (90, 200, 255, int(160 * A3)), 2)
            AL = A3 * (1 - ease((lt - e[4]) / 0.4))
            f.label(rp + [0, 2.2, 0], '专属云端电脑', 22, WHITE, dx=-20, dy=-20, a=AL)
            f.label(bp + [0, 1.6, 0], '自带浏览器', 22, WHITE, dx=20, dy=-20, a=AL)
        # 4000+ 应用
        if lt > e[4]:
            t = lt - e[4]; n = int(len(APPS) * ease(t / 2.0))
            A4 = 1 - ease((lt - e[5] - 0.6) / 0.5)
            for i in range(n):
                q = roty(lt * 0.1) @ APPS[i]
                cube(f, P + q, 0.42, APP_COL[i % 8], 0.35, alpha=int(255 * A4))
            for i in range(0, n, 9):
                ph = (lt * 1.5 + i * 0.37) % 1
                if ph < 0.5:
                    q = P + roty(lt * 0.1) @ APPS[i]; f.line([P, q], (*APP_COL[i % 8], int(120 * A4)), 2)
            card(f, 40, 160, 270, 104, '可连接', counter(lt, e[4], e[4] + 2.0, 0, 4000), '+ 个应用', BLUE, a=ease(t / 0.4) * (1 - ease((lt - e[6] + 0.3) / 0.3)))
        # 共享记忆
        if lt > e[5]:
            t = lt - e[5]; A5 = ease(t / 0.6)
            ring(f, P, 4.6, (140, 220, 255), R=rotx(0.2), thick=True, emis=0.7, alpha=int(230 * A5))
            for j, (nm, col) in enumerate([('ChatGPT', TEAL), ('Slack', PURPLE), ('Teams', BLUE)]):
                ang = lt * 0.5 + j * 2 * pi / 3; q = P + rotx(0.2) @ np.array([4.6 * math.cos(ang), 0, 4.6 * math.sin(ang)])
                slab(f, q, 1.8 * A5, 1.2 * A5, col, R=roty(-ang), emis=0.4)
                f.label(q, nm, 20, WHITE, dx=0, dy=-50, dot=False, a=A5)
            f.label(P + [0, 2.0, 0], '跨应用共享记忆', 22, (170, 230, 255), dx=0, dy=-30, dot=False, a=A5)
        chrome(f, ACC, TAG); headline(f, lt, ACC, '1', 'Dots：永远在线的智能体', '由 GPT-6 Astra 驱动 · 每个 Dot 一台云端电脑')
        return f
    if lt < e[9]:                                         # 审核闸门
        t = lt - e[6]
        cam = orbit(0.45 - 0.03 * t, 13.5, 3.0, (-0.5, 1.6, 0), 45)
        f = base(cam, lt, d, cuts)
        floor(f, -1.0, 30, 3, 30)
        P = np.array([-6, 1.6 + 0.15 * math.sin(lt * 2.2), 0])
        avatar(f, P, DOT, 1.2, blink=blink)
        gate = np.array([2.5, 1.5, 0])
        approve = lt > e[8] + 1.2
        hold = e[7] + 0.4 < lt and not approve
        gcol = GREEN if approve else (GOLD if hold else BLUE)
        f.mesh(M_SHIELD, R=roty(pi / 2), T=gate, sc=1.0, col=gcol, emis=0.45, alpha=200)
        ring(f, gate, 2.6, gcol, R=roty(pi / 2), emis=0.9, alpha=150)
        # 只读数据包：自由往返
        for j in range(6):
            ph = (lt * 0.45 + j / 6) % 1; x = lerp(-4.5, 9, ph); y = 1.2 + 0.4 * math.sin(j)
            cube(f, (x, y, -1.4 + (j % 3) * 0.9), 0.35, (120, 180, 255), 0.5, alpha=180)
        # 写操作：停在闸门前 → 批准后通过
        acts = [('发消息', ORANGE), ('付款', RED)]
        for j, (nm, col) in enumerate(acts):
            t0 = e[7] + j * 0.5
            if lt < t0: continue
            x = lerp(-4.5, 1.2, ease((lt - t0) / 1.0))
            if approve: x = lerp(1.2, 8.5, ease((lt - e[8] - 1.2 - j * 0.3) / 1.2))
            Pq = np.array([x, 2.6 - j * 1.6, 0.6])
            cube(f, Pq, 0.7, col, 0.5)
            f.label(Pq, nm, 20, col, dx=0, dy=-30, dot=False, a=1 - ease((x - 6) / 1.5))
        f.label(gate + [0, 2.3, 0], '自动审核 + 你的规则', 22, gcol, dx=0, dy=-40, dot=False, a=ease((lt - e[7] - 0.3) / 0.4))
        if approve: f.label(gate + [0, -2.3, 0], '✓ 用户已批准', 22, GREEN, dx=0, dy=30, dot=False, a=ease((lt - e[8] - 1.2) / 0.3))
        card(f, 40, 160, 260, 104, '后台模式', '默认只读', '', BLUE, a=ease(t / 0.4), vsz=34)
        chrome(f, ACC, TAG); headline(f, lt, ACC, '1', 'Dots：永远在线的智能体', '涉及账户的操作必须过审核')
        return f
    t = lt - e[9]                                         # 开放范围
    cam = orbit(0.1 * math.sin(t * 0.4), 15, 2.5, (0, 1.0, 0), 45)
    f = base(cam, lt, d, cuts)
    floor(f, -1.2, 30, 3, 30)
    plans = [('Pro', BLUE), ('Business Premium', PURPLE), ('Enterprise', TEAL)]
    for j, (nm, col) in enumerate(plans):
        x = (j - 1) * 4.6; s = pop(t, 0.1 + j * 0.25)
        slab(f, (x, 1.3, 0), 3.8 * s, 2.4 * s, col, R=rotx(-0.15), emis=0.45)
        avatar(f, (x, 3.5 + 0.12 * math.sin(lt * 2 + j), 0.3), DOT, 0.5 * s, blink=blink)
        f.label((x, -0.2, 0.5), nm, 22, WHITE, dx=0, dy=30, dot=False, a=ease((t - 0.2 - j * 0.25) / 0.3))
    f.text(640, 600, '首发暂不含欧洲经济区、英国、瑞士的 Pro 用户', 18, col=DIM, anc='mm', bold=False, a=ease((t - 1.2) / 0.5))
    chrome(f, ACC, TAG); headline(f, lt, ACC, '1', 'Dots：首批开放对象', '企业版、教育版需管理员开启（测试版）')
    return f


# =====================================================================
# 3 GPT-6.1 Sol：Astra 晶体 vs Sol 太阳 → 价格柱 → 缓存 → DeepSWE 打平 → 电脑操作差 2.1 → 成本 1/7
# =====================================================================
M_CRYSTAL = part(*lathe([(0, -2.2), (1.3, -0.4), (1.3, 0.4), (0, 2.6)], 6), (150, 120, 255))
M_SUN = sphere(1.6, (255, 150, 50), 28, 14)


def sc3(lt, d):
    k = 2; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[5]]
    AX, SX = -4.2, 4.2
    t = lt
    if lt < e[5]:
        a = -0.15 + 0.035 * t
        cam = orbit(a, lerp(19, 24, ease((lt - e[2]) / 1.5)), lerp(3, 5.0, ease((lt - e[2]) / 1.5)), (0, lerp(3.6, 4.2, ease((lt - e[2]) / 1.5)), 0), 45)
    else:
        a = 0.25 - 0.03 * (lt - e[5])
        cam = orbit(a, 24, 5, (0, 4.0, 0), 45)
    f = base(cam, lt, d, cuts)
    floor(f, 0, 30, 3, 32)
    # 模型本体
    up = 1 if lt < e[2] else 1 - ease((lt - e[2]) / 0.8) * 0.0
    yA = 7.6 if lt > e[2] else 4.2
    yA = lerp(4.0, 6.6, ease((lt - e[2]) / 1.0)); yS = yA
    f.mesh(M_CRYSTAL, R=roty(lt * 0.6), T=(AX, yA, -2.5), sc=0.85 * pop(lt, 0.15), emis=0.35)
    f.mesh(M_SUN, T=(SX, yS, -2.5), sc=0.85 * pop(lt, 0.45) * (1 + 0.03 * math.sin(lt * 5)), emis=0.75)
    ring(f, (SX, yS, -2.5), 2.1, (255, 200, 120), R=rotx(1.2) @ rotz(lt * 0.4), emis=0.9, alpha=170)
    f.label((AX, yA + 2.0, -2.5), 'GPT-6 Astra · 旗舰', 22, (200, 180, 255), dx=0, dy=-30, dot=False, a=ease((lt - 0.3) / 0.4))
    f.label((SX, yS + 1.9, -2.5), 'GPT-6.1 Sol · 新', 22, (255, 200, 140), dx=0, dy=-30, dot=False, a=ease((lt - 0.6) / 0.4))
    if e[1] < lt < e[2] + 0.4:
        A = win(lt, e[1] + 0.2, e[2] + 0.4)
        f.line([[AX + 1.6, yA, 0], [SX - 2.0, yS, 0]], (255, 255, 255, int(150 * A)), 3)
        f.label((0, yA, 0), '能力接近', 24, WHITE, dx=0, dy=-20, dot=False, a=A)
    if e[2] <= lt < e[5]:                                  # 价格柱：每百万 token
        sc = 0.085
        for x0, (pin, pout), col in ((AX, (10, 50), (150, 120, 255)), (SX, (2, 10), ORANGE)):
            g = ease((lt - e[3] + 0.3) / 1.0) if x0 == SX else ease((lt - e[2]) / 1.0)
            bar(f, x0 - 1.0, 1.0, pin * sc * g * 1.0 + 0.0, (90, 170, 255), 1.4, 0.3)
            bar(f, x0 + 1.0, 1.0, pout * sc * g, col, 1.4, 0.35)
            f.label((x0 - 1.0, pin * sc * g + 0.5, 1.0), f'${pin}', 22, (170, 210, 255), dx=0, dy=-10, dot=False, a=g)
            f.label((x0 + 1.0, pout * sc * g + 0.5, 1.0), f'${pout}', 22, WHITE, dx=0, dy=-10, dot=False, a=g)
        if lt > e[4]:                                       # 缓存输入
            g = ease((lt - e[4]) / 0.6); bar(f, SX + 3.0, 1.0, 0.12 + 0.0, (120, 255, 200), 1.4, 0.8)
            f.label((SX + 3.0, 0.6, 1.0), '缓存 $0.1', 20, (150, 255, 210), dx=0, dy=-26, dot=False, a=g)
        card(f, 40, 160, 300, 112, '每百万 token：输入 / 输出', '1/5', '价格', ORANGE, a=ease((lt - e[2]) / 0.4), note='蓝 = 输入 · 橙/紫 = 输出')
    if lt >= e[5]:
        osw = lt >= e[6]
        hA = 72.6 if osw else 70; hS = 70.5 if osw else 70
        g = ease((lt - e[5]) / 0.8)
        for x0, h, col in ((AX, hA, (150, 120, 255)), (SX, hS, ORANGE)):
            bar(f, x0, 1.0, h * 0.075 * g, col, 2.2, 0.35)
        if not osw:
            f.label((0, 5.2, 1.0), 'DeepSWE v1.1：打平', 26, WHITE, dx=0, dy=-10, dot=False, a=g)
            card(f, 40, 160, 330, 104, '软件工程测试 DeepSWE', 'Sol = Astra', '', ORANGE, a=g, vsz=34)
        else:
            f.label((AX, 72.6 * 0.075 + 1.4, 1.0), '72.6%', 24, WHITE, dx=0, dy=-8, dot=False, a=ease((lt - e[6]) / 0.4))
            f.label((SX, 70.5 * 0.075 + 1.4, 1.0), '70.5%', 24, WHITE, dx=0, dy=-8, dot=False, a=ease((lt - e[6]) / 0.4))
            card(f, 40, 160, 330, 104, '电脑操作 OSWorld 2.0', '只差 2.1', '分', ORANGE, a=ease((lt - e[6]) / 0.4), vsz=34)
            if lt > e[7]:                                   # 成本：7 块 vs 1 块
                for j in range(7):
                    x = ease((lt - e[7] - j * 0.08) / 0.4)
                    if x > 0: cube(f, (AX - 2.2, 0.55 + j * 0.85, 2.6), 0.75 * x, GOLD, 0.35)
                x = ease((lt - e[7]) / 0.4)
                if x > 0: cube(f, (SX + 2.2, 0.55, 2.6), 0.75 * x, GOLD, 0.35)
                f.label((AX - 2.2, 6.6, 2.6), '单任务成本 7', 20, GOLD, dx=0, dy=-10, dot=False, a=ease((lt - e[7] - 0.6) / 0.3))
                f.label((SX + 2.2, 1.6, 2.6), '1', 22, GOLD, dx=0, dy=-10, dot=False, a=ease((lt - e[7]) / 0.3))
    chrome(f, ACC, TAG); headline(f, lt, ORANGE, '2', 'GPT-6.1 Sol：接近 Astra，价格 1/5', '已在 API 与 ChatGPT 付费版上线 · 模型名 gpt-6.1-sol')
    return f


# =====================================================================
# 4 Ultrafast：光速隧道 + 速度表 → 6 倍价格 → 上线状态 → Pro 500 / Pro 200
# =====================================================================
def sc4(lt, d):
    k = 3; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[5]]
    if lt < e[5]:
        spd = lerp(6, 40, ease((lt - e[1]) / 2.0))
        z_cam = -(lt * 6 + max(0, lt - e[1]) ** 1.6 * 4.0)
        cam = Cam([0.4 * math.sin(lt * 0.5), 0.3 * math.cos(lt * 0.4), z_cam], [0.8 * math.sin(lt * 0.5 + 0.6), 0, z_cam - 30], 58)
        f = base(cam, lt, d, cuts)
        f.stars = True
        for j in range(1, 26):
            z = math.floor(z_cam / 5) * 5 - j * 5 - 6
            hue = (TEAL if j % 2 else BLUE)
            ring(f, (0, 0, z), 4.6, hue, R=rotz(z * 0.05) @ rotx(pi / 2), thick=False, emis=0.9, alpha=200)
        pts, cols = [], []
        for i in range(260):
            h = (i * 7919) % 1000 / 1000; h2 = (i * 104729) % 997 / 997
            ang = h * 2 * pi; r = 1.2 + 2.4 * h2
            zz = z_cam - ((i * 3.1 + lt * spd * 3) % 110)
            if zz > z_cam - 4: continue
            pts.append([r * math.cos(ang), r * math.sin(ang), zz]); cols.append((180, 255, 230, 220) if i % 3 else (255, 255, 255, 240))
        f.dots(pts, 0.05 + 0.001 * spd, cols)
        v = counter(lt, e[1], e[1] + 2.0, 40, 300) if lt > e[1] else '40'
        card(f, 40, 160, 300, 108, '生成速度（最高）', v, 'token/秒', TEAL, a=ease((lt - 0.2) / 0.4))
        if lt > e[2]:
            A = ease((lt - e[2]) / 0.4)
            for j, (nm, mult, mx) in enumerate([('Codex', 8, 8), ('API', 6, 8)]):
                y = 300 + j * 64; w = 260 * ease((lt - e[2] - j * 0.25) / 0.8) * mult / mx
                f.rect(40, y, 340, y + 46, (10, 16, 30, int(190 * A)), r=8)
                f.rect(44, y + 4, 44 + w, y + 42, (*TEAL, int(200 * A)), r=6)
                f.text(56, y + 23, f'{nm}  最高 {mult}×', 22, anc='lm', a=A, stroke=2)
        if lt > e[3]:
            A = ease((lt - e[3]) / 0.4)
            f.rect(40, 448, 340, 494, (60, 30, 10, int(200 * A)), r=8, outline=(*GOLD, int(200 * A)))
            f.text(56, 471, '代价：价格 ×6', 22, col=GOLD, anc='lm', a=A)
        if lt > e[4]:
            A = ease((lt - e[4]) / 0.4)
            f.text(1240, 470, '✓ GPT-6 Astra：今天可用', 22, col=GREEN, anc='rm', a=A, stroke=2)
            f.text(1240, 506, 'GPT-6.1 Sol：即将推出', 22, col=DIM, anc='rm', a=ease((lt - e[4] - 0.6) / 0.4), stroke=2)
        chrome(f, ACC, TAG); headline(f, lt, TEAL, '3', 'Ultrafast：付费的极速档', None)
        return f
    t = lt - e[5]
    cam = orbit(-0.1 + 0.03 * t, 12, 2.5, (1.2, 2.4, 0), 45)
    f = base(cam, lt, d, cuts)
    floor(f, -0.5, 30, 3, 30)
    s = pop(t, 0.1, 0.6)
    cp = np.array([-3.2, 3.2, 0]); R = roty(0.5 * math.sin(lt * 0.6)) @ rotx(-0.2)
    slab(f, cp, 6.0 * s, 3.7 * s, (55, 50, 75), R=R, emis=0.35)
    f.label(cp, 'PRO 500', 40, GOLD, dx=0, dy=14, dot=False, a=ease((t - 0.3) / 0.4))
    cube(f, cp + R @ np.array([0, -1.2 * s, 0.07]), (4.6 * s, 0.12, 0.03), GOLD, 0.8, R=R)
    f.label(cp + [0, -1.4, 0], '每月 500 美元', 24, GOLD, dx=0, dy=30, dot=False, a=ease((t - 0.2) / 0.4))
    if lt > e[6]:                                          # 25× 用量
        for i in range(25):
            x = ease((lt - e[6] - i * 0.03) / 0.35)
            if x > 0: cube(f, (2.0 + (i % 5) * 0.75, 0.4 + (i // 5) * 0.75, 0), 0.6 * x, TEAL, 0.4)
        cube(f, (6.6, 0.4, 0), 0.6 * ease((lt - e[6]) / 0.3), (150, 160, 180), 0.2)
        f.label((3.5, 4.4, 0), '用量 = 25 × Plus', 22, TEAL, dx=0, dy=-10, dot=False, a=ease((lt - e[6] - 0.5) / 0.3))
        f.label((6.6, 1.0, 0), 'Plus', 18, DIM, dx=0, dy=-12, dot=False, a=ease((lt - e[6]) / 0.3))
    if lt > e[7]:
        A = ease((lt - e[7]) / 0.5)
        card(f, 40, 470, 330, 104, '同时', 'Pro 200 重新开放', '', BLUE, a=A, vsz=30, note='每月 200 美元')
    chrome(f, ACC, TAG); headline(f, lt, TEAL, '3', '新套餐：Pro 500', '含 Ultrafast 极速档')
    return f


# =====================================================================
# 5 Codex 与 API：合上电脑云端照跑 → 语音 + 多智能体 → 安全扫描 → 电脑操作 / Decisions → AWS
# =====================================================================
FILES = [(x, z) for x in range(-4, 5) for z in range(-2, 3)]
BUGS = {3, 11, 19, 30, 38}


def laptop(f, P, ang, col=(170, 176, 188), screen=(30, 60, 70)):
    """ang：屏幕相对竖直的角度。-0.3 = 打开（略向后仰），pi/2 = 合上（盖在键盘上）。"""
    P = np.array(P, float)
    cube(f, P + [0, 0.08, 0], (3.2, 0.16, 2.2), col, 0.1)
    for r in range(3):                                         # 键盘
        for c in range(8): cube(f, P + [-1.2 + c * 0.34, 0.17, -0.5 + r * 0.36], (0.26, 0.03, 0.26), (60, 64, 72), 0.05)
    R = rotx(ang)
    hinge = P + np.array([0, 0.21, -1.05])
    f.mesh(M_BOX, R=R @ np.diag([3.2, 2.1, 0.08]), T=hinge + R @ np.array([0, 1.05, -0.04]), col=col, emis=0.1)
    if ang < 1.35: f.mesh(M_BOX, R=R @ np.diag([2.9, 1.8, 0.02]), T=hinge + R @ np.array([0, 1.05, 0.01]), col=screen, emis=0.7 * (1 - ang / 1.6))


def sc5(lt, d):
    k = 4; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[3], e[5], e[7], e[9], e[10], e[12]]
    if lt < e[3]:
        cam = orbit(0.15 + 0.03 * lt, 17, 5, (0.5, 1.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30, 3, 32)
        lid = lerp(-0.3, pi / 2, ease((lt - e[2] - 0.2) / 1.1))
        laptop(f, (-5, 0, 1), lid)
        for j in range(3): f.mesh(M_RACK, T=(3.2 + j * 2.4, 2.0, -1.0), sc=1.0, emis=0.05)
        cloud_y = 5.2
        ring(f, (5.6, cloud_y, -1.0), 2.4, (150, 200, 255), R=rotx(pi / 2), emis=0.6, alpha=120)
        f.label((5.6, 4.6, -1.0), '云端环境', 22, (170, 210, 255), dx=0, dy=-40, dot=False, a=ease((lt - e[1]) / 0.4))
        f.label((-5, 2.6, 1), '本地电脑', 20, DIM, dx=0, dy=-50, dot=False, a=ease(lt / 0.4))
        if lt > e[1]:                                       # 任务飞向云端
            x = ease((lt - e[1]) / 1.0)
            P = np.array([-5, 2.0, 0.5]) * (1 - x) + np.array([5.6, 4.6, -1.0]) * x + np.array([0, math.sin(pi * x) * 2, 0])
            cube(f, P, 0.6, TEAL, 0.7)
            prog = clamp((lt - e[1] - 1.0) / (d - e[1] - 1.5))
            cube(f, (5.6, 0.25, 1.4), (7.0, 0.18, 0.3), (40, 50, 64), 0.1)
            if prog > 0: cube(f, (5.6 - 3.5 + 3.5 * prog, 0.3, 1.45), (7.0 * prog, 0.2, 0.3), TEAL, 0.7)
        if lt > e[2]:
            f.label((-5, 0.8, 1), '合上了，任务继续', 22, TEAL, dx=0, dy=75, dot=False, a=ease((lt - e[2] - 0.6) / 0.4))
        chrome(f, ACC, TAG); headline(f, lt, PURPLE, '4', 'Codex：搬到云端', '用手机也能远程操控')
        return f
    if lt < e[5]:
        t = lt - e[3]
        cam = orbit(-0.2 + 0.04 * t, 15, 3.5, (0, 2.6, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30, 3, 30)
        slab(f, (0, 3.0, -1.0), 7.0, 4.0, (14, 20, 30), emis=0.1)
        for j in range(6):
            w = 1.5 + 3.5 * ((j * 37) % 10) / 10; on = ease((t - j * 0.2) / 0.3)
            if on > 0: cube(f, (-3.1 + w / 2, 4.4 - j * 0.5, -0.9), (w * on, 0.16, 0.03), (90, 230, 160) if j == 0 else (120, 140, 160), 0.6)
        for j in range(24):                                 # 语音波形
            h = 0.2 + 1.2 * abs(math.sin(lt * 7 + j * 0.7)) * math.sin(pi * j / 23) * win(lt, e[3], e[4] + 0.6)
            cube(f, (-3.0 + j * 0.26, 0.4 + h / 2, 1.6), (0.14, h, 0.14), TEAL, 0.6)
        f.label((0, 0.5, 1.6), '语音下指令', 22, TEAL, dx=0, dy=40, dot=False, a=win(lt, e[3] + 0.3, e[4] + 0.6))
        if lt > e[4]:
            for j in range(4):
                x = ease((lt - e[4] - j * 0.15) / 0.7); q = np.array([(j - 1.5) * 2.8, 6.4, 0.5])
                P = np.array([0, 3.0, -0.9]) * (1 - x) + q * x
                f.mesh(M_BALL, T=P, sc=0.45, col=[BLUE, PURPLE, TEAL, GOLD][j], emis=0.6)
                f.line([[0, 4.9, -0.9], P], (180, 200, 255, 140), 2)
            f.label((0, 7.4, 0.5), '/agents：同时调度多个智能体', 22, WHITE, dx=0, dy=-20, dot=False, a=ease((lt - e[4] - 0.5) / 0.4))
        chrome(f, ACC, TAG); headline(f, lt, PURPLE, '4', 'Codex 命令行工具焕新', None)
        return f
    if lt < e[7]:
        t = lt - e[5]
        cam = orbit(0.5 + 0.04 * t, 15, 9, (0, 0, 0), 45)
        f = base(cam, lt, d, cuts)
        sweep = lerp(-6, 6, clamp(t / (e[6] - e[5] + 0.3)))
        fixed = lt > e[6] + 0.6
        for i, (x, z) in enumerate(FILES):
            bad = i in BUGS and x * 1.3 < sweep
            col = (GREEN if fixed else RED) if bad else (70, 90, 120)
            h = 0.3 + 0.25 * ((i * 13) % 5)
            cube(f, (x * 1.3, h / 2, z * 1.3), (1.0, h, 1.0), col, 0.5 if bad else 0.15)
        f.layer()
        if not fixed: slab(f, (sweep, 1.5, 0), 0.06, 3.0, (120, 200, 255), R=roty(pi / 2) @ np.diag([2.5, 1, 1]), emis=0.9, alpha=120)
        found = sum(1 for i in BUGS if FILES[i][0] * 1.3 < sweep)
        card(f, 40, 160, 320, 104, 'Codex Security Cloud', f'{found} 处漏洞' if not fixed else '已备好修复', '', RED if not fixed else GREEN, a=ease(t / 0.4), vsz=32,
             note=None)
        chrome(f, ACC, TAG); headline(f, lt, PURPLE, '4', '安全扫描：整库定时检查', '电脑合上也在云端跑')
        return f
    if lt < e[9]:
        t = lt - e[7]
        cam = orbit(-0.15 + 0.03 * t, 11.5, 2.5, (0.8 if lt > e[8] else 0, 2.8, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30, 3, 28)
        if lt < e[8]:
            slab(f, (0, 3.0, 0), 8.0, 4.6, (20, 28, 44), emis=0.1)
            btns = [(-2.5, 4.2), (1.0, 3.2), (2.6, 1.6), (-1.5, 1.8)]
            for (bx, by) in btns: cube(f, (bx, by, 0.08), (1.8, 0.6, 0.04), (60, 90, 140), 0.4)
            tt = (lt - e[7]) / 0.9; i0 = int(tt) % 4; x = ease(tt % 1)
            a_, b_ = btns[i0], btns[(i0 + 1) % 4]; cx, cy = lerp(a_[0], b_[0], x), lerp(a_[1], b_[1], x)
            cube(f, (cx + 0.15, cy - 0.2, 0.3), (0.18, 0.5, 0.05), WHITE, 0.8, R=rotz(0.5))
            if x > 0.85: ring(f, (cx, cy, 0.2), 0.3 + (x - 0.85) * 4, TEAL, emis=1.0)
            f.label((0, 5.6, 0), 'Agents API：电脑操作', 24, WHITE, dx=0, dy=-20, dot=False, a=ease(t / 0.4))
        else:
            t2 = lt - e[8]
            x = ease(t2 / 0.8); cube(f, (lerp(-6, -1.5, x), 2.5, 0), 0.9, (200, 210, 230), 0.4)
            ring(f, (-0.8, 2.5, 0), 1.0, PURPLE, R=roty(pi / 2), thick=True, emis=0.8)
            outs = [('A  92%', 4.4, TEAL), ('B   6%', 2.5, (120, 130, 150)), ('C   2%', 0.6, (120, 130, 150))]
            for j, (nm, y, col) in enumerate(outs):
                g = ease((t2 - 0.8 - j * 0.15) / 0.6)
                f.line([[-0.2, 2.5, 0], [lerp(-0.2, 4.0, g), lerp(2.5, y, g), 0]], (*col, 220), 3)
                if g > 0.95: f.label((4.3, y, 0), nm, 22, col, dx=20, dy=8, dot=False)
            f.label((0, 5.6, 0), 'Decisions API：带置信度的快速决策', 24, WHITE, dx=0, dy=-20, dot=False, a=ease(t2 / 0.4))
        chrome(f, ACC, TAG); headline(f, lt, PURPLE, '4', 'API：让智能体动手', None)
        return f
    if lt < e[10]:                                         # OpenAI × 亚马逊
        t = lt - e[9]
        cam = orbit(0.05 * math.sin(t), 14, 2, (0, 1.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, -0.4, 30, 3, 28)
        f.mesh(M_BALL, T=(-3.6, 1.5, 0), sc=1.4 * pop(t, 0.1), col=TEAL, emis=0.5)
        f.mesh(M_BALL, T=(3.6, 1.5, 0), sc=1.4 * pop(t, 0.4), col=ORANGE, emis=0.5)
        f.label((-3.6, 0, 0), 'OpenAI', 26, TEAL, dx=0, dy=40, dot=False, a=ease(t / 0.4))
        f.label((3.6, 0, 0), 'Amazon 亚马逊', 26, ORANGE, dx=0, dy=40, dot=False, a=ease((t - 0.3) / 0.4))
        f.label((0, 1.5, 0), '×', 48, WHITE, dx=0, dy=16, dot=False, a=ease((t - 0.6) / 0.3))
        chrome(f, ACC, TAG); headline(f, lt, PURPLE, '4', 'OpenAI × 亚马逊', None)
        return f
    if lt < e[12]:                                         # AWS 是什么：一座座数据中心
        t = lt - e[10]
        cam = orbit(0.6 + 0.05 * t, 22, 8, (0, 1.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30, 3, 28)
        for r in range(3):
            for c in range(7):
                f.mesh(M_RACK, T=((c - 3) * 2.3, 2.0, (r - 1) * 3.4), sc=1.0 * pop(t, 0.05 * (r * 7 + c) * 0.4), emis=0.05)
        if lt > e[11]:                                     # 企业数据 / 系统 落进机房
            for j, (x, z, col) in enumerate([(-5, -3.4, BLUE), (-1.5, 0, GOLD), (2.5, 3.4, GREEN), (5.5, -3.4, PURPLE), (0.5, -3.4, TEAL)]):
                g = ease((lt - e[11] - j * 0.25) / 0.6)
                for q in range(3):
                    f.mesh(disc(0.6, 0.25, col), T=(x, 4.6 + q * 0.32 + (1 - g) * 4, z), emis=0.5, alpha=int(255 * g))
            f.label((0, 6.2, 0), '企业的数据库、业务系统', 22, WHITE, dx=0, dy=-30, dot=False, a=ease((lt - e[11] - 0.5) / 0.4))
        card(f, 40, 160, 360, 112, 'AWS = Amazon Web Services', '亚马逊云服务', '', ORANGE, a=ease(t / 0.4), vsz=30, note='全球最大的云计算平台')
        chrome(f, ACC, TAG); headline(f, lt, PURPLE, '4', 'AWS 是什么？', '把服务器"租"给企业的云平台')
        return f
    t = lt - e[12]                                         # Bedrock：智能体进 AWS，数据不出门
    cam = orbit(0.1 + 0.04 * t, 17, 6, (0, 1.0, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, -0.4, 30, 3, 28)
    f.mesh(disc(3.0, 0.4, TEAL), T=(-4.8, -0.4, 0), emis=0.35); f.mesh(disc(3.6, 0.4, ORANGE), T=(4.8, -0.4, 0), emis=0.35)
    f.mesh(M_BOX, R=np.diag([3.6, 0.15, 1.2]), T=(0, 0, 0), col=(80, 90, 110), emis=0.1)
    for q in range(3): f.mesh(disc(0.8, 0.3, GOLD), T=(6.2, 0.2 + q * 0.4, -1.2), emis=0.5)
    f.label((6.2, 1.4, -1.2), '企业数据', 18, GOLD, dx=0, dy=-24, dot=False, a=ease(t / 0.4))
    for j in range(5):
        ph = ((lt - e[12]) * 0.5 + j / 5) % 1
        x = lerp(-4.8, 4.0, ph); f.mesh(M_BALL, T=(x, 0.8 + 0.8 * math.sin(pi * ph), 0), sc=0.4, col=[BLUE, PURPLE, TEAL, GOLD, GREEN][j], emis=0.6)
    ring(f, (4.8, 0.2, 0), 3.4, ORANGE, R=I3, thick=True, emis=0.7, alpha=int(200 * ease((lt - e[13]) / 0.5)))
    f.label((-4.8, 0.2, 0), 'OpenAI 智能体', 22, TEAL, dx=0, dy=50, dot=False, a=ease(t / 0.4))
    f.label((4.8, 0.2, 0), 'AWS Bedrock', 22, ORANGE, dx=0, dy=50, dot=False, a=ease((t - 0.3) / 0.4))
    f.label((4.8, 3.6, 0), '数据留在 AWS 内', 22, GREEN, dx=0, dy=-20, dot=False, a=ease((lt - e[13] - 0.3) / 0.4))
    card(f, 40, 160, 330, 104, 'Bedrock 托管智能体', '直接部署', '', ORANGE, a=ease(t / 0.4), vsz=30, note='Bedrock：AWS 上的 AI 模型平台')
    chrome(f, ACC, TAG); headline(f, lt, PURPLE, '4', 'OpenAI 智能体进驻 AWS', None)
    return f


# =====================================================================
# 6 ChatGPT 平台：插件插槽 → 侧边栏 → MCP 事件链 → Space 共享空间 + Pages 共写 → 协作幻灯片
# =====================================================================
def sc6(lt, d):
    k = 5; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[3], e[5]]
    if lt < e[3]:
        cam = orbit(0.3 + 0.05 * lt, 16, 7, (0, 1.2, 0), 45)
        f = base(cam, lt, d, cuts)
        f.mesh(disc(5.0, 0.5, (20, 30, 40)), T=(0, -0.5, 0), emis=0.1)
        ring(f, (0, 0.05, 0), 5.0, TEAL, R=I3, thick=True, emis=0.9)
        f.label((0, -0.3, 5.2), 'ChatGPT', 24, TEAL, dx=0, dy=40, dot=False, a=ease(lt / 0.4))
        for j in range(8):
            ang = j * pi / 4; P = np.array([3.9 * math.cos(ang), 0, 3.9 * math.sin(ang)])
            cube(f, P + [0, 0.05, 0], (0.95, 0.1, 0.95), (50, 60, 75), 0.1)
            x = ease((lt - e[1] - j * 0.18) / 0.5)
            if x > 0: cube(f, P + [0, 0.45 + (1 - x) * 4, 0], 0.8, APP_COL[j], 0.4)
        f.label((0, 4.0, 0), '插件扩展', 22, WHITE, dx=0, dy=-10, dot=False, a=win(lt, e[1], e[2] + 0.2))
        if lt > e[2]:
            x = ease((lt - e[2]) / 0.6)
            slab(f, (-0.9, 1.9 * x + 0.3, -0.6), 3.4, 2.6 * x, (26, 34, 50), emis=0.15)
            slab(f, (1.9, 1.9 * x + 0.3, -0.6), 1.6, 2.6 * x, (16, 60, 60), emis=0.35)
            for j in range(3): cube(f, (1.9, (2.6 - j * 0.6) * x + 0.3, -0.52), (1.2, 0.3 * x, 0.04), (90, 210, 180), 0.6)
            f.label((1.9, 3.6 * x, -0.6), '侧边栏交互面板', 22, (150, 255, 220), dx=40, dy=-30, a=x)
        chrome(f, ACC, TAG); headline(f, lt, GREEN, '5', 'ChatGPT 变成平台', '开发者可在 ChatGPT 内做原生体验')
        return f
    if lt < e[5]:
        t = lt - e[3]
        cam = orbit(-0.1 + 0.04 * t, 16, 4, (0, 2.0, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30, 3, 30)
        slab(f, (-5.0, 2.4, 0), 3.0, 3.6, (24, 30, 44), emis=0.1)
        x = ease(t / 0.6); cube(f, (-5.0, lerp(7, 3.2, x), 0.12), (2.2, 0.7, 0.06), GOLD, 0.6)
        f.label((-5.0, 4.6, 0), '新任务进来', 20, GOLD, dx=0, dy=-30, dot=False, a=x)
        if t > 0.6:
            rr = ((t - 0.6) * 4) % 6; ring(f, (-5.0, 3.2, 0.1), 0.5 + rr, GOLD, emis=0.9, alpha=int(200 * (1 - rr / 6)))
        steps = ['读取文档', '起草计划', '完成']
        for j, nm in enumerate(steps):
            g = ease((lt - e[4] - j * 0.6) / 0.4); P = np.array([-0.8 + j * 3.4, 2.4, 0])
            f.mesh(M_BALL, T=P, sc=0.75, col=GREEN if g > 0.5 else (70, 80, 100), emis=0.6 * g + 0.1)
            if j: f.line([P - [3.4, 0, 0], P - [3.4 - 3.4 * g, 0, 0]], (120, 255, 160, 220), 4)
            f.label(P, nm, 20, WHITE if g > 0.5 else DIM, dx=0, dy=-46, dot=False, a=ease((lt - e[3]) / 0.4))
        f.line([[-3.4, 2.4, 0], [-1.6, 2.4, 0]], (255, 210, 120, int(200 * ease((lt - e[4]) / 0.3))), 4)
        card(f, 40, 160, 300, 104, '插件自动化', 'MCP 事件', '', GOLD, a=ease(t / 0.4), vsz=34, note='人不在，也能自动开工')
        chrome(f, ACC, TAG); headline(f, lt, GREEN, '5', 'ChatGPT 变成平台', None)
        return f
    t = lt - e[5]
    cam = orbit(0.2 + 0.05 * t, 18, 6, (0, 2.2, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, 0, 30, 3, 34)
    for j in range(8):                                   # 环绕的 Pages
        ang = j * pi / 4 + lt * 0.12; P = np.array([7.5 * math.cos(ang), 3.5 + 0.4 * math.sin(lt + j), 7.5 * math.sin(ang)])
        slab(f, P, 1.6, 2.1, (40, 60, 80), R=roty(-ang - pi / 2), emis=0.25, alpha=200)
    page = np.array([0, 3.0, 0])
    slab(f, page, 4.2, 5.0, (235, 238, 245), emis=0.25)
    who = [((-3.8, 0, 2.4), (230, 170, 120), '你和同事'), ((3.8, 0, 2.4), TEAL, 'ChatGPT'), ((0, 0, 4.2), (60, 140, 255), '你的 Dot')]
    for j, (P, col, nm) in enumerate(who):
        g = ease((lt - e[7] - j * 0.25) / 0.4)
        if j == 0: f.mesh(M_PERSON, T=P, sc=1.2 * g, col=(210, 200, 190))
        elif j == 1: f.mesh(M_BALL, T=np.array(P) + [0, 1.5, 0], sc=0.8 * g, col=col, emis=0.7)
        else: avatar(f, np.array(P) + [0, 1.5, 0], col, 0.8 * g)
        f.label(np.array(P) + [0, 0.2, 0], nm, 20, col, dx=0, dy=40, dot=False, a=g)
    if lt > e[8]:                                        # 三方在同一页写字
        n = int(ease((lt - e[8]) / 2.2) * 9)
        for i in range(n):
            col = [(230, 150, 100), TEAL, (60, 140, 255)][i % 3]
            w = 3.0 - ((i * 7) % 4) * 0.4
            cube(f, (-1.7 + w / 2, 4.8 - i * 0.45, 0.08), (w, 0.16, 0.03), col, 0.4)
    if lt > e[9]:
        for j in range(3):
            g = ease((lt - e[9] - j * 0.15) / 0.5)
            slab(f, (4.2 + j * 0.5, 4.8 + j * 0.3, -1.5 - j * 0.2), 2.6 * g, 1.6 * g, [ORANGE, BLUE, PURPLE][j], R=roty(-0.3), emis=0.4)
        f.label((5.0, 6.3, -1.8), '协作幻灯片 · 几周内上线', 20, ORANGE, dx=20, dy=-20, a=ease((lt - e[9] - 0.4) / 0.4))
    card(f, 40, 160, 320, 104, '团队协作', 'Space + Pages', '', GREEN, a=ease(t / 0.4), vsz=32, note='人和智能体共写一份文档')
    chrome(f, ACC, TAG); headline(f, lt, GREEN, '5', 'ChatGPT Space：共享空间', None)
    return f


# =====================================================================
# 7 场外背景：IPO 上锁 → 会场外抗议 → 估值硬币塔
# =====================================================================
M_SHACKLE = torus(0.9, 0.16, (200, 205, 215), 24, 8, arc=pi)


def sc7(lt, d):
    k = 6; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[4], e[5]]
    if lt < e[4]:
        cam = orbit(-0.2 + 0.04 * lt, 13, 2.5, (0, 2.4, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30, 3, 30)
        slab(f, (0, 3.6, -1.5), 8.0, 4.2, (18, 24, 34), emis=0.1)
        f.label((0, 4.2, -1.4), 'IPO', 60, (120, 140, 170), dx=0, dy=20, dot=False, a=ease(lt / 0.5))
        drop = ease((lt - e[3]) / 0.4)
        lp_ = np.array([0, 2.2, 0.8])
        cube(f, lp_, (1.8, 1.5, 0.6), GOLD, 0.4)
        f.mesh(M_SHACKLE, R=rotx(pi / 2) @ rotz(0) @ rotx(-pi / 2) @ roty(0), T=lp_ + [0, 0.75 + 0.6 * (1 - drop), 0], col=(200, 205, 215), emis=0.2)
        f.mesh(M_SHACKLE, R=rotx(-pi / 2) @ rotx(pi / 2), T=lp_ + [0, 0.75 + 0.6 * (1 - drop), 0], col=(200, 205, 215), emis=0.2)
        f.label(lp_ + [0, -1.2, 0], '安全承诺到位之前：不上市', 24, GOLD, dx=0, dy=40, dot=False, a=ease((lt - e[2]) / 0.4))
        card(f, 40, 160, 300, 104, '奥特曼 · 会后答记者', '暂无时间表', '', GOLD, a=ease((lt - e[1]) / 0.4), vsz=32)
        chrome(f, ACC, TAG); headline(f, lt, GOLD, '6', '场外：安全、上市与资本', None)
        return f
    if lt < e[5]:
        t = lt - e[4]
        cam = orbit(0.6 + 0.08 * t, 22, 9, (0, 1.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30, 3, 28)
        cube(f, (0, 2.0, -3), (10, 4, 5), (60, 66, 80), 0.1)
        for j in range(5): cube(f, (-4 + j * 2, 2.4, -0.48), (1.2, 1.6, 0.05), (255, 210, 140), 0.6)
        for j in range(16):
            ang = -pi * 0.1 + j * pi * 1.2 / 15; r = 7.5 + 0.6 * (j % 2)
            P = np.array([r * math.cos(ang), 0, -3 + r * math.sin(ang) * 0.7 + 3.5])
            hop = 0.15 * abs(math.sin(lt * 3 + j))
            f.mesh(M_PERSON, T=P + [0, hop, 0], sc=0.9, col=(170 + (j * 13) % 60, 160, 150))
            cube(f, P + [0, 2.2 + hop, 0], (1.1, 0.7, 0.05), (240, 240, 230), 0.3, R=roty(-ang + pi / 2))
        f.label((0, 4.6, -3), 'DevDay 会场', 20, DIM, dx=0, dy=-30, dot=False, a=ease(t / 0.4))
        f.label((6.5, 3.5, 4), '“PEOPLE OVER PROFIT”', 22, (255, 230, 200), dx=20, dy=-20, a=ease((t - 0.3) / 0.4))
        chrome(f, ACC, TAG); headline(f, lt, GOLD, '6', '会场外有抗议', None)
        return f
    t = lt - e[5]
    cam = orbit(-0.4 + 0.05 * t, 16, 5, (0, 3.5, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, 0, 30, 3, 30)
    n = int(ease((lt - e[6] + 0.5) / 2.0) * 28)
    for i in range(n): f.mesh(M_COIN, T=(-2.2 + 0.05 * math.sin(i), 0.2 + i * 0.24, 0), sc=1.3, col=GOLD, emis=0.3)
    m = int(ease((lt - e[7]) / 1.0) * 7)
    for i in range(m): f.mesh(M_COIN, T=(2.4, 0.2 + i * 0.24, 0.5), sc=1.0, col=(255, 220, 120), emis=0.4)
    f.label((-2.2, 0.2 + max(n, 1) * 0.24 + 0.5, 0), '估值 约1.4万亿美元', 22, GOLD, dx=0, dy=-20, dot=False, a=ease((lt - e[6]) / 0.4))
    f.label((2.4, 0.2 + max(m, 1) * 0.24 + 0.5, 0.5), '新融资 300亿美元', 20, (255, 225, 150), dx=0, dy=-20, dot=False, a=ease((lt - e[7]) / 0.4))
    card(f, 40, 160, 300, 104, '据彭博社报道', '融资洽谈中', '', GOLD, a=ease(t / 0.4), vsz=32, note='尚未官宣')
    chrome(f, ACC, TAG); headline(f, lt, GOLD, '6', '资本：估值或达 1.4 万亿美元', None)
    return f


# =====================================================================
# 8 收尾：五件回顾转盘 → 聊天 → 干活 → 第二天：Gemini 4 Argon 同价 → 下一条
# =====================================================================
def sc8(lt, d):
    k = 7; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[5], e[7]]
    blink = max(0, 1 - abs(((lt * 0.7) % 3.1) - 0.1) / 0.1)
    if lt < e[5]:
        cur = min(4, sum(1 for i in range(5) if lt >= e[i]) - 1) if lt >= e[0] else 0
        prev = max(0, cur - 1); x = ease((lt - e[cur]) / 0.6) if cur else 1
        rot = -(prev + (cur - prev) * x) * 2 * pi / 5
        cam = orbit(0.0, 14, 3.0, (0, 1.6, 4.0), 45)
        f = base(cam, lt, d, cuts); floor(f, -0.5, 30, 3, 26)
        names = ['Dots 永远在线', 'Sol 价格 1/5', 'Ultrafast 300 token/秒', 'Codex 上云', 'ChatGPT 平台化']
        for i in range(5):
            ang = rot + i * 2 * pi / 5; P = np.array([5.0 * math.sin(ang), 1.6, 5.0 * math.cos(ang)])
            hi = i == cur
            if i == 0: avatar(f, P, (60, 140, 255), 1.0, blink=blink)
            elif i == 1: f.mesh(M_SUN, T=P, sc=0.6, emis=0.8)
            elif i == 2: ring(f, P, 1.1, TEAL, R=rotx(0.3) @ roty(lt), thick=True, emis=0.9)
            elif i == 3: f.mesh(M_RACK, T=P, sc=0.55, emis=0.05)
            else:
                f.mesh(disc(1.2, 0.25, (20, 30, 40)), T=P - [0, 0.2, 0], emis=0.1); ring(f, P, 1.2, TEAL, thick=True, emis=0.9)
            if hi: f.label(P + [0, -1.6, 0], names[i], 24, WHITE, dx=0, dy=30, dot=False, a=ease((lt - e[i]) / 0.3) if lt >= e[i] else 1)
        chrome(f, ACC, TAG); headline(f, lt, ACC, None, '总结：DevDay 2026')
        return f
    if lt < e[7]:
        t = lt - e[5]
        cam = orbit(0.1 * math.sin(t * 0.5), 13, 2.5, (0, 2.0, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, -0.5, 30, 3, 26)
        g = ease((lt - e[6]) / 1.0)
        bub = np.array([-3.5, 2.6, 0]); sb = lerp(1.0, 0.35, g)
        slab(f, bub, 3.6 * sb, 2.2 * sb, (230, 235, 245), emis=0.3)
        for j in range(3): cube(f, bub + [(-0.9 + j * 0.9) * sb, 0, 0.08], 0.3 * sb, (60, 70, 90), 0.2)
        f.label(bub + [0, -1.8 * sb, 0], '会聊天', 22, DIM, dx=0, dy=30, dot=False, a=1 - g * 0.5)
        P = np.array([3.0, 2.2, 0]); sa = lerp(0.5, 1.3, g)
        avatar(f, P, (60, 140, 255), sa, blink=blink)
        for j in range(5):
            ang = lt * 1.2 + j * 2 * pi / 5
            cube(f, P + np.array([2.2 * sa * math.cos(ang), 0.5 * math.sin(ang * 2), 2.2 * sa * math.sin(ang)]), 0.35 * sa, APP_COL[j], 0.5)
        f.label(P + [0, -2.4 * sa, 0], '持续替你干活', 24, (120, 190, 255), dx=0, dy=30, dot=False, a=g)
        chrome(f, ACC, TAG); headline(f, lt, ACC, None, '押注方向：从聊天到干活')
        return f
    t = lt - e[7]
    cam = orbit(-0.15 + 0.04 * t, 14, 3.0, (0, 2.4, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, -0.5, 30, 3, 26)
    flip = ease((t - 0.3) / 0.6)
    cal = np.array([-4.8, 3.0, 0])
    slab(f, cal, 2.8, 2.8, (240, 240, 245), emis=0.3, R=rotx(-pi * flip if flip < 0.5 else -pi * (1 - flip)) if 0 < flip < 1 else I3)
    cube(f, cal + [0, 1.25, 0.08], (2.8, 0.5, 0.05), RED, 0.4)
    f.label(cal, '9月29日' if flip < 0.5 else '9月30日', 30, (30, 30, 40), dx=0, dy=14, dot=False, a=1 if abs(flip - 0.5) > 0.15 else 0)
    gp = np.array([0.5, 3.0, 0])
    gcols = [(66, 133, 244), (234, 67, 53), (251, 188, 5), (52, 168, 83)]
    if lt > e[8] - 0.2:
        g = pop(lt, e[8] - 0.2, 0.6)
        f.mesh(M_BALL, T=gp, sc=1.0 * g, col=(235, 240, 255), emis=0.5)
        for j in range(4):
            ang = lt * 1.6 + j * pi / 2
            f.mesh(M_BALL, T=gp + np.array([1.9 * math.cos(ang), 0.5 * math.sin(ang), 1.9 * math.sin(ang)]) * g, sc=0.35 * g, col=gcols[j], emis=0.6)
        f.label(gp + [0, 1.9, 0], 'Gemini 4 Argon', 26, WHITE, dx=0, dy=-20, dot=False, a=ease((lt - e[8]) / 0.4))
    sp = np.array([5.2, 3.0, 0])
    f.mesh(M_SUN, T=sp, sc=0.6, emis=0.8)
    f.label(sp + [0, 1.6, 0], 'GPT-6.1 Sol', 22, (255, 200, 140), dx=0, dy=-20, dot=False, a=ease(t / 0.4))
    if lt > e[9]:
        A = ease((lt - e[9]) / 0.4)
        f.label(gp + [0, -1.7, 0], '$2 / $10', 26, WHITE, dx=0, dy=30, dot=False, a=A)
        f.label(sp + [0, -1.7, 0], '$2 / $10', 26, WHITE, dx=0, dy=30, dot=False, a=A)
        f.label((2.85, 1.3, 0), '=', 40, GOLD, dx=0, dy=20, dot=False, a=A)
    if lt > e[10]:
        A = ease((lt - e[10]) / 0.5)
        f.rect(390, 560, 890, 608, (*ACC, int(225 * A)), r=10)
        f.text(640, 584, '下一条：Gemini 4 Argon 发布', 26, anc='mm', a=A)
    chrome(f, ACC, TAG); headline(f, lt, ACC, None, '第二天，谷歌出手')
    return f


FILM = Film(SEG, dur, [sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8], SUBS,
            chapters=['开场', 'Dots', 'GPT-6.1 Sol', 'Ultrafast', 'Codex 与 API', 'ChatGPT 平台', '场外', '总结'],
            total=TOTAL, lead=0.15)
