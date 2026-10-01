"""马斯克 · 三分钟 3D 传记（信息截至 2026-09-30）—— Blockbuster 样例片
渲染：python3 -m bb render examples/musk/film.py out.mp4 --jobs 2
静帧：python3 -m bb still examples/musk/film.py 30 112
"""
from bb.render3d import *
from bb.assets import *
from bb.timeline import split_subs, starts_from_durations

dur = [18.17, 22.08, 20.49, 22.96, 28.60, 26.66, 22.54, 26.79]   # 实测旁白时长（s1–s8，已 1.1× 变速）
SEG = starts_from_durations(dur, first=0.6, gap=0.4)
TOTAL = SEG[-1] + dur[-1] + 0.4 + 1.5

# ---------------- subtitles（| 为手动断句，按字数分配时长）----------------
# ---------------- subtitles ----------------
RAW = [
 [(0,5,"2026年9月28日，SpaceX的星舰第一次进入轨道"),(5,8,"还顺手部署了26颗星链卫星"),(8,10,"站在这枚巨型火箭背后的"),(10,13,"是全球最富有、也最具争议的人之一"),(13,15,"埃隆·马斯克"),(15,18.1,"接下来三分钟，我们看看他是怎么走到今天的")],
 [(0,4.4,"1971年，马斯克出生在南非比勒陀利亚"),(4.4,8.8,"他从小沉迷电脑，12岁就卖出了自己编写的游戏"),(8.8,12.5,"17岁离开南非，经加拿大来到美国"),(12.5,16.6,"在宾夕法尼亚大学拿下物理和经济学位"),(16.6,22,"1995年，他进入斯坦福读博，两天后就退学创业")],
 [(0,5.2,"第一家公司Zip2在1999年以约3亿美元卖出"),(5.2,8.9,"随后，他创办的在线银行并入PayPal"),(8.9,12.6,"2002年，被eBay以15亿美元收购"),(12.6,15.6,"30岁出头，他已身家过亿"),(15.6,20.4,"却把几乎全部的钱|压在了两件看起来最不可能成功的事上")],
 [(0,23,"第一件是火箭|2002年他创立SpaceX|前三次发射全部失败|2008年第四次才成功入轨|之后猎鹰9号实现了火箭回收复用|龙飞船把宇航员送上空间站|星链在轨卫星超过11000颗|成为公司最赚钱的业务")],
 [(0,10.8,"第二件是电动车|2004年他投资特斯拉|2008年出任首席执行官|那一年特斯拉和SpaceX都差点破产"),(10.8,16.5,"此后Model S、Model 3和Model Y让电动车走进主流"),(16.5,21.2,"2025年，股东批准了他|可能价值上万亿美元的新薪酬方案"),(21.2,26.6,"2026年9月，没有方向盘的|无人驾驶出租车开始在奥斯汀载客"),(26.6,28.6,"不过目前只有45辆")],
 [(0,26.6,"他的版图远不止于此|脑机接口公司Neuralink|隧道公司Boring|2022年，他以440亿美元收购推特|并改名为X|2023年创办人工智能公司xAI，推出Grok|2026年2月，SpaceX合并了xAI|火箭、卫星、社交网络和人工智能|被装进了同一家公司")],
 [(0,23,"他也始终处在争议中心|2024年他高调支持特朗普|2025年领导政府效率部|几个月后离开，并与特朗普公开决裂|之后又重修旧好|2026年5月，他起诉OpenAI的案子被陪审团驳回|9月，一部关于他的纪录片在威尼斯首映|他斥之为“抹黑”")],
 [(0,3.8,"今年6月，SpaceX完成史上规模最大的上市"),(3.8,6,"市值约2万亿美元"),(6,10.2,"马斯克成为有史以来第一位身家破万亿美元的人"),(10.2,13.1,"9月29日，他坐在特朗普身旁"),(13.1,16,"出席白宫人工智能协议的签署"),(16,19.7,"有人说他是这个时代最伟大的工程企业家"),(19.7,23,"也有人认为他权力过大、言行失控"),(23,26.8,"唯一确定的是，未来很多年我们都绕不开这个名字")]]
SUBS = split_subs(RAW)
def ev(k, i): return SUBS[k][i][0]

# ---------------- models ----------------
M_SHIP = starship(); M_F9 = falcon(); M_F1 = falcon(7, 0.3); M_LEGS = legs()
M_GLOBE = sphere(10, (22,52,110), 36, 18); M_MARS = sphere(6, (170,70,40), 28, 14); M_EARTH_S = sphere(3, (30,80,170), 20, 10)
M_CARS = [car((200,30,40)), car((225,228,235)), car((40,90,200)), car((150,155,165))]
M_CAPS = merge([part(*lathe([(0,0),(1.2,0),(1.2,0.3),(0.5,1.8),(0,1.9)], 16), (230,232,236))])
M_STATION = merge([box(6, 1, 1, (200,200,205)), box(1, 1, 4, (190,190,195)), box(0.1, 3, 5, (40,70,150), T=(-3.6, 0, 0)), box(0.1, 3, 5, (40,70,150), T=(3.6, 0, 0))])
M_COIN = disc(1.5, 0.25, (230,180,60))
M_NODE = sphere(1, (255,255,255), 16, 8)
M_BOX = box(1, 1, 1, (255,255,255))

