"""AI 早报特别篇 · 具身智能国际前沿（约 3.5 分钟）
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
SUBS = [[(a, b - 0.2 if i + 1 < len(s) else b, t) for i, (a, b, t) in enumerate(s)] for s in TM['subs']]
def _merge_short(s, m=0.8):                               # 过短字幕并入下一句（只影响显示）
    out = []
    i = 0
    while i < len(s):
        a, b, t = s[i]
        if b - a < m and i + 1 < len(s):
            a2, b2, t2 = s[i + 1]; out.append((a, b2, t + '，' + t2)); i += 2
        else: out.append((a, b, t)); i += 1
    return out
DISP = [_merge_short(s) for s in SUBS]
TOTAL = SEG[-1] + dur[-1] + 2.4
def ev(k, i): return SUBS[k][i][0]

ACC = (255, 140, 60); TAG = '具身智能 · 国际前沿 · 信息截至 10月1日'
CYAN = (70, 200, 255); GREEN = (80, 220, 120); RED = (240, 80, 80); GOLD = (245, 190, 70)
PURPLE = (160, 110, 255); BLUE = (80, 140, 255); CN = (235, 80, 70); GREY = (120, 130, 150)
STEEL = (200, 206, 216); DARK = (40, 46, 58)

M_BOX = box(1, 1, 1, WHITE)
M_BALL = sphere(1, WHITE, 18, 10)
M_BALL_S = sphere(1, WHITE, 10, 6)
M_PANEL = panel(1, 1)
M_RACK = rack(led=(255, 160, 80))
M_PERSON = person((150, 160, 180))
M_COIN = coin(1.0)
M_RING = torus(1, 0.06, WHITE, 48, 6)


def base(cam, lt, d, cuts=()):
    f = Fr(cam); f.dim = min(ease(lt / 0.3), 1 - ease((lt - d - 0.02) / 0.32), dip(lt, cuts)); return f
def cube(f, P, s, col, emis=0.15, alpha=255, R=I3):
    f.mesh(M_BOX, R=R @ np.diag(s if hasattr(s, '__len__') else [s, s, s]), T=P, col=col, emis=emis, alpha=alpha)
def bar(f, x, z, h, col, w=1.0, emis=0.25):
    if h > 0.01: cube(f, (x, h / 2, z), (w, h, w), col, emis)
def floor(f, y=0.0, a=34):
    f.grid(y, 30, 3, (255, 170, 110, a)); f.layer()
def lab(f, P, s, sz=20, col=WHITE, dy=-10, a=1.0):
    f.label(P, s, sz, col, dx=0, dy=dy, dot=False, a=a)


# ---------------------------------------------------------------------
# 带关节的人形机器人（正向运动学）
#   walk：步态相位（弧度，None = 站立）；arms：(左肩, 右肩, 左肘, 右肘) 前摆角；glow：高亮部位集合
# ---------------------------------------------------------------------
def robot(f, P, yaw=0.0, s=1.0, walk=None, arms=None, col=STEEL, accent=ACC, glow=(), alpha=255, emis=0.12, wave=0.0):
    P = np.array(P, float); Y = roty(yaw)
    ph = walk if walk is not None else 0.0
    amp = 0.45 if walk is not None else 0.0
    bob = abs(math.sin(ph)) * 0.03 * s if walk is not None else 0.0
    pel = P + np.array([0, 0.98 * s + bob, 0])
    def seg(top, ang_x, L, w, d, c, key, ang_z=0.0):
        R = Y @ rotz(ang_z) @ rotx(ang_x)
        e_ = 0.9 if key in glow else emis
        cc = accent if key in glow else c
        f.mesh(M_BOX, R=R @ np.diag([w * s, L * s, d * s]), T=top + R @ np.array([0, -L * s / 2, 0]), col=cc, emis=e_, alpha=alpha)
        return top + R @ np.array([0, -L * s, 0])
    # 腿
    for side, sg in (('l', 1), ('r', -1)):
        a = amp * math.sin(ph + (0 if sg > 0 else pi))
        knee = max(0.0, -amp * 1.3 * math.sin(ph + (0 if sg > 0 else pi) - 0.9)) if walk is not None else 0.0
        hip = pel + Y @ np.array([0.11 * s * sg, 0, 0])
        k = seg(hip, -a, 0.46, 0.13, 0.15, col, 'leg')
        ank = seg(k, -a + knee, 0.46, 0.11, 0.13, col, 'leg')
        cube(f, ank + Y @ np.array([0, -0.03 * s, 0.05 * s]), (0.12 * s, 0.06 * s, 0.24 * s), DARK, 0.9 if 'leg' in glow else 0.1, alpha, R=Y)
    # 躯干与头
    cube(f, pel + Y @ np.array([0, 0.05 * s, 0]), (0.32 * s, 0.14 * s, 0.2 * s), DARK, 0.1, alpha, R=Y)
    tor_c = pel + np.array([0, 0.36 * s, 0])
    f.mesh(M_BOX, R=Y @ np.diag([0.44 * s, 0.5 * s, 0.24 * s]), T=tor_c, col=accent if 'torso' in glow else col, emis=0.9 if 'torso' in glow else emis, alpha=alpha)
    cube(f, tor_c + Y @ np.array([0, 0.06 * s, 0.125 * s]), (0.2 * s, 0.06 * s, 0.02 * s), accent, 0.9, alpha, R=Y)
    neck = pel + np.array([0, 0.66 * s, 0])
    hc = neck + np.array([0, 0.14 * s, 0])
    f.mesh(M_BALL, R=Y @ np.diag([0.13, 0.15, 0.14]) * s, T=hc, col=accent if 'head' in glow else (60, 66, 80), emis=0.9 if 'head' in glow else 0.15, alpha=alpha)
    f.mesh(M_BOX, R=Y @ np.diag([0.2 * s, 0.05 * s, 0.03 * s]), T=hc + Y @ np.array([0, 0.01 * s, 0.12 * s]), col=CYAN, emis=1.0, alpha=alpha)
    # 手臂
    L, Rr, El, Er = arms if arms is not None else (0.0, 0.0, 0.25, 0.25)
    for sg, sh, el in ((1, L, El), (-1, Rr, Er)):
        swing = amp * 0.7 * math.sin(ph + (pi if sg > 0 else 0))
        sp = pel + np.array([0, 0.58 * s, 0]) + Y @ np.array([0.27 * s * sg, 0, 0])
        if sg < 0 and wave > 0:                                  # 右手挥手
            e1 = seg(sp, 0, 0.3, 0.09, 0.09, col, 'arm', ang_z=-(2.4 * wave))
            hand = seg(e1, 0, 0.28, 0.08, 0.08, col, 'arm', ang_z=-(2.4 * wave) - 0.5 * math.sin(f_time[0] * 9) * wave)
        else:
            e1 = seg(sp, -(sh + swing), 0.3, 0.09, 0.09, col, 'arm', ang_z=0.08 * sg)
            hand = seg(e1, -(sh + swing + el), 0.28, 0.08, 0.08, col, 'arm', ang_z=0.08 * sg)
        f.mesh(M_BALL_S, R=np.eye(3) * 0.06 * s, T=hand, col=accent if 'hand' in glow else DARK, emis=0.95 if 'hand' in glow else 0.1, alpha=alpha)
    return hc


f_time = [0.0]


def house(f, P, lit, s=1.0):
    P = np.array(P, float)
    cube(f, P + [0, 0.4 * s, 0], (1.0 * s, 0.8 * s, 1.0 * s), (60, 70, 90) if not lit else (70, 120, 90), 0.15 if not lit else 0.4)
    cube(f, P + [0, 0.95 * s, 0], (0.8 * s, 0.8 * s, 1.02 * s), (110, 70, 60) if not lit else GREEN, 0.15 if not lit else 0.6, R=rotz(pi / 4))
    if lit: cube(f, P + [0, 0.35 * s, 0.51 * s], (0.3 * s, 0.3 * s, 0.02), GOLD, 1.0)


# =====================================================================
# 1 开场：机器人从暗处走来 → AI 光球落入头部 → 实验室 / 工厂 / 家 → 五个章节
# =====================================================================
def sc1(lt, d):
    k = 0; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[3], e[4]]
    if lt < e[3]:
        cam = orbit(0.5 - 0.06 * lt, lerp(6.5, 5.0, ease(lt / 6)), 1.4, (0, 1.0, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 40)
        z = lerp(-3, 0, ease(lt / 4.5)); walking = lt < 4.5
        orb_g = ease((lt - e[2]) / 1.4)
        hc = robot(f, (0, 0, z), 0, 1.0, walk=lt * 6 if walking else None, glow={'head'} if orb_g >= 1 else ())
        if lt > e[2] - 0.3 and orb_g < 1:
            P = hc + np.array([0, 2.2 * (1 - orb_g), 0])
            f.mesh(M_BALL, T=P, sc=0.22 * (1 - 0.4 * orb_g), col=CYAN, emis=1.0)
            for j in range(10):
                a = j * 0.63 + lt * 3; f.dots([P + [0.35 * math.cos(a), 0.2 * math.sin(a * 1.3), 0.35 * math.sin(a)]], 0.04, (*CYAN, 200))
        if orb_g >= 1:
            ring_r = 0.2 + (lt - e[2] - 1.4) * 2.5
            if ring_r < 3: f.mesh(M_RING, R=I3, T=hc, sc=ring_r, col=CYAN, emis=0.9, alpha=int(255 * (1 - ring_r / 3)))
        f.text(640, 560, '具身智能 Embodied AI', 44, a=ease((lt - e[1]) / 0.5) * (1 - ease((lt - e[2]) / 0.4)), anc='mm', stroke=3)
        if lt > e[2]: f.text(640, 560, 'AI  +  身体  =  在真实世界干活', 30, col=(200, 225, 255), a=ease((lt - e[2] - 0.3) / 0.4), anc='mm', stroke=3)
        chrome(f, ACC, TAG, a=ease((lt - 0.3) / 0.5))
        return f
    if lt < e[4]:
        t = lt - e[3]
        cam = orbit(0.15 * math.sin(t * 0.4), 15, 4, (0, 1.2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30)
        for j, (x, nm, col) in enumerate([(-5, '实验室', GREY), (0, '工厂', ACC), (5, '家庭', GREEN)]):
            g = ease((t - j * 0.5) / 0.5)
            f.mesh(disc(1.8, 0.2, col), T=(x, 0, 0), emis=0.3 + 0.3 * (j > 0), alpha=int(255 * g))
            if j == 0:
                for q in range(3): cube(f, (x - 0.8 + q * 0.8, 0.5, -0.6), (0.5, 0.6, 0.5), (90, 100, 120), 0.2)
            if j == 1:
                for q in range(2): f.mesh(M_RACK, T=(x - 0.7 + q * 1.4, 1.0, -0.8), sc=0.5, emis=0.05)
            if j == 2: house(f, (x, 0.2, -0.7), True, 1.0)
            robot(f, (x + 0.6 if j < 2 else x + 0.9, 0.2, 0.6), -0.3, 0.75, walk=None, alpha=int(255 * g))
            lab(f, (x, 0, 1.8), nm, 24, col, dy=40, a=g)
        for j in range(2):
            g = ease((t - 0.5 - j * 0.6) / 0.5)
            if g > 0: cube(f, (-2.5 + j * 5, 0.4, 0), (1.4 * g, 0.12, 0.12), GOLD, 0.8)
        chrome(f, ACC, TAG); headline(f, lt, ACC, None, '2026：从实验室走向工厂和家庭')
        return f
    t = lt - e[4]
    cam = orbit(0.05 * math.sin(t), 14, 2.5, (0, 1.5, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, 0, 26)
    names = ['规模', '大脑', '数据', '量产', '家庭']; cols = [CN, CYAN, PURPLE, ACC, GREEN]
    for j in range(5):
        x = (j - 2) * 2.6; g = pop(t, 0.15 + j * 0.18)
        cube(f, (x, 1.6, 0), (2.1 * g, 1.6 * g, 0.2), cols[j], 0.35)
        lab(f, (x, 1.6, 0.2), names[j], 26, WHITE, dy=10, a=g)
        lab(f, (x, 2.6, 0.2), f'0{j + 1}', 18, cols[j], dy=-10, a=g)
    chrome(f, ACC, TAG); headline(f, lt, ACC, None, '五个维度看前沿')
    return f


# =====================================================================
# 2 规模：机器人方阵 + 出货计数 → 中国占 78% → 厂商排名
# =====================================================================
def sc2(lt, d):
    k = 1; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[5]]
    if lt < e[5]:
        cam = orbit(0.55 + 0.02 * lt, 19, 9, (0, 0.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30)
        n = int(100 * ease((lt - e[2]) / 2.0))
        china = lt > e[4]
        for i in range(n):
            r, c = divmod(i, 10)
            x = (c - 4.5) * 1.1; z = (r - 4.5) * 1.1
            col = (CN if i < 78 else (150, 160, 180)) if china else (150, 160, 180)
            f.mesh(M_PERSON, T=(x, 0, z), sc=0.55, col=col, emis=0.35 if china and i < 78 else 0.1)
        card(f, 40, 160, 330, 112, '2026 上半年 · 全球人形机器人出货', counter(lt, e[2], e[2] + 2.0, 0, 24900, '{:,.0f}') if lt > e[2] else '0', '台', ACC,
             a=ease((lt - e[1]) / 0.4), vsz=36, note='同比 +432% · 市场约 7.4 亿美元' if lt > e[3] else 'IDC 数据')
        if china: card(f, 900, 470, 330, 104, '其中中国', '19,000+', '台 · 约 78%', CN, a=ease((lt - e[4]) / 0.4), vsz=34)
        lab(f, (6.5, 0.5, 5.5), '每个小人 = 1%', 18, DIM, dy=30, a=ease((lt - e[2]) / 0.4))
        chrome(f, ACC, TAG); headline(f, lt, CN, '1', '规模：出货量半年翻五倍', None)
        return f
    t = lt - e[5]
    cam = orbit(-0.2 + 0.03 * t, 16, 4, (0, 2.6, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, 0, 30)
    rows = [('智元 AgiBot', 8600, 35, ACC), ('宇树 Unitree', 5900, 31, CYAN)]
    for j, (nm, v, p, col) in enumerate(rows):
        x = (j - 0.5) * 5.0
        g = ease((lt - e[5] - j * 0.2) / 0.9) if j < 2 else ease((lt - e[7]) / 0.9)
        if j == 1: g = ease((lt - e[7] + 0.2) / 0.9)
        h = v / 2000 * g
        bar(f, x, 0, h, col, 2.4, 0.5 if j == 0 else 0.25)
        lab(f, (x, h + 0.4, 0), f'{v:,}台 · {p}%' if j < 2 else f'约 {p}%', 24, WHITE, a=g)
        lab(f, (x, 0, 1.4), nm, 20, col, dy=40, a=ease((t - j * 0.2) / 0.3))
        if j == 0 and lt > e[6]:
            lab(f, (x, h + 1.3, 0), '全球第一', 26, GOLD, a=ease((lt - e[6]) / 0.4))
    chrome(f, ACC, TAG); headline(f, lt, CN, '1', '智元首次超过宇树', '上半年出货 · 数据：IDC')
    return f


# =====================================================================
# 3 大脑：VLA 流水线 → Gemini Robotics 2 全身控制 → 五项任务 → π0.7 技能重组 → Helix 30 个家庭
# =====================================================================
def sc3(lt, d):
    k = 2; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[3], e[6], e[8]]
    if lt < e[3]:
        t = lt
        cam = orbit(0.2 + 0.02 * t, 12.5, 3, (0, 1.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 28)
        stages = [(-6.5, '视觉', '摄像头画面', CYAN), (-3.5, '语言', '“把杯子放进水槽”', GOLD), (0, 'VLA 模型', '', PURPLE), (3.6, '动作', '电机指令', GREEN)]
        for j, (x, nm, sub, col) in enumerate(stages):
            g = pop(lt, e[1] + j * 0.25)
            if j == 2:
                for q in range(3): cube(f, (x, 1.0 + q * 0.75, 0), (2.2 * g, 0.6 * g, 1.6 * g), col, 0.35 + 0.2 * math.sin(lt * 4 + q))
            elif j == 0:
                f.mesh(M_BALL, T=(x, 1.8, 0), sc=0.7 * g, col=(30, 40, 60), emis=0.2); f.mesh(M_BALL, T=(x, 1.8, 0.45), sc=0.32 * g, col=col, emis=1.0)
            elif j == 1:
                slab_ = M_PANEL; f.mesh(slab_, R=np.diag([2.2 * g, 1.1 * g, 1]), T=(x, 1.8, 0), col=(30, 34, 50), emis=0.2)
            else:
                for q in range(4): cube(f, (x + (q % 2) * 0.6 - 0.3, 1.4 + (q // 2) * 0.6, 0), 0.4 * g, col, 0.5 + 0.4 * math.sin(lt * 8 + q))
            lab(f, (x, 0.3, 0.8), nm, 22, col, dy=30, a=g)
            if sub: lab(f, (x, 0.3, 0.8), sub, 16, DIM, dy=56, a=g)
        for j in range(3):
            x0 = stages[j][0] + 1.1; x1 = stages[j + 1][0] - 1.1
            for q in range(4):
                ph = (lt * 0.9 + q / 4) % 1
                if lt > e[2] - 0.6: f.dots([(lerp(x0, x1, ph), 1.8, 0)], 0.09, (*stages[j + 1][3], 230))
        robot(f, (6.6, 0, 0), -0.9, 1.0, arms=(0.6 + 0.5 * math.sin(lt * 2), 0.3, 0.6, 0.4), glow={'arm', 'hand'} if lt > e[2] else ())
        chrome(f, ACC, TAG); headline(f, lt, CYAN, '2', '大脑：VLA 视觉-语言-动作模型', '一个模型，从看到听到做')
        return f
    if lt < e[6]:
        t = lt - e[3]
        cam = orbit(0.6 + 0.08 * t, 7.5, 1.6, (0, 1.0, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 30)
        order = ['leg', 'torso', 'arm', 'hand', 'head']
        n = int(clamp((lt - e[4]) / 2.0) * 5.99) if lt > e[4] else 0
        glow = set(order[:n]) if lt < e[5] else set(order)
        robot(f, (0, 0, 0), 0.3, 1.0, walk=lt * 5 if lt > e[4] + 2.2 and lt < e[5] else None,
              arms=(0.5 + 0.3 * math.sin(lt * 3), 0.9, 0.5, 0.7), glow=glow, accent=BLUE)
        card(f, 40, 160, 330, 104, 'Google DeepMind · 7月30日', 'Gemini Robotics 2', '', BLUE, a=ease(t / 0.4), vsz=28,
             note='首次用一个模型控制人形全身' if lt > e[4] else None)
        if lt > e[5]:
            A = ease((lt - e[5]) / 0.4)
            f.rect(880, 400, 1240, 560, (12, 16, 26, int(220 * A)), r=10)
            f.text(1060, 424, '公布的 5 项手部任务', 20, a=A, anc='mm')
            for j in range(5):
                ok = j < 2
                cx = 930 + j * 64
                f.rect(cx - 24, 450, cx + 24, 498, ((*GREEN, int(230 * A)) if ok else (*RED, int(230 * A))), r=8)
                f.text(cx, 474, '≥50%' if ok else '<50%', 15, a=A, anc='mm')
            f.text(1060, 530, '最高 92%（拧灯泡） 最低 32%（扫地）', 16, col=DIM, a=A, anc='mm', bold=False)
        chrome(f, ACC, TAG); headline(f, lt, CYAN, '2', '全身控制：从脚到手指', '仅限早期合作伙伴使用')
        return f
    if lt < e[8]:                                          # π0.7 技能重组
        t = lt - e[6]
        cam = orbit(-0.2 + 0.03 * t, 9.5, 2.5, (0, 1.9, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 28)
        skills = [('抓取', CYAN), ('开门', GOLD), ('按按钮', GREEN), ('倒水', PURPLE)]
        mix = ease((lt - e[7]) / 1.2)
        for j, (nm, col) in enumerate(skills):
            x0 = (j - 1.5) * 2.6; P0 = np.array([x0, 1.4, 0])
            P1 = np.array([-0.8 + (j % 2) * 1.6, 2.2 + (j // 2) * 1.0, 0]) if j < 3 else P0 + [0, -0.1, -2]
            P = P0 + (P1 - P0) * mix
            cube(f, P, (1.4, 0.8, 0.5), col, 0.45, alpha=int(255 * (1 - 0.7 * mix)) if j == 3 else 255)
            lab(f, P + [0, 0, 0.3], nm, 18, WHITE, dy=8, a=ease((t - j * 0.15) / 0.3) * (1 - 0.7 * mix * (j == 3)))
        if mix > 0.6:
            A = ease((mix - 0.6) / 0.4)
            f.mesh(M_RING, R=I3, T=(0, 2.7, 0), sc=2.2, col=GOLD, emis=0.9, alpha=int(255 * A))
            lab(f, (0, 4.0, 0), '新任务：用陌生的咖啡机', 22, GOLD, dy=-20, a=A)
        card(f, 40, 160, 330, 104, 'Physical Intelligence · 4月', 'π0.7', '', PURPLE, a=ease(t / 0.4), vsz=36, note='技能组合，泛化到没训练过的任务')
        chrome(f, ACC, TAG); headline(f, lt, CYAN, '2', '组合泛化：学过的技能拼成新本领', None)
        return f
    t = lt - e[8]                                          # Helix 2.5：30 个陌生家庭
    cam = orbit(0.5 + 0.03 * t, 18, 9, (0, 0.5, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, 0, 28)
    m = int(30 * ease(t / 1.2)); lit_n = int(17 * ease((lt - e[9]) / 1.5)) if lt > e[9] else 0
    LIT = [0, 2, 3, 5, 7, 8, 11, 12, 14, 16, 17, 19, 22, 23, 25, 27, 28]
    for i in range(m):
        r, c = divmod(i, 6)
        house(f, ((c - 2.5) * 2.0, 0, (r - 2) * 2.0), i in LIT[:lit_n], 0.9)
    card(f, 40, 160, 330, 112, 'Figure · Helix 2.5 · 9月', counter(lt, e[9], e[9] + 1.5, 0, 56) + '%' if lt > e[9] else '30 个家庭', '', ACC,
         a=ease(t / 0.4), vsz=36, note='零样本：没见过的家、没见过的物品')
    chrome(f, ACC, TAG); headline(f, lt, CYAN, '2', '走进 30 个陌生家庭', 'Figure 自测，尚无独立复现')
    return f


# =====================================================================
# 4 数据：互联网数据塔 vs 机器人数据 → Figure 35 亿算力 → 三种数据来源 → 英伟达参考机器人
# =====================================================================
def sc4(lt, d):
    k = 3; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[3], e[4], e[6]]
    if lt < e[3]:
        cam = orbit(0.3 + 0.02 * lt, 17, 4, (0, 3.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 28)
        g = ease((lt - e[1]) / 1.4)
        for q in range(int(24 * g)):
            cube(f, (-3.0, 0.15 + q * 0.32, 0), (2.4, 0.26, 1.6), (90, 130, 200) if q % 2 else (70, 110, 180), 0.3)
        cube(f, (3.0, 0.15, 0), (0.6, 0.26, 0.6), ACC, 0.7)
        lab(f, (-3.0, 0, 1.0), '互联网文本 / 图像', 20, (150, 190, 255), dy=40, a=ease((lt - e[1]) / 0.4))
        lab(f, (3.0, 0, 0.5), '机器人动作数据', 20, ACC, dy=40, a=ease((lt - e[1] - 0.3) / 0.4))
        if lt > e[2]: lab(f, (3.0, 0.6, 0), '要靠花钱“造”', 22, GOLD, dy=-30, a=ease((lt - e[2]) / 0.4))
        chrome(f, ACC, TAG); headline(f, lt, PURPLE, '3', '瓶颈：数据', '机器人没有现成的“互联网”')
        return f
    if lt < e[4]:
        t = lt - e[3]
        cam = orbit(0.4 + 0.05 * t, 18, 6, (0, 1.6, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 28)
        for r in range(2):
            for c in range(6): f.mesh(M_RACK, T=((c - 2.5) * 2.2, 2.0, (r - 0.5) * 3.2), sc=1.0, emis=0.05)
        for q in range(int(35 * ease(t / 1.4))): f.mesh(M_COIN, T=(7.5, 0.1 + q * 0.19, 0), sc=0.8, emis=0.3)
        card(f, 40, 160, 330, 104, 'Figure · 9月', '$3.5B', '算力承诺', ACC, a=ease(t / 0.4), vsz=36, note='训练 Helix · 与 nscale 合作')
        chrome(f, ACC, TAG); headline(f, lt, PURPLE, '3', '砸钱买算力', None)
        return f
    if lt < e[6]:
        t = lt - e[4]
        cam = orbit(0.05 * math.sin(t * 0.5), 11.5, 3, (0, 1.3, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 28)
        # 动捕
        x = -5.5
        robot(f, (x, 0, 0), 0.4, 0.9, walk=lt * 4, col=(60, 66, 80))
        for j in range(10):
            f.dots([(x + 0.25 * math.sin(j * 1.7 + lt * 4), 0.3 + j * 0.16, 0.25 * math.cos(j)) ], 0.06, (255, 255, 255, 255))
        for a in range(4):
            P = np.array([x + 2.2 * math.cos(a * pi / 2 + 0.7), 2.8, 2.2 * math.sin(a * pi / 2 + 0.7)])
            cube(f, P, 0.28, (40, 44, 56), 0.2); f.dots([P + (np.array([x, 1, 0]) - P) * 0.15], 0.07, (255, 60, 60, 255))
        # 遥操作
        x = 0
        f.mesh(M_PERSON, T=(x - 1.0, 0, 0), sc=1.0, emis=0.2)
        cube(f, (x - 1.0, 1.65, 0.15), (0.32, 0.12, 0.12), (30, 30, 40), 0.3)
        robot(f, (x + 1.0, 0, 0), -0.3, 0.9, arms=(0.8 + 0.4 * math.sin(lt * 2), 0.8 + 0.4 * math.sin(lt * 2 + 1), 0.4, 0.4))
        for q in range(5): f.dots([(x - 0.6 + q * 0.3, 2.2 + 0.1 * math.sin(lt * 5 + q), 0)], 0.05, (*CYAN, 220))
        # 第一视角视频
        x = 5.5
        f.mesh(M_PANEL, R=np.diag([2.4, 1.5, 1]), T=(x, 1.8, 0), col=(18, 26, 44), emis=0.3)
        for q in range(3): cube(f, (x - 0.6 + q * 0.6, 1.6 + 0.2 * math.sin(lt * 3 + q), 0.08), (0.35, 0.2, 0.02), [GOLD, GREEN, CYAN][q], 0.8)
        cube(f, (x + 0.7 * math.sin(lt * 1.5), 1.4, 0.1), (0.5, 0.18, 0.02), (235, 200, 170), 0.6)
        for j, (xx, nm) in enumerate([(-5.5, '动作捕捉实验室'), (0, '遥操作录像'), (5.5, '第一视角视频')]):
            lab(f, (xx, 0, 1.4), nm, 20, GOLD, dy=40, a=ease((t - j * 0.3) / 0.4))
        if lt > e[5]: f.text(640, 560, '9 月：数据交易市场相继出现', 24, col=WHITE, anc='mm', a=ease((lt - e[5]) / 0.4), stroke=3)
        chrome(f, ACC, TAG); headline(f, lt, PURPLE, '3', '三种“造数据”的方式', None)
        return f
    t = lt - e[6]
    cam = orbit(-0.4 + 0.07 * t, 8, 1.8, (0, 1.1, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, 0, 28)
    hc = robot(f, (0, 0, 0), 0.0, 1.1, arms=(0.4, 0.4 + 0.4 * math.sin(lt * 2), 0.8, 0.8), glow={'torso', 'hand'}, accent=(118, 185, 0))
    chip = np.array([1.8, 1.4, 0.4])
    cube(f, chip, (0.9, 0.12, 0.9), (30, 34, 40), 0.3)
    cube(f, chip + [0, 0.08, 0], (0.5, 0.06, 0.5), (118, 185, 0), 0.9)
    f.line([chip, np.array([0, 1.45, 0])], (118, 185, 0, 160), 2)
    lab(f, chip, 'Jetson Thor · 2070 TFLOPS (FP4)', 18, (170, 230, 90), dy=-34)
    lab(f, (-1.0, 1.0, 0), '宇树 H2 Plus 机身', 18, CYAN, dy=0, a=ease((lt - e[7]) / 0.4))
    lab(f, (-1.0, 0.7, 0), '+ Sharpa 灵巧手', 18, CYAN, dy=10, a=ease((lt - e[7] - 0.3) / 0.4))
    card(f, 40, 160, 330, 104, 'NVIDIA · 开放参考设计', 'Isaac GR00T', '', (118, 185, 0), a=ease(t / 0.4), vsz=32, note='年底由宇树供货 · 面向科研')
    chrome(f, ACC, TAG); headline(f, lt, PURPLE, '3', '英伟达：开放的参考人形机器人', None)
    return f


# =====================================================================
# 5 量产：特斯拉（罩布 + 每周数百台）→ Atlas 产量去向 + 年产 3 万工厂 → 小鹏 IRON 产线
# =====================================================================
def line_bots(f, lt, z, col, n=6, speed=0.6):
    cube(f, (0, 0.2, z), (16, 0.4, 1.6), (50, 56, 70), 0.1)
    for q in range(n):
        x = ((lt * speed + q * 16 / n) % 16) - 8
        robot(f, (x, 0.4, z), 0.0, 0.8, col=col)


def sc5(lt, d):
    k = 4; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[4], e[8]]
    if lt < e[4]:
        t = lt
        cam = orbit(0.4 + 0.03 * t, 12, 3.5, (0, 1.2, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 28)
        line_bots(f, lt, 2.5, STEEL, 7, 0.7)
        # 罩布下的 V3
        P = np.array([0, 0, -1.5])
        f.mesh(M_PERSON, T=P, sc=1.35, col=(70, 70, 82), emis=0.1)
        cube(f, P + [0, 0.05, 0], (1.6, 0.1, 1.6), (40, 40, 50), 0.1)
        lab(f, P + [0, 2.6, 0], '?', 60, GOLD, dy=-10, a=ease((t - e[1]) / 0.4))
        lab(f, P + [0, 0, 1.0], 'Optimus 第三代 · 未正式亮相', 20, DIM, dy=30, a=ease((t - e[1]) / 0.4))
        if lt > e[2]: card(f, 40, 160, 330, 112, '据 The Information', '数百台 / 周', '', RED, a=ease((lt - e[2]) / 0.4), vsz=32,
                           note='但还不是交付客户的最终版本' if lt > e[3] else None)
        chrome(f, ACC, TAG); headline(f, lt, ACC, '4', '量产：特斯拉 Optimus', None)
        return f
    if lt < e[8]:
        t = lt - e[4]
        cam = orbit(0.2 + 0.04 * t, 14.5, 5, (0, 0.8, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 28)
        src = np.array([-6, 0, 0])
        cube(f, src + [0, 1.2, 0], (2.6, 2.4, 2.6), (40, 70, 110), 0.2)
        lab(f, src + [0, 2.6, 0], '波士顿动力', 20, BLUE, dy=-14, a=ease(t / 0.4))
        dests = [(np.array([4, 0, -3.2]), '现代汽车 RMAC', BLUE), (np.array([4, 0, 3.2]), '谷歌 DeepMind', (66, 133, 244))]
        for j, (D, nm, col) in enumerate(dests):
            f.mesh(disc(1.5, 0.2, col), T=D, emis=0.4)
            lab(f, D, nm, 20, col, dy=46, a=ease((lt - e[5] - j * 0.2) / 0.4))
            if lt > e[5]:
                for q in range(3):
                    ph = ((lt - e[5]) * 0.35 + q / 3) % 1
                    robot(f, src + (D - src) * ph + [0, 0, 0], math.atan2((D - src)[0], (D - src)[2]), 0.8, walk=lt * 6 + q, col=(220, 225, 232), accent=BLUE)
        if lt > e[6]:
            A = ease((lt - e[6]) / 0.4)
            f.rect(880, 400, 1240, 470, (12, 16, 26, int(220 * A)), r=10)
            f.text(1060, 435, '外部客户：2027 年初', 22, col=GOLD, a=A, anc='mm')
        if lt > e[7]:
            card(f, 40, 160, 330, 104, '现代汽车计划', '30,000', '台 / 年', BLUE, a=ease((lt - e[7]) / 0.4), vsz=28, note='美国新建机器人工厂')
        else:
            card(f, 40, 160, 330, 104, '量产版 Atlas', '2026 年产量', '已全部预订', BLUE, a=ease(t / 0.4), vsz=28)
        chrome(f, ACC, TAG); headline(f, lt, ACC, '4', '波士顿动力 Atlas', None)
        return f
    t = lt - e[8]
    cam = orbit(-0.5 + 0.05 * t, 12, 4, (0, 1.2, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, 0, 28)
    line_bots(f, lt, 0, (230, 232, 236), 6, 0.9)
    for q in range(4):
        x = -6 + q * 4; a = math.sin(lt * 2 + q) * 0.6
        cube(f, (x, 1.1, -1.8), (0.4, 2.2, 0.4), (70, 76, 90), 0.2)
        cube(f, (x, 2.2, -1.8) + rotx(-0.8 + a) @ np.array([0, 0, 0.8]), (0.25, 0.25, 1.6), ACC, 0.4, R=rotx(-0.8 + a))
    card(f, 40, 160, 330, 104, '小鹏 XPENG', 'IRON', '', ACC, a=ease(t / 0.4), vsz=36, note='自动化产线 · 核心工序 80%+ · 目标年底量产')
    chrome(f, ACC, TAG); headline(f, lt, ACC, '4', '中国：小鹏 IRON 上产线', None)
    return f


# =====================================================================
# 6 家庭：客厅里叠衣服的 NEO + 价格 → 远程人工接管 → $30/小时保洁
# =====================================================================
def room(f):
    cube(f, (0, -0.05, 0), (10, 0.1, 8), (70, 58, 50), 0.1)
    cube(f, (0, 2.0, -4), (10, 4, 0.1), (46, 50, 62), 0.1)
    cube(f, (-3.2, 0.4, -2.8), (3.0, 0.8, 1.2), (90, 110, 140), 0.15)
    cube(f, (-3.2, 0.95, -3.3), (3.0, 0.7, 0.3), (90, 110, 140), 0.15)
    cube(f, (1.2, 0.75, -1.0), (2.4, 0.08, 1.2), (150, 120, 90), 0.15)
    for x in (0.1, 2.3):
        for z in (-1.5, -0.5): cube(f, (x, 0.37, z), (0.08, 0.74, 0.08), (110, 90, 70), 0.1)
    f.layer()


def sc6(lt, d):
    k = 5; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[5]]
    if lt < e[5]:
        t = lt
        cam = orbit(0.5 + 0.03 * t, 9.5, 3.5, (0.5, 1.0, -1), 45)
        f = base(cam, lt, d, cuts); room(f)
        fold = (lt * 0.5) % 1
        robot(f, (1.2, 0, 0.1), pi, 1.0, arms=(1.1 + 0.3 * math.sin(lt * 3), 1.1 + 0.3 * math.sin(lt * 3 + pi), 0.4, 0.4),
              col=(215, 200, 180), accent=(190, 150, 110))
        for q in range(3): cube(f, (1.0 + q * 0.12, 0.84 + q * 0.06, -1.0), (0.5 * (1 - 0.4 * (q == 2) * fold), 0.05, 0.4), [(230, 90, 90), (90, 150, 230), (240, 230, 220)][q], 0.3)
        card(f, 40, 160, 330, 104, '1X · NEO 家用人形机器人', '$20,000', '或 $499/月', GREEN, a=ease((t - e[1]) / 0.4), vsz=34,
             note='今年开始在美国交付' if lt > e[3] else None)
        if lt > e[4]:
            A = ease((lt - e[4]) / 0.5)
            op = np.array([4.2, 0, 1.6])
            f.mesh(M_PERSON, T=op, sc=1.0, col=(150, 170, 200), emis=0.2, alpha=int(255 * A))
            cube(f, op + [0, 1.65, 0.15], (0.32, 0.12, 0.12), (30, 30, 40), 0.3, alpha=int(255 * A))
            for q in range(8):
                ph = (lt * 0.8 + q / 8) % 1
                f.dots([op + [0, 1.8, 0] + (np.array([1.2, 1.9, 0.1]) - op - [0, 1.8, 0]) * ph], 0.05, (*CYAN, int(220 * A)))
            lab(f, op, '远程专家接管', 20, CYAN, dy=40, a=A)
        chrome(f, ACC, TAG); headline(f, lt, GREEN, '5', '进入家庭：1X NEO', None)
        return f
    t = lt - e[5]
    cam = orbit(-0.3 + 0.05 * t, 10, 3.5, (0, 1.0, -1), 45)
    f = base(cam, lt, d, cuts); room(f)
    robot(f, (-1.0, 0, 0.5), 0.5 + 0.3 * math.sin(lt), 1.0, arms=(0.9, 0.9, 0.3, 0.3), col=(220, 225, 232), accent=GREEN)
    cube(f, (-0.7, 0.4, 1.1), (0.08, 0.9, 0.08), (120, 100, 80), 0.1, R=rotx(0.4))
    cube(f, (-0.7, 0.05, 1.35), (0.5, 0.08, 0.2), GREEN, 0.4)
    card(f, 40, 160, 330, 104, '旧金山 · Tau Robotics', '$30', '/ 小时', GREEN, a=ease(t / 0.4), vsz=36, note='遥控人形机器人上门保洁')
    chrome(f, ACC, TAG); headline(f, lt, GREEN, '5', '更务实的玩法：人在背后遥控', None)
    return f


# =====================================================================
# 7 资本：OpenAI 虚线机器人 → 并购资金流 → 上市三道门槛 → 泡沫
# =====================================================================
def sc7(lt, d):
    k = 6; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[3], e[5]]
    if lt < e[3]:
        t = lt
        cam = orbit(0.2 + 0.03 * t, 9, 2, (0, 1.1, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 28)
        a = 0.35 + 0.15 * math.sin(lt * 2)
        robot(f, (0, 0, 0), 0.2, 1.1, col=(16, 163, 127), accent=(16, 163, 127), alpha=int(255 * a), emis=0.6)
        if lt > e[1]: f.text(640, 170, '“我们肯定会做人形机器人”', 32, a=ease((lt - e[1]) / 0.4), anc='mm', stroke=3)
        if lt > e[1]: f.text(640, 210, '—— 奥特曼，9 月 · Sources 播客', 18, col=DIM, a=ease((lt - e[1] - 0.3) / 0.4), anc='mm', bold=False)
        if lt > e[2]:
            A = ease((lt - e[2]) / 0.4)
            f.rect(880, 420, 1240, 520, (12, 16, 26, int(220 * A)), r=10)
            for j, s_ in enumerate(['发布日期：无', '产量目标：无', '原型机：未公开']):
                f.text(900, 440 + j * 28, s_, 18, col=RED, a=A, anc='lm', bold=False)
        chrome(f, ACC, TAG); headline(f, lt, GOLD, None, 'OpenAI 宣布入局')
        return f
    if lt < e[5]:
        t = lt - e[3]
        cam = orbit(0.1 + 0.03 * t, 17, 4, (0, 1.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 28)
        deals = [(-1, 'AMD', 'World Labs（李飞飞）', '$8.2B', e[3], RED), (1, '软银', '1X（洽谈控股）', '约 $6B 估值', e[4], GOLD)]
        for zs, a_, b_, v, t0, col in deals:
            z = zs * 2.6
            if lt < t0 - 0.1: continue
            g = ease((lt - t0) / 0.5)
            f.mesh(M_BALL, T=(-5, 1.2, z), sc=0.9 * g, col=col, emis=0.5)
            f.mesh(M_BALL, T=(5, 1.2, z), sc=0.9 * g, col=(160, 170, 190), emis=0.3)
            for q in range(6):
                ph = ((lt - t0) * 0.6 + q / 6) % 1
                f.mesh(M_COIN, R=rotx(pi / 2), T=(lerp(-4, 4, ph), 1.2 + 0.6 * math.sin(pi * ph), z), sc=0.35, emis=0.4, alpha=int(255 * g))
            lab(f, (-5, 0, z), a_, 22, col, dy=40, a=g); lab(f, (5, 0, z), b_, 20, WHITE, dy=40, a=g)
            lab(f, (0, 2.2, z), v, 26, GOLD, dy=-10, a=g)
        chrome(f, ACC, TAG); headline(f, lt, GOLD, None, '资本：大手笔并购', None)
        return f
    t = lt - e[5]
    cam = orbit(-0.25 + 0.03 * t, 15, 3, (0, 2.0, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, 0, 28)
    for j, nm in enumerate(['持续收入', '亏损收窄', '核心技术']):
        x = (j - 1) * 3.2; g = ease((lt - e[6] - j * 0.3) / 0.4)
        cube(f, (x - 1.1, 1.6, 0), (0.25, 3.2, 0.25), (80, 90, 110), 0.2)
        cube(f, (x + 1.1, 1.6, 0), (0.25, 3.2, 0.25), (80, 90, 110), 0.2)
        cube(f, (x, 3.2, 0), (2.5, 0.25, 0.25), CN, 0.3 + 0.5 * g)
        lab(f, (x, 3.2, 0), nm, 20, WHITE, dy=-26, a=max(g, 0.2))
    if lt > e[7]:                                          # 泡沫
        g = ease((lt - e[7]) / 2.0)
        f.layer(); f.mesh(M_BALL, T=(0, 1.4, 2.0), sc=0.6 + 1.0 * g, col=(200, 220, 255), emis=0.5, alpha=90)
        lab(f, (0, 1.4, 2.0), '泡沫？', 26, GOLD, dy=10, a=g)
    card(f, 40, 160, 330, 104, '据报道 · 中国证监会', '上市门槛提高', '', CN, a=ease(t / 0.4), vsz=28, note='香港已有至少 24 家具身智能公司排队')
    chrome(f, ACC, TAG); headline(f, lt, GOLD, None, '中国：监管降温', None)
    return f


# =====================================================================
# 8 总结 + 片尾：三根进度条 → 机器人挥手
# =====================================================================
def sc8(lt, d):
    k = 7; e = [ev(k, i) for i in range(len(SUBS[k]))]
    cuts = [e[5]]
    if lt < e[5]:
        cam = orbit(0.1 * math.sin(lt * 0.3), 10, 1.5, (0, 2.4, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, 0, 28)
        rows = [('硬件量产', 0.8, e[1], ACC), ('通用大脑泛化', 0.6, e[1] + 0.6, CYAN), ('可靠性 / 速度', 0.55, e[2], RED)]
        for j, (nm, v, t0, col) in enumerate(rows):
            y = 3.6 - j * 1.4; g = ease((lt - t0) / 1.0)
            cube(f, (0, y, 0), (8, 0.5, 0.3), (40, 46, 58), 0.1)
            if g > 0: cube(f, (-4 + 4 * v * g, y, 0.05), (8 * v * g, 0.5, 0.32), col, 0.5)
            lab(f, (-4.2, y, 0), nm, 22, col, dy=-30, a=ease((lt - t0) / 0.3))
        if lt > e[2]: lab(f, (4.4 * 0.55 - 4 + 4.4 * 0.55, 3.6 - 2.8, 0), '成功率 50-60%', 20, WHITE, dy=-30, a=ease((lt - e[2] - 0.5) / 0.4))
        if lt > e[4]: f.text(640, 560, '具身智能的“ChatGPT 时刻”：还没到，但已不远', 26, a=ease((lt - e[4]) / 0.4), anc='mm', stroke=3)
        chrome(f, ACC, TAG); headline(f, lt, ACC, None, '总结')
        return f
    t = lt - e[5]
    f_time[0] = lt
    cam = orbit(0.3 + 0.05 * t, lerp(6.5, 8.5, ease(t / 3)), 1.5, (0, 1.1, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, 0, 34)
    robot(f, (0, 0, 0), 0.25, 1.0, wave=ease(t / 0.6), glow={'head'})
    for j in range(3): robot(f, ((j - 1) * 2.4 + (0.6 if j == 1 else 0), 0, -3.0), 0.2, 0.9, walk=lt * 5 + j, col=(150, 160, 180))
    f.rect(390, 548, 890, 600, (*ACC, int(225 * ease(t / 0.5))), r=10)
    f.text(640, 574, 'AI 早报 · 我们下期见', 28, anc='mm', a=ease(t / 0.5))
    chrome(f, ACC, TAG)
    return f


FILM = Film(SEG, dur, [sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8], DISP,
            chapters=['开场', '规模', '大脑', '数据', '量产', '家庭', '资本', '总结'], total=TOTAL, lead=0.15)
