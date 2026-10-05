"""把若干时刻的静帧拼成一张图，方便一次看完：python3 tools/stills_grid.py film.py out.png t1 t2 ...（每行 3 张）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageDraw
from bb.loader import load_film
from bb.render3d import render_frame, FPS, font
film = load_film(sys.argv[1]); ts = [float(x) for x in sys.argv[3:]]
cols = 3; w, h = 640, 360; rows = (len(ts) + cols - 1) // cols
G = Image.new('RGB', (cols * w, rows * h))
for i, t in enumerate(ts):
    im = render_frame(film, int(t * FPS)).resize((w, h)); ImageDraw.Draw(im).text((8, h - 30), f'{t:.1f}s', font=font(22), fill=(255, 255, 0))
    G.paste(im, ((i % cols) * w, (i // cols) * h))
G.save(sys.argv[2]); print(sys.argv[2])
