#!/usr/bin/env python3
"""audio3.py — score for the V3 ink film ("墨").

Thin wrapper kept for provenance/reproducibility of video/code3d-v3.mp4.
The engine lives in skills/blockbuster/scripts/{guqin,score}.py (physical plucked-string model);
this file only pins the exact arrangement used for the delivered cut.
"""
import pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
SCORE = HERE / "skills" / "blockbuster" / "scripts" / "score.py"
PINNED = ["--dur=10", "--anchors=drop=1.0,impact=1.9,stamp=8.0",
          "--arrange=ink", "--instrument=mix"]

if __name__ == "__main__":
    args = sys.argv[1:] or ["out/audio3.wav"]
    extra = [] if any(a.startswith(("--anchors", "--dur", "--arrange", "--instrument")) for a in args) else PINNED
    cmd = [sys.executable, str(SCORE), *args, *extra]
    raise SystemExit(subprocess.call(cmd))
