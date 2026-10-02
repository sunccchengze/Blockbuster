"""陀飞轮机芯 · 10 秒展示片（Blender 4.2 Cycles，纯代码程序化建模，无外部模型/贴图）
运行：blender -b -P scene.py -- [render|still FRAME|save]
单位：1 = 1 cm；机芯直径约 3.2 cm。
"""
import bpy, bmesh, math, sys, os
from mathutils import Vector, Euler, Matrix
pi = math.pi
ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '.cache')
FPS, NF = 25, 250

# ---------------------------------------------------------------- 场景
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.render.engine = 'CYCLES'; S.cycles.device = 'CPU'
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = 1280, 720, int(os.environ.get('PCT', 100))
S.render.fps = FPS; S.frame_start, S.frame_end = 1, NF
S.cycles.samples = int(os.environ.get('SAMPLES', 40)); S.cycles.adaptive_threshold = 0.03
S.cycles.use_denoising = True; S.cycles.denoiser = 'OPENIMAGEDENOISE'
S.cycles.max_bounces = 5; S.cycles.glossy_bounces = 3; S.cycles.transmission_bounces = 4; S.cycles.diffuse_bounces = 1; S.cycles.transparent_max_bounces = 4
S.render.use_persistent_data = True; S.cycles.use_light_tree = True
S.cycles.caustics_reflective = False; S.cycles.caustics_refractive = False
S.cycles.blur_glossy = 0.6; S.cycles.sample_clamp_indirect = 6
S.render.use_motion_blur = True; S.render.motion_blur_shutter = 0.45
S.view_settings.view_transform = 'AgX'; S.view_settings.look = 'AgX - Medium High Contrast'
S.render.image_settings.file_format = 'PNG'; S.render.image_settings.color_depth = '8'
S.render.film_transparent = False
S.cycles.use_auto_tile = True; S.cycles.tile_size = 2048
S.render.threads_mode = 'AUTO'

# ---------------------------------------------------------------- 材质
def mat(name, col, metal=1.0, rough=0.2, aniso=0.0, trans=0.0, ior=1.5, emit=None, coat=0.0, noise_rough=0.0, bands=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough; b.inputs['IOR'].default_value = ior
    b.inputs['Anisotropic'].default_value = aniso
    b.inputs['Transmission Weight'].default_value = trans
    b.inputs['Coat Weight'].default_value = coat
    if emit:
        b.inputs['Emission Color'].default_value = (*emit[0], 1); b.inputs['Emission Strength'].default_value = emit[1]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    if aniso > 0:   # 径向拉丝：切线绕物体 Z 轴
        tg = nt.nodes.new('ShaderNodeTangent'); tg.direction_type = 'RADIAL'; tg.axis = 'Z'
        nt.links.new(tg.outputs[0], b.inputs['Tangent'])
    if noise_rough:
        nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 900; nz.inputs['Detail'].default_value = 4
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs[3].default_value = rough * (1 - noise_rough); mr.inputs[4].default_value = rough * (1 + noise_rough)
        nt.links.new(tc.outputs['Object'], nz.inputs['Vector']); nt.links.new(nz.outputs[0], mr.inputs[0]); nt.links.new(mr.outputs[0], b.inputs['Roughness'])
    if bands:      # 日内瓦波纹（Côtes de Genève）：沿 X 的平行弧形条纹 → 粗糙度 + 凹凸
        wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'; wv.wave_profile = 'SAW'
        wv.inputs['Scale'].default_value = bands; wv.inputs['Distortion'].default_value = 0.0
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value[2] = 0.35
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs[0], wv.inputs['Vector'])
        bm_ = nt.nodes.new('ShaderNodeBump'); bm_.inputs['Strength'].default_value = 0.25; bm_.inputs['Distance'].default_value = 0.002
        nt.links.new(wv.outputs['Fac'], bm_.inputs['Height']); nt.links.new(bm_.outputs[0], b.inputs['Normal'])
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs[3].default_value = 0.12; mr.inputs[4].default_value = 0.32
        nt.links.new(wv.outputs['Fac'], mr.inputs[0]); nt.links.new(mr.outputs[0], b.inputs['Roughness'])
        tg = nt.nodes.new('ShaderNodeTangent'); tg.direction_type = 'UV_MAP' if False else 'RADIAL'; tg.axis = 'Y'
        b.inputs['Anisotropic'].default_value = 0.5; nt.links.new(tg.outputs[0], b.inputs['Tangent'])
    return m

