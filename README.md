# Blockbuster

用代码做视频的工具箱。画面由程序逐帧渲染，配乐由程序合成，讲解片的旁白使用已经录好的 FLAC 或 Opus。机械表展示片使用 Blender Cycles。

没有“输入一句话、12 秒出片”的通用流水线。按关键词套模板的旧管线已经废弃，不要恢复。每部片都要单独研究、写场景、写配乐；制作规范见 [`skills/blockbuster/SKILL.md`](skills/blockbuster/SKILL.md)。

## 目录

```text
bb/                          Python 工具包
  render3d.py                相机、网格、光照、字幕、3D 标签、2D 面板
  assets.py                  低多边形模型
  figure3d.py                Dan Koe / Karpathy 共用人物和道具
  news.py                    新闻包装和通用模型
  explain.py                 讲解片包装、几何和字幕时间线
  explain_score.py           讲解片配乐提示表
  timeline.py                按实测旁白时长建时间线
  score.py                   配乐和音效
  media.py                   ffmpeg、并行渲染、换音轨
  qc.py                      内容质检
  fonts.py                   中文字体查找
examples/<name>/             13 个项目，索引和重建命令见下表
  narration/                 85 段旁白；FLAC 无损压缩，Opus 原样保留
  film.py 或 scene.js        讲解片画面
  score.py、build.sh          混音和重建入口
  script.py、timing.json      新增讲解片的逐句稿和实测时间
examples/watch/              Blender 场景、配乐、帧序列装配，无旁白
skills/blockbuster/SKILL.md  制作规范
tools/                       重建、字幕对齐、录音切分、静帧接触单
MEMORY.md                    经验、坑、用户偏好
docs/IMPORT.md               解压、版本选择与瘦身记录
```

2026-10-02 已解压、去重并合并两个备份：新增 8 个项目；浓差电池恢复到 71.7 秒的 v4 科学修正版。文件来源、版本选择和验证范围见 [`docs/IMPORT.md`](docs/IMPORT.md)。没有保留第二套嵌套的 `Blockbuster/`，没有恢复废弃的模板流水线。

按用户要求，两个 ZIP 在全部 344 个条目完成解压核对后删除。重复工作区文档、可生成的录音稿、依赖缓存和渲染产物也已清理；13 个项目、85 段旁白、可复现训练数据和制作规范保留。当前项目文件约 **52.4 MiB**，主要是旁白，不做有损降质来换体积。

成片 mp4 不进 Git，也不上传 Release。删除文件只瘦身当前树：Git 历史仍包含原 ZIP，不改写历史。旧成片的历史线索和 ZIP 来源见 [`docs/IMPORT.md`](docs/IMPORT.md)，不是已核验的下载地址。

新增的新闻、人物项目是**历史工程归档**；脚本和来源说明保持原有信息截止日期，本次没有重新核查新闻事实，不应当作最新报道。

## 安装

Python 3.9+。在仓库根目录：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

中文字体使用 Noto Sans CJK。Debian/Ubuntu：

```bash
sudo apt install fonts-noto-cjk
```

没有系统包时，把字体目录指给 `BB_FONT_DIR`，目录里放下面任一对字体：

- `NotoSansCJK-Bold.ttc` 和 `NotoSansCJK-Regular.ttc`
- `NotoSansCJKsc-Bold.otf` 和 `NotoSansCJKsc-Regular.otf`

也可以分别设置 `BB_FONT_BOLD`、`BB_FONT_REGULAR`。字体不要入库。

ffmpeg 优先使用 PATH 或 `BB_FFMPEG`，否则使用 `imageio-ffmpeg` 自带的二进制。想把 ffmpeg 放进当前 shell 的 PATH，可以 `source tools/ensure_ff.sh`（必须 source）。

四个 Node 场景还需要：

```bash
npm ci
```

Node 只保留 `@napi-rs/canvas`，不再下载第二套 ffmpeg/ffprobe；与 Python 共用 ffmpeg（可直接识别仓库 `.venv`）。依赖和缓存不入库，需要运行时重新安装。机械表项目另外需要 Blender 4.2，见 [`examples/watch/README.md`](examples/watch/README.md)。

## 快速上手

在仓库根目录、已激活虚拟环境时：

```bash
python3 -m bb still examples/musk/film.py 30
python3 -m bb qc examples/musk/film.py
python3 examples/concentration_cell/score.py
python3 tools/stills_grid.py examples/dankoe/film.py contact_sheet_dankoe.png 10 60 120
```

