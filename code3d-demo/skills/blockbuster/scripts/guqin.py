#!/usr/bin/env python3
"""
guqin.py — 物理建模的中国拨弦乐器引擎（纯 numpy，无采样、无模型）。

为什么加法合成听起来"塑料"，以及这里怎么修：
  1 静态泛音 → 真实弦的高次模衰减快得多，亮度随时间下落。
     修：Karplus-Strong 块递归——循环里的均值低通天然给出频率相关衰减。
  2 没有拨弦位置 → 真实音色有一排谱梳齿（节点/反节点）。
     修：激励 = noise - delay(noise, 拨弦位置)，产生梳状谐波强调。
  3 没有滑音/吟猱 → 古琴的"韵"全在左手：绰、注、吟、猱。
     修：周期长度随时间变化（重采样缓冲）= 真实滑音；延迟起振的正弦调制 = 吟。
  4 没有琴体 → 平板共振峰给音色"木头味"。
     修：FFT 域乘共振峰曲线（guqin/guzheng/pipa 各一组）。
  5 没有摩擦 → 滑指时弦与指的沙声。
     修：滑音期间按滑速叠加带通噪声。
  6 起音太干净 → 肉拨/甲拨的瞬态完全不同。
     修：excite='flesh'|'nail'|'pick' 三种激励整形。

全部向量化：KS 按"周期"块迭代（每周期一次 numpy 操作），10 秒音符也只要几十次调用。
"""
import numpy as np

SR = 48000

# 琴体共振峰 (Hz, gain dB, Q)
BODY = {
    'guqin':   [(110,  4.0, 6), (240, 6.0, 8), (520, 4.5, 10), (1100, 2.5, 12), (2200, -3.0, 8)],
    'guzheng': [(180,  3.0, 6), (420, 5.0, 9), (950, 4.0, 10), (1900, 2.0, 12), (3200, 1.0, 10)],
    'pipa':    [(220,  3.5, 7), (600, 5.0, 9), (1300, 4.0, 10), (2600, 3.0, 12), (4000, 0.0, 10)],
}
DECAY = {'guqin': 0.9985, 'guzheng': 0.9975, 'pipa': 0.9960}   # 每周期损耗
PLUCKPOS = {'guqin': 0.16, 'guzheng': 0.11, 'pipa': 0.09}      # 拨弦位置（占弦长比例）


def _onepole_lp(x, coef):
    """向量化一pole低通（用 cumsum 技巧的近似：指数移动平均）"""
    # 用 FFT 做精确一pole太慢；这里用累加近似足够用于激励整形
    y = np.empty_like(x)
    acc = 0.0
    # 激励很短（< 40ms），Python 循环可接受
    for i in range(len(x)):
        acc = acc + coef * (x[i] - acc)
        y[i] = acc
    return y


def _excitation(n, kind, rng, pluckpos):
    """拨弦激励：噪声 + 拨弦位置梳齿 + 起音瞬态"""
    e = rng.standard_normal(n)
    if kind == 'flesh':                      # 肉拨：闷、圆
        e = _onepole_lp(e, 0.10)
        e = _onepole_lp(e, 0.10)
        atk = np.minimum(np.arange(n) / (SR * 0.004), 1.0)
    elif kind == 'nail':                     # 甲拨：亮、有 click
        e = _onepole_lp(e, 0.42)
        atk = np.minimum(np.arange(n) / (SR * 0.0012), 1.0)
        cn = min(n, int(SR * 0.0016))
        click = np.zeros(n); click[:cn] = rng.standard_normal(cn) * 1.6
        e = e + click
    else:                                    # pick / 琵琶：更冲
        e = _onepole_lp(e, 0.55)
        atk = np.minimum(np.arange(n) / (SR * 0.0010), 1.0)
        cn = min(n, int(SR * 0.0012))
        click = np.zeros(n); click[:cn] = rng.standard_normal(cn) * 2.2
        e = e + click
    e *= atk
    # 拨弦位置梳齿：e - delay(e, pos*N)
    d = max(1, int(round(n * pluckpos)))
    comb = e.copy()
    comb[d:] -= e[:-d] * 0.85
    return comb


def _body_filter(y, inst):
    """FFT 域乘琴体共振峰"""
    Y = np.fft.rfft(y)
    f = np.fft.rfftfreq(len(y), 1 / SR)
    mag = np.zeros_like(f)
    for (fc, db, Q) in BODY[inst]:
        mag += db * np.exp(-0.5 * ((f - fc) / (fc / Q)) ** 2)
    mag -= 18 * np.exp(-0.5 * ((f - 0) / 45) ** 2)          # 去 rumble
    mag -= 12 / (1 + np.exp(-(f - 7500) / 900))             # 空气高频滚降
    Y *= 10 ** (mag / 20.0)
    return np.fft.irfft(Y, len(y))