# ---------- Austin city (static) ----------
ROADS = list(range(-24, 25, 8))
def _build_city():
    cr = np.random.default_rng(11); ms = []; E = []; gs = []
    def put(m, e=0.0): ms.append(m); E.append(np.full(len(m.F), e))
    def gput(m): gs.append(m)
    gput(box(64, 0.1, 70, (18,22,28), T=(0, -0.05, 2)))
    gput(box(64, 0.12, 7, (22,55,105), T=(0, -0.02, 30)))                    # 湖
    put(box(2.4, 0.5, 8, (90,92,100), T=(-8, 0.25, 30))); put(box(2.4, 0.5, 8, (90,92,100), T=(8, 0.25, 30)))  # 桥
    for v in ROADS:
        gput(box(54, 0.04, 2.2, (40,42,48), T=(0, 0.02, v))); gput(box(2.2, 0.045, 54, (40,42,48), T=(v, 0.02, 0)))
    for i in range(-3, 3):
        for j in range(-3, 3):
            cx, cz = i * 8 + 4, j * 8 + 4
            gput(box(5.6, 0.18, 5.6, (70,72,80), T=(cx, 0.09, cz)))           # 人行道街区
            if (i, j) == (1, 2):                                           # 议会大厦
                put(box(4.6, 1.2, 3.0, (200,160,140), T=(cx, 0.8, cz))); put(box(1.8, 1.0, 1.8, (205,165,145), T=(cx, 1.9, cz)))
                V, F = lathe([(0.95, 0), (0.95, 0.3), (0.8, 0.9), (0.5, 1.3), (0.15, 1.5), (0.1, 2.0), (0, 2.1)], 14)
                put(part(V, F, (215,175,150), T=(cx, 2.4, cz)))
                for x in (-1.9, 1.9): put(box(0.5, 0.9, 0.5, (190,150,130), T=(cx + x, 1.85, cz)))
                continue
            if (i, j) in ((1, 1), (-3, 0)):                                   # 公园
                gput(box(5.4, 0.05, 5.4, (30,70,40), T=(cx, 0.2, cz)))
                for q in range(9):
                    tx, tz = cx + cr.uniform(-2.2, 2.2), cz + cr.uniform(-2.2, 2.2)
                    put(box(0.15, 0.6, 0.15, (70,50,35), T=(tx, 0.5, tz)))
                    V, F = lathe([(0, 0), (0.6, 0.3), (0.5, 0.9), (0, 1.3)], 6); put(part(V, F, (40, 110 + q * 5, 55), T=(tx, 0.7, tz)))
                continue
            dist = math.hypot(cx, cz + 4); down = math.exp(-dist ** 2 / 180)
            subs_ = [(cx, cz, 5.0)] if down > 0.5 else [(cx - 1.35, cz - 1.35, 2.3), (cx + 1.35, cz - 1.35, 2.3), (cx - 1.35, cz + 1.35, 2.3), (cx + 1.35, cz + 1.35, 2.3)]
            for bx, bz, w in subs_:
                if w < 3 and cr.random() < 0.2: continue
                h = (1.2 + cr.uniform(0, 2.5)) + down * cr.uniform(9, 18)
                w2 = w * cr.uniform(0.75, 0.95); tone = cr.integers(0, 3)
                col = [(52,66,92), (70,76,88), (46,58,70)][tone]
                put(box(w2, h, w2, col, T=(bx, 0.18 + h / 2, bz), top=0.92 if h > 10 else 1.0))
                bands = int(h / 0.9)
                for b in range(1, bands):
                    if cr.random() < 0.3: continue
                    y = 0.18 + b * 0.9; sh = 0.92 if h > 10 else 1.0; ww = w2 * (1 - (1 - sh) * (y - 0.18) / h) + 0.04
                    put(box(ww, 0.13, ww, (255, 200, 120) if cr.random() < 0.7 else (160, 210, 255), T=(bx, y, bz)), 0.45)
                if h > 14: put(box(0.1, 2.2, 0.1, (160,160,170), T=(bx, 0.18 + h + 1.1, bz)))
    M = merge(ms); M.E = np.concatenate(E); return merge(gs), M
M_GROUND, M_CITY = _build_city()
CAPITOL_TOP = (12, 4.6, 20)
LAMPS = [(v + sgn * 1.3, 0.5, a) for v in ROADS for a in range(-24, 25, 4) for sgn in (-1, 1)][::2]
M_CAB = merge([box(1.7, 0.45, 0.85, (200,205,215), T=(0, 0.33, 0)), box(1.0, 0.36, 0.78, (25,30,40), T=(-0.1, 0.72, 0), top=0.7)])

# ---------------- scenes ----------------
GOLD = (255, 200, 80); CY = (110, 200, 255); RED = (255, 90, 80)
def big_date(f, lt, s1, s2, a=1.0):
    e = ease(lt / 0.6) * a
    f.text(70 - 30 * (1 - e), 70, s1, 64, GOLD, 'la', a=e); f.text(72 - 30 * (1 - e), 150, s2, 30, (230,235,245), 'la', a=e)

