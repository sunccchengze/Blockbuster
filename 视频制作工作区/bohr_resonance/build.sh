#!/usr/bin/env bash
# 一键重建：配乐 → 混音(旁白+闪避配乐) → 渲染画面并封装
set -e
cd "$(dirname "$0")"
BB=../Blockbuster
[ -d $BB/node_modules/@napi-rs ] || (cd $BB && npm install --no-audit --no-fund)
mkdir -p ~/bin
ln -sf $(realpath $BB/node_modules/@ffmpeg-installer/linux-x64/ffmpeg) ~/bin/ffmpeg
ln -sf $(realpath $BB/node_modules/@ffprobe-installer/linux-x64/ffprobe) ~/bin/ffprobe
F=~/bin/ffmpeg
node music.js
N=narration
$F -v error -y -i $N/s1.flac -i $N/s2.flac -i $N/s3.flac -i $N/s4.flac -i $N/s5.flac -i $N/s6.flac -i music.flac -filter_complex \
"[0]adelay=800[a];[1]adelay=9800[b];[2]adelay=21780[c];[3]adelay=31830[d];[4]adelay=41780[e];[5]adelay=50490[f];\
[a][b][c][d][e][f]amix=inputs=6:duration=longest,volume=6,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad,asplit[v][sc];\
[6]volume=1.2,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[mu];\
[mu][sc]sidechaincompress=threshold=0.03:ratio=4:attack=80:release=600[duck];\
[v][duck]amix=inputs=2:duration=shortest,volume=2,volume=-0.7dB,alimiter=limit=0.8:level=false[m]" -map "[m]" -t 60.4 mix.flac
node scene.js video
$F -v error -y -i bohr_resonance.mp4 -vf "select='not(mod(n\,120))',scale=320:-1,tile=4x3" -frames:v 1 contact_sheet.png
rm -f music.flac mix.flac
$F -hide_banner -i bohr_resonance.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
