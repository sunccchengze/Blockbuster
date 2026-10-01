"""定位中文字体。优先系统的 Noto Sans CJK，也可用环境变量覆盖。"""
import os
from fontTools.ttLib import TTCollection, TTFont

_NAMES = {
    True: [
        'NotoSansCJK-Bold.ttc',
        'NotoSansCJK-Bold.otf',
        'NotoSansCJKsc-Bold.otf',
        'NotoSansSC-Bold.otf',
    ],
    False: [
        'NotoSansCJK-Regular.ttc',
        'NotoSansCJK-Regular.otf',
        'NotoSansCJKsc-Regular.otf',
        'NotoSansSC-Regular.otf',
    ],
}
_DIRS = [
    '/usr/share/fonts/opentype/noto',
    '/usr/share/fonts/opentype/noto-cjk',
    '/usr/share/fonts/noto-cjk',
    '/usr/share/fonts/truetype/noto',
    '/usr/share/fonts/truetype/noto-cjk',
]


def cjk_font(bold=True):
    env_key = 'BB_FONT_BOLD' if bold else 'BB_FONT_REGULAR'
    env = os.environ.get(env_key)
    if env:
        if os.path.isfile(env):
            return env
        raise FileNotFoundError('%s 指向的文件不存在：%s' % (env_key, env))
    dirs = []
    if os.environ.get('BB_FONT_DIR'):
        dirs.append(os.environ['BB_FONT_DIR'])
    dirs.extend(_DIRS)
    for d in dirs:
        for name in _NAMES[bold]:
            p = os.path.join(d, name)
            if os.path.isfile(p):
                return p
    raise FileNotFoundError(
        '找不到中文字体（Noto Sans CJK）。安装 fonts-noto-cjk，'
        '或设置 BB_FONT_DIR / BB_FONT_BOLD / BB_FONT_REGULAR。'
    )


def cmap(path):
    if path.lower().endswith(('.ttc', '.otc')):
        font = TTCollection(path).fonts[0]
    else:
        font = TTFont(path)
    return set(font.getBestCmap().keys())
