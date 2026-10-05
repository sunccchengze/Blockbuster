python3 -c "import imageio_ffmpeg" 2>/dev/null || pip install -q imageio-ffmpeg 2>/dev/null
python3 -c "import scipy" 2>/dev/null || pip install -q scipy 2>/dev/null
mkdir -p ~/bin; ln -sf $(python3 -c "import imageio_ffmpeg as i;print(i.get_ffmpeg_exe())") ~/bin/ffmpeg
export PATH=~/bin:$PATH
