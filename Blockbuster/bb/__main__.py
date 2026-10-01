"""命令行：
  python3 -m bb render <film.py> <out.mp4> [--jobs 2]
  python3 -m bb still  <film.py> <秒> [<秒> ...]         → still_<秒>.png（每次写新文件名，避免读图缓存）
  python3 -m bb qc     <film.py> [<成片.mp4>]            → 内容质检 + 接触单
  python3 -m bb remux  <video.mp4> <mix.wav> [out.mp4]  → 换音轨并对齐 −14 LUFS
"""
import sys, os, time
from .media import ffmpeg
def main(a):
    cmd = a[0] if a else 'help'
    if cmd == '_encode':
        from .loader import load_film; from .render3d import encode
        encode(load_film(a[1]), int(a[2]), int(a[3]), a[4], ffmpeg()); return
    if cmd == 'render':
        from .media import render_parallel
        jobs = int(a[a.index('--jobs') + 1]) if '--jobs' in a else 2; t0 = time.time()
        render_parallel(a[1], a[2], jobs); print(f'rendered {a[2]} in {time.time()-t0:.0f}s'); return
    if cmd == 'still':
        from .loader import load_film; from .render3d import render_frame, FPS
        film = load_film(a[1])
        for ts in a[2:]:
            p = f'still_{ts}_{int(time.time()*1000)%100000}.png'; render_frame(film, int(float(ts) * FPS)).save(p); print(p)
        return
    if cmd == 'qc':
        from .loader import load_film; from .qc import check_film, check_video; from .media import contact_sheet
        film = load_film(a[1]); issues, stills = check_film(film, 1.0, '.')
        if len(a) > 2:
            (I, P), vi = check_video(a[2]); issues += vi; contact_sheet(a[2], 'qc_contact.png'); print(f'loudness {I} LUFS, peak {P} dBFS')
        print('\n'.join(issues) if issues else 'QC 通过：无缺字形 / 字幕问题'); print('静帧:', ' '.join(stills)); return
    if cmd == 'remux':
        from .media import remux; print(remux(a[1], a[2], a[3] if len(a) > 3 else None)); return
    print(__doc__)
main(sys.argv[1:])
