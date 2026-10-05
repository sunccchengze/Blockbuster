# 兼容层：配乐引擎已迁入 Blockbuster 仓库 bb/score.py
import sys, os; sys.path.insert(0, os.path.expanduser('~/Blockbuster'))
from bb.score import *
from bb import score as _s
def buses(T):
    m, s = _s.buses(T); globals()['mus'], globals()['sfx'] = m, s; return m, s