def sc1(lt, d):
    if lt < 7.2:
        ry = 0 if lt < 1 else 0.7 * (lt - 1) ** 2
        a = 0.5 + 0.06 * lt
        f = Fr(orbit(a, 42 + lt * 2, 4 + lt * 1.2, (0, 9 + ry * 0.75, 0), 50)); f.grid(0, 60, 5)
        f.layer()
        f.mesh(box(8, 0.6, 8, (60,62,68)), T=(0, 0.3, 0))
        f.mesh(box(1.6, 24, 1.6, (70,72,80)), T=(4.5, 12, 0)); f.mesh(box(3, 0.4, 0.6, (80,82,90)), T=(3, 20, 0))
        f.mesh(M_SHIP, T=(0, 0.6 + ry, 0))
        f.layer(); exhaust(f, lambda b: (0, 0.6 + (0 if b < 1 else 0.7 * (b - 1) ** 2), 0), lt, 90, 1.0, 3.0, ground=0.3, t0=0.2)
        f.dim = 1 - ease((lt - 6.9) / 0.3)
        big_date(f, lt, "2026.09.28", "星舰 Flight 14 · 首次入轨")
        return f
    if lt < 13:
        u = lt - 7.2
        f = Fr(orbit(0.3 + 0.04 * u, 36, 9, (0, 0, 0), 45))
        Rm = draw_globe(f, (0, 0, 0), 10, 0.1 * u)
        tilt = rotx(0.35); ring = [tilt @ [13.5 * math.cos(q), 0, 13.5 * math.sin(q)] for q in np.linspace(0, 2 * pi, 97)]
        f.layer()
        rp = [p for p in ring]
        for i in range(len(rp) - 1):
            if not occluded(f, np.array(rp[i]), np.zeros(3), 10): f.line(rp[i:i + 2], (110,200,255,90), 2)
        ang0 = 0.35 * u + 1.2; ship = tilt @ [13.5 * math.cos(ang0), 0, 13.5 * math.sin(ang0)]
        if not occluded(f, ship, np.zeros(3), 10): f.dots([ship], 0.45, (255,255,255,255))
        sats = []
        for i in range(26):
            tb = 0.8 + 0.14 * i
            if u > tb:
                q = ang0 - 0.03 * (u - tb) * (1 + i * 0.08) - 0.02 * i
                P = tilt @ [13.5 * math.cos(q), 0, 13.5 * math.sin(q)]
                if not occluded(f, P, np.zeros(3), 10): sats.append(P)
        if sats: f.dots(sats, 0.22, (255,210,110,255))
        n = sum(1 for i in range(26) if u > 0.8 + 0.14 * i)
        f.label(ship, "Starship", 22, (255,255,255), 30, -30)
        f.text(70, 70, "%d" % n, 96, GOLD, 'la'); f.text(74, 185, "颗 Starlink V3 卫星入轨", 30, (230,235,245))
        f.dim = ease(u / 0.3) * (1 - ease((lt - 12.7) / 0.3))
        return f
    u = lt - 13
    f = Fr(orbit(0.2 * u, 30, 4, (0, 0, 0), 45))
    pts, cols = [], []
    for i in range(420):
        a = i / 420 * 2 * pi + 0.1 * u * (1 + (i % 3) * 0.3); rr = 11 + 1.5 * math.sin(i * 1.7)
        pts.append([rr * math.cos(a), 1.5 * math.sin(i * 2.3 + u), rr * math.sin(a)]); cols.append((255, 190 + (i % 60), 90, 200))
    f.dots(pts, 0.12, cols)
    e = ease(u / 0.8)
    f.text(W / 2, H / 2 - 60, "ELON MUSK", 104, (255,255,255), 'mm', a=e)
    f.text(W / 2, H / 2 + 40, "埃隆 · 马斯克", 44, GOLD, 'mm', a=ease((u - 0.4) / 0.8))
    f.text(W / 2, H / 2 + 100, "3 分钟 · 8 个节点", 26, (180,190,210), 'mm', bold=False, a=ease((u - 2.0) / 0.8))
    f.dim = ease(u / 0.3); return f

