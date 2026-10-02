"""人物讲解 · Dan Koe：一人企业、写作系统、价值阶梯、AI 时代的判断（约 3 分 10 秒）
信息截至 2026-10-01。人物为风格化 3D 角色，不使用肖像。渲染：python3 -m bb render film.py video.mp4 --jobs 4
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from bb.explain import *
from bb.figure3d import *
dur, SEG, SUBS, DISP, TOTAL = load_timing(HERE)
def ev(k, i): return SUBS[k][i][0]
def EV(k): return [ev(k, i) for i in range(len(SUBS[k]))]
ACC = (240, 200, 120); TAG = 'Dan Koe · 一人企业'; FL = (230, 200, 150)
TK = [(CYAN, '把兴趣和成长写出来'), (GREEN, '用系统代替意志力'), (PURPLE, '做只有你才会做的东西')]
CH = lambda f, a=1.0: chrome_x(f, ACC, TAG, a=a, badge='人物讲解')
DSHIRT = (34, 34, 40); DPANTS = (50, 52, 60)
def koe(f, P, yaw=0.0, s=1.0, **kw):
    """Dan Koe 风格化角色：黑 T 恤、无眼镜。"""
    return figure(f, P, yaw, s, shirt=DSHIRT, pants=DPANTS, glasses=False, **kw)
def lerp_c(a, b, x): return tuple(int(lerp(a[i], b[i], x)) for i in range(3))


def screen_panel(f, P, w, h, a=1.0, col=(16, 20, 30), frame=(80, 90, 110)):
    P = np.array(P, float)
    cube(f, P, (w + 0.1, h + 0.1, 0.06), frame, 0.2, 255 * a)
    cube(f, P + [0, 0, 0.035], (w, h, 0.01), col, 0.35, 255 * a)


def tag3d(f, P, s, col, sz=17, a=1.0, txt=WHITE):
    x, y, z = f.pt(P)
    if z < 0.5 or a < 0.02: return
    w = font(sz).getlength(s) + 18
    f.rect(x - w / 2, y - sz * 0.75, x + w / 2, y + sz * 0.75, (12, 14, 24, int(215 * a)), r=6, outline=(*col, int(200 * a)), w=2)
    f.text(x, y, s, sz, col=txt, anc='mm', a=a)


def desk(f, P, yaw=0.0, lid=1.0, glow=CYAN):
    """书桌 + 笔记本电脑（屏幕绕铰链转动；lid=1 打开）。"""
    P = np.array(P, float); Y = roty(yaw)
    def W(v): return P + Y @ np.array(v, float)
    cube(f, W([0, 0.74, 0]), (1.6, 0.06, 0.8), (120, 96, 72), 0.2, R=Y)
    for sx in (-0.72, 0.72):
        for sz in (-0.32, 0.32): cube(f, W([sx, 0.355, sz]), (0.06, 0.71, 0.06), (70, 60, 50), 0.15, R=Y)
    cube(f, W([0, 0.785, 0.05]), (0.62, 0.03, 0.42), (170, 175, 185), 0.25, R=Y)
    Rl = Y @ rotx(-(1.0 - lid) * 1.75 + 0.25)
    hinge = W([0, 0.80, -0.16])
    cube(f, hinge + Rl @ np.array([0, 0.2, 0]), (0.62, 0.4, 0.02), (150, 155, 165), 0.25, R=Rl)
    if lid > 0.6: cube(f, hinge + Rl @ np.array([0, 0.2, 0.013]), (0.56, 0.34, 0.004), glow, 0.8, R=Rl)


def page(f, P, col=(235, 232, 222), s=1.0, R=I3, lines=4, a=255):
    P = np.array(P, float)
    cube(f, P, (0.5 * s, 0.66 * s, 0.02), col, 0.45, a, R=R)
    for q in range(lines):
        cube(f, P + R @ np.array([-0.04 * (q % 2) * s, (0.2 - q * 0.13) * s, 0.012]), ((0.36 - 0.08 * (q % 2)) * s, 0.035 * s, 0.004), (90, 90, 100), 0.3, a, R=R)


def method(f, lt, t0, s, col):
    if lt > t0:
        A = ease((lt - t0) / 0.5)
        f.rect(240, 520, 1040, 594, (12, 16, 28, int(225 * A)), r=12, outline=(*col, int(220 * A)), w=3)
        f.text(270, 557, '可借鉴', 20, col=col, a=A, anc='lm')
        f.text(360, 557, s, 24, a=A, anc='lm')


# =====================================================================
# 1 开场：一张书桌、一个人 → 收入/利润率/工时三张卡 → 周围亮起 400 万关注者的光点、书、软件
# =====================================================================
def sc1(lt, d):
    k = 0; e = EV(k)
    cam = orbit(0.35 + 0.035 * lt, lerp(6.5, 9.5, ease((lt - e[2]) / 5)), lerp(2.4, 4.2, ease((lt - e[2]) / 5)), (0, 1.1, 0), 45)
    f = base(cam, lt, d); floor(f, FL)
    desk(f, (0, 0, 0), lid=1.0, glow=ACC)
    cube(f, (0, 0.45, 0.85), (0.5, 0.06, 0.5), (60, 60, 70), 0.15)
    koe(f, (0, 0, 1.15), pi, 0.95, la=1.2, ra=1.2, le=0.5, re=0.5, nod=0.1 + 0.04 * math.sin(lt * 5))
    if lt > e[2]:
        g = ease((lt - e[2]) / 3)
        n = int(320 * g)
        for i in range(n):
            a_ = i * 2.39996; r = 2.2 + 0.28 * math.sqrt(i)
            tw = 0.5 + 0.5 * math.sin(lt * 2 + i)
            f.dots([(r * math.cos(a_), 0.06 + 0.15 * math.sin(i), r * math.sin(a_))], 0.045, (*lerp_c(ACC, WHITE, tw), int(200 * g)))
        gb = pop(lt, e[2] + 0.8); gs = pop(lt, e[2] + 1.4)
        if gb > 0.01:
            B = np.array([-1.9, 1.3 + 0.08 * math.sin(lt * 1.5), 0.3]); R = roty(0.5 + 0.2 * lt)
            cube(f, B, (0.5 * gb, 0.7 * gb, 0.12 * gb), (190, 60, 50), 0.35, R=R)
            cube(f, B + R @ np.array([0.02, 0, 0]), (0.47 * gb, 0.66 * gb, 0.13 * gb), (240, 236, 224), 0.3, R=R)
            tag3d(f, B + [0, 0.65, 0], '书', ACC, 15, gb)
        if gs > 0.01:
            S = np.array([1.9, 1.4 + 0.08 * math.sin(lt * 1.5 + 1), 0.3])
            screen_panel(f, S, 0.9 * gs, 0.6 * gs)
            for q in range(3): cube(f, S + [-0.25 + q * 0.25, 0, 0.05], (0.18 * gs, 0.3 * gs, 0.01), [CYAN, GOLD, PINK][q], 0.7)
            tag3d(f, S + [0, 0.6, 0], 'AI 软件', ACC, 15, gs)
    ca = ease((lt - 0.4) / 0.5)
    if lt < e[2] + 0.6:
        A = ca * (1 - ease((lt - e[2]) / 0.6))
        card(f, 60, 170, 290, 100, '年收入（2024，第三方报道）', '$4.1M', '', ACC, a=A, vsz=36)
        card(f, 60, 290, 290, 100, '利润率', '≈98%', '', GREEN, a=A * ease((lt - 1.8) / 0.4), vsz=36)
        if lt > e[1]:
            g = ease((lt - e[1]) / 0.4) * (1 - ease((lt - e[2]) / 0.6))
            card(f, 930, 170, 290, 100, '自称每天工作', '2–4', '小时', CYAN, a=g, vsz=36)
            cx, cy = 1075, 360; f.rect(cx - 52, cy - 52, cx + 52, cy + 52, (14, 18, 30, int(220 * g)), r=52, outline=(*CYAN, int(200 * g)), w=3)
            for h_ in range(24):
                on = h_ < 4 and h_ >= 0; ang = h_ / 24 * 2 * pi - pi / 2
                f.rect(cx + 40 * math.cos(ang) - 3, cy + 40 * math.sin(ang) - 3, cx + 40 * math.cos(ang) + 3, cy + 40 * math.sin(ang) + 3, (*(CYAN if on else GREY), int(255 * g)), r=3)
            f.text(cx, cy, '24h', 18, col=WHITE, a=g, anc='mm')
    if lt > e[2]:
        g = ease((lt - e[2] - 0.3) / 0.5) * (1 - ease((lt - e[3]) / 0.4))
        card(f, 60, 170, 300, 100, '各平台关注者', '≈400万', '', ACC, a=g, vsz=36)
    if lt > e[3]:
        A = ease((lt - e[3]) / 0.4)
        lab(f, (0, 2.9, 0), 'Dan Koe', 40, ACC, a=A)
    if lt > e[4]:
        note(f, 640, 470, '今天的主题：一人企业', ease((lt - e[4]) / 0.4), 26, accent=ACC)
    CH(f, ease((lt - 0.3) / 0.5)); headline(f, lt, ACC, None, '一个人的公司')
    return f


# =====================================================================
# 2 起点：快餐店柜台 + 七个室友 → 四次尝试一一熄灭 → 自由职业桌前写作 → 时间换钱撞上天花板
# =====================================================================
TRIES = [('脸书广告', BLUE), ('邮件营销', GOLD), ('网页设计', TEAL), ('电商', PINK)]
def sc2(lt, d):
    k = 1; e = EV(k); cuts = [e[2]]
    if lt < e[2]:
        cam = orbit(-0.3 + 0.03 * lt, 8.5, 2.6, (0, 1.6, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        cube(f, (-1.6, 0.55, -0.6), (3.0, 1.1, 0.8), (190, 60, 50), 0.2)
        cube(f, (-1.6, 1.13, -0.6), (3.1, 0.06, 0.9), (230, 220, 200), 0.3)
        cube(f, (-1.6, 2.6, -1.2), (2.6, 0.7, 0.1), (40, 30, 30), 0.3)
        for q in range(3): cube(f, (-2.4 + q * 0.8, 2.6, -1.14), (0.6, 0.45, 0.01), [GOLD, ORANGE, RED][q], 0.7)
        cube(f, (-1.0, 1.2, -0.5), (0.5, 0.04, 0.35), (220, 120, 60), 0.4)
        ball(f, (-1.0, 1.29, -0.5), 0.12, (210, 150, 70), 0.3)
        figure(f, (-1.6, 0, -1.3), 0.0, 0.9, la=0.6, ra=0.5, le=1.1, re=1.0, shirt=(190, 50, 45), pants=DPANTS, glasses=False)
        g7 = ease(lt / 1.5)
        for j in range(7):
            x = 1.6 + (j % 4) * 0.75; z = 0.2 + (j // 4) * 0.9
            mini(f, (x, 0, z), (110 + j * 15, 120, 150), 0.8 * g7, 0.15, yaw=-0.4)
        tag3d(f, (2.7, 1.3, 0.6), '7 个室友', ACC, 16, g7)
        if lt > e[1]:
            for j, (nm, col) in enumerate(TRIES):
                g = pop(lt, e[1] + j * 1.1)
                dead = lt > e[1] + j * 1.1 + 1.0
                P = np.array([-2.7 + j * 1.8, 2.9 + 0.1 * math.sin(lt * 2 + j), 0.8])
                cube(f, P, (0.8 * g, 0.5 * g, 0.5 * g), DARK if dead else col, 0.15 if dead else 0.6, R=roty(0.3 * lt + j))
                tag3d(f, P + [0, 0.62, 0], nm, GREY if dead else col, 16, g)
                if dead:
                    sx, sy, _ = f.pt(P + [0, 0.62, 0]); w = font(16).getlength(nm) / 2 + 6
                    f.rect(sx - w, sy - 1.5, sx + w, sy + 1.5, (*RED, 230))
        CH(f); headline(f, lt, ACC, '1', '起点：2018 年', '在快餐店打工，什么生意都试过')
        return f
    t = lt - e[2]
    cam = orbit(0.6 + 0.03 * t, lerp(6.5, 8.5, ease(t / 6)), 2.4, (0.6, 1.5, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    desk(f, (0, 0, 0), lid=1.0)
    koe(f, (0, 0, 0.75), pi, 0.95, la=1.2, ra=1.2, le=0.5, re=0.5, nod=0.08 * math.sin(lt * 4))
    for j in range(3):
        mini(f, (-2.6 + j * 0.0, 0, -0.8 + j * 0.9), (150, 130, 110), 0.6, 0.2, yaw=pi / 2)
        if (lt * 0.8 + j * 0.33) % 1 < 0.5: flow(f, (-2.4, 0.9, -0.8 + j * 0.9), (-0.5, 1.0, 0), lt + j * 0.3, GOLD, 1, 0.9, 0.06)
    tag3d(f, (-2.6, 1.4, 0.1), '客户：创作者', GOLD, 15)
    if lt > e[3]:
        n = int((lt - e[3]) * 2.2)
        for q in range(min(n, 14)):
            P = np.array([0.6 + (q % 7) * 0.45, 1.6 + (q // 7) * 0.75 + 0.05 * math.sin(lt * 2 + q), -0.6])
            page(f, P, s=0.7, lines=3)
        tag3d(f, (2.0, 3.3, -0.6), '公开写作 · 记录所学', ACC, 16, ease((lt - e[3]) / 0.4))
    if lt > e[4] - 0.3:
        g = ease((lt - e[4] + 0.3) / 0.6)
        ox, oy = 880, 260; W_, H_ = 320, 200
        f.rect(ox - 20, oy - 50, ox + W_ + 20, oy + H_ + 40, (12, 16, 28, int(220 * g)), r=12)
        f.text(ox, oy - 30, '收入 = 时薪 × 工时', 18, col=WHITE, a=g, anc='lm')
        for q in range(8):
            h = min(H_ * 0.12 * (q + 1), H_ * 0.72) * ease((lt - e[4] - q * 0.15) / 0.4)
            f.rect(ox + q * 40, oy + H_ - h, ox + q * 40 + 28, oy + H_, (*GOLD, int(230 * g)), r=3)
        f.rect(ox - 10, oy + H_ * 0.28 - 2, ox + W_ + 10, oy + H_ * 0.28 + 2, (*RED, int(255 * g)))
        f.text(ox + W_, oy + H_ * 0.28 - 14, '天花板：一天只有 24 小时', 15, col=RED, a=g, anc='rm')
    CH(f); headline(f, lt, ACC, '1', '自由职业：用时间换钱', None)
    return f


# =====================================================================
# 3 核心观点：人物走进透明“产品盒” → 独自一个市场 → 反愿景双路 → 书 → 兴趣光球汇成内容
# =====================================================================
INTS = [('健身', RED), ('哲学', PURPLE), ('设计', CYAN), ('商业', GOLD), ('写作', GREEN)]
def sc3(lt, d):
    k = 2; e = EV(k); cuts = [e[2], e[4]]
    if lt < e[2]:
        cam = orbit(0.2 + 0.03 * lt, lerp(7, 13, ease((lt - e[1]) / 2.5)), lerp(2.2, 6.5, ease((lt - e[1]) / 2.5)), (0, 1.0, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        g = ease((lt - 0.5) / 1.0)
        koe(f, (0, 0.12, 0), 0.4, 0.85, ra=0.3 + 1.2 * g, re=0.4)
        cube(f, (0, 0.06, 0), (1.4, 0.12, 1.4), ACC, 0.4)
        if g > 0.02:
            for x in (-0.7, 0.7):
                for z in (-0.7, 0.7): cube(f, (x, 0.12 + 1.1 * g, z), (0.04, 2.2 * g, 0.04), ACC, 0.7)
            for y in (0.12, 0.12 + 2.2 * g):
                for z in (-0.7, 0.7): cube(f, (0, y, z), (1.44, 0.04, 0.04), ACC, 0.7)
                for x in (-0.7, 0.7): cube(f, (x, y, 0), (0.04, 0.04, 1.44), ACC, 0.7)
            tag3d(f, (0, 2.75, 0), '产品：你自己', ACC, 18, g)
        if lt > e[1]:
            gc = ease((lt - e[1]) / 1.5)
            for i in range(60):
                a_ = i * 2.39996; r = 4.5 + 0.35 * math.sqrt(i)
                cube(f, (r * math.cos(a_) + 0, 0.3, r * math.sin(a_) - 2.5), (0.5, 0.6 * gc, 0.5), GREY, 0.1, R=roty(a_))
            ring(f, (0, 0.03, 0), 2.6, ACC, int(200 * gc), R=I3)
            note(f, 640, 470, '“你自己”这个市场：竞争者 = 0', gc, 24, accent=ACC)
        CH(f); headline(f, lt, ACC, '2', '核心观点：把你自己产品化', None)
        return f
    if lt < e[4]:
        t = lt - e[2]
        cam = orbit(0.0 + 0.02 * t, 11, 3.6, (0, 1.0, -1.5), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        for side, col, nm, sub in ((-1, RED, '反愿景', '绝不想过的人生'), (1, GOLD, '愿景', '想成为的人')):
            g = ease((t - (0.3 if side < 0 else 2.5)) / 0.8)
            for q in range(10):
                z = -q * 0.9
                cube(f, (side * (1.2 + q * 0.18), 0.03, z), (1.0, 0.06, 0.8), col if q < 10 * g else DARK, 0.3 * g + 0.05)
            tag3d(f, (side * 3.2, 1.0, -8.5), nm + ' · ' + sub, col, 17, g)
            if side < 0 and g > 0.2:
                for q in range(4): cube(f, (-2.4 - q * 0.3, 0.4 + 0.3 * q, -5 - q * 0.9), (0.5, 0.8, 0.5), (70, 40, 40), 0.1, R=roty(q))
        run = ease((t - 4.5) / 3.5)
        koe(f, (lerp(0, 2.4, run), 0, 1.0 - 6.0 * run), pi + 0.2, 0.85, walk=lt * 7 if 0 < run < 1 else None)
        if lt > e[3]:
            gb = pop(lt, e[3]); B = np.array([-3.5, 1.8, 0.8]); R = roty(0.6 + 0.15 * math.sin(lt))
            cube(f, B, (0.9 * gb, 1.25 * gb, 0.2 * gb), (30, 30, 34), 0.3, R=R)
            cube(f, B + R @ np.array([0.03, 0, 0]), (0.85 * gb, 1.2 * gb, 0.21 * gb), (235, 232, 222), 0.3, R=R)
            lab(f, B + [0, 0.15, 0], 'The Art', 13, (30, 30, 34), dy=0, a=gb); lab(f, B + [0, -0.1, 0], 'of Focus', 13, (30, 30, 34), dy=0, a=gb)
            tag3d(f, B + [0, 1.0, 0], '《专注的艺术》2024', ACC, 16, gb)
        CH(f); headline(f, lt, ACC, '2', '反愿景：先想清楚不要什么', None)
        return f
    t = lt - e[4]
    cam = orbit(0.3 + 0.04 * t, 9.5, 2.8, (0, 1.6, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    koe(f, (0, 0, 0), 0.3, 0.9, la=0.5, ra=0.5, lo=0.6, ro=0.6, le=0.6, re=0.6)
    merge_ = ease((lt - e[5]) / 1.5)
    for j, (nm, col) in enumerate(INTS):
        a_ = j / 5 * 2 * pi + t * 0.6; r = lerp(2.4, 0.5, merge_)
        P = np.array([r * math.cos(a_), 2.4 + 0.3 * math.sin(t * 2 + j) + 1.0 * merge_, r * math.sin(a_)])
        ball(f, P, 0.28 * pop(t, j * 0.25), col, 0.7)
        if merge_ < 0.5: tag3d(f, P + [0, 0.5, 0], nm, col, 15, pop(t, j * 0.25) * (1 - merge_ * 2))
    if merge_ > 0.3:
        A = ease((merge_ - 0.3) / 0.5)
        for q in range(6):
            page(f, (2.4, 0.4 + q * 0.5 * A, -0.4), s=0.8, R=roty(-0.4) @ rotx(-1.45), lines=3)
        tag3d(f, (2.4, 0.9 + 3 * A, -0.4), '成长 → 内容', GREEN, 17, A)
        if A > 0.3: beam(f, (0.3, 3.4, 0), (2.2, 0.6 + 2.5 * A, -0.4), GREEN, 180 * A, 3)
    CH(f); headline(f, lt, ACC, '2', '兴趣广泛是优势', '多个兴趣交汇 = 别人复制不了的视角')
    return f


# =====================================================================
# 4 写作系统：一个大想法光球 → 拆成短帖/长推文/长信 → 轮播/视频 → 四个平台 → 关注者与一亿浏览
# =====================================================================
PLAT = [('X', (230, 230, 235)), ('YouTube', (240, 60, 60)), ('Instagram', PINK), ('Newsletter', GOLD)]
def sc4(lt, d):
    k = 3; e = EV(k); cuts = [e[4]]
    if lt < e[4]:
        cam = orbit(0.15 + 0.03 * lt, lerp(7, 9.5, ease((lt - e[2]) / 3)), lerp(2.4, 3.2, ease((lt - e[2]) / 3)), (lerp(-2.2, 0.2, ease((lt - e[2]) / 3)), 2.3, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        koe(f, (-4.6, 0, 1.0), 0.9, 0.85, la=0.9, le=1.2, ra=0.2)
        gi = pop(lt, e[1])
        C = np.array([-2.6, 2.6 + 0.1 * math.sin(lt * 2), 0])
        if gi > 0:
            ball(f, C, 0.55 * gi, GOLD, 0.9)
            for q in range(3): ring(f, C, (0.75 + q * 0.18) * gi, GOLD, 120 - q * 30, R=rotx(lt * (0.7 + q * 0.3)) @ rotz(q))
            tag3d(f, C + [0, 0.95, 0], '每周 1 个大想法', GOLD, 17, gi)
        rows = [('短帖 × 3 / 天', CYAN, 0.5, 3), ('长推文 × 1 / 周', GREEN, 0, 1), ('长信 × 1 / 周', ORANGE, -0.5, 1)]
        if lt > e[2]:
            for j, (nm, col, dy, n) in enumerate(rows):
                g = ease((lt - e[2] - j * 0.5) / 0.6)
                P = np.array([0.6, 2.6 + dy * 3, 0])
                beam(f, C + [0.6, dy * 0.6, 0], P - [0.9, 0, 0], col, 180 * g, 3)
                flow(f, C + [0.6, dy * 0.6, 0], P - [0.9, 0, 0], lt + j, col, 2, 0.8, 0.06, a=int(230 * g))
                for q in range(n): page(f, P + [q * 0.3, 0, -q * 0.1], col=lerp_c(col, WHITE, 0.6), s=0.9 if n == 1 else 0.7, lines=3, a=255 * g)
                tag3d(f, P + [0.3 * (n - 1) / 2, -0.6, 0], nm, col, 15, g)
        if lt > e[3]:
            g = ease((lt - e[3]) / 0.8)
            for q in range(5):
                P = np.array([2.6 + q * 0.42 * g, 2.6 + 0.05 * math.sin(lt * 3 + q), -q * 0.05])
                cube(f, P, (0.38, 0.38, 0.02), lerp_c(GREEN, WHITE, q / 6), 0.5, R=roty(-0.3))
            tag3d(f, (3.4, 3.2, 0), '→ 图文轮播', GREEN, 15, g)
            beam(f, (1.1, 2.6, 0), (2.3, 2.6, 0), GREEN, 160 * g, 2)
            g2 = ease((lt - e[3] - 1.2) / 0.8)
            S = np.array([3.2, 1.1, 0]); screen_panel(f, S, 1.3 * g2 + 0.01, 0.8 * g2 + 0.01, a=g2)
            if g2 > 0.5: cube(f, S + [0, 0, 0.05], (0.24, 0.24, 0.01), (240, 60, 60), 0.8)
            tag3d(f, S + [0, -0.65, 0], '→ 视频', ORANGE, 15, g2)
            beam(f, (1.1, 1.1, 0), (2.5, 1.1, 0), ORANGE, 160 * g2, 2)
        CH(f); headline(f, lt, ACC, '3', '武器：写作系统', '一个想法 → 多种形式')
        return f
    t = lt - e[4]
    cam = orbit(0.1 * math.sin(t * 0.2), 10.5, 3.0, (0, 1.8, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    C = np.array([0, 3.6, 1.2])
    ball(f, C, 0.45, GOLD, 0.9); ring(f, C, 0.7, GOLD, 120, R=rotx(lt))
    grow = ease((lt - e[5]) / 4)
    for j, (nm, col) in enumerate(PLAT):
        P = np.array([(j - 1.5) * 2.6, 0, -1.8])
        h = 0.6 + 2.4 * grow * [0.55, 0.9, 1.0, 0.35][j]
        cube(f, P + [0, h / 2, 0], (1.2, h, 1.2), col, 0.35)
        tag3d(f, P + [0, h + 0.4, 0], nm, col, 16)
        flow(f, C, P + [0, h, 0], lt + j * 0.25, col, 3, 0.7, 0.07)
        for q in range(int(14 * grow)):
            b = q * 2.39996; r = 0.9 + 0.12 * q
            f.dots([P + [r * math.cos(b), 0.05, r * math.sin(b)]], 0.04, (*col, 180))
    if lt > e[5]:
        card(f, 60, 170, 300, 100, '各平台关注者（2026）', f'≈{int(400 * grow)}万', '', ACC, a=ease((lt - e[5]) / 0.4), vsz=34)
    if lt > e[6]:
        g = ease((lt - e[6]) / 0.5); v = ease((lt - e[6]) / 2.0)
        ox, oy = 940, 200
        f.rect(ox - 20, oy - 40, ox + 280, oy + 230, (12, 16, 28, int(220 * g)), r=12)
        f.text(ox, oy - 18, '2026.1 长文浏览量', 17, col=WHITE, a=g, anc='lm')
        f.rect(ox + 40, oy + 200 - 6, ox + 100, oy + 200, (*GREY, int(255 * g)))
        f.text(ox + 70, oy + 212, '普通帖', 14, col=GREY, a=g, anc='mm')
        f.rect(ox + 150, oy + 200 - 180 * v, ox + 210, oy + 200, (*ACC, int(255 * g)), r=3)
        f.text(ox + 180, oy + 190 - 180 * v, '1亿+', 20, col=ACC, a=g, anc='mb')
        f.text(ox + 180, oy + 212, '“一天修复人生”', 14, col=ACC, a=g, anc='mm')
    CH(f); headline(f, lt, ACC, '3', '同一想法，分发到所有平台', None)
    return f


# =====================================================================
# 5 价值阶梯：四级台阶，小人越往上越少 → 顶端软件 Kortex 碎裂 → 重组成 Eden 画布
# =====================================================================
LADDER = [('免费内容', '吸引读者', GREY, 1), ('2 Hour Writer', '低价 · 方法', CYAN, 2), ('Digital Economics', '高价 · 转变', PURPLE, 2), ('软件', 'Kortex → Eden', GOLD, 4)]
def sc5(lt, d):
    k = 4; e = EV(k); cuts = [e[5]]
    if lt < e[5]:
        cam = orbit(0.22 + 0.01 * lt, 10.5, 3.4, (0.4, 1.6, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        for j, (nm, sub, col, si) in enumerate(LADDER):
            g = ease((lt - e[si] - (0.8 if j == 2 else 0)) / 0.6) if j else ease((lt - e[1]) / 0.6)
            x = (j - 1.5) * 2.3; h = 0.5 + j * 0.8
            cube(f, (x, h / 2, 0), (2.2, h, 2.2), lerp_c(DARK, col, g), 0.2 + 0.2 * g)
            tag3d(f, (x, h + 0.02, 1.1), nm, col, 16, max(g, 0.25))
            if g > 0.5: lab(f, (x, h + 0.02, 1.1), sub, 14, col, dy=26, a=g)
            n = [26, 10, 5, 0][j]
            for q in range(int(n * g)):
                mini(f, (x - 0.8 + (q % 6) * 0.32, h, -0.8 + (q // 6) * 0.45), (130, 140, 165), 0.42, 0.15, yaw=-pi / 2)
        ky = 0.5 + 3 * 0.8
        if lt > e[4]:
            gk = pop(lt, e[4]); P = np.array([(3 - 1.5) * 2.3, ky + 0.6 + 0.05 * math.sin(lt * 2), 0])
            cube(f, P, (1.1 * gk, 0.7 * gk, 0.7 * gk), GOLD, 0.6, R=roty(lt * 0.5))
        koe(f, (-5.6, 0, 1.2), 0.6, 0.85, ra=1.4, re=0.4, la=0.1)
        if e[3] < lt < e[4] + 0.6: note(f, 640, 200, '卖的不是“怎么赚钱”，而是“成为会赚钱的人”', ease((lt - e[3]) / 0.4) * (1 - ease((lt - e[4]) / 0.6)), 22, accent=PURPLE)
        CH(f); headline(f, lt, ACC, '4', '商业模式：价值阶梯', '越往上，人越少，价值越高（示意）')
        return f
    t = lt - e[5]
    cam = orbit(0.08 * math.sin(t * 0.25), lerp(8.5, 8.0, ease((lt - e[6]) / 3)), 2.6, (0, 2.3, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    br = ease((lt - e[6] - 0.8) / 1.2); rb = ease((lt - e[6] - 2.6) / 2.0)
    rng = np.random.default_rng(3)
    off = rng.normal(0, 1, (36, 3)); spin = rng.normal(0, 1, 36)
    if rb < 1:
        for q in range(36):
            gx, gy = q % 6, q // 6
            home = np.array([(gx - 2.5) * 0.42, 2.0 + (gy - 2.5) * 0.42, 0])
            fly = home + off[q] * [1.6, 0.9, 1.2] * br + [0, -1.4 * br * br * (1 - rb), 0]
            P = lerp(fly, home * [2.6, 0, 0] + [0, 2.3 + (gy - 2.5) * 0.1, -0.5], rb) if rb > 0 else fly
            a = 255 * (1 - rb)
            cube(f, P, (0.38, 0.38, 0.38), GOLD if (gx + gy) % 3 else ORANGE, 0.4, a, R=roty(spin[q] * br * 3) @ rotx(spin[q] * br * 2))
        if lt > e[6] + 0.6:
            for q in range(4):
                g = ease((lt - e[6] - 0.6 - q * 0.1) / 0.3) * (1 - br)
                f.line([(-1.2 + q * 0.6, 3.2, 0.22), (-0.8 + q * 0.5, 2.4, 0.22), (-1.0 + q * 0.6, 1.4, 0.22)], (*RED, int(230 * g)), 3)
    if rb > 0:
        A = rb
        cube(f, (0, 2.3, -0.6), (6.4 * A, 3.4 * A, 0.08), (26, 30, 40), 0.3)
        cube(f, (0, 4.1 * A + 0.2 * (1 - A), -0.55), (6.4 * A, 0.28, 0.06), (50, 56, 70), 0.3)
        lab(f, (-2.6, 4.1, -0.5), 'Eden', 18, ACC, dy=0, a=A)
        f.layer()
        if lt > e[7]:
            items = [('文件', BLUE, (-2.2, 3.0)), ('视频链接', RED, (-2.2, 2.2)), ('网页', TEAL, (-2.2, 1.4))]
            gA = ease((lt - e[7] - 1.5) / 0.6)
            AIc = np.array([1.9, 2.3, -0.4])
            for j, (nm, col, (x, y)) in enumerate(items):
                g = pop(lt, e[7] + j * 0.35)
                P = np.array([x, y, -0.45])
                cube(f, P, (1.3 * g, 0.55 * g, 0.06), col, 0.45)
                tag3d(f, P + [0, 0, 0.1], nm, col, 14, g)
                if gA > 0:
                    Q = np.array([0.0, 3.0 - j * 0.8, -0.45])
                    beam(f, P + [0.7, 0, 0], Q - [0.55, 0, 0], col, 160 * gA, 2)
                    cube(f, Q, (1.1 * gA, 0.45, 0.06), (60, 66, 84), 0.4)
                    tag3d(f, Q + [0, 0, 0.1], ['转写', '打标签', '摘要'][j], WHITE, 13, gA)
                    beam(f, Q + [0.55, 0, 0], AIc, PURPLE, 140 * gA, 2)
            gi = ease((lt - e[7] - 2.4) / 0.6)
            if gi > 0:
                ball(f, AIc, 0.4 * gi, PURPLE, 0.9); ring(f, AIc, 0.6 * gi, PURPLE, 150, R=rotx(lt) @ rotz(0.4))
                tag3d(f, AIc + [0, 0.8, 0], 'AI 一起整理', PURPLE, 14, gi)
    if lt < e[6] + 1.0:
        g = ease(t / 0.4) * (1 - ease((lt - e[6] - 0.6) / 0.4))
        lab(f, (0, 3.75, 0), 'Kortex', 26, GOLD, a=g)
        card(f, 60, 170, 330, 100, 'Kortex 公开上线前（预售）', '≈$76万', '', GOLD, a=g, vsz=34, note='第三方报道 · 约 6 个月')
    elif lt < e[6] + 3.5:
        note(f, 640, 200, '底层架构有问题 → 推倒重来', ease((lt - e[6] - 1.0) / 0.4) * (1 - ease((lt - e[6] - 3.1) / 0.4)), 22, accent=RED)
    CH(f); headline(f, lt, ACC, '4', '最上面一级：软件', None)
    return f


# =====================================================================
# 6 AI 时代：灰色网课屏退潮 → AI 光球一对一陪练 → 地球上 70 亿个光点 → 复制品 vs 你 → 护城河
# =====================================================================
def sc6(lt, d):
    k = 5; e = EV(k); cuts = [e[3], e[4]]
    if lt < e[3]:
        cam = orbit(-0.15 + 0.02 * lt, 9.0, 3.0, (1.0, 1.5, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        fade = ease((lt - e[1]) / 1.5)
        S = np.array([-2.8, 2.0 - 1.5 * fade, -1.0])
        screen_panel(f, S, 2.6, 1.6, a=1 - 0.7 * fade)
        cube(f, S + [0, 0, 0.05], (0.35, 0.35, 0.01), (110, 110, 120), 0.5, 255 * (1 - fade))
        tag3d(f, S + [0, 1.1, 0], '静态网课', GREY, 16, 1 - 0.5 * fade)
        if fade > 0.5:
            sx, sy, _ = f.pt(S + [0, 1.1, 0]); f.rect(sx - 45, sy - 1.5, sx + 45, sy + 1.5, (*RED, 230))
        if lt > e[1] + 1.0:
            g = ease((lt - e[1] - 1.0) / 0.8)
            tag3d(f, (2.0, 3.6, 0), '学习体验', ACC, 18, g)
        if lt > e[2]:
            n = 6
            for j in range(n):
                g = pop(lt, e[2] + j * 0.25)
                x = 0.2 + (j % 3) * 1.6; z = -0.6 + (j // 3) * 1.8
                mini(f, (x, 0, z), (140, 150, 175), 0.6 * g, 0.2, yaw=0)
                O = np.array([x, 1.35 + 0.1 * math.sin(lt * 3 + j), z])
                ball(f, O, 0.15 * g, PURPLE, 0.9)
                ring(f, O, 0.25 * g, PURPLE, int(140 * g), R=rotx(lt * 2 + j))
            B = np.array([4.8, 2.0, -0.8])
            koe(f, (5.6, 0, -0.8), -pi / 2, 0.85, ra=1.0, re=0.8)
            ball(f, B, 0.3 * ease((lt - e[2]) / 0.5), GOLD, 0.9)
            for j in range(n):
                x = 0.2 + (j % 3) * 1.6; z = -0.6 + (j // 3) * 1.8
                flow(f, B, (x, 1.35, z), lt + j * 0.2, GOLD, 1, 0.6, 0.05)
            tag3d(f, B + [0, 0.6, 0], '他的知识', GOLD, 15)
            tag3d(f, (1.8, 2.2, 0.3), 'AI 一对一陪练', PURPLE, 16, ease((lt - e[2] - 1) / 0.4))
        CH(f); headline(f, lt, ACC, '5', 'AI 时代的判断', None)
        return f
    if lt < e[4]:
        t = lt - e[3]
        cam = orbit(0.4 + 0.08 * t, 7.5, 1.6, (0, 2.0, 0), 45)
        f = base(cam, lt, d, cuts); floor(f, FL)
        C = np.array([0, 2.0, 0]); ball(f, C, 1.6, (30, 50, 90), 0.25)
        n = int(900 * ease(t / 3))
        pts = []
        for i in range(n):
            y = 1 - 2 * (i + 0.5) / 900; r = math.sqrt(1 - y * y); a_ = i * 2.39996 + t * 0.4
            P = C + 1.63 * np.array([r * math.cos(a_), y, r * math.sin(a_)])
            pts.append(P)
        f.dots(pts, 0.03, (*ACC, 220))
        card(f, 60, 170, 330, 100, '他的愿景', '≈70亿', '家公司', ACC, a=ease(t / 0.5), vsz=34, note='每个人都是一家公司')
        CH(f); headline(f, lt, ACC, '5', '每个人都是一家公司', None)
        return f
    t = lt - e[4]
    cam = orbit(0.1 + 0.03 * t, lerp(11, 9, ease((lt - e[7]) / 2)), lerp(4.0, 3.0, ease((lt - e[7]) / 2)), (0, 1.0, 0), 45)
    f = base(cam, lt, d, cuts); floor(f, FL)
    copies = int(40 * ease(t / 3))
    for i in range(copies):
        a_ = i * 2.39996; r = 3.0 + 0.3 * math.sqrt(i)
        mini(f, (r * math.cos(a_), 0, r * math.sin(a_)), (120, 125, 140), 0.55, 0.1, yaw=math.atan2(-math.cos(a_), -math.sin(a_)))
        if i % 3 == 0: page(f, (r * math.cos(a_), 1.25, r * math.sin(a_)), col=(170, 170, 180), s=0.45, lines=2, R=roty(-a_))
    if copies: tag3d(f, (-3.5, 1.9, 2.0), '人人都能复制', GREY, 15, ease(t / 1))
    hi = ease((lt - e[6]) / 0.8)
    koe(f, (0, 0.25, 0), 0.2, 0.95, la=0.3, ra=0.3 + 2.0 * hi, re=0.4)
    cube(f, (0, 0.12, 0), (1.6, 0.24, 1.6), lerp_c(DARK, ACC, hi), 0.3)
    if hi > 0: ball(f, (0.35, 2.75, 0.2), 0.14 * hi, ACC, 1.0)
    if lt > e[5] and lt < e[6] + 0.5:
        note(f, 640, 200, '“AI 能模仿你的风格，却不能替你决定什么重要”', ease((lt - e[5]) / 0.4) * (1 - ease((lt - e[6]) / 0.5)), 22, accent=ACC)
    if lt > e[6]:
        tag3d(f, (0, 3.3, 0), '你的视角 · 你的品味', ACC, 17, hi)
    if lt > e[7]:
        A = ease((lt - e[7]) / 1.0)
        ring(f, (0, 0.04, 0), 1.6, CYAN, int(200 * A), R=I3)
        ring(f, (0, 0.04, 0), 2.3, CYAN, int(200 * A), R=I3)
        for q in range(48):
            a_ = q / 48 * 2 * pi; r = 1.95
            f.dots([(r * math.cos(a_), 0.06 + 0.04 * math.sin(lt * 3 + q), r * math.sin(a_))], 0.06, (*CYAN, int(200 * A)))
        note(f, 640, 200, '最后的护城河，就是你自己', A, 28, accent=CYAN)
    CH(f); headline(f, lt, ACC, '5', 'AI 让模仿变便宜', None)
    return f


# =====================================================================
# 7 三点借鉴：三根柱子依次升起（标签在柱顶上方，总结提示放在画面上方）→ 片尾
# =====================================================================
def sc7(lt, d):
    k = 6; e = EV(k)
    cam = orbit(0.1 * math.sin(lt * 0.3), lerp(10.5, 12, ease(lt / 8)), 2.8, (0, 1.8, 0), 45)
    f = base(cam, lt, d); floor(f, FL)
    words = [('写出来', '学习 = 输出'), ('建系统', '固定节奏 · 一稿多用'), ('做你自己', 'AI 替代不了')]
    for j in range(3):
        c = TK[j][0]; g = ease((lt - e[1 + j]) / 0.7)
        if g < 0.01: continue
        x = (j - 1) * 3.6; h = 2.6 * g
        cube(f, (x, h / 2, -0.6), (2.4, max(h, 0.02), 1.4), c, 0.4)
        lab(f, (x, h + 0.6, -0.6), words[j][0], 24, WHITE, a=g); lab(f, (x, h + 0.6, -0.6), words[j][1], 17, c, dy=14, a=g)
    koe(f, (5.0, 0, 1.6), -0.5, 0.85, ra=2.6 if lt > e[5] else 0.2, ro=0.3, re=0.3 + 0.4 * math.sin(lt * 6) if lt > e[5] else 0.2)
    if e[4] < lt:
        f.text(640, 500, '文中收入、关注者等数字来自公开报道，仅供参考', 16, col=GREY, a=ease((lt - e[4]) / 0.4), anc='mm')
    if lt > e[5]:
        A = ease((lt - e[5]) / 0.5)
        f.rect(390, 530, 890, 584, (*ACC, int(220 * A)), r=10); f.text(640, 557, '人物讲解 · 我们下期见', 26, col=(20, 20, 24), anc='mm', a=A)
    CH(f); headline(f, lt, ACC, None, '三点借鉴')
    return f


FILM = Film(SEG, dur, [sc1, sc2, sc3, sc4, sc5, sc6, sc7], DISP,
            chapters=['开场', '起点', '核心观点', '写作系统', '价值阶梯', 'AI 时代', '借鉴'], total=TOTAL, lead=0.15)
