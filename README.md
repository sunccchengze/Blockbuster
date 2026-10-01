# Blockbuster

用代码做讲解视频的工具箱。画面由程序逐帧渲染，配乐由程序合成，旁白是事先录好的 FLAC。

没有“输入一句话、12 秒出片”的通用流水线。那套按关键词套模板的管线已经废弃，不在当前代码里，也不要恢复。每部片都要单独研究、写场景、写配乐。仓库提供可复用的零件和制作规范（[`skills/blockbuster/SKILL.md`](skills/blockbuster/SKILL.md)）。

## 目录

```
bb/                          Python 工具包
  render3d.py                3D 引擎：相机、网格、光照、字幕、3D 标签
  assets.py                  低多边形模型
  timeline.py                按实测旁白时长建时间线
  score.py                   配乐和音效
  media.py                   ffmpeg、并行渲染、换音轨
  qc.py                      内容质检
  fonts.py                   中文字体查找
examples/
  musk/                      三分钟人物传记（Python 3D，film.py）
  concentration_cell/        浓差电池（Node 场景 scene.js + score.py）
  law_of_large_numbers/      大数定律
  bohr_resonance/            波尔共振
  pinn/                      PINN
  每个样例的 narration/*.flac 是旁白，入库，用来重建
skills/blockbuster/SKILL.md  制作规范
tools/                       ensure_ff.sh、node 场景的字体/ffmpeg 查找、旧场景重建脚本
MEMORY.md                    经验、坑、用户偏好
```

五部成片均以普通 Git 文件保存在各自的 `examples/<name>/` 目录中（每个文件都小于 100 MB，不使用 Git LFS）。渲染过程中产生的临时 mp4 仍由 `.gitignore` 忽略。

## 成片一览

| 样例 | 成片文件 | 时长 | 简介 |
|---|---|---:|---|
| 浓差电池 | [`concentration_cell_nernst.mp4`](examples/concentration_cell/concentration_cell_nernst.mp4) | 约 62 秒 | 用铜电极浓差电池讲解能斯特方程；0.059 V 明确标为理想溶液理论模拟值，非实验实测。 |
| 大数定律 | [`law_of_large_numbers.mp4`](examples/law_of_large_numbers/law_of_large_numbers.mp4) | 60.4 秒 | 从硬币试验、频率收敛到切比雪夫界与蒙特卡洛估算。 |
| 波尔共振 | [`bohr_resonance.mp4`](examples/bohr_resonance/bohr_resonance.mp4) | 60.4 秒 | 用数值仿真展示阻尼、受迫振动、共振和相位差。 |
| PINN | [`pinn_explained.mp4`](examples/pinn/pinn_explained.mp4) | 60.4 秒 | 以阻尼振子对比普通神经网络与物理信息神经网络。 |
| 马斯克 | [`musk_3min.mp4`](examples/musk/musk_3min.mp4) | 3:14 | 以 3D 时间线讲述人物经历与相关公司；事实截至 2026-09-30。 |

历史提交仍包含旧演示和压缩包，因此完整克隆会下载较多历史对象。只需要当前代码时可浅克隆：`git clone --depth 1`。

## 安装

Python 3.9+。在仓库根目录：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

中文字体是 Noto Sans CJK。Debian/Ubuntu：

```bash
sudo apt install fonts-noto-cjk
```

没有系统包时，把字体目录指给 `BB_FONT_DIR`。目录里要有下面任一命名：

- `NotoSansCJK-Bold.ttc` 和 `NotoSansCJK-Regular.ttc`
- `NotoSansCJKsc-Bold.otf` 和 `NotoSansCJKsc-Regular.otf`

也可以分别设置 `BB_FONT_BOLD`、`BB_FONT_REGULAR`。

ffmpeg 不必单独安装。`bb` 会用 PATH 里的 ffmpeg，或 `imageio-ffmpeg` 自带的二进制。也可以设置 `BB_FFMPEG`。

四个旧 node 场景还需要：

```bash
npm install
```

依赖是 `@napi-rs/canvas`。想把 ffmpeg 放进当前 shell 的 PATH，可以 `source tools/ensure_ff.sh`（必须 source，不要直接执行）。

## 快速上手

在仓库根目录、已激活虚拟环境时：

```bash
python3 -m bb still examples/musk/film.py 30
python3 -m bb qc examples/musk/film.py
python3 examples/concentration_cell/score.py
```

- `still` 把指定秒的静帧写到当前目录，文件名带时间后缀，避免读图缓存。
- `qc` 不传成片时，只检查字形、字幕和文字出画/重叠，不检查响度。
- `score.py` 把混音写到该样例目录的 `mix.wav`（已在 `.gitignore` 里）。

其他命令：

```bash
python3 -m bb render examples/musk/film.py out.mp4 --jobs 2
python3 -m bb remux video.mp4 mix.wav
python3 -m bb qc examples/musk/film.py out.mp4
```

`render` 和带成片的 `qc` 会比较慢。这台机器按 2 核估算，马斯克整片大约几分钟，不是几秒。

## 重建每部片

旁白已经在 `examples/<name>/narration/`，成片也保存在对应样例目录并入库。重新渲染产生的临时 mp4 由 `.gitignore` 忽略。

| 样例 | 成片文件名 | 命令 | 说明 |
|---|---|---|---|
| musk | `musk_3min.mp4` | `bash examples/musk/build.sh` | Python 3D。渲染、混音、封装、质检 |
| concentration_cell | `concentration_cell_nernst.mp4` | `bash examples/concentration_cell/build.sh` | node 场景，需要 `npm install` |
| law_of_large_numbers | `law_of_large_numbers.mp4` | `bash examples/law_of_large_numbers/build.sh` | 同上 |
| bohr_resonance | `bohr_resonance.mp4` | `bash examples/bohr_resonance/build.sh` | 同上 |
| pinn | `pinn_explained.mp4` | `bash examples/pinn/build.sh` | 同上。画面读 `train_data.json`，不必重训 |

只换音轨、不重渲画面：

```bash
python3 examples/<name>/score.py
python3 -m bb remux 成片.mp4 examples/<name>/mix.wav
```

旧的 `music.js`、`scorelib.py`、`remux.sh` 已删除。配乐用 `bb.score`，换音轨用 `python3 -m bb remux`。

## 新片

按 [`skills/blockbuster/SKILL.md`](skills/blockbuster/SKILL.md)。要点：标准普通话，只用 voice-01；旁白里不要写希腊字母符号；必须有真正的 3D 场景和逐句字幕；配乐跟画面走。这个仓库不包含 TTS，新旁白要在外面用 voice-01 生成后再放进 `narration/`。

交付前 `python3 -m bb qc` 必须是 0 问题，并且要看接触单和关键帧。qc 查的是字形、版面、字幕时长和（有成片时）响度，不代替看图。
