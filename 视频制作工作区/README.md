# 工作区总览（2026-09-30）

## 成片（2026-10-01 起工作区不再存放 mp4）
| 视频 | 文件 | 时长 |
|---|---|---|
| 浓差电池与能斯特方程 | concentration_cell/concentration_cell_nernst.mp4 | 60.4s |
| 大数定律 | law_of_large_numbers/law_of_large_numbers.mp4 | 60.4s |
| 波尔共振实验 | bohr_resonance/bohr_resonance.mp4 | 60.4s |
| PINN 一分钟讲明白 | pinn/pinn_explained.mp4 | 60.4s |
| 三分钟了解马斯克（3D，信息截至 2026-09-30） | musk/musk_3min.mp4 | 3:14 |
**工作区里的成片已删除，为后续制作腾空间。**恢复成片（5 个 mp4 都在 GitHub 提交 08b26af 的 `.zip` 里，已核对 md5 与原文件一致）：
```bash
git clone --filter=blob:none --no-checkout https://github.com/sunccchengze/Blockbuster.git bbtmp && cd bbtmp
git show 08b26af:.zip > ws.zip && unzip ws.zip '*.mp4'
```

每个项目目录里有 README（内容、分镜、重建方法）和旁白 narration/*.flac。

## 代码
- Blockbuster/ — 重构后的工具仓库（bb/ 引擎 + examples/ 5 部片代码 + skills/blockbuster/SKILL.md 制作规范 + MEMORY.md）。
- scorelib.py — 配乐引擎兼容层（转到 Blockbuster/bb/score.py）；remux.sh — 换音轨并对齐 −14 LUFS；ensure_ff.sh — 自动安装/链接 ffmpeg。
- memory.md — 工作记忆：用户要求、环境坑、项目状态。

## 仓库状态
- Blockbuster 已整理并合并进 GitHub main（PR #2、#3）。本地 Blockbuster/ 是旧副本，以远端 main 为准。
- 成片不放 Release（用户决定），留在仓库历史提交 08b26af 的 `.zip` 里。待办：仓库 README 里关于 Release 的说明需要同步修改（需要推送权限）。

## 依赖（重建用）
Python 3：numpy pillow scipy fonttools imageio-ffmpeg；字体 Noto Sans CJK；旧版 node 场景需在 Blockbuster/ 下 `npm install`。