GOLD = mat('gold', (1.0, 0.74, 0.42), rough=0.2, aniso=0.55, noise_rough=0.3)
ROSE = mat('rose', (0.98, 0.6, 0.48), rough=0.16, aniso=0.4, noise_rough=0.25)
STEEL = mat('steel', (0.92, 0.92, 0.94), rough=0.06)
SATIN = mat('satin', (0.82, 0.83, 0.86), rough=0.28, aniso=0.6)
BLUE = mat('blued', (0.04, 0.12, 0.62), rough=0.12, coat=0.4)
RUBY = mat('ruby', (0.95, 0.04, 0.12), metal=0.0, rough=0.02, trans=1.0, ior=1.77)
PLATE = mat('plate', (0.34, 0.35, 0.38), rough=0.2, bands=9.0)
DARK = mat('dark', (0.02, 0.02, 0.025), metal=0.0, rough=0.5)
GLOW = mat('glowring', (0.2, 0.5, 1.0), metal=0.0, rough=0.4, emit=((0.3, 0.6, 1.0), 6.0))

# ---------------------------------------------------------------- 几何工具
def new_obj(name, me, m=None, parent=None):
    o = bpy.data.objects.new(name, me); S.collection.objects.link(o)
    if m: o.data.materials.append(m)
    if parent: o.parent = parent
    return o

def finish(o, bevel=0.004, smooth=True, seg=2):
    if bevel:
        md = o.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = seg; md.limit_method = 'ANGLE'; md.angle_limit = math.radians(35)
        md.harden_normals = False
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
        md = o.modifiers.new('ws', 'WEIGHTED_NORMAL'); md.keep_sharp = True
        o.data.set_sharp_from_angle(angle=math.radians(40))
    return o

def prism(name, outer, inner, z0, z1, m, parent=None, bevel=0.004):
    """outer/inner：等点数闭合多边形（XY）。inner=None 时为实心（扇形三角化）。"""
    bm = bmesh.new(); n = len(outer)
    def ring(pts, z): return [bm.verts.new((x, y, z)) for x, y in pts]
    ob, ot = ring(outer, z0), ring(outer, z1)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
    if inner is None:
        bm.faces.new(ot); bm.faces.new(list(reversed(ob)))
    else:
        ib, it = ring(inner, z0), ring(inner, z1)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((ib[j], ib[i], it[i], it[j]))
            bm.faces.new((ot[i], ot[j], it[j], it[i])); bm.faces.new((ob[j], ob[i], ib[i], ib[j]))
    me = bpy.data.meshes.new(name); bm.normal_update(); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = new_obj(name, me, m, parent); finish(o, bevel); return o

def circle(r, n, a0=0.0): return [(r * math.cos(a0 + 2 * pi * i / n), r * math.sin(a0 + 2 * pi * i / n)) for i in range(n)]

TOOTH = [(0.0, 'f'), (0.18, 'f'), (0.26, 'p-'), (0.31, 'p+'), (0.38, 'a'), (0.5, 'a'), (0.62, 'a'), (0.69, 'p+'), (0.74, 'p-'), (0.82, 'f')]
def gear_outline(r, n):
    m = 2 * r / n; R = {'f': r - 1.25 * m, 'p-': r - 0.35 * m, 'p+': r + 0.55 * m, 'a': r + m * 0.95}
    pts = []
    for i in range(n):
        for fr, k in TOOTH:
            a = 2 * pi * (i + fr) / n; pts.append((R[k] * math.cos(a), R[k] * math.sin(a)))
    return pts, r - 1.25 * m

def gear(name, r, n, z, th, m=GOLD, spokes=5, parent=None, hub=None, pinion=None):
    """带齿轮缘 + 辐条 + 轮毂；pinion=(齿数, 半径, 高度) 为同轴小齿轮。返回空物体（旋转它即可）。"""
    root = bpy.data.objects.new(name, None); S.collection.objects.link(root); root.empty_display_size = r
    if parent: root.parent = parent
    out, rf = gear_outline(r, n)
    if spokes:
        rin = rf - max(0.035, 0.1 * r)
        inn = [(rin * math.cos(math.atan2(y, x)), rin * math.sin(math.atan2(y, x))) for x, y in out]
        prism(name + '_rim', out, inn, z, z + th, m, root)
        hr = hub or max(0.05, 0.18 * r)
        prism(name + '_hub', circle(hr, 40), circle(0.018, 40), z - 0.004, z + th + 0.004, m, root)
        for k in range(spokes):
            a = 2 * pi * k / spokes + 0.3; ca, sa = math.cos(a), math.sin(a)
            w0, w1 = 0.11 * r + 0.012, 0.06 * r + 0.008     # 渐细辐条，向外弯
            pts = []
            for t, side in ((0, -1), (1, -1), (1, 1), (0, 1)):
                rr = lerp(hr * 0.8, rin + 0.01, t); ww = lerp(w0, w1, t) * side; bend = 0.12 * r * math.sin(pi * t) * 0
                pts.append((rr * ca - ww * sa, rr * sa + ww * ca))
            prism(name + f'_sp{k}', pts, None, z + th * 0.12, z + th * 0.88, m, root, bevel=0.003)
    else:
        prism(name + '_body', out, circle(0.018, len(out)), z, z + th, m, root)
    if pinion:
        pn, pr, ph = pinion
        po, _ = gear_outline(pr, pn)
        prism(name + '_pin', po, circle(0.012, len(po)), z - ph, z + th + 0.01, STEEL, root, bevel=0.002)
    return root