CITIES = [(-25.7, 28.2, "1971 · 南非 比勒陀利亚"), (44.2, -76.5, "1989 · 17 岁 · 加拿大"), (39.95, -75.2, "宾夕法尼亚大学 · 物理 + 经济"), (37.4, -122.2, "1995 · 斯坦福读博 2 天 → 退学")]
def sc2(lt, d):
    cues = [0, ev(1, 2), ev(1, 3), ev(1, 4)]
    idx = max(i for i in range(4) if lt >= cues[i])
    def rot_for(i): return math.radians(CITIES[i][1]) - pi / 2
    def lat_for(i): return CITIES[i][0]
    if idx == 0: rot, lat = rot_for(0) + 0.05 * lt, lat_for(0)
    else:
        e = ease((lt - cues[idx]) / 1.6); p = idx - 1
        r0 = rot_for(p) + (0.05 * cues[1] if p == 0 else 0); r1 = rot_for(idx)
        while r1 - r0 > pi: r1 -= 2 * pi
        while r1 - r0 < -pi: r1 += 2 * pi
        rot, lat = lerp(r0, r1, e), lerp(lat_for(p), lat_for(idx), e)
    el = math.radians(lat) * 0.8
    f = Fr(Cam([0, 30 * math.sin(el), 30 * math.cos(el)], [0, 0, 0], 45))
    Rm = draw_globe(f, (0, 0, 0), 10, -rot)
    f.layer()
    P = [Rm @ ll(la, lo) * 10 for la, lo, _ in CITIES]
    for i in range(1, 4):
        if lt > cues[i]:
            pr = ease((lt - cues[i]) / 1.4); a, b = nrm(P[i - 1]), nrm(P[i]); om = math.acos(clamp(np.dot(a, b), -1, 1))
            arc = []
            for s_ in np.linspace(0, pr, 40):
                v = (math.sin((1 - s_) * om) * a + math.sin(s_ * om) * b) / math.sin(om) if om > 1e-3 else a
                arc.append(v * 10 * (1 + 0.3 * math.sin(pi * s_)))
            for j in range(len(arc) - 1):
                if not occluded(f, arc[j], np.zeros(3), 10): f.line(arc[j:j + 2], (255,200,80,230), 4)
    for i in range(4):
        if lt > cues[i] + (1.2 if i else 0) and facing(f, P[i], np.zeros(3)):
            pulse = (lt * 1.2) % 1
            f.dots([P[i] * 1.01], 0.35, (255,210,90,255))
            if i == idx: f.label(P[i], CITIES[i][2], 26, (255,255,255), 40, -60)
    yrs = [(0, 1971), (ev(1, 1), 1983), (cues[1], 1989), (cues[2], 1992), (cues[3], 1995)]
    y = [v for t_, v in yrs if lt >= t_][-1]
    f.text(70, 60, str(y), 88, GOLD, 'la')
    if ev(1, 1) <= lt < cues[1]:
        e = ease((lt - ev(1, 1)) / 0.5)
        f.text(74, 170, "12 岁 · 自编游戏 Blastar 卖出 500 美元", 28, (230,235,245), a=e)
    f.dim = ease(lt / 0.4); return f

def sc3(lt, d):
    c1, c2, c3, c4 = ev(2, 1), ev(2, 2), ev(2, 3), ev(2, 4)
    th = lerp(4, 11, ease((lt - c2) / 2)); rad = lerp(26, 34, ease((lt - c3) / 2))
    f = Fr(orbit(-0.5 + 0.05 * lt, rad, lerp(5, 12, ease((lt - c2) / 2)), (0, th, 0), 45)); f.grid(0, 40, 4, (255,200,80,35)); f.layer()
    fade = 1 - ease((lt - c4) / 1.0)
    h1 = 3.07 * 1.3 * ease((lt - 0.4) / 1.8)
    if fade > 0.02:
        if h1 > 0.01: f.mesh(M_BOX, sc=1, R=np.diag([3, h1, 3]), T=(-5, h1 / 2, 0), col=(90,170,255))
        if lt > c1:
            m = ease((lt - c1) / 2.2)
            f.mesh(M_BOX, R=np.diag([1.6, 1.6, 1.6]), T=(lerp(9, 5, m), 0.8, lerp(4, 0, m)), col=(120,210,140))
            f.mesh(M_BOX, R=np.diag([1.6, 1.6, 1.6]), T=(lerp(1, 5, m), 0.8, lerp(-4, 0, m)), col=(90,140,255))
        if lt > c2:
            h2 = 15 * 1.3 * ease((lt - c2) / 2.2); f.mesh(M_BOX, R=np.diag([3, h2, 3]), T=(5, h2 / 2, 0), col=(255,200,80))
            f.label((5, h2, 0), "PayPal → eBay · 15 亿美元 · 2002", 28, GOLD, 40, -40, a=fade)
        f.label((-5, h1, 0), "Zip2 · 约 3.07 亿美元 · 1999", 28, (150,210,255), -40, -60, a=fade * ease((lt - 1) / 0.6))
        if c1 < lt < c2 + 1:
            f.label((5, 2, 0), "X.com + Confinity = PayPal", 26, (180,240,190), 40, 40, a=ease((lt - c1) / 0.6))
    if lt > c3:
        f.text(70, 60, "30 岁出头", 40, (230,235,245), a=ease((lt - c3) / 0.6))
        f.text(70, 115, "身家过亿", 72, GOLD, a=ease((lt - c3 - 0.3) / 0.6))
    if lt > c4:
        for i, (nm, col, x) in enumerate([("火箭", (255,120,80), -4), ("电动车", (80,200,255), 4)]):
            tb = c4 + 0.3 + i * 0.8; u = lt - tb
            if u > 0:
                y = max(1.6, 25 - 20 * u * u); f.mesh(M_BOX, R=roty(u * 0.8) @ np.diag([3.2, 3.2, 3.2]), T=(x, y, 3), col=col, emis=0.2)
                if y < 10: f.label((x, y + 1.6, 3), nm, 34, col, 0, -40, dot=False)
        f.text(W - 70, 60, "ALL IN", 88, (255,255,255), 'ra', a=ease((lt - c4 - 2) / 0.6))
    f.dim = ease(lt / 0.4); return f

