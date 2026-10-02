# 飞行陀飞轮机芯 · 10 秒展示片

从 `10.2-1200.zip` 恢复的最新版工程：Blender 4.2 Cycles CPU、全程序化建模、微距一镜到底、金属与红宝石材质。没有旁白，配乐由程序合成。

| 文件 | 用途 |
|---|---|
| `scene.py` | 建模、材质、灯光、运镜；25 fps，共 250 帧 |
| `score.py` | 10.4 秒配乐，封装时裁到画面时长 |
| `assemble.py` | 对完整帧序列叠加片尾字卡、编码 H.264 |
| `build.sh` | 渲染 → 装配 → 混音 → 封装成 `watch.mp4` |
| `LESSONS.md` | 原制作复盘，环境与旧路径仅供历史参考 |

## 依赖

仓库的 Python 依赖、Noto Sans CJK 字体，以及另外安装的 **Blender 4.2**。Blender 本体和最终视频不入 Git；本次没有下载或运行 Blender，只做了脚本语法和配乐生成检查。

若 Blender 不在 PATH，设置 `BB_BLENDER=/path/to/blender`。Linux 便携版可能还需要系统库 `libxkbcommon0`。历史安装方式和渲染预算见 `LESSONS.md`，以实际环境为准。

## 先检查低清静帧

在仓库根目录：

```bash
SAMPLES=1 PCT=25 /path/to/blender -b --factory-startup \
  -P examples/watch/scene.py -- still 1 58 215
```

静帧写在本目录，可用 `SDIR` 指定另外的输出目录。默认正式渲染为 1280×720、40 采样；历史交付使用 8 采样和降噪。在原 2 核环境中，250 帧约需 4 小时，不要未经预算就重渲整片。

## 一键重建

```bash
BB_BLENDER=/path/to/blender SAMPLES=8 bash examples/watch/build.sh
```

也可分步执行（在仓库根目录、已激活 `.venv`）：

```bash
SAMPLES=8 /path/to/blender -b --factory-startup \
  -P examples/watch/scene.py -- render 1 250
python3 examples/watch/assemble.py
python3 examples/watch/score.py
python3 -m bb remux examples/watch/video.mp4 examples/watch/mix.wav examples/watch/watch.mp4
```

路径已改为相对工程文件定位，不再依赖 `~/watch`：

- `frames/f_0001.jpg`–`f_0250.jpg`：渲染帧；先写临时文件再原子重命名，已有帧自动跳过。
- `.cache/overlay/`：叠字临时 PNG；`.cache/watch.blend`：`save` 模式的场景。
- `mix.wav`、`video.mp4`、`watch.mp4`：音频和视频产物。

这些产物都被 Git 忽略。`frames/` 保留以便续渲；改模型、材质或画质后须先清理旧帧，避免混用不同版本。最终交付后可清理帧、缓存和混音。不要调用 `python3 -m bb qc scene.py`，它不支持 Blender 工程；视觉、穿模和声画同步仍需看图及试听。
