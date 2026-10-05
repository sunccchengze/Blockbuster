"""Muse 讲解配乐：温暖的钢琴 + 弦乐为底（个人助理感），安全架构段落转入低音悬疑。"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import film as r3d
from bb.explain_score import *
Q = Cues(r3d); mus, sfx = Q.mus, Q.sfx
# 1 开场：明亮钢琴 + 钟琴 → 榜单上升
k = 0; e = Q.E(k)
Q.piano_arp(Q.G(k, 0), Q.end(k), 96, [C, G_, Am, F], 0.4, 0.35)
Q.sparkle(Q.G(k, 0.8), [72, 76, 79, 84], 0.45)
add(sfx, e[2], riser(1.6, 0.25)); Q.sparkle(e[2] + 2.0, [84, 88, 91], 0.4)
# 2 是什么：轻律动 → 手机熄屏 → 通知 ping → 价格
k = 1; e = Q.E(k)
Q.groove(Q.G(k, 0), e[3], 104, [F, C, Dm, Bb], 0.35, 0.5, snare_v=0.12)
add(sfx, e[1] + 0.2, blip(1200, 0.3)); add(sfx, e[2] + 0.6, tick(0.3)); add(sfx, e[2] + 1.2, tick(0.3))
add(sfx, e[3] + 0.4, thud(0.3))
Q.pad(e[3], e[5], [Am, F], 0.4)
add(sfx, e[3] + 3.2, ping(2400, 0.45))
Q.groove(e[5], Q.end(k), 112, [C, G_], 0.4, 0.6, snare_v=0.15)
for j in range(3): add(mus, e[5] + j * 0.25, bell(76 + j * 4, 0.4))
# 3 大脑：大提琴推进 → 百万上下文盘旋 → 基准柱鼓点 → 铺路上行
k = 2; e = Q.E(k)
Q.cello(Q.G(k, 0), e[2], 116, [45, 41], 0.45); Q.pad(Q.G(k, 0), e[2], [Am, F], 0.3)
add(mus, e[1] + 0.6, timpani(41, 0.6))
add(sfx, e[2], whoosh(0.7, 300, 3000, 0.25))
for q in range(30): add(sfx, e[2] + q * 0.08, tick(0.22, 2000 + q * 40))
Q.groove(e[3], e[5], 120, [Dm, Bb, F, C], 0.45, 0.65, snare_v=0.25)
add(mus, e[3] + 0.4, timpani(38, 0.6)); add(sfx, e[4] + 0.6, beep(330, 0.2, 0.25))
Q.pad(e[5], Q.end(k), [F, G_], 0.45)
Q.sparkle(e[5] + 0.3, [72, 74, 76, 79, 84], 0.4, 0.3)
# 4 Secure VM：低音悬疑 + 框线搭建 → 九台机器
k = 3; e = Q.E(k)
chord_strings(Q.G(k, 0), e[3], [36, 48, 55, 62], 0.5, 1.0, 0.7, 0.8)
add(sfx, e[1], riser(0.8, 0.25)); add(mus, e[1] + 0.8, timpani(36, 0.6))
for j in range(3): add(sfx, e[2] + j * 0.35, clink(0.35))
Q.cello(e[3], Q.end(k), 108, [36, 44, 39, 43], 0.45); Q.pad(e[3], Q.end(k), [Cm, Ab, Eb, G_], 0.3)
# 5 Sentinel：紧张律动 → 放行/拦截提示音 → 弹窗 ping → 权限矩阵 → 保险库转盘
k = 4; e = Q.E(k)
Q.groove(Q.G(k, 0), e[5], 118, [Cm, Ab, Eb, G_], 0.45, 0.6, pl=False, snare_v=0.2)
Q.cello(Q.G(k, 0), e[5], 118, [36, 44, 39, 43], 0.35)
for q in range(8): add(sfx, e[3] + q * 0.55, blip([1200, 300, 900][q % 3], 0.25))
add(sfx, e[4] + 0.2, ping(2200, 0.45))
Q.piano_arp(e[5], Q.end(k), 92, [Eb, Bb, Cm, Ab], 0.35)
for q in range(8): add(sfx, e[6] + q * 0.15, tick(0.3, 1400))
# 6 支付与生态：亮色律动 → 连接器逐个点亮
k = 5; e = Q.E(k)
Q.groove(Q.G(k, 0), Q.end(k), 116, [C, G_, Am, F], 0.4, 0.6, snare_v=0.2)
for j in range(3): add(sfx, Q.G(k, 0.2) + j * 1.5, clink(0.4))
for j in range(6): add(mus, e[2] + 0.3 + j * 0.2, bell([72, 76, 79, 81, 84, 88][j], 0.4))
# 7 Confidential VM：悬疑 → 外壳合拢 timpani → 透明日志一块块
k = 6; e = Q.E(k)
chord_strings(Q.G(k, 0), e[2], [40, 52, 55, 59], 0.5, 0.8, 0.7, 0.8)
add(sfx, e[2], riser(0.8, 0.3)); add(mus, e[2] + 0.8, timpani(40, 0.8))
Q.pad(e[2], e[5], [E_, A7, D, E_], 0.4)
add(sfx, e[4] + 0.1, thud(0.5))
Q.piano_arp(e[5], Q.end(k), 100, [D, A7, G_, D], 0.38)
for q in range(6): add(sfx, e[6] + 0.8 + q * 0.33, clink(0.35))
# 8 硬件 → 总结 → 片尾
k = 7; e = Q.E(k)
Q.groove(Q.G(k, 0), e[5], 110, [F, C, G_, Am], 0.4, 0.6, snare_v=0.15)
Q.sparkle(Q.G(k, 0.3), [79, 84, 88], 0.45)
add(sfx, e[5] - 1.0, riser(1.0, 0.3)); add(mus, e[5] + 0.05, timpani(36, 0.9))
Q.sparkle(e[5], [72, 76, 79, 84, 88], 0.45)
Q.ending(e[5], [F, G_])
Q.finish(HERE)