def sc4(lt, d):
    e = [ev(3, i) for i in range(8)]
    if lt < e[4]:
        f = Fr(orbit(0.3 + 0.03 * lt, 26, 5, (0, 4 + (max(0, lt - e[3]) ** 2) * 0.6, 0), 45)); f.grid(0, 40, 4); f.layer()
        for i in range(4):
            x = -7.5 + i * 5; f.mesh(box(2.5, 0.4, 2.5, (60,62,68)), T=(x, 0.2, 0))
            if i < 3:
                tf = e[2] + i * 0.8; u = lt - tf
                if u > 0:
                    ang = min(1.35, u * u * 2.5); col = (255, int(lerp(235, 90, min(1, u))), int(lerp(240, 80, min(1, u))))
                    f.mesh(M_F1, R=rotz(-ang), T=(x, 0.4, 0), col=col)
                    f.label((x + 2, 1.5, 0), "× 第 %d 次" % (i + 1), 28, RED, 0, -50, dot=False)
                else: f.mesh(M_F1, T=(x, 0.4, 0))
            else:
                ry = max(0, lt - e[3]) ** 2 * 1.2; f.mesh(M_F1, T=(x, 0.4 + ry, 0))
                if lt > e[3]:
                    f.layer(); exhaust(f, lambda b: (x, 0.4 + max(0, b - e[3]) ** 2 * 1.2, 0), lt, 60, 0.8, 1.5, ground=0.4, t0=e[3], scale=0.6)
                    f.label((x, 7.5 + ry, 0), "成功！2008 · 第 4 次入轨", 30, (140,255,160), 30, -30)
        if lt > e[1]: f.text(70, 60, "2002", 88, GOLD, a=ease((lt - e[1]) / 0.5)); f.text(74, 165, "创立 SpaceX", 32, (230,235,245), a=ease((lt - e[1]) / 0.5))
        f.dim = ease(lt / 0.4) * (1 - ease((lt - e[4] + 0.3) / 0.3)); return f
    if lt < e[6]:
        u = lt - e[4]; T5 = e[5] - e[4]
        if lt < e[5]:
            y = max(0.6, 26 * (1 - u / (T5 - 0.6)) ** 2) if u < T5 - 0.6 else 0.6
            f = Fr(orbit(0.8 + 0.08 * u, 30, 3, (0, 7 + y * 0.4, 0), 45)); f.grid(0, 50, 5); f.layer()
            f.mesh(disc(5, 0.3, (70,72,80)), T=(0, 0, 0)); f.mesh(M_F9, T=(0, y, 0)); f.mesh(M_LEGS, T=(0, y, 0), sc=1)
            if y > 0.7: f.layer(); exhaust(f, lambda b: (0, max(0.6, 26 * (1 - (b - e[4]) / (T5 - 0.6)) ** 2), 0), lt, 80, 0.5, 1.2, ground=0.3, t0=e[4], scale=0.7)
            f.label((0, y + 7, 0), "猎鹰 9 号 · 垂直回收 · 复用", 30, (255,255,255), 40, -20)
            f.dim = ease(u / 0.3) * (1 - ease((lt - e[5] + 0.3) / 0.3)); return f
        u = lt - e[5]; T6 = e[6] - e[5]; m = ease(u / T6)
        f = Fr(orbit(0.4 + 0.05 * u, 22, 4, (0, 0, 0), 45)); f.layer()
        f.mesh(M_STATION, R=roty(0.3), T=(3, 2, -2)); f.mesh(M_CAPS, R=rotz(pi / 2), T=(lerp(-16, -0.5, m), 2, -2), sc=1)
        f.label((lerp(-16, -0.5, m), 3.5, -2), "龙飞船 · 载人往返空间站", 28, (255,255,255), 30, -50)
        f.dim = ease(u / 0.3) * (1 - ease((lt - e[6] + 0.3) / 0.3)); return f
    u = lt - e[6]
    f = Fr(orbit(0.2 + 0.05 * u, 38 - 4 * ease(u / 4), 8, (0, 0, 0), 45))
    draw_globe(f, (0, 0, 0), 10, 0.05 * u); f.layer()
    pts = []; nshow = int(1400 * ease(u / 3))
    for i in range(nshow):
        pl = i % 28; k = i // 28; inc = 0.93 if pl % 2 else 0.55; raan = pl * 2 * pi / 28
        q = k / 50 * 2 * pi + u * 0.25; r = 10.6
        p = roty(raan) @ rotx(inc) @ [r * math.cos(q), 0, r * math.sin(q)]
        if not occluded(f, p, np.zeros(3), 10): pts.append(p)
    if pts: f.dots(pts, 0.07, (180,230,255,230))
    n = int(11000 * ease(u / 3))
    f.text(70, 60, "{:,}+".format(n), 88, GOLD); f.text(74, 178, "颗星链卫星在轨 · SpaceX 最赚钱的业务", 30, (230,235,245))
    f.dim = ease(u / 0.3); return f