def lerp(a, b, t): return a + (b - a) * t

def cyl(name, r, z0, z1, m, x=0, y=0, n=48, parent=None, hole=0.0, bevel=0.003):
    o = prism(name, circle(r, n), circle(hole, n) if hole else None, z0, z1, m, parent, bevel)
    o.location = (x, y, 0); return o

def jewel(name, x, y, z, r=0.055, parent=None):
    """红宝石轴承：镜面金套 + 带油池凹面的红宝石 + 钢轴尖。"""
    cyl(name + '_chaton', r * 1.45, z - 0.012, z + 0.018, GOLD, x, y, parent=parent, hole=r * 1.02)
    bm = bmesh.new()
    prof = [(0.0, z + 0.012), (r * 0.25, z + 0.01), (r * 0.55, z + 0.03), (r * 0.9, z + 0.034), (r, z + 0.02), (r, z - 0.01), (0.0, z - 0.01)]
    me = bpy.data.meshes.new(name)
    verts = []
    N = 48
    for (rr, zz) in prof:
        verts.append([bm.verts.new((x + rr * math.cos(2 * pi * j / N), y + rr * math.sin(2 * pi * j / N), zz)) for j in range(N)])
    for i in range(len(prof) - 1):
        for j in range(N):
            k = (j + 1) % N
            bm.faces.new((verts[i][j], verts[i + 1][j], verts[i + 1][k], verts[i][k]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free(); o = new_obj(name, me, RUBY, parent)
    for p in o.data.polygons: p.use_smooth = True
    cyl(name + '_pivot', 0.012, z + 0.0, z + 0.03, STEEL, x, y, n=16, parent=parent, bevel=0)

def screw(name, x, y, z, r=0.045, parent=None, rot=0.0):
    """烧蓝螺丝：圆顶螺帽 + 一字槽（两半圆顶，中间留槽）。"""
    root = bpy.data.objects.new(name, None); S.collection.objects.link(root); root.location = (x, y, z); root.rotation_euler[2] = rot
    if parent: root.parent = parent
    slot = r * 0.18
    for side in (-1, 1):
        bm = bmesh.new(); N = 20; pts = []
        for i in range(N + 1):
            a = -pi / 2 + pi * i / N
            pts.append((r * math.cos(a) * side if False else r * math.cos(a), r * math.sin(a)))
        # 半圆盘（x>slot/2 部分）以曲面圆顶表示：分层
        rows = []
        for h in range(5):
            s = math.cos(h / 4 * pi / 2 * 0.85); zz = 0.03 * math.sin(h / 4 * pi / 2 * 0.85) + 0.012
            row = []
            for i in range(N + 1):
                a = -pi / 2 + pi * i / N; px = max(r * s * math.cos(a), slot / 2); py = r * s * math.sin(a)
                row.append(bm.verts.new((side * px, py, zz)))
            rows.append(row)
        base = [bm.verts.new((side * max(r * math.cos(-pi / 2 + pi * i / N), slot / 2), r * math.sin(-pi / 2 + pi * i / N), -0.004)) for i in range(N + 1)]
        allr = [base] + rows
        for k in range(len(allr) - 1):
            for i in range(N):
                f = (allr[k][i], allr[k][i + 1], allr[k + 1][i + 1], allr[k + 1][i])
                bm.faces.new(f if side > 0 else tuple(reversed(f)))
        bm.faces.new(allr[-1] if side > 0 else list(reversed(allr[-1])))
        side_face = [r[0] for r in allr] + [r[-1] for r in reversed(allr)]
        try: bm.faces.new(side_face)
        except Exception: pass
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(name + str(side)); bm.to_mesh(me); bm.free()
        o = new_obj(name + str(side), me, BLUE, root)
        for p in o.data.polygons: p.use_smooth = True
    return root

def bridge(name, pts_path, w, z, th, m, parent=None, ends=True):
    """沿折线生成两端圆头的桥板（宽度 w），外轮廓用偏移多边形。"""
    P = [Vector((x, y)) for x, y in pts_path]; L, R = [], []
    for i, p in enumerate(P):
        d = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized(); nrm = Vector((-d.y, d.x))
        L.append(p + nrm * w / 2); R.append(p - nrm * w / 2)
    def cap(c, d0, sgn):
        nrm = Vector((-d0.y, d0.x)); out = []
        for k in range(1, 12):
            a = pi * k / 12; out.append(c + (nrm * math.cos(a) * sgn + d0 * math.sin(a) * sgn) * w / 2 * (1 if sgn > 0 else 1))
        return out
    d_end = (P[-1] - P[-2]).normalized(); d_st = (P[0] - P[1]).normalized()
    ring_ = L + [P[-1] + (Vector((-d_end.y, d_end.x)) * math.cos(pi * k / 12) + d_end * math.sin(pi * k / 12)) * w / 2 for k in range(1, 12)] \
        + list(reversed(R)) + [P[0] + (Vector((-d_st.y, d_st.x)) * math.cos(pi * k / 12) + d_st * math.sin(pi * k / 12)) * w / 2 for k in range(1, 12)]
    o = prism(name, [(v.x, v.y) for v in ring_], None, z, z + th, m, parent, bevel=0.006)
    return o

# ---------------------------------------------------------------- 机芯
ROOT = bpy.data.objects.new('movement', None); S.collection.objects.link(ROOT)
# 主夹板（日内瓦波纹 + 外圈倒角），中间开陀飞轮窗
TB = Vector((0.0, -0.62))       # 陀飞轮中心
plate_out = circle(1.62, 160); plate_in = [(TB.x + 0.62 * math.cos(2 * pi * i / 160), TB.y + 0.62 * math.sin(2 * pi * i / 160)) for i in range(160)]
# 主夹板拆为外环 + 带窗口的主体：用外圈多边形和窗口多边形桥接（点数一致，窗口偏心）
prism('plate', plate_out, plate_in, -0.16, 0.0, PLATE, ROOT, bevel=0.01)
prism('plate_rim', circle(1.72, 160), circle(1.62, 160), -0.2, 0.03, STEEL, ROOT, bevel=0.012)
prism('case_ring', circle(1.95, 200), circle(1.72, 200), -0.35, 0.12, STEEL, ROOT, bevel=0.03)
# 表壳刻度环（60 格，带蓝色发光小点作为夜光）
for i in range(60):
    a = 2 * pi * i / 60; big = i % 5 == 0
    o = prism(f'tick{i}', [(-0.012 if not big else -0.02, -0.06 if big else -0.035), (0.012 if not big else 0.02, -0.06 if big else -0.035),
                           (0.012 if not big else 0.02, 0.06 if big else 0.035), (-0.012 if not big else -0.02, 0.06 if big else 0.035)], None,
              0.12, 0.135, ROSE if big else SATIN, ROOT, bevel=0.002)
    r = 1.835; o.location = (r * math.cos(a), r * math.sin(a), 0); o.rotation_euler[2] = a + pi / 2
    if big:
        g = cyl(f'lume{i}', 0.012, 0.135, 0.142, GLOW, 1.89 * math.cos(a), 1.89 * math.sin(a), n=12, parent=ROOT, bevel=0)
# 陀飞轮窗口内的下沉底面（深色，衬托框架）
cyl('tb_floor', 0.62, -0.2, -0.16, DARK, TB.x, TB.y, n=96, parent=ROOT, bevel=0)

# ----- 传动轮系（齿数比真实啮合：中心距 = r1 + r2）
TRAIN = []   # (empty, 角速度 rad/帧)
def place(o, x, y): o.location = (x, y, 0); return o
w_barrel = 0.004
barrel = place(gear('barrel', 0.62, 96, 0.05, 0.06, GOLD, 6, ROOT, hub=0.16), -0.72, 0.62)
TRAIN.append((barrel, w_barrel))
# 发条盒盖（磨砂 + 太阳纹）与刻字
cyl('barrel_cover', 0.42, 0.11, 0.13, SATIN, -0.72, 0.62, n=96, parent=barrel, bevel=0.004).location = (0, 0, 0)
r1, n1 = 0.62, 96; rp2, np2 = 0.095, 12; r2, n2 = 0.48, 80
c2 = Vector((-0.72, 0.62)) + Vector((math.cos(-0.25), math.sin(-0.25))) * (r1 + rp2)
center = place(gear('center', r2, n2, 0.13, 0.05, GOLD, 5, ROOT, pinion=(np2, rp2, 0.1)), c2.x, c2.y)
w2 = -w_barrel * n1 / np2; TRAIN.append((center, w2))
rp3, np3 = 0.08, 10; r3, n3 = 0.36, 72
c3 = c2 + Vector((math.cos(-1.45), math.sin(-1.45))) * (r2 + rp3)
third = place(gear('third', r3, n3, 0.06, 0.045, ROSE, 5, ROOT, pinion=(np3, rp3, 0.09)), c3.x, c3.y)
w3 = -w2 * n2 / np3; TRAIN.append((third, w3))
# 第三轮驱动陀飞轮框架下方的四轮（框架同轴）—— 框架转速
rp4, np4 = 0.07, 10
d34 = (c3 - TB).length
# ----- 陀飞轮框架（整体旋转）
CAGE = bpy.data.objects.new('cage', None); S.collection.objects.link(CAGE); CAGE.parent = ROOT; CAGE.location = (TB.x, TB.y, 0)
w_cage = 2 * pi / 30 / FPS * 1.0   # 展示用：约 30 秒一圈
# 框架：上下两层三叉桥（抛光钢）+ 三根立柱
for zl, nm in ((-0.12, 'lo'), (0.36, 'hi')):
    prism(f'cage_ring_{nm}', circle(0.54, 120), circle(0.49, 120), zl, zl + 0.025, STEEL, CAGE, bevel=0.004)
    for k in range(3):
        a = 2 * pi * k / 3 + pi / 2
        pts = [(0.06 * math.cos(a + 1.2), 0.06 * math.sin(a + 1.2)), (0.5 * math.cos(a + 0.12), 0.5 * math.sin(a + 0.12)),
               (0.5 * math.cos(a - 0.12), 0.5 * math.sin(a - 0.12)), (0.06 * math.cos(a - 1.2), 0.06 * math.sin(a - 1.2))]
        prism(f'cage_arm_{nm}{k}', pts, None, zl, zl + 0.025, STEEL, CAGE, bevel=0.003)
    prism(f'cage_hub_{nm}', circle(0.08, 48), circle(0.02, 48), zl - 0.005, zl + 0.03, STEEL, CAGE, bevel=0.003)
for k in range(3):
    a = 2 * pi * k / 3 + pi / 2
    cyl(f'pillar{k}', 0.022, -0.1, 0.36, STEEL, 0.515 * math.cos(a), 0.515 * math.sin(a), n=24, parent=CAGE)
    screw(f'cscrew{k}', 0.515 * math.cos(a), 0.515 * math.sin(a), 0.385, 0.03, CAGE, rot=k)
# 陀飞轮固定四轮（大环形齿圈，固定在夹板上）—— 擒纵小齿轮绕它滚动
prism('fixed_wheel', gear_outline(0.6, 120)[0], circle(0.56, 1200), -0.16, -0.13, ROSE, ROOT, bevel=0.002).location = (TB.x, TB.y, 0)
# 摆轮（双臂 + 8 颗金调校螺丝）
BAL = bpy.data.objects.new('balance', None); S.collection.objects.link(BAL); BAL.parent = CAGE; BAL.location = (0, 0, 0)
prism('bal_rim', circle(0.33, 128), circle(0.295, 128), 0.17, 0.205, GOLD, BAL, bevel=0.004)
for k in range(2):
    a = pi * k
    pts = [(0.02 * math.cos(a + pi / 2), 0.02 * math.sin(a + pi / 2)), (0.3 * math.cos(a) + 0.018 * math.cos(a + pi / 2), 0.3 * math.sin(a) + 0.018 * math.sin(a + pi / 2)),
           (0.3 * math.cos(a) - 0.018 * math.cos(a + pi / 2), 0.3 * math.sin(a) - 0.018 * math.sin(a + pi / 2)), (0.02 * math.cos(a - pi / 2), 0.02 * math.sin(a - pi / 2))]
    prism(f'bal_arm{k}', pts, None, 0.175, 0.2, GOLD, BAL, bevel=0.002)
for k in range(8):
    a = 2 * pi * k / 8 + pi / 8
    o = cyl(f'bal_screw{k}', 0.018, -0.02, 0.02, GOLD, 0, 0, n=20, parent=BAL)
    o.rotation_euler = (0, pi / 2, a); o.location = (0.35 * math.cos(a), 0.35 * math.sin(a), 0.1875)
    o.rotation_euler = Euler((0, pi / 2, 0)).to_matrix().to_euler(); o.matrix_basis = Matrix.Translation((0.35 * math.cos(a), 0.35 * math.sin(a), 0.1875)) @ Matrix.Rotation(a, 4, 'Z') @ Matrix.Rotation(pi / 2, 4, 'Y')
cyl('bal_staff', 0.012, -0.12, 0.38, STEEL, 0, 0, n=16, parent=BAL, bevel=0)
cyl('bal_roller', 0.05, 0.12, 0.14, STEEL, 0, 0, n=40, parent=BAL)
# 游丝：阿基米德螺线（14 圈），带圆形截面
cu = bpy.data.curves.new('hairspring', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.0028; cu.bevel_resolution = 2
sp = cu.splines.new('POLY'); NS = 1400; sp.points.add(NS - 1)
for i in range(NS):
    t = i / (NS - 1); a = t * 2 * pi * 14; r = 0.05 + 0.2 * t
    sp.points[i].co = (r * math.cos(a), r * math.sin(a), 0.235, 1)
HS = new_obj('hairspring', cu, STEEL, BAL)
# 擒纵轮（15 齿钩形齿）+ 擒纵叉
ESC_C = Vector((0.0, -0.36))
ESC = bpy.data.objects.new('escape', None); S.collection.objects.link(ESC); ESC.parent = CAGE; ESC.location = (ESC_C.x, ESC_C.y, 0)
pts = []
for i in range(15):
    a = 2 * pi * i / 15
    for fr, rr in ((0.0, 0.07), (0.55, 0.075), (0.62, 0.115), (0.68, 0.11), (0.95, 0.072)):
        b = a + 2 * pi / 15 * fr; pts.append((rr * math.cos(b), rr * math.sin(b)))
prism('esc_wheel', pts, circle(0.055, len(pts)), 0.02, 0.04, STEEL, ESC, bevel=0.002)
prism('esc_hub', circle(0.02, 32), circle(0.008, 32), 0.015, 0.045, STEEL, ESC, bevel=0.002)
po, _ = gear_outline(0.045, 9); prism('esc_pinion', po, circle(0.008, len(po)), -0.13, 0.015, STEEL, ESC, bevel=0.0015)
FORK = bpy.data.objects.new('fork', None); S.collection.objects.link(FORK); FORK.parent = CAGE; FORK.location = (0, -0.2, 0)
prism('fork_body', [(-0.012, -0.06), (0.012, -0.06), (0.01, 0.15), (-0.01, 0.15)], None, 0.08, 0.1, STEEL, FORK, bevel=0.002)
prism('fork_arms', [(-0.07, -0.1), (0.07, -0.1), (0.075, -0.085), (0.0, -0.05), (-0.075, -0.085)], None, 0.06, 0.08, STEEL, FORK, bevel=0.002)
for sx in (-1, 1):
    o = prism(f'pallet{sx}', [(-0.008, -0.02), (0.008, -0.02), (0.008, 0.02), (-0.008, 0.02)], None, 0.055, 0.085, RUBY, FORK, bevel=0.001)
    o.location = (sx * 0.07, -0.11, 0)
# 陀飞轮上桥上的红宝石
jewel('tb_jewel', 0, 0, 0.39, 0.045, parent=CAGE)

# ----- 桥板（玫瑰金，弧形）+ 宝石 + 烧蓝螺丝
bridge('barrel_bridge', [(-1.35, 0.95), (-0.72, 0.62), (-0.2, 1.15)], 0.3, 0.2, 0.07, ROSE, ROOT)
jewel('j_barrel', -0.72, 0.62, 0.275, 0.07, ROOT)
bridge('train_bridge', [(-0.95, -0.2), (c3.x, c3.y), (c2.x, c2.y), (0.95, 0.9)], 0.22, 0.24, 0.06, ROSE, ROOT)
jewel('j_center', c2.x, c2.y, 0.305, 0.055, ROOT); jewel('j_third', c3.x, c3.y, 0.305, 0.05, ROOT)
for i, (x, y) in enumerate([(-1.3, 0.95), (-0.25, 1.12), (-0.92, -0.2), (0.92, 0.88)]):
    screw(f'scr{i}', x, y, 0.27 if i < 2 else 0.30, 0.055, ROOT, rot=i * 0.7)
# 飞行陀飞轮：上方无桥，框架只由下方支撑
# 刻字（在发条盒盖上，凹刻）
tx = bpy.data.curves.new('engr', 'FONT'); tx.body = 'TOURBILLON  ·  CODE-BUILT'; tx.size = 0.06; tx.extrude = 0.002; tx.align_x = 'CENTER'
to = new_obj('engr', tx, GOLD, barrel); to.location = (0, -0.24, 0.132)
tx2 = bpy.data.curves.new('engr2', 'FONT'); tx2.body = '27 JEWELS'; tx2.size = 0.05; tx2.extrude = 0.002; tx2.align_x = 'CENTER'
to2 = new_obj('engr2', tx2, GOLD, ROOT); to2.location = (0.75, -0.2, 0.002)

# ---------------------------------------------------------------- 动画
def linear_spin(o, w):
    o.rotation_euler[2] = 0; o.keyframe_insert('rotation_euler', index=2, frame=1)
    o.rotation_euler[2] = w * (NF + 30); o.keyframe_insert('rotation_euler', index=2, frame=NF + 31)
    for fc in o.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
for o, w in TRAIN: linear_spin(o, w)
linear_spin(CAGE, w_cage)
# 擒纵小齿轮绕固定轮滚动：相对框架转速 = w_cage * 120/9
BEAT = 2.0                               # 展示用摆频 2 Hz（每秒 4 拍）
for f in range(1, NF + 31):
    t = (f - 1) / FPS
    ang = 2.6 * math.sin(2 * pi * BEAT * t)           # 摆轮振幅 ±150°
    BAL.rotation_euler[2] = ang; BAL.keyframe_insert('rotation_euler', index=2, frame=f)
    HS.rotation_euler[2] = -0.12 * ang; HS.scale = (1 + 0.015 * math.sin(2 * pi * BEAT * t),) * 3
    HS.keyframe_insert('rotation_euler', index=2, frame=f); HS.keyframe_insert('scale', frame=f)
    beats = 2 * BEAT * t; k = math.floor(beats); fr_ = beats - k
    step = k + min(1.0, fr_ / 0.18)                    # 擒纵轮“跳拍”：快速前进后停住
    ESC.rotation_euler[2] = -step * 2 * pi / 30; ESC.keyframe_insert('rotation_euler', index=2, frame=f)
    side = 1 if k % 2 == 0 else -1
    FORK.rotation_euler[2] = side * 0.14 * min(1.0, fr_ / 0.12) + (-side) * 0.14 * max(0.0, 1 - fr_ / 0.12)
    FORK.keyframe_insert('rotation_euler', index=2, frame=f)

# ---------------------------------------------------------------- 灯光与世界
W = bpy.data.worlds.new('w'); S.world = W; W.use_nodes = True; wn = W.node_tree
env = wn.nodes.new('ShaderNodeTexEnvironment')
exr = os.path.join(os.path.dirname(bpy.app.binary_path), '4.2', 'datafiles', 'studiolights', 'world', 'interior.exr')
env.image = bpy.data.images.load(exr)
bg = wn.nodes['Background']; bg.inputs['Strength'].default_value = 0.12
lp = wn.nodes.new('ShaderNodeLightPath'); mix = wn.nodes.new('ShaderNodeMixShader'); dark = wn.nodes.new('ShaderNodeBackground')
dark.inputs['Color'].default_value = (0.004, 0.005, 0.009, 1)
wn.links.new(env.outputs[0], bg.inputs['Color'])
wn.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); wn.links.new(bg.outputs[0], mix.inputs[1]); wn.links.new(dark.outputs[0], mix.inputs[2])
wn.links.new(mix.outputs[0], wn.nodes['World Output'].inputs[0])
def area(name, loc, rot, size, energy, col, shape='RECTANGLE', sy=None):
    L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.color = col; L.shape = shape; L.size = size; L.size_y = sy or size
    o = bpy.data.objects.new(name, L); S.collection.objects.link(o); o.location = loc; o.rotation_euler = rot; return o
area('key', (-3, 2.5, 5), (math.radians(-30), math.radians(-30), 0), 3.5, 220, (1.0, 0.93, 0.85))
area('rim', (4, -3, 1.6), (math.radians(70), 0, math.radians(55)), 0.6, 450, (0.6, 0.75, 1.0), sy=5)
area('strip', (0, 4, 2.0), (math.radians(-65), 0, 0), 0.25, 300, (1.0, 0.85, 0.7), sy=6)
area('top', (0, 0, 6), (0, 0, 0), 1.2, 60, (1, 1, 1))
# 极淡的体积雾（仅用于远景光柱感）——关闭以控制渲染时间

# ---------------------------------------------------------------- 摄影机：连续一镜到底，路径关键帧 + 焦点关键帧
CAM = bpy.data.cameras.new('cam'); CO = bpy.data.objects.new('cam', CAM); S.collection.objects.link(CO); S.camera = CO
CAM.lens = 50; CAM.sensor_width = 36; CAM.clip_start = 0.005; CAM.clip_end = 100
CAM.dof.use_dof = True; CAM.dof.aperture_blades = 7; CAM.dof.aperture_rotation = 0.3
TGT = bpy.data.objects.new('tgt', None); S.collection.objects.link(TGT)
FOC = bpy.data.objects.new('foc', None); S.collection.objects.link(FOC); CAM.dof.focus_object = FOC
tc_ = CO.constraints.new('TRACK_TO'); tc_.target = TGT; tc_.track_axis = 'TRACK_NEGATIVE_Z'; tc_.up_axis = 'UP_Y'
tbw = lambda x, y, z: Vector((TB.x + x, TB.y + y, z))
# (帧, 机位, 注视点, 焦点, 光圈 f, 焦距 mm, 滚转)
W_ = lambda x, y, z: Vector((x, y, z))
C2 = Vector((c2.x, c2.y, 0.15)); C3 = Vector((c3.x, c3.y, 0.1))
SHOTS = [
    (1,   W_(0.42, -1.58, 0.13), W_(0.0, -0.98, 0.03), W_(0.03, -1.04, 0.04), 1.4, 100, 0.0),    # 微距：擒纵轮齿尖
    (34,  W_(-0.38, -1.55, 0.2), W_(0.03, -0.93, 0.07), W_(0.07, -0.93, 0.07), 1.4, 100, 0.08),  # 横移到擒纵叉红宝石
    (48,  W_(0.62, -1.62, 0.42), W_(0.0, -0.75, 0.15), W_(0.3, -1.1, 0.2), 2.8, 85, 0.0),
    (62,  W_(0.35, -1.35, 0.78), W_(0.0, -0.62, 0.2), W_(0.0, -0.72, 0.22), 2.0, 70, -0.15),     # 抬升，焦点拉到摆轮/游丝
    (92,  W_(-0.85, -0.25, 0.72), W_(0.0, -0.62, 0.2), W_(0.0, -0.62, 0.24), 2.2, 55, 0.45),     # 绕飞行陀飞轮环绕（荷兰角）
    (124, W_(1.05, 0.05, 1.35), C3, C3, 3.2, 40, 0.15),                                      # 高空弧线甩到轮系
    (152, W_(1.45, 1.45, 0.3), C2, C2 + W_(0.25, 0.3, 0.0), 1.8, 45, -0.1),                     # 从表壳外贴面低掠
    (182, W_(-0.25, 0.25, 1.05), W_(-0.72, 0.62, 0.2), W_(-0.72, 0.62, 0.28), 2.8, 45, -0.25),  # 升起俯瞰发条盒 + 刻字
    (215, W_(1.3, -3.0, 3.0), W_(0, -0.1, 0), W_(0.0, -0.4, 0.2), 5.0, 50, 0.0),               # 拉远：完整机芯
    (250, W_(0.6, -4.3, 5.3), W_(0, 0.0, 0), W_(0.0, -0.3, 0.15), 6.0, 50, 0.0),
]
for fr, p, t, fo, fs, lens, roll in SHOTS:
    CO.location = p; CO.keyframe_insert('location', frame=fr)
    TGT.location = t; TGT.keyframe_insert('location', frame=fr)
    FOC.location = fo; FOC.keyframe_insert('location', frame=fr)
    CAM.dof.aperture_fstop = fs; CAM.dof.keyframe_insert('aperture_fstop', frame=fr)
    CAM.lens = lens; CAM.keyframe_insert('lens', frame=fr)
    CO.rotation_euler = (0, 0, 0)
    tc_.influence = 1.0
# 滚转：用一个子空物体实现太复杂 → 用 Track To 的 up 轴 + 在相机上加 Z 偏转约束
rot_c = CO.constraints.new('TRANSFORM_CACHE') if False else None
ROLL = bpy.data.objects.new('roll', None); S.collection.objects.link(ROLL)
for fr, p, t, fo, fs, lens, roll in SHOTS:
    ROLL.rotation_euler[2] = roll; ROLL.keyframe_insert('rotation_euler', index=2, frame=fr)
cr = CO.constraints.new('COPY_ROTATION'); cr.target = ROLL; cr.use_x = False; cr.use_y = False; cr.use_z = True; cr.mix_mode = 'ADD'; cr.owner_space = 'LOCAL'
for ob in (CO, TGT, FOC, ROLL):
    for fc in ob.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = 'BEZIER'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
for fc in CAM.animation_data.action.fcurves:
    for k in fc.keyframe_points: k.interpolation = 'BEZIER'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'

# ---------------------------------------------------------------- 执行
os.makedirs(OUT, exist_ok=True)
if ARGV and ARGV[0] == 'still':
    for fr in ARGV[1:]:
        S.frame_set(int(fr)); S.render.filepath = os.path.join(os.environ.get('SDIR', HERE), f'still_{int(fr):03d}.png')
        bpy.ops.render.render(write_still=True)
elif ARGV and ARGV[0] == 'render':
    a, b = (int(ARGV[1]), int(ARGV[2])) if len(ARGV) > 2 else (1, NF)
    FD = os.path.join(HERE, 'frames') + os.sep; os.makedirs(FD, exist_ok=True)
    S.render.image_settings.file_format = 'JPEG'; S.render.image_settings.quality = 96
    for fr in range(a, b + 1):
        p = FD + f'f_{fr:04d}.jpg'
        if os.path.exists(p): continue
        S.frame_set(fr); S.render.filepath = p + '.tmp.jpg'
        bpy.ops.render.render(write_still=True); os.replace(p + '.tmp.jpg', p); print('Saved', p, flush=True)
elif ARGV and ARGV[0] == 'save':
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'watch.blend'))
