"""bb.timeline — 以实测旁白为准的时间线：段落起点、逐句字幕切分、事件锚点。"""
import subprocess, re

def audio_duration(path, ffmpeg='ffmpeg'):
    info = subprocess.run([ffmpeg, '-i', path], capture_output=True, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', info).groups(); return int(h) * 3600 + int(m) * 60 + float(s)

def starts_from_durations(durs, first=0.6, gap=0.4):
    out, t = [], first
    for d in durs: out.append(t); t += d + gap
    return out

def split_subs(raw):
    """raw[k] = [(start, end, "句子|可手动断句"), ...]（段内局部时间）。
    返回 subs[k] = [(start, end, text)]，每个 | 片段按字数比例分配时长。"""
    subs = []
    for lst in raw:
        out = []
        for a, b, s in lst:
            parts = s.split('|'); tot = sum(len(p) for p in parts); x = a
            for p in parts:
                e = x + (b - a) * len(p) / tot; out.append((x, e, p)); x = e
        subs.append(out)
    return subs
