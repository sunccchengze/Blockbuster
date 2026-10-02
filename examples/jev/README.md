# jev 讲解片（任务 10）

> 2026-10-02 从工作区备份恢复。本页的来源、数字与响度是原项目记录，本次未重新核查事实、重渲整片或试听；不要当作最新报道。

成片：jev.mp4（1280×720，-14 LUFS，内嵌字幕，3D 动画）。信息截至 2026-10-01。
重建（仓库根目录）：`bash examples/jev/build.sh`。
原始 take 录音不在备份中；重复的 take 文稿可从 `script.py` 生成；旁白实际为 `narration/s1–8.opus`，另有 `timing.json`。
文件：script.py（逐句稿）· film.py（8 段 3D 场景）· score.py（提示表配乐）。公共件：`bb/explain.py`、`bb/explain_score.py`、`tools/split_takes.py`。
来源：aiwiki.ai/wiki/jev、firecrawl.dev/blog/what-is-jev、TypeSafe 文档（jaggedness 1.13）、The Register、Forbes。评测数据为官方自测。
