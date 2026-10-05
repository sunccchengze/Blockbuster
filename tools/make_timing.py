"""逐段对齐旁白 → timing.json：{durs: [...], subs: [[[start, end, 字幕], ...], ...]}。
用法：python3 tools/make_timing.py <片目录>     （目录里要有 script.py 的 SEGS 和 narration/s1..sN.flac 或 .opus）
字幕时间：每句从该句第一个字开始，持续到下一句开始（最后一句到段尾），中间停顿也挂着字幕，避免闪烁。
"""
import sys, os, json, importlib.util
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.align import align
d = os.path.abspath(sys.argv[1])
spec = importlib.util.spec_from_file_location('script', os.path.join(d, 'script.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out = {'durs': [], 'subs': []}
for k, seg in enumerate(m.SEGS):
    audio = os.path.join(d, f'narration/s{k + 1}.flac')
    if not os.path.isfile(audio):
        audio = os.path.join(d, f'narration/s{k + 1}.opus')
    t, dur = align(audio, [sp for sp, _ in seg])
    subs = []
    for i, ((a, b), (_, shown)) in enumerate(zip(t, seg)):
        nxt = t[i + 1][0] if i + 1 < len(t) else max(b, dur - 0.05)
        subs.append([round(float(a), 2), round(float(max(b, nxt - 0.05)), 2), shown])
    out['durs'].append(round(dur, 2)); out['subs'].append(subs)
    print(k + 1, round(dur, 2), len(subs), flush=True)
json.dump(out, open(os.path.join(d, 'timing.json'), 'w'), ensure_ascii=False, indent=0)