def sc5(lt, d):
    e = [ev(4, i) for i in range(len(SUBS[4]))]  # 0..3 intro, 4 models, 5,6 pay, 7,8 cab, 9 45
    if lt < e[4]:
        f = Fr(orbit(0.6 + 0.25 * lt, 12, 3, (0, 1, 0), 45)); f.grid(0, 30, 2, (255,90,80,30) if lt > e[3] else (90,160,255,40)); f.layer()
        f.mesh(disc(3.4, 0.15, (50,52,60)), T=(0, -0.15, 0)); f.mesh(M_CARS[0], T=(0, 0, 0))
        if lt > e[1]: f.text(70, 60, "2004", 80, GOLD, a=ease((lt - e[1]) / 0.5)); f.text(74, 160, "投资特斯拉", 30, (230,235,245), a=ease((lt - e[1]) / 0.5))
        if lt > e[2]: f.text(70, 220, "2008", 80, GOLD, a=ease((lt - e[2]) / 0.5)); f.text(74, 320, "出任 CEO", 30, (230,235,245), a=ease((lt - e[2]) / 0.5))
        if lt > e[3]:
            fl = 0.6 + 0.4 * abs(math.sin((lt - e[3]) * 5))
            f.text(W - 70, 70, "特斯拉 + SpaceX", 36, RED, 'ra', a=fl); f.text(W - 70, 125, "双双濒临破产", 52, RED, 'ra', a=fl)
        f.dim = ease(lt / 0.4) * (1 - ease((lt - e[4] + 0.3) / 0.3)); return f
    if lt < e[5]:
        u = lt - e[4]; f = Fr(orbit(0.5 + 0.04 * u, 20, 5, (0, 1, 0), 45)); f.grid(0, 30, 2); f.layer()
        for i, (nm, x) in enumerate([("Model S", -5.5), ("Model 3", 0), ("Model Y", 5.5)]):
            m = ease((u - i * 0.9) / 1.0)
            if m > 0:
                f.mesh(M_CARS[i], R=roty(0.4), T=(x, 0, lerp(-25, 0, m)))
                f.label((x, 2.2, lerp(-25, 0, m)), nm, 28, (255,255,255), 0, -50, a=m, dot=False)
        f.text(70, 60, "走进主流", 56, GOLD, a=ease(u / 0.5))
        f.dim = ease(u / 0.3) * (1 - ease((lt - e[5] + 0.3) / 0.3)); return f
    if lt < e[7]:
        u = lt - e[5]; n = int(40 * ease(u / 3.2))
        f = Fr(orbit(0.3 + 0.1 * u, 20, 5, (0, 3 + n * 0.12, 0), 45)); f.grid(0, 30, 2, (255,200,80,35)); f.layer()
        for i in range(n): f.mesh(M_COIN, R=roty(i * 0.7), T=(math.sin(i * 1.3) * 0.15, i * 0.27, math.cos(i * 1.1) * 0.15))
        f.label((0, n * 0.27 + 0.5, 0), "≈ 1 万亿美元 薪酬方案", 32, GOLD, 50, -40)
        f.text(70, 60, "2025.11", 72, GOLD, a=ease(u / 0.5)); f.text(74, 150, "特斯拉股东投票通过", 30, (230,235,245), a=ease(u / 0.5))
        f.dim = ease(u / 0.3) * (1 - ease((lt - e[7] + 0.3) / 0.3)); return f
    u = lt - e[7]
    ang = 0.9 + 0.06 * u; rad = lerp(58, 40, ease(u / 6)); hgt = lerp(34, 17, ease(u / 6))
    f = Fr(orbit(ang, rad, hgt, (0, 2, 0), 45)); f.stars = True; f.layer()
    f.mesh(M_GROUND)
    f.layer()
    for v in ROADS:   # 车道虚线
        for a0 in np.arange(-26, 26, 2.0):
            f.line([[a0, 0.07, v], [a0 + 0.9, 0.07, v]], (240,200,90,110), 1)
            f.line([[v, 0.07, a0], [v, 0.07, a0 + 0.9]], (240,200,90,110), 1)
    f.layer(); f.mesh(M_CITY); f.dots(LAMPS, 0.18, (255,210,140,200))
    n = min(45, int(45 * ease(u / 2.5)))
    for i in range(n):
        road = ROADS[i % 7]; d_ = 1 if (i // 7) % 2 else -1; spd = 0.9 + (i % 5) * 0.18
        s_ = ((i * 0.37 * 54 + d_ * u * spd * 3.0) % 54) - 27
        if i % 2: P = (s_, 0.0, road + 0.55 * d_); R = roty(0 if d_ > 0 else pi); hd = np.array([d_, 0, 0])
        else: P = (road - 0.55 * d_, 0.0, s_); R = roty(-pi / 2 if d_ > 0 else pi / 2); hd = np.array([0, 0, d_])
        f.mesh(M_CAB, R=R, T=P)
        p = np.array(P); side = np.cross(hd, [0, 1, 0]) * 0.28
        f.dots([p + hd * 0.85 + side + [0, 0.35, 0], p + hd * 0.85 - side + [0, 0.35, 0]], 0.09, (255,250,230,255))
        f.dots([p - hd * 0.85 + side + [0, 0.35, 0], p - hd * 0.85 - side + [0, 0.35, 0]], 0.07, (255,40,40,230))
        f.dots([p + [0, 0.95, 0]], 0.1, (90,220,255,255))
    f.label(CAPITOL_TOP, "得州议会大厦", 22, (255,220,180), 30, -30, a=ease((u - 1) / 0.6))
    f.label((0, 0.5, 30), "Lady Bird Lake", 20, (140,190,255), 30, -20, a=ease((u - 1.5) / 0.6))
    f.text(70, 60, "Cybercab", 60, (255,255,255), a=ease(u / 0.5)); f.text(74, 140, "奥斯汀 · 无方向盘 · 2026.09 开始载客", 28, (230,235,245), a=ease(u / 0.5))
    if lt > e[9] - 0.3: f.text(W - 70, 60, "%d 辆" % n, 96, GOLD, 'ra', a=ease((lt - e[9] + 0.3) / 0.5))
    else: f.text(W - 70, 60, "%d" % n, 60, (255,210,90), 'ra')
    f.dim = ease(u / 0.3); return f

NODES = {"SpaceX": ((0, -1, 5), (255,120,80), 1.6, 0), "Tesla": ((-7, 1, -2), (230,60,70), 1.3, 0), "Neuralink": ((6, 4, -3), (170,120,255), 1.0, 1),
         "Boring": ((-5, -4, 5), (200,170,110), 0.9, 2), "X": ((7, -3, 3), (240,240,240), 1.1, 4), "xAI": ((1, 6, -6), (90,200,255), 1.1, 5)}
def sc6(lt, d):
    e = [ev(5, i) for i in range(len(SUBS[5]))]
    mg = ease((lt - e[6] - 0.3) / 1.8)
    f = Fr(orbit(0.15 * lt, 23, 5, (0, 0.5, 0), 45)); f.layer()
    hub = np.zeros(3)
    f.mesh(M_NODE, T=hub, sc=0.7, col=(255,255,255), emis=0.3); f.label(hub, "马斯克", 26, (255,255,255), 0, 50, dot=False)
    for nm, (p, col, r, ci) in NODES.items():
        t0 = e[ci] if ci else 0
        if lt < t0: continue
        a = ease((lt - t0) / 0.6); p = np.array(p, float)
        if nm in ("X", "xAI"): p = lerp(p, np.array(NODES["SpaceX"][0], float), mg)
        rr = r * a * (1 + 0.5 * mg if nm == "SpaceX" else (1 - 0.8 * mg) if nm in ("X", "xAI") else 1)
        f.line([hub, p], (col[0], col[1], col[2], int(120 * a)), 3)
        f.mesh(M_NODE, T=p, sc=max(rr, 0.05), col=col, emis=0.15)
        if nm in ("X", "xAI") and mg > 0.9: continue
        lab = {"X": "X（原推特）· 440 亿美元 · 2022", "xAI": "xAI · Grok · 2023", "SpaceX": "SpaceX"}.get(nm, nm)
        if nm == "SpaceX" and mg > 0.5: lab = "SpaceX ＝ 火箭 + 卫星 + X + xAI"
        f.label(p + [0, rr, 0], lab, 26 if nm != "SpaceX" else 30, col, 30, -40, a=a)
    if lt > e[6]: f.text(70, 60, "2026.02", 72, GOLD, a=ease((lt - e[6]) / 0.5)); f.text(74, 150, "SpaceX 合并 xAI", 32, (230,235,245), a=ease((lt - e[6]) / 0.5))
    f.dim = ease(lt / 0.4); return f

EVENTS = [(1, "2024", "高调支持特朗普", (255,120,90)), (2, "2025", "领导“政府效率部” DOGE", (255,200,80)), (3, "2025", "离开，与特朗普公开决裂", (255,90,80)),
          (4, "之后", "重修旧好", (140,220,160)), (5, "2026.05", "诉 OpenAI 案被陪审团驳回", (120,180,255)), (6, "2026.09", "纪录片《Musk》威尼斯首映", (200,160,255)), (7, "他说：", "“抹黑”", (255,90,80))]
M_CARD = part([[-3,-1.6,0],[3,-1.6,0],[3,1.6,0],[-3,1.6,0]], [[0,1,2,3]], (30,36,50))
def sc7(lt, d):
    e = [ev(6, i) for i in range(len(SUBS[6]))]
    cur = 0.0
    for i in range(1, 8):
        cur += ease((lt - e[i] + 0.4) / 1.0)
    z_cam = 22 - cur * 12
    f = Fr(Cam([1.2 * math.sin(lt * 0.3), 2.5, z_cam], [0, 1.2, z_cam - 14], 50)); f.grid(-1.5, 90, 4, (255,110,90,30))
    f.layer()
    f.line([[0, -1.5, 12], [0, -1.5, -95]], (255,200,80,120), 3)
    for i, (ci, y, t, col) in enumerate(EVENTS):
        z = -i * 12 - 4; x = -3.4 if i % 2 else 3.4
        if z > z_cam - 5: continue
        f.mesh(M_CARD, R=roty(0.35 if i % 2 else -0.35), T=(x, 1.2, z), cull=False)
        f.line([[x, -0.4, z], [x, -1.5, z], [0, -1.5, z]], (*col, 160), 2)
        X, Y, Z = f.pt((x, 1.2, z))
        if 0.5 < Z < 60 and 230 < X < W - 230:
            sc = 1100 / Z
            a = clamp(1.4 - abs(Z - 14) / 12) if Z > 6 else 0
            f.text(X, Y - sc * 0.25, y, sc * 0.55, col, 'mm', a=a); f.text(X, Y + sc * 0.35, t, sc * (0.34 if len(t) < 10 else 0.27), (240,240,245), 'mm', a=a)
    f.text(70, 60, "争议", 72, RED, a=ease(lt / 0.5))
    f.dim = ease(lt / 0.4); return f

def sc8(lt, d):
    e = [ev(7, i) for i in range(8)]
    if lt < e[3]:
        h = 20 * ease(lt / 3.5)
        f = Fr(orbit(0.3 + 0.06 * lt, 40, 8, (0, 4 + h * 0.5, 0), 45)); f.grid(0, 40, 4, (255,200,80,35)); f.layer()
        f.mesh(M_BOX, R=np.diag([4, max(h, 0.01), 4]), T=(0, h / 2, 0), col=(255,140,90))
        f.mesh(M_SHIP, sc=0.25, T=(0, h, 0))
        f.label((0, h + 5, 0), "SpaceX IPO · 2026.06 · 史上最大", 28, (255,255,255), -40, -30)
        if lt > e[1]: f.text(70, 60, "≈ 2 万亿美元", 64, GOLD, a=ease((lt - e[1]) / 0.5)); f.text(74, 145, "SpaceX 市值", 28, (230,235,245), a=ease((lt - e[1]) / 0.5))
        if lt > e[2]:
            a = ease((lt - e[2]) / 0.6)
            f.text(W - 70, 60, "$1,000,000,000,000", 48, GOLD, 'ra', a=a); f.text(W - 70, 125, "史上首位万亿富翁（福布斯）", 28, (255,255,255), 'ra', a=a)
            f.layer(); u = lt - e[2]; pts, cols = [], []
            for i in range(160):
                h1 = (i * 97 % 101) / 101; h2 = (i * 57 % 89) / 89
                v = np.array([math.cos(h1 * 6.28) * 6 * h2, 10 + 8 * h1, math.sin(h1 * 6.28) * 6 * h2])
                p = np.array([0, h, 0]) + v * u - np.array([0, 9.8, 0]) * u * u / 2
                if p[1] > 0: pts.append(p); cols.append((255, 200, 70, 230))
            if pts: f.dots(pts, 0.25, cols)
        f.dim = ease(lt / 0.4) * (1 - ease((lt - e[3] + 0.3) / 0.3)); return f
    if lt < e[5]:
        u = lt - e[3]; f = Fr(orbit(0.5 * math.sin(u * 0.4), 14, 1, (0, 0, 0), 45)); f.layer()
        f.mesh(part([[-5,-2.8,0],[5,-2.8,0],[5,2.8,0],[-5,2.8,0]], [[0,1,2,3]], (28,34,50)), cull=False)
        X, Y, Z = f.pt((0, 0, 0)); a = ease(u / 0.6)
        f.text(X, Y - 60, "2026.09.29", 52, GOLD, 'mm', a=a); f.text(X, Y + 10, "白宫 · AI 协议签署", 40, (255,255,255), 'mm', a=a)
        f.text(X, Y + 70, "马斯克坐在特朗普身旁", 28, (200,205,220), 'mm', bold=False, a=ease((u - 0.8) / 0.6))
        f.dim = ease(u / 0.3) * (1 - ease((lt - e[5] + 0.3) / 0.3)); return f
    if lt < e[7]:
        u = lt - e[5]; flip = ease((lt - e[6] + 0.3) / 1.0) * pi
        f = Fr(Cam([0, 1, 16], [0, 0, 0], 45)); f.layer()
        R = roty(flip + 0.25 * math.sin(u * 1.5))
        f.mesh(disc(4.5, 0.6, (230,180,60)), R=R @ rotx(pi / 2), T=R @ [0, 0, -0.3], sc=1)
        side = flip < pi / 2
        a = clamp(abs(math.cos(flip)) * 1.6)
        if side: f.text(W / 2, H / 2 - 20, "这个时代最伟大的", 34, (60,40,10), 'mm', a=a); f.text(W / 2, H / 2 + 30, "工程企业家", 46, (60,40,10), 'mm', a=a)
        else: f.text(W / 2, H / 2 - 20, "权力过大", 46, (90,20,10), 'mm', a=a); f.text(W / 2, H / 2 + 35, "言行失控", 46, (90,20,10), 'mm', a=a)
        f.dim = ease(u / 0.3) * (1 - ease((lt - e[7] + 0.3) / 0.3)); return f
    u = lt - e[7]; m = ease(u / 3.2)
    f = Fr(orbit(-0.2 + 0.03 * u, 40, 6, (0, 0, 0), 45))
    Rm = draw_globe(f, (-14, 0, 0), 3, u * 0.4, m=M_EARTH_S, gridcol=(90,170,255,60))
    f.layer(); draw_globe(f, (12, 0, 0), 6, u * 0.2, m=M_MARS, gridcol=(255,160,120,60)); f.layer()
    path = [np.array([lerp(-11, 6, s), 5 * math.sin(pi * s), 0]) for s in np.linspace(0, 1, 60)]
    k = int(m * 59); f.line(path[:k + 1], (255,200,80,200), 3)
    f.mesh(M_SHIP, sc=0.12, R=rotz(-pi / 2 + (0.6 - 1.2 * m)), T=path[k])
    f.label((12, 6, 0), "火星", 28, (255,170,130), 30, -40); f.label((-14, 3, 0), "地球", 28, (140,200,255), -60, -40)
    a = ease((u - 1.2) / 1.0)
    f.text(W / 2, 120, "ELON MUSK", 80, (255,255,255), 'mm', a=a); f.text(W / 2, 190, "1971 —", 30, GOLD, 'mm', a=a)
    f.text(W - 30, H - 120, "信息截至 2026.09.30", 20, (170,180,200), 'rs', bold=False, a=a)
    f.dim = ease(u / 0.3); return f

SCENES = [sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8]
CH = ["序章", "少年", "第一桶金", "SpaceX", "特斯拉", "版图", "争议", "现在"]

FILM = Film(SEG, dur, SCENES, SUBS, CH, total=TOTAL)
