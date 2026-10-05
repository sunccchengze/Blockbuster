# 用法: remux.sh 原视频.mp4 mix.wav  —— 保留画面，替换音轨，响度对齐 -14 LUFS
set -e; V=$1; A=$2; source ~/ensure_ff.sh
I=$(ffmpeg -i $A -af ebur128 -f null - 2>&1 | grep " I:" | tail -1 | awk '{print $2}')
G=$(python3 -c "print(-14.0-($I))")
ffmpeg -v error -y -i $V -i $A -map 0:v -map 1:a -c:v copy -af "volume=${G}dB,alimiter=limit=0.8:level=false" -c:a aac -b:a 192k -shortest tmp_remux.mp4
mv tmp_remux.mp4 $V
ffmpeg -i $V -af ebur128=peak=true -f null - 2>&1 | grep -E " I:|Peak:" | tail -2
