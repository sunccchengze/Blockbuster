#!/usr/bin/env python3
"""check_env.py — verify the render/sound toolchain; print exact fix commands.

Usage: python3 check_env.py     (from the project root). Exit 0 = ready, 1 = missing pieces.
"""
import shutil, subprocess, sys, os, pathlib

problems = []
def need(label, cond, fix=''):
    print(('  [ok]      ' if cond else '  [MISSING] ') + label)
    if not cond:
        problems.append(label)
        if fix: print('              fix: ' + fix)

print('blockbuster env check')
need('node >= 18', shutil.which('node') is not None, 'install Node.js 18+')
need('npm', shutil.which('npm') is not None, 'install npm')
need('ffmpeg-static (or system ffmpeg)',
     bool(shutil.which('ffmpeg')) or os.path.exists('node_modules/ffmpeg-static/ffmpeg'),
     'npm i ffmpeg-static')
need('playwright (node pkg)', os.path.exists('node_modules/playwright'), 'npm i playwright')
need('chromium browser binary',
     bool(list(pathlib.home().glob('.cache/ms-playwright/chromium*'))),
     'npx playwright install chromium && npx playwright install-deps chromium')
fc = shutil.which('fc-list')
cjk = b'CJK' in subprocess.run([fc], capture_output=True).stdout if fc else False
need('CJK font (中文 titles)', cjk, 'sudo apt-get install fonts-noto-cjk')
need('serif CJK font (calligraphic titles)',
     b'Serif CJK' in subprocess.run([fc], capture_output=True).stdout if fc else False,
     'sudo apt-get install fonts-noto-cjk (ships Sans+Serif)')
try:
    import numpy  # noqa
    npy = True
except Exception:
    npy = False
need('numpy (score.py / audio_qa.py)', npy, 'python3 -m pip install numpy')

gpu = os.path.exists('/dev/dri')
print(f'  [info] GPU: {"hardware GL" if gpu else "none -> SwiftShader software WebGL; budget 0.5-2 s/frame @720p"}')
print('  [info] deps & out/ are NOT persisted between sessions: reinstall + re-render after a reset.')
print('  [info] deliverables must not live in out/ (excluded from workspace snapshots).')
if problems:
    print(f'  => NOT READY: {", ".join(problems)}')
sys.exit(1 if problems else 0)
