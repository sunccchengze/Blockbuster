# Blockbuster — 内容优先的代码驱动视频工具箱

> 旧版"输入一句话、12 秒出片"的通用流水线已**废弃**：它按关键词套 5 套配色，所有主题共用同一个粒子场景，
> 没有旁白、字幕和真实内容，质检只测响度和分辨率，所以只能产出好看但空洞、没有信息量的画面。
>
> 新版思路：**不存在能通吃所有主题的模板。** 由 Agent 按流程做：研究 → 脚本 → 配音 → 为这个主题专门写 3D 场景 → 按场景写配乐 → 看图质检。
> 仓库提供可复用的零件（渲染引擎、模型、配乐引擎、质检工具）和制作规范（[`skills/blockbuster/SKILL.md`](skills/blockbuster/SKILL.md)）。

## 目录
```
bb/                       Python 工具包
  render3d.py             3D 引擎：透视相机/轨道运镜、网格(旋转体/方块/球/合并)、平面光照+边缘光、
                          画家算法分层、粒子、地球+经纬网+遮挡、3D 标签(自动收进画面+防碰撞)、逐句字幕、章节进度
  assets.py               可复用低多边形模型（星舰、猎鹰、汽车…），按需扩充
  timeline.py             以实测旁白时长生成时间线、逐句字幕切分
  score.py                配乐引擎：弦乐群/钢琴/大提琴断奏/拨弦/钟琴/定音鼓/鼓组 + 20 余种同步音效 + 混响 + 人声闪避
  media.py                ffmpeg 自举、多进程并行渲染、换音轨 + −14 LUFS 对齐、接触单
  qc.py                   内容质检：缺字形、文字出画/重叠、字幕长度/字速、响度/峰值、抽样静帧
examples/
  musk/                   三分钟人物传记（Python 3D，完整新流程，build.sh 一键重建）
  concentration_cell/ law_of_large_numbers/ bohr_resonance/ pinn/
                          60 秒理科讲解（旧版 node canvas 场景 scene.js + 新版 score.py 配乐）
skills/blockbuster/SKILL.md   制作规范（Agent 必读）
MEMORY.md                 经验、坑和用户偏好
```

## 快速上手
```bash
export PYTHONPATH=~/Blockbuster
python3 -m bb still  examples/musk/film.py 30 112        # 导出任意时刻静帧（文件名带随机后缀，避免读图缓存）
python3 -m bb render examples/musk/film.py out.mp4 --jobs 2
python3 -m bb qc     examples/musk/film.py out.mp4        # 内容质检 + 接触单
python3 -m bb remux  video.mp4 mix.wav                   # 换音轨并对齐 −14 LUFS
bash examples/musk/build.sh                              # 整片：渲染 → 配乐 → 封装 → 质检（约 2.5 分钟，2 核）
```
依赖：`numpy pillow scipy fonttools imageio-ffmpeg`（`bb.media.ffmpeg()` 会自动安装并链接 ffmpeg），字体 Noto Sans CJK。
旧版 node 场景需要 `npm install`（@napi-rs/canvas）。

## 写一部新片
1. 按 SKILL.md 做 brief/研究/脚本 → 分段配音 → 实测时长。
2. 新建 `examples/<name>/film.py`：`from bb.render3d import *`，每段写一个 `scene(lt, dur) -> Fr`，最后 `FILM = Film(starts, durs, scenes, subs, chapters)`。
3. `score.py`：`from bb.score import *` → `buses(T)` → 按场景写配乐和音效 → `finish(...)`。
4. `python3 -m bb qc` 直到 0 问题，再**亲自看**接触单和关键帧。
