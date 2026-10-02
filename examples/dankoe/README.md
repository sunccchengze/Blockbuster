# Dan Koe · 人物讲解（约 3 分 15 秒）

> 2026-10-02 从工作区备份恢复。本页的来源、数字与响度是原项目记录，本次未重新核查事实、重渲整片或试听；不要当作最新报道。

信息截至 2026-10-01。人物为风格化 3D 角色，不使用肖像。收入等数字来自第三方公开报道，片中已注明。

结构（与 Karpathy 片同逻辑：人物 → 领域 → 借鉴）：开场 / 起点 2018 / 核心观点（把自己产品化、反愿景、兴趣广泛）/ 写作系统 / 价值阶梯（Kortex → Eden）/ AI 时代判断 / 三点借鉴。

来源：
- letters.thedankoe.com（2026 年各期信件：AI 与“最后的护城河”、70 亿家公司、学习体验）
- grokipedia.com/page/Dan_Koe（经历、关注者、书、Eden）
- yespress.io/dan-koe（2024 年收入约 410 万美元、利润率约 98%、写作节奏）
- thesaasmaker.com（Kortex 预售约 75.99 万美元、架构问题与重建）
- eden.so/bootcamp（Eden：AI Canvas & Drive）

制作：TTS voice-01，atempo 1.22；film.py（bb render3d）；score.py（bb explain_score）。

## 重建

在仓库根目录：`bash examples/dankoe/build.sh`。旁白为 `narration/s1.opus`–`s7.opus`，原样保留；字幕时间在 `timing.json`，无需重新生成。

共用人物与道具模型在 `bb/figure3d.py`，不再在项目目录各存一份。
