# MEMORY

更新日期：2026-10-01。这是仓库里的经验记录，不是宣传。

## 这个仓库现在是什么

内容优先的代码驱动视频工具箱：`bb/` 引擎、`examples/` 五部样例、`skills/blockbuster/SKILL.md` 制作规范。

旧的“通用 prompt→video”流水线（`src/`、`scripts/`、`code3d-demo/`、`video/`、DEVLOG、HANDOFF，以及“一句话 12 秒出片”的说法）已从当前树删除。原因：按关键词套模板，主题共用粒子场景，没有旁白和真实内容，质检只看技术参数。不要恢复。

删除只发生在新提交里。历史里仍有这些大文件和 `浓差电池.zip`、工作区 `.zip`。不要为了清历史而 force push，除非用户明确改口。

## 用户硬性要求

完整版在 SKILL.md 第 0 节。

- 新片旁白默认标准普通话、voice-01；浓差电池本次修订是明确例外，仅 s5/s6 使用用户第一次试听所选 voice-00。原 s1–s4 男声保留；不要把现有 FLAC 描述成可克隆原声的模型。
- 旁白里不要写希腊字母符号。μ 读作 “miu”，ε 读作 “epsilon”，其他字母读英文名。
- 画面必须有真正的 3D 场景和逐句字幕，不能只是图片轮播或模板粒子。
- 配乐要随画面事件变化，要有弦乐等多种乐器和氛围音效。禁止持续嗡鸣或单音垫底，禁止刺耳的转场音效。
- 时效性题材必须先搜索，事实截止到当天，并记录来源。
- 需求有歧义时先用选择题问。
- 外部资源首次访问失败后，如果用户确认权限或资源状态已改变，应主动重试并核对结果，不要把此前的错误当成最终状态。
- 不要擅自改仓库公开/私有。不要 force push，不要改写已有历史。
- 交付前 `bb qc` 为 0 问题，并且要看接触单和关键帧。没法试听就如实说，不要夸大。

## 样例

旁白在 `examples/<name>/narration/*.flac`，入库；五部交付成片也放在各自样例目录并入库，临时渲染 mp4 忽略。历史 Release `films-2026-09-30` 曾为空；不要再把它当作成片的交付位置。原始成片曾归档在提交 `08b26af` 的 `.zip` 里。

| 样例 | 时长 | 重建 |
|---|---|---|
| musk | 3:14 | `bash examples/musk/build.sh` |
| concentration_cell | 62s（修订版） | `bash examples/concentration_cell/build.sh` |
| law_of_large_numbers | 60.4s | `bash examples/law_of_large_numbers/build.sh` |
| bohr_resonance | 60.4s | `bash examples/bohr_resonance/build.sh` |
| pinn | 60.4s | `bash examples/pinn/build.sh` |

前四部理科片的画面仍是 node `scene.js`，配乐已改成 `score.py`。`music.js` 已不存在，不要在 build 里调用它。PINN 的曲线来自真实训练，结果在 `examples/pinn/train_data.json`：普通网络 RMSE 0.57，PINN 0.004，反推 μ = 4.20。渲染不需要 PyTorch。

浓差电池制作时确认过：观众是大学物理化学；写实实验室；公式同时给出 ln 和 lg，并写明 2.303RT/F = 0.0592 V；负极导线绿色，正极红色。旁白 s4 按自然对数来念；若改成 lg，要重录并重新计时。新版明确区分浓度比与浓度差：理想溶液近似下，浓度比决定理论电压；初始浓度差关联可释放电量。0.059 V 是动画模拟的理想理论值，不是实测开路电压；不要未经可靠资料核验就宣称 CuSO₄ 活度系数或真实电压。经验原文在 `examples/concentration_cell/LESSONS.md`。

## 环境

- 依赖见 `requirements.txt`。Debian 的系统 Python 可能拒绝直接 pip，用仓库根的 `.venv`。
- 字体：`fonts-noto-cjk`，或 `BB_FONT_DIR`。Noto CJK 缺 `✕ ⚠ ₃ ⁺ ⁻` 等字形（`✓` 和 `²` 有）。`bb qc` 会报。
- ffmpeg：PATH、`BB_FFMPEG`，或 imageio-ffmpeg。不要再链到 `~/bin`。
- 旧版 ffmpeg 不要用单遍 loudnorm。`bb remux` 用固定增益加 `alimiter`（限幅 0.8，给 AAC 过冲留余量）。
- 画家算法：地面、道路、湖面必须 `f.layer()` 先画，否则会盖住建筑。
- 长片用 `--jobs 2`。不要在内存里缓存整片帧。
- 读图工具可能缓存同名图片。`bb still` 的文件名带后缀。

## 马斯克片用过的事实（截至 2026-09-30）

下次做时效题材必须重新搜索。下面不是“最新事实”，只是这部片当时用过的要点：

- 2026-09-28 星舰 Flight 14 首次入轨，部署 26 颗 Starlink V3；星链在轨约 11,119 颗。
- SpaceX 2026 年 6 月上市，估值约 2 万亿美元；2026-06-12 福布斯称马斯克成为首位万亿富翁。
- 2026 年 2 月 SpaceX 收购 xAI（X 此前已并入 xAI）。
- 2025 年 11 月特斯拉股东通过约 1 万亿美元薪酬方案。
- 2026 年 9 月 Cybercab 在奥斯汀开始载客，共 45 辆。
- 2026 年 5 月诉 OpenAI 案被陪审团驳回，马斯克将上诉。
- 2026-09-29 白宫 AI 协议签署，马斯克坐在特朗普身旁。
- 纪录片《Musk》（导演 Gibney）威尼斯首映，美国 2026-10-09 上映，马斯克称其为抹黑。

## 2026-10-01 整理时实际跑过

在仓库根目录新建 `.venv`，`pip install -r requirements.txt`。这台环境的 apt 装不上 `fonts-noto-cjk`，所以设置了 `BB_FONT_DIR`，指向 NotoSansCJKsc 的 Regular/Bold OTF。没有试听。

- `python3 -m bb still examples/musk/film.py 30`：约 0.4 秒，写出静帧。看过这一帧：地球、1989 标注和底部字幕都在。
- `python3 -m bb qc examples/musk/film.py`：输出 `QC 通过：无缺字形 / 字幕问题`。这条命令不传成片，所以没有检查响度，也没有接触单。
- `bash examples/concentration_cell/build.sh`：重建 62.0 秒成片（1280×720、24fps、H.264/AAC、48 kHz 双声道）；响度/峰值检查 −14.2 LUFS / −1.7 dBFS，通过 `bb.qc.check_video` 门限。没有人工试听。
- 从重制后 MP4 抽取并看过 46、51.3、58.6、60.4、61.5 秒帧；0.059 V 的理想理论模拟标注和片尾结论可读，放电图阶段的浓度标签不再压住字幕。
- GitHub Release `films-2026-09-30` 当前仍是 0 个附件（已用 `gh release view` 核实）；本次没有改 Release。

## 可改进

- 四个 node 场景还没迁到 `bb.render3d`。
- `assets.py` 还可以加人物剪影、实验器材、图表组件。
- `qc` 还不能比对 `film.py` 事件点和 `score.py` 重音时间。
