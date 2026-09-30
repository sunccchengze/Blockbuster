/**
 * @file app.js
 * @description Blockbuster Studio 前端主逻辑：
 * 1. 影院级视口播控、逐帧步进与高精度时间码；
 * 2. 9 个视听叙事 Beat 可视化时间轴与瞬态对齐；
 * 3. 实时纯函数 Canvas 模拟器；
 * 4. SSE 日志推流、API 交互与质检图像大图审查。
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM 元素引用
  const video = document.getElementById("main-video");
  const videoContainer = document.getElementById("video-container");
  const canvasContainer = document.getElementById("canvas-container");
  const interactiveCanvas = document.getElementById("interactive-canvas");
  const canvasCtx = interactiveCanvas.getContext("2d");

  const btnPlayPause = document.getElementById("btn-play-pause");
  const btnStepBack = document.getElementById("btn-step-back");
  const btnStepForward = document.getElementById("btn-step-forward");
  const btnLoop = document.getElementById("btn-loop");
  const seekSlider = document.getElementById("seek-slider");
  const playbackSpeed = document.getElementById("playback-speed");
  const timecodeDisplay = document.getElementById("timecode-display");
  const canvasTimecode = document.getElementById("canvas-timecode");
  const frameCounter = document.getElementById("frame-counter");
  const viewportBadge = document.getElementById("viewport-badge");
  const beatsTrack = document.getElementById("beats-track");

  const tabButtons = document.querySelectorAll(".tab-btn");
  const terminalLogs = document.getElementById("terminal-logs");
  const btnClearLogs = document.getElementById("btn-clear-logs");
  const btnRunRender = document.getElementById("btn-run-render");
  const btnRecomposeAudio = document.getElementById("btn-recompose-audio");

  const imageModal = document.getElementById("image-modal");
  const modalImg = document.getElementById("modal-img");
  const modalTitle = document.getElementById("modal-title");
  const modalClose = document.getElementById("modal-close");
  const cardContactSheet = document.getElementById("card-contact-sheet");
  const cardSpectrogram = document.getElementById("card-spectrogram");
  const artifactsList = document.getElementById("artifacts-list");

  let isInteractiveMode = false;
  let interactiveT = 0;
  let interactiveAnimId = null;
  let isInteractivePlaying = false;
  let totalDuration = 10.0;
  const fps = 24;

  // 格式化时间戳 00:00:SS.mmm
  function formatTime(sec) {
    const s = Math.max(0, sec);
    const mins = Math.floor(s / 60);
    const secs = Math.floor(s % 60);
    const ms = Math.floor((s - Math.floor(s)) * 1000);
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
  }

  // 更新时间码与帧计数
  function updateTimeDisplay(currentTime, dur) {
    dur = dur || totalDuration || 10.0;
    const curFrame = Math.floor(currentTime * fps);
    const totalFrames = Math.round(dur * fps);

    timecodeDisplay.textContent = `${formatTime(currentTime)} / ${formatTime(dur)}`;
    frameCounter.textContent = `FRAME ${String(curFrame).padStart(3, "0")} / ${totalFrames}`;
    seekSlider.value = currentTime;
    seekSlider.max = dur;
  }

  // 1. 播放器事件绑定
  video.addEventListener("timeupdate", () => {
    if (!isInteractiveMode) {
      updateTimeDisplay(video.currentTime, video.duration);
    }
  });

  video.addEventListener("play", () => {
    btnPlayPause.textContent = "⏸ 暂停";
    btnPlayPause.classList.add("playing");
  });

  video.addEventListener("pause", () => {
    btnPlayPause.textContent = "▶ 播放";
    btnPlayPause.classList.remove("playing");
  });

  btnPlayPause.addEventListener("click", () => {
    if (isInteractiveMode) {
      isInteractivePlaying = !isInteractivePlaying;
      btnPlayPause.textContent = isInteractivePlaying ? "⏸ 暂停" : "▶ 播放";
      if (isInteractivePlaying) runInteractiveLoop();
    } else {
      if (video.paused) {
        video.play();
      } else {
        video.pause();
      }
    }
  });

  btnStepBack.addEventListener("click", () => {
    if (isInteractiveMode) {
      interactiveT = Math.max(0, interactiveT - 1 / fps);
      renderInteractiveFrame(interactiveT);
    } else {
      video.pause();
      video.currentTime = Math.max(0, video.currentTime - 1 / fps);
    }
  });

  btnStepForward.addEventListener("click", () => {
    if (isInteractiveMode) {
      interactiveT = Math.min(totalDuration, interactiveT + 1 / fps);
      renderInteractiveFrame(interactiveT);
    } else {
      video.pause();
      video.currentTime = Math.min(video.duration, video.currentTime + 1 / fps);
    }
  });

  btnLoop.addEventListener("click", () => {
    video.loop = !video.loop;
    btnLoop.classList.toggle("active", video.loop);
  });

  seekSlider.addEventListener("input", (e) => {
    const val = parseFloat(e.target.value);
    if (isInteractiveMode) {
      interactiveT = val;
      renderInteractiveFrame(interactiveT);
    } else {
      video.currentTime = val;
      updateTimeDisplay(val, video.duration);
    }
  });

  playbackSpeed.addEventListener("change", (e) => {
    video.playbackRate = parseFloat(e.target.value);
  });

  // 2. Tab 切换版本与模式
  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const mode = btn.dataset.type;
      const title = btn.dataset.title;

      if (mode === "interactive") {
        isInteractiveMode = true;
        video.pause();
        videoContainer.classList.add("hidden");
        canvasContainer.classList.remove("hidden");
        viewportBadge.textContent = "LIVE SEEK(t) EVALUATION · 纯函数逐帧即时求值";
        renderInteractiveFrame(interactiveT);
      } else {
        isInteractiveMode = false;
        canvasContainer.classList.add("hidden");
        videoContainer.classList.remove("hidden");
        viewportBadge.textContent = title;

        const src = btn.dataset.video;
        if (video.src !== window.location.origin + src) {
          video.src = src;
          video.load();
        }
      }
    });
  });

  // 3. 交互式 Canvas 纯函数渲染模拟器 (实时求解水墨与粒子)
  function renderInteractiveFrame(t) {
    const w = interactiveCanvas.width;
    const h = interactiveCanvas.height;

    // 宣纸暖米底色
    const grad = canvasCtx.createRadialGradient(w / 2, h / 2, 80, w / 2, h / 2, 650);
    grad.addColorStop(0, "#f8f5ee");
    grad.addColorStop(0.7, "#efe8d8");
    grad.addColorStop(1, "#dfd4c0");
    canvasCtx.fillStyle = grad;
    canvasCtx.fillRect(0, 0, w, h);

    // 绘制水墨动态求值
    if (t < 1.4) {
      const dropP = Math.min(1.0, t / 1.15);
      const easeY = dropP * dropP * dropP;
      const y = -40 + easeY * (h / 2 + 40);
      canvasCtx.fillStyle = "#121214";
      canvasCtx.beginPath();
      canvasCtx.ellipse(w / 2, y, 7, 12, 0, 0, Math.PI * 2);
      canvasCtx.fill();
    }

    if (t >= 1.2 && t < 3.2) {
      const burstT = t - 1.2;
      const p = 1 - Math.exp(-burstT * 4);
      canvasCtx.fillStyle = "#101114";
      canvasCtx.beginPath();
      canvasCtx.arc(w / 2, h / 2, 26 + p * 40, 0, Math.PI * 2);
      canvasCtx.fill();
    }

    if (t >= 2.4 && t < 5.2) {
      canvasCtx.strokeStyle = "#16171a";
      canvasCtx.lineWidth = 18;
      canvasCtx.lineCap = "round";
      canvasCtx.beginPath();
      canvasCtx.moveTo(w * 0.2, h * 0.75);
      canvasCtx.bezierCurveTo(w * 0.35, h * 0.2, w * 0.65, h * 0.8, w * 0.8, h * 0.35);
      canvasCtx.stroke();
    }

    if (t >= 6.0) {
      canvasCtx.fillStyle = "rgba(40, 44, 52, 0.45)";
      canvasCtx.beginPath();
      canvasCtx.moveTo(80, h * 0.78);
      canvasCtx.quadraticCurveTo(w * 0.35, h * 0.42, w * 0.68, h * 0.72);
      canvasCtx.quadraticCurveTo(w * 0.85, h * 0.58, w - 80, h * 0.75);
      canvasCtx.lineTo(w - 80, h);
      canvasCtx.lineTo(80, h);
      canvasCtx.fill();

      if (t >= 6.5) {
        canvasCtx.fillStyle = "#121214";
        canvasCtx.font = "900 84px serif";
        canvasCtx.textAlign = "center";
        canvasCtx.fillText("墨", w / 2, h * 0.44);
      }
    }

    if (t >= 8.2) {
      canvasCtx.fillStyle = "#af261e";
      canvasCtx.fillRect(w / 2 + 90, h * 0.38, 54, 54);
      canvasCtx.strokeStyle = "#efe8d8";
      canvasCtx.lineWidth = 2.5;
      canvasCtx.strokeRect(w / 2 + 95, h * 0.38 + 5, 44, 44);
    }

    // 宽银幕遮幅
    canvasCtx.fillStyle = "#0c0d10";
    canvasCtx.fillRect(0, 0, w, 50);
    canvasCtx.fillRect(0, h - 50, w, 50);

    canvasCtx.fillStyle = "rgba(220, 200, 160, 0.6)";
    canvasCtx.font = "12px monospace";
    canvasCtx.textAlign = "left";
    canvasCtx.fillText("BLOCKBUSTER LIVE CANVAS // SEEK(t) PURE EVALUATION", 50, 32);

    canvasTimecode.textContent = `T = ${t.toFixed(3)}s / 10.000s (Frame ${Math.floor(t * fps)}/240)`;
    updateTimeDisplay(t, 10.0);
  }

  function runInteractiveLoop() {
    if (!isInteractivePlaying || !isInteractiveMode) return;
    interactiveT += 1 / fps;
    if (interactiveT > totalDuration) interactiveT = 0;
    renderInteractiveFrame(interactiveT);
    interactiveAnimId = requestAnimationFrame(runInteractiveLoop);
  }

  // 4. 加载 9 个叙事 Beat 清单并渲染时间轴
  const beatColors = [
    "#3b82f6", "#06b6d4", "#10b981", "#84cc16",
    "#eab308", "#f97316", "#ef4444", "#d946ef", "#8b5cf6"
  ];

  async function loadBeats() {
    try {
      const res = await fetch("/api/beats");
      const beats = await res.json();
      beatsTrack.innerHTML = "";

      beats.forEach((beat, idx) => {
        const beatDur = beat.end - beat.start;
        const widthPercent = (beatDur / totalDuration) * 100;
        const block = document.createElement("div");
        block.className = "beat-block";
        block.style.width = `${widthPercent}%`;
        block.style.backgroundColor = `${beatColors[idx % beatColors.length]}22`;
        block.style.borderTop = `3px solid ${beatColors[idx % beatColors.length]}`;

        block.innerHTML = `
          <span class="beat-num">BEAT ${beat.id}</span>
          <span class="beat-label">${beat.name.split(" ")[0]}</span>
          <span class="beat-time">${beat.start.toFixed(1)}s</span>
        `;

        block.title = `${beat.name} (${beat.start.toFixed(2)}s ~ ${beat.end.toFixed(2)}s)`;

        block.addEventListener("click", () => {
          if (isInteractiveMode) {
            interactiveT = beat.start;
            renderInteractiveFrame(interactiveT);
          } else {
            video.currentTime = beat.start;
            video.play();
          }
        });

        beatsTrack.appendChild(block);
      });
    } catch (err) {
      console.error("加载 Beat 清单失败:", err);
    }
  }

  // 5. 加载资产清单列表
  async function loadArtifacts() {
    try {
      const res = await fetch("/api/artifacts");
      const list = await res.json();
      artifactsList.innerHTML = "";

      list.forEach((item) => {
        const row = document.createElement("div");
        row.className = "artifact-item";
        row.innerHTML = `
          <div class="artifact-info">
            <span class="artifact-title">${item.name}</span>
            <span class="artifact-sub">${item.filename} · ${item.sizeFormatted || "就绪"}</span>
          </div>
          <a href="${item.path}" download="${item.filename}" class="artifact-btn">下载</a>
        `;
        artifactsList.appendChild(row);
      });
    } catch (err) {
      console.error("加载资产清单失败:", err);
    }
  }

  // 6. 模态框大图核验
  cardContactSheet.addEventListener("click", () => {
    modalTitle.textContent = "9 叙事 Beat 九宫格接触印相质检单 (来自编码后 code3d-v3.mp4)";
    modalImg.src = "/video/contact-sheet-v3.png?" + Date.now();
    imageModal.classList.remove("hidden");
  });

  cardSpectrogram.addEventListener("click", () => {
    modalTitle.textContent = "v3.1 物理建模配乐声学频谱瀑布图 (True Physical String Acoustics)";
    modalImg.src = "/video/score-spectrogram.png?" + Date.now();
    imageModal.classList.remove("hidden");
  });

  modalClose.addEventListener("click", () => imageModal.classList.add("hidden"));
  document.querySelector(".modal-backdrop").addEventListener("click", () => imageModal.classList.add("hidden"));

  // 7. 实时日志推流 (Server-Sent Events)
  function setupSSE() {
    const es = new EventSource("/api/logs");
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        const line = document.createElement("div");
        line.className = "log-line";
        line.textContent = `[${data.time}] ${data.text}`;
        terminalLogs.appendChild(line);
        terminalLogs.scrollTop = terminalLogs.scrollHeight;
      } catch (err) {}
    };
  }

  btnClearLogs.addEventListener("click", () => {
    terminalLogs.innerHTML = "";
  });

  // 8. 触发重新渲染流水线
  btnRunRender.addEventListener("click", async () => {
    if (!confirm("确定要启动全量流水线渲染吗？将重新计算 V1、V2、v3.1 配乐、V3 成片并执行 MP4 抽帧质检。")) return;
    try {
      const res = await fetch("/api/render", { method: "POST" });
      const data = await res.json();
      alert(data.message || "渲染已在后台启动，请关注左侧日志窗口");
    } catch (err) {
      alert("触发失败: " + err.message);
    }
  });

  btnRecomposeAudio.addEventListener("click", async () => {
    try {
      const res = await fetch("/api/audio", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        alert("物理建模配乐重算成功！6 项客观门禁全部合格！");
        loadArtifacts();
      }
    } catch (err) {
      alert("音频重算失败: " + err.message);
    }
  });

  // 初始化
  loadBeats();
  loadArtifacts();
  setupSSE();
});