def _friction(n, velocity, rng):
    """滑指摩擦沙声：带通噪声，量随滑速"""
    x = rng.standard_normal(n)
    x = np.diff(x, prepend=0.0)                 # 高通
    x = _onepole_lp(x, 0.22)                    # 再低通 → 带通 ~1-3k
    env = np.sin(np.linspace(0, np.pi, n)) ** 0.7
    return x * env * min(abs(velocity), 1.0) * 0.16


def note(f0, dur=1.8, inst='guqin', excite=None, amp=0.2,
         slide_to=None, slide_start=0.06, slide_dur=0.22, slide_curve=0.6,
         vibrato=0.0, vib_hz=4.6, vib_start=0.35, vib_depth=0.006,
         sr=SR, seed=None):
    """
    一个音。
      slide_to   : 目标频率（None=不滑）。slide_start 后开始，slide_dur 内滑到，curve<1=先快后慢
      vibrato   : 0=无；1=吟（浅）；2=猱（深慢）。自动设 depth/hz
      返回 mono float array
    """
    rng = np.random.default_rng(seed if seed is not None else int(f0 * 977) & 0xFFFF)
    if excite is None:
        excite = {'guqin': 'flesh', 'guzheng': 'nail', 'pipa': 'pick'}[inst]
    if vibrato == 1:
        vib_depth, vib_hz, vib_start = 0.0045, 4.8, 0.40
    elif vibrato == 2:
        vib_depth, vib_hz, vib_start = 0.011, 3.1, 0.30

    total = int(dur * sr)
    out = np.zeros(total, dtype=np.float64)
    # 周期长度随时间的轨迹（滑音 + 吟猱）
    tt = np.arange(total) / sr
    freq = np.full(total, f0, dtype=np.float64)
    if slide_to:
        x = np.clip((tt - slide_start) / slide_dur, 0, 1)
        x = x ** slide_curve if slide_curve else x
        x = np.where(tt < slide_start, 0.0, x)
        # 用 smoothstep 让滑音两端不折角
        x = np.where((tt >= slide_start) & (tt <= slide_start + slide_dur),
                     x * x * (3 - 2 * x), x)
        freq = f0 * (1 - x) + slide_to * x
    if vibrato:
        vm = np.clip((tt - vib_start) / 0.25, 0, 1)
        freq *= 1 + vib_depth * vm * np.sin(2 * np.pi * vib_hz * (tt - vib_start))

    # 块 KS：按周期迭代
    period_samples = sr / freq
    buf = _excitation(max(8, int(round(period_samples[0]))), excite, rng, PLUCKPOS[inst])
    loss = DECAY[inst]
    pos = 0
    k = 0
    friction_buf = None
    while pos < total - 4:
        n = max(4, int(round(period_samples[min(pos, total - 1)])))
        # 周期长度变化 → 重采样缓冲（滑音的物理实现）
        if n != len(buf):
            idx = np.linspace(0, len(buf) - 1, n)
            buf = np.interp(idx, np.arange(len(buf)), buf)
        take = min(n, total - pos)
        out[pos:pos + take] += buf[:take]
        # 循环滤波：均值低通 + 损耗（频率相关衰减的来源）
        buf = loss * 0.5 * (buf + np.roll(buf, 1))
        # 极轻微的非线性：弦-码耦合产生的倍频嗡声
        buf += 0.006 * np.tanh(buf * 3.0) * np.exp(-k * 0.02)
        pos += take
        k += 1
        if k > 20000:
            break

    # 滑指摩擦
    if slide_to:
        i0 = int(slide_start * sr); i1 = int((slide_start + slide_dur) * sr)
        if i1 > i0:
            vel = abs(np.log2(slide_to / f0)) / max(slide_dur, 1e-3) * 0.35
            out[i0:i1] += _friction(i1 - i0, vel, rng)

    out = _body_filter(out, inst)

    # 两阶段包络：KS 已有自然衰减，这里补一个极慢的整体释放 + 止音余韵
    env = np.exp(-tt / (dur * 0.62))
    out *= env
    # 末端止音（手指触弦）的小闷声
    rel = int(0.03 * sr)
    if total > rel:
        out[-rel:] *= np.linspace(1, 0.15, rel)
    return out * amp


def guozhi(f_start, f_end, n_notes=9, dur=1.6, inst='guzheng', amp=0.14, step=0.045, seed=1):
    """刮奏：快速上行/下行琶音扫弦（古筝招牌）"""
    rng = np.random.default_rng(seed)
    total = int((dur + step * n_notes) * SR)
    out = np.zeros(total)
    for i in range(n_notes):
        r = i / max(1, n_notes - 1)
        f = f_start * (f_end / f_start) ** r
        t0 = int(i * step * SR)
        s = note(f, dur=dur, inst=inst, excite='nail', amp=amp * (0.8 + 0.4 * rng.random()),
                 seed=seed + i)
        n = min(len(s), total - t0)
        out[t0:t0 + n] += s[:n]
    return out
