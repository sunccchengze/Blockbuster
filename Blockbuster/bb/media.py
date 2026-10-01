"""bb.media — ffmpeg 自举、并行渲染、换音轨+响度对齐、接触单。"""
import os, subprocess, shutil, re, sys, tempfile

def ffmpeg():
    """返回可用 ffmpeg 路径；沙箱会丢 ~/bin 与 pip 包，这里自动重装 imageio-ffmpeg 并链接。"""
    p = shutil.which('ffmpeg')
    if p: return p
    try: import imageio_ffmpeg
    except ImportError:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'imageio-ffmpeg'], check=True); import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe(); b = os.path.expanduser('~/bin'); os.makedirs(b, exist_ok=True)
    link = os.path.join(b, 'ffmpeg')
    if os.path.lexists(link): os.remove(link)
    os.symlink(exe, link); os.environ['PATH'] = b + os.pathsep + os.environ['PATH']; return link

def render_parallel(film_path, out, jobs=2):
    """把一部片按帧切成 jobs 段并行渲染，再无损 concat。"""
    ff = ffmpeg(); from .loader import load_film
    film = load_film(film_path); N = film.nframes; cuts = [N * i // jobs for i in range(jobs + 1)]
    tmp = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(out)) or '.')
    parts = [os.path.join(tmp, 'p%d.mp4' % i) for i in range(jobs)]
    procs = [subprocess.Popen([sys.executable, '-m', 'bb', '_encode', film_path, str(cuts[i]), str(cuts[i + 1]), parts[i]],
                              env={**os.environ, 'PYTHONPATH': os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}) for i in range(jobs)]
    if any(p.wait() for p in procs): raise SystemExit('render failed')
    lst = os.path.join(tmp, 'l.txt'); open(lst, 'w').write(''.join("file '%s'\n" % p for p in parts))
    subprocess.run([ff, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out], check=True)
    shutil.rmtree(tmp)

def loudness(path):
    r = subprocess.run([ffmpeg(), '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]); P = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1]); return I, P

def remux(video, audio, out=None, target=-14.0):
    """保留画面，替换音轨，响度对齐 target LUFS（固定增益 + 限幅，避免单遍 loudnorm 漂移）。"""
    ff = ffmpeg(); I, _ = loudness(audio); g = target - I; out = out or video
    tmp = out + '.tmp.mp4'
    subprocess.run([ff, '-v', 'error', '-y', '-i', video, '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-af', f'volume={g}dB,alimiter=limit=0.8:level=false', '-c:a', 'aac', '-b:a', '192k', '-shortest', tmp], check=True)
    os.replace(tmp, out); return loudness(out)

def contact_sheet(video, out, cols=4, rows=3):
    ff = ffmpeg(); info = subprocess.run([ff, '-i', video], capture_output=True, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', info).groups(); D = int(h) * 3600 + int(m) * 60 + float(s)
    n = cols * rows; step = D / (n + 1)
    subprocess.run([ff, '-v', 'error', '-y', '-i', video, '-vf', f"fps=1/{step:.3f},scale=480:-1,tile={cols}x{rows}", '-frames:v', '1', out], check=True)