- `still` 写出带时间后缀的静帧，避免读图缓存。
- `qc` 不传成片时，检查字形、字幕、文字出画和重叠，不检查响度。仅适用于 Python `film.py`，不是 Node 或 Blender 场景。
- `score.py` 把旁白与配乐混音写到该项目的 `mix.wav`（不入库）。
- 重建脚本不会生成新旁白，直接使用归档录音和 `timing.json`。

其他命令：

```bash
python3 -m bb render examples/musk/film.py out.mp4 --jobs 2
python3 -m bb remux video.mp4 mix.wav
python3 -m bb qc examples/musk/film.py out.mp4
```

## 项目索引与重建

命令均从仓库根目录执行：`bash examples/<目录>/build.sh`。成片默认写在项目目录里，可用第一个参数修改输出路径。时长来自脚本时间线，取近似值；本次没有重渲整片。

| 目录 / 说明 | 时长 | 成片文件名 | 引擎 / 旁白 |
|---|---|---|---|
| [musk](examples/musk/README.md) · 马斯克传记 | 3:14 | `musk_3min.mp4` | Python / FLAC |
| [concentration_cell](examples/concentration_cell/README.md) · 浓差电池 v4 | 71.7 s | `concentration_cell_nernst.mp4` | Node / FLAC |
| [law_of_large_numbers](examples/law_of_large_numbers/README.md) · 大数定律 | 60.4 s | `law_of_large_numbers.mp4` | Node / FLAC |
| [bohr_resonance](examples/bohr_resonance/README.md) · 波尔共振 | 60.4 s | `bohr_resonance.mp4` | Node / FLAC |
| [pinn](examples/pinn/README.md) · PINN | 60.4 s | `pinn_explained.mp4` | Node / FLAC；无需重训 |
| [dankoe](examples/dankoe/README.md) · Dan Koe | 3:15 | `dankoe.mp4` | Python / Opus（7 段） |
| [devday](examples/devday/README.md) · OpenAI DevDay | 3:35 | `devday_2026_news.mp4` | Python / FLAC |
| [embodied](examples/embodied/README.md) · 具身智能 | 3:35 | `embodied_ai_frontier.mp4` | Python / FLAC |
| [gemini4](examples/gemini4/README.md) · Gemini 4 Argon | 2:03 | `gemini4_argon_news.mp4` | Python / FLAC |
| [jev](examples/jev/README.md) · Jev | 4:01 | `jev.mp4` | Python / Opus |
| [karpathy](examples/karpathy/README.md) · Karpathy | 3:40 | `karpathy.mp4` | Python / Opus |
| [muse](examples/muse/README.md) · Muse | 3:50 | `muse.mp4` | Python / Opus |
| [watch](examples/watch/README.md) · 飞行陀飞轮 | 10 s | `watch.mp4` | Blender Cycles / 无旁白 |

Python 重建默认两个渲染进程，新增项目可用 `JOBS=2 bash examples/dankoe/build.sh` 覆盖。Blender 的渲染成本显著更高，先渲低清静帧，勿把整片重建当成快速测试。重建脚本会执行 QC；归档工程如存在原有质检问题，应先修正再重新交付。

只换音轨、不重渲画面：

```bash
python3 examples/<name>/score.py
python3 -m bb remux 成片.mp4 examples/<name>/mix.wav
```

旧的 `music.js`、`scorelib.py`、根目录 `remux.sh` 不恢复。配乐用 `bb.score`，换音轨用 `python3 -m bb remux`。

## 录音和字幕工具（可选）

只重建归档视频不需要语音识别模型。重新切分录音或生成字幕时间时，再安装 `faster-whisper`（首次运行会下载模型）：

```bash
pip install faster-whisper
python3 tools/split_takes.py examples/<name> 1.22
python3 tools/make_timing.py examples/<name>
```

`split_takes.py` 需要 `script.py` 的 `SEGS`、`TAKES` 和原始 `take*.wav`；备份没有原始 take 音频。重复的 `take*.txt` 已删除，录音稿可由 `script.TEXT` 按 `script.TAKES` 拼接生成。不要对已变速的归档旁白再做一次变速。`make_timing.py` 支持 FLAC / Opus，会重写 `timing.json`，请先保存旧版本。

## 检查与新片

结构和合并回归测试（不需要中文字体或 Blender）：

```bash
python3 -m unittest discover -s tests -v
```

新片按 [`skills/blockbuster/SKILL.md`](skills/blockbuster/SKILL.md)：标准普通话、voice-01、逐句字幕、真正的 3D 场景、跟随画面变化的配乐。仓库不包含 TTS，新旁白须在外部生成后放进 `narration/`。

交付视频前 `python3 -m bb qc` 必须是 0 问题，并且要看接触单和关键帧。QC 不代替看图、核查事实或试听。此次整理不是一次新的成片交付，验证边界见整理记录。
