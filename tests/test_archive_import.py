"""归档合并的结构与共享组件回归；不需要字体、ASR 模型或 Blender。"""
import ast
import json
import gzip
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from bb import render3d as R
from bb.explain_score import Cues

ROOT = Path(__file__).resolve().parents[1]
TIMED = {
    'dankoe': (7, '.opus'),
    'devday': (8, '.flac'),
    'embodied': (8, '.flac'),
    'gemini4': (6, '.flac'),
    'jev': (8, '.opus'),
    'karpathy': (8, '.opus'),
    'muse': (8, '.opus'),
}
ORIGINAL = {'musk', 'concentration_cell', 'law_of_large_numbers', 'bohr_resonance', 'pinn'}


class ArchiveImportTests(unittest.TestCase):
    def test_project_index_is_complete(self):
        expected = ORIGINAL | set(TIMED) | {'watch'}
        actual = {p.name for p in (ROOT / 'examples').iterdir() if p.is_dir()}
        self.assertEqual(actual, expected)
        for name in expected:
            with self.subTest(project=name):
                d = ROOT / 'examples' / name
                self.assertTrue((d / 'README.md').is_file())
                self.assertTrue((d / 'build.sh').is_file())
                self.assertTrue((d / 'score.py').is_file())

    def test_timing_and_original_audio_formats(self):
        for name, (count, ext) in TIMED.items():
            with self.subTest(project=name):
                d = ROOT / 'examples' / name
                tm = json.loads((d / 'timing.json').read_text())
                self.assertEqual(len(tm['durs']), count)
                self.assertEqual(len(tm['subs']), count)
                expected = {f's{i}{ext}' for i in range(1, count + 1)}
                actual = {p.name for p in (d / 'narration').iterdir() if p.is_file()}
                self.assertEqual(actual, expected)
                for i, (dur, subs) in enumerate(zip(tm['durs'], tm['subs']), 1):
                    self.assertGreater(dur, 0)
                    self.assertTrue(subs)
                    previous = -1
                    for start, end, text in subs:
                        self.assertGreaterEqual(start, 0)
                        self.assertGreaterEqual(start, previous)
                        self.assertGreater(end, start)
                        self.assertLessEqual(end, dur + .05)
                        self.assertTrue(text.strip())
                        previous = start
                    with (d / 'narration' / f's{i}{ext}').open('rb') as audio:
                        self.assertEqual(audio.read(4), b'fLaC' if ext == '.flac' else b'OggS')

    def test_python_film_entrypoints_load_independently(self):
        # Isolate each project film module; the character models are shared in bb.figure3d.
        code = '''
from bb.loader import load_film
import sys
film = load_film(sys.argv[1])
assert len(film.starts) == len(film.durs) == len(film.scenes) == len(film.subs)
assert film.total >= film.starts[-1] + film.durs[-1]
assert film.nframes > 0
'''
        for name in ['musk', *TIMED]:
            with self.subTest(project=name):
                result = subprocess.run(
                    [sys.executable, '-c', code, str(ROOT / 'examples' / name / 'film.py')],
                    cwd=ROOT, capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_shared_character_models(self):
        self.assertTrue((ROOT / 'bb' / 'figure3d.py').is_file())
        for name in ['dankoe', 'karpathy']:
            d = ROOT / 'examples' / name
            self.assertFalse((d / 'figure3d.py').exists())
            self.assertIn('from bb.figure3d import *', (d / 'film.py').read_text())

    def test_minimal_node_dependencies(self):
        package = json.loads((ROOT / 'package.json').read_text())
        self.assertEqual(set(package['dependencies']), {'@napi-rs/canvas'})
        lock = json.loads((ROOT / 'package-lock.json').read_text())
        self.assertEqual(lock['packages']['']['dependencies'], package['dependencies'])
        self.assertFalse(any('ffmpeg-installer' in name or 'ffprobe-installer' in name
                             for name in lock['packages']))

    def test_compressed_training_snapshots(self):
        d = ROOT / 'examples' / 'pinn'
        self.assertFalse((d / 'train_data.json').exists())
        with gzip.open(d / 'train_data.json.gz', 'rt', encoding='utf8') as f:
            data = json.load(f)
        self.assertEqual(len(data['t']), len(data['exact']))
        for name in ['nn', 'pinn', 'inv']:
            self.assertEqual(len(data[name]['snap'][-1]), len(data['t']))
            self.assertEqual(len(data[name]['snap']), len(data[name]['step']))
        rmse = lambda run: (sum((v - t)**2 for v, t in
                               zip(data[run]['snap'][-1], data['exact'])) / len(data['t']))**.5
        self.assertLess(rmse('pinn'), .01)
        self.assertGreater(rmse('nn'), .5)
        self.assertAlmostEqual(data['inv']['mu'][-1], 4.2, delta=.1)

    def test_concentration_v4_timeline(self):
        d = ROOT / 'examples' / 'concentration_cell'
        tree = ast.parse((d / 'score.py').read_text())
        values = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name) and target.id in {'T', 'SEG'}:
                    values[target.id] = ast.literal_eval(node.value)
        self.assertEqual(values['T'], 71.7)
        self.assertEqual(values['SEG'], [.8, 9.6, 21.45, 33.27, 43.31, 57.43])
        scene = (d / 'scene.js').read_text()
        self.assertIn('DUR = 71.7', scene)
        self.assertIn('function warp(t)', scene)
        self.assertIn('浓度比决定电压', scene)
        self.assertIn("require(path.join(__dirname, '../../tools/node_env.js'))", scene)
        for i in [5, 6]:
            self.assertTrue((d / 'narration' / f's{i}.flac').is_file())

    def test_cues_uses_actual_narration_segment_count(self):
        from types import SimpleNamespace
        film = SimpleNamespace(TOTAL=1, SEG=[0] * 7)
        cues = Cues(film)
        with patch('bb.explain_score.load_voice', return_value=object()) as load_voice, \
                patch('bb.explain_score.finish') as finish:
            cues.finish('/unused')
        paths = load_voice.call_args.args[0]
        self.assertEqual(paths, [f'/unused/narration/s{i}.opus' for i in range(1, 8)])
        finish.assert_called_once()

    def test_rect_is_a_panel_not_a_text_entry(self):
        frame = R.Fr(R.Cam((0, 0, 5), (0, 0, 0)))
        frame.rect(10, 10, 40, 40, (200, 100, 50, 255), r=4)
        film = R.Film([0], [1], [lambda t, d: frame], [[]], chip=False)
        image = Image.new('RGB', (R.W, R.H))
        R.draw_overlay(image, frame, film, 0, 0, .5)
        self.assertEqual(image.getpixel((25, 25)), (100, 50, 25))
        self.assertEqual(image.getpixel((5, 5)), (0, 0, 0))
        self.assertEqual(R.BOX_LOG, [])


if __name__ == '__main__':
    unittest.main()
