# memory.md — 工作区记忆（更新：2026-09-30）

## 用户长期要求（务必遵守）
- 配音：标准普通话，只用 **voice-01**（battle-00 的两个声音已被否决）。
- 希腊字母不要直接写进旁白：μ 读英文 "miu"，ε 读 "epsilon"，其他字母同理读英文名。
- 配乐：不要持续的嗡鸣或单音垫底，不要刺耳的转场音效。**要跟着画面变化**，要有弦乐等多种乐器和氛围音效。现在的 scorelib 系统用户"很满意"。
- 画面：要有真正的 3D 动画和技术含量，不能只是图片轮播；**必须有逐句字幕**。
- 时效性题材要先搜索最新信息。
- 需求不清楚时，先用选择题问清楚。
- 用户操作后要主动重试，不要停着等；不要擅自把仓库设为公开。
- 工作区容量紧张：中间文件及时删，旁白存 FLAC。

## 环境注意
- 每次开工先运行 `source ~/ensure_ff.sh`（对话之间 `~/bin/ffmpeg` 和 pip 包会丢失；脚本会重装 imageio-ffmpeg/scipy 并建立 ffmpeg 链接）。没有 ffprobe，时长用 `ffmpeg -i` 查看。
- 机器配置：2 核、约 1GB 内存。长视频用两个进程分段渲染后再 concat。
- `read_file` 读同名图片可能返回缓存，检查新截图时换一个文件名。
- ~/Blockbuster 是用户的仓库（node 管线，提供 @napi-rs/canvas）。前 4 个项目的 scene.js 依赖它：需要时 `npm install`；不要删改。
- 已删除 Blockbuster/video/（早期流水线自动生成的演示片，用户认为粗糙无用）。注意：`npm test` 引用了其中的 code3d-v3-score.wav，已无法运行；需要时 `git checkout -- video` 可恢复。

## Blockbuster 仓库（已交给我维护，2026-09-30 重构）
- 新结构：`bb/`（render3d / assets / timeline / score / media / qc）+ `examples/`（5 部片的代码）+ `skills/blockbuster/SKILL.md`（制作规范）+ `MEMORY.md`。
- 命令：`PYTHONPATH=~/Blockbuster python3 -m bb still|render|qc|remux ...`
- 新片流程见 SKILL.md；交付前必须 `bb qc` 为 0 问题，并亲自看接触单。
- 只在本地提交，推送前先问用户。
- 2026-10-01 状态：仓库已由新 agent 整理并合并进 main（PR #2、#3）。根目录是 bb/ examples/ skills/ tools/；旁白已入库；写死的路径已修复；成片不入 git。
  - 成片**不放 Release**（用户决定）。5 个 mp4 存在仓库提交 08b26af 的 `.zip` 里（已核对 md5 一致），工作区里的 mp4 已删除，恢复方法见 ~/README.md。仓库 README 里关于 Release 的那段说明需要同步修改（等有推送权限时做）。
  - 旧分支 arena/01a0f07e-blockbuster、arena/01a0f5cf-blockbuster 还在。旧的 bundle 已作废并删除。
  - 本地 ~/Blockbuster 是旧副本，以远端 main 为准；修改仓库时在 /tmp 拉取，不要在 ~ 下保留 git 历史。

## 共享工具
- `~/scorelib.py`：兼容层，实际代码在 ~/Blockbuster/bb/score.py。配乐引擎（48 kHz）。
  - 乐器：strings、cello_stac、piano、pluck、bell、timpani、kick、snare、hat。
  - 音效：rumble、whoosh、riser、boom、ping、clink、blip、alarm、city、heartbeat、bubbles、zap、tick、chalk、beep、rattle、thud、creak、glitch、shutter。
  - 函数：`buses(T)`、`add(bus, t, sig, pan, g)`、`chord_strings`、`prog`、`read_audio`（读 FLAC）、`load_voice`、`finish()`（混响 + 人声闪避 + 输出 mix.wav）。
- `~/remux.sh <视频.mp4> mix.wav`：保留画面，替换音轨，响度对齐 −14 LUFS。
- `~/ensure_ff.sh`：环境自检。

## 项目
| 目录 | 成片 | 说明 |
|---|---|---|
| concentration_cell/ | concentration_cell_nernst.mp4（60.4s） | 浓差电池与能斯特方程；scene.js（node），score.py；代码副本也在 Blockbuster/examples/ |
| law_of_large_numbers/ | law_of_large_numbers.mp4（60.4s） | 大数定律；同上 |
| bohr_resonance/ | bohr_resonance.mp4（60.4s） | 波尔共振，RK4 仿真；同上 |
| pinn/ | pinn_explained.mp4（60.4s） | PINN，train.py 做了真实训练，结果在 train_data.json；RMSE：普通网络 0.57、PINN 0.004；反推 μ = 4.20 |
| musk/ | musk_3min.mp4（3:14） | 马斯克传记；代码在 ~/Blockbuster/examples/musk/，本目录只放成片和旁白 |

- 前 4 个项目的配乐已用 score.py 重制，最新音轨已封装进 mp4。旧的 music.js 已删除，**build.sh 里调用 music.js 的配乐步骤已失效**：
  - 只换音轨：`python3 score.py && bash ~/remux.sh X.mp4 mix.wav`
  - 需要重渲染画面：先用 scene.js 渲染，再 remux。
- 马斯克项目重建：`bash ~/Blockbuster/examples/musk/build.sh`
- 所有旁白都在各项目的 `narration/s*.flac`，脚本读 FLAC（build.sh 已改为 .flac）。

## 马斯克事实要点（2026-09 搜索所得）
- 9/28 星舰 Flight 14 首次入轨，部署 26 颗 Starlink V3；星链在轨约 11,119 颗。
- SpaceX 2026 年 6 月上市，是史上最大 IPO，估值约 2 万亿美元；6/12 福布斯称马斯克成为首位万亿富翁。
- 2026 年 2 月 SpaceX 收购 xAI（X 此前已并入 xAI）。
- 2025 年 11 月特斯拉股东通过约 1 万亿美元的薪酬方案。
- 2026 年 9 月 Cybercab 在奥斯汀开始载客，共 45 辆。
- 2026 年 5 月诉 OpenAI 案被陪审团驳回，马斯克将上诉。
- 9/29 白宫 AI 协议签署，马斯克坐在特朗普身旁。
- 纪录片《Musk》（导演 Gibney）在威尼斯首映，美国 10/9 上映，马斯克称其为"抹黑"。
