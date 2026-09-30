/**
 * @file app.js
 * @description Blockbuster Studio 客户端交互逻辑 (Strict Apple Design System)
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM 元素引用
  const video = document.getElementById("main-video");
  const videoWrapper = document.getElementById("video-wrapper");
  const canvasWrapper = document.getElementById("canvas-wrapper");
  const interactiveCanvas = document.getElementById("interactive-canvas");
  const canvasCtx = interactiveCanvas.getContext("2d");

  const btnPlayPause = document.getElementById("btn-play-pause");
  const iconPlay = document.getElementById("icon-play");
  const iconPause = document.getElementById("icon-pause");
  const btnStepBack = document.getElementById("btn-step-back");
  const btnStepForward = document.getElementById("btn-step-forward");
  const btnLoop = document.getElementById("btn-loop");
  const seekSlider = document.getElementById("seek-slider");
  const playbackSpeed = document.getElementById("playback-speed");
  const timecodeDisplay = document.getElementById("timecode-display");
  const frameCounter = document.getElementById("frame-counter");
  const screenBadge = document.getElementById("screen-badge");

  const segButtons = document.querySelectorAll(".seg-btn");
  const beatsGrid = document.getElementById("beats-grid");
  const artifactsList = document.getElementById("artifacts-list");
  const terminalLogs = document.getElementById("terminal-logs");
  const btnClearLogs = document.getElementById("btn-clear-logs");

  const btnNavRender = document.getElementById("nav-btn-render");
  const btnHeroWatch = document.getElementById("btn-hero-watch");
  const btnHeroPipeline = document.getElementById("btn-hero-pipeline");
  const btnRunRenderBottom = document.getElementById("btn-run-render-bottom");
  const btnRecomposeAudio = document.getElementById("btn-recompose-audio");

  const imageModal = document.getElementById("image-modal");
  const modalImg = document.getElementById("modal-img");
  const modalTitle = document.getElementById("modal-title");
  const modalClose = document.getElementById("modal-close");
  const cardContactSheet = document.getElementById("card-contact-sheet");
  const cardSpectrogram = document.getElementById("card-spectrogram");

  let isInteractiveMode = false;
  let interactiveT = 0;
  let isInteractivePlaying = false;
  let animFrameId = null;
  const fps = 24;
  let totalDuration = 10.0;

  function formatTime(sec) {
    const s = Math.max(0, sec);
    const mins = Math.floor(s / 60);
    const secs = Math.floor(s % 60);
    const ms = Math.floor((s - Math.floor(s)) * 1000);
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
  }

  function updateTimeDisplay(curTime, dur) {
    dur = dur || totalDuration || 10.0;
    const curFrame = Math.floor(curTime * fps);
    const totalFrames = Math.round(dur * fps);

    timecodeDisplay.textContent = `${formatTime(curTime)} / ${formatTime(dur)}`;
    frameCounter.textContent = `FRAME ${String(curFrame).padStart(3, "0")} / ${totalFrames}`;
    seekSlider.value = curTime;
    seekSlider.max = dur;
  }

  // 1. 播放器状态同步
  video.addEventListener("timeupdate", () => {
    if (!isInteractiveMode) {
      updateTimeDisplay(video.currentTime, video.duration);
    }
  });

  video.addEventListener("play", () => {
    iconPlay.classList.add("hidden");
    iconPause.classList.remove("hidden");
  });

  video.addEventListener("pause", () => {
    iconPlay.classList.remove("hidden");
    iconPause.classList.add("hidden");
  });

  btnPlayPause.addEventListener("click", () => {
    if (isInteractiveMode) {
      isInteractivePlaying = !isInteractivePlaying;
      if (isInteractivePlaying) {
        iconPlay.classList.add("hidden");
        iconPause.classList.remove("hidden");
        runInteractiveLoop();
      } else {
        iconPlay.classList.remove("hidden");
        iconPause.classList.add("hidden");
        cancelAnimationFrame(animFrameId);
      }
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

  // 2. Sub-Nav Segmented Control
  segButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      segButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const type = btn.dataset.type;
      const badgeText = btn.dataset.badge;

      if (type === "interactive") {
        isInteractiveMode = true;
        video.pause();
        videoWrapper.classList.add("hidden");
        canvasWrapper.classList.remove("hidden");
        screenBadge.textContent = badgeText;
        renderInteractiveFrame(interactiveT);
      } else {
        isInteractiveMode = false;
        canvasWrapper.classList.add("hidden");
        videoWrapper.classList.remove("hidden");
        screenBadge.textContent = badgeText;

        const src = btn.dataset.video;
        if (video.src !== window.location.origin + src) {
          video.src = src;
          video.load();
        }
      }
    });
  });

  btnHeroWatch.addEventListener("click", () => {
    video.play();
  });

  // 3. 交互式纯函数实时 Canvas 渲染模拟器
  function renderInteractiveFrame(t) {
    const w = interactiveCanvas.width;
    const h = interactiveCanvas.height;

    // 宣纸底色
    const grad = canvasCtx.createRadialGradient(w / 2, h / 2, 80, w / 2, h / 2, 650);
    grad.addColorStop(0, "#f8f5ee");
    grad.addColorStop(0.7, "#efe8d8");
    grad.addColorStop(1, "#dfd4c0");
    canvasCtx.fillStyle = grad;
    canvasCtx.fillRect(0, 0, w, h);

    // 墨滴坠落
    if (t < 1.4) {
      const p = Math.min(1.0, t / 1.15);
      const easeY = p * p * p;
      const y = -40 + easeY * (h / 2 + 40);
      canvasCtx.fillStyle = "#121214";
      canvasCtx.beginPath();
      canvasCtx.ellipse(w / 2, y, 7, 12, 0, 0, Math.PI * 2);
      canvasCtx.fill();
    }

    // 破墨扩散
    if (t >= 1.2 && t < 3.2) {
      const burstT = t - 1.2;
      const p = 1 - Math.exp(-burstT * 4);
      canvasCtx.fillStyle = "#101114";
      canvasCtx.beginPath();
      canvasCtx.arc(w / 2, h / 2, 26 + p * 40, 0, Math.PI * 2);
      canvasCtx.fill();
    }

    // 运笔狂草
    if (t >= 2.4 && t < 5.2) {
      canvasCtx.strokeStyle = "#16171a";
      canvasCtx.lineWidth = 18;
      canvasCtx.lineCap = "round";
      canvasCtx.beginPath();
      canvasCtx.moveTo(w * 0.2, h * 0.75);
      canvasCtx.bezierCurveTo(w * 0.35, h * 0.2, w * 0.65, h * 0.8, w * 0.8, h * 0.35);
      canvasCtx.stroke();
    }

    // 远山意象
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

    // 朱砂古印
    if (t >= 8.2) {
      canvasCtx.fillStyle = "#af261e";
      canvasCtx.fillRect(w / 2 + 90, h * 0.38, 54, 54);
      canvasCtx.strokeStyle = "#efe8d8";
      canvasCtx.lineWidth = 2.5;
      canvasCtx.strokeRect(w / 2 + 95, h * 0.38 + 5, 44, 44);
    }

    // 宽银幕黑边
    canvasCtx.fillStyle = "#000000";
    canvasCtx.fillRect(0, 0, w, 50);
    canvasCtx.fillRect(0, h - 50, w, 50);

    updateTimeDisplay(t, 10.0);
  }

  function runInteractiveLoop() {
    if (!isInteractivePlaying || !isInteractiveMode) return;
    interactiveT += 1 / fps;
    if (interactiveT > totalDuration) interactiveT = 0;
    renderInteractiveFrame(interactiveT);
    animFrameId = requestAnimationFrame(runInteractiveLoop);
  }

  // 4. 加载 9 个叙事 Beat 清单并渲染为 Apple Store Utility Cards
  const beatDescriptions = [
    "宣纸微暖光晕，孤墨自天际垂直坠落",
    "墨滴触纸炸裂，分形水晕向外毛细渗透",
    "狂草游龙，中锋行笔与外缘枯笔飞白",
    "焦浓重淡清五色墨韵交融层叠漫润",
    "墨气蒸腾，细微水汽粒子离散升华",
    "苍茫远山与天地大写意结构浮现",
    "万象收敛，极度空灵的东方留白回甘",
    "朱砂古印雷霆盖落，金石裂帛印泥回弹",
    "红黑辉映，墨韵浸润入定，余韵悠长"
  ];

  async function loadBeats() {
    try {
      const res = await fetch("/api/beats");
      const beats = await res.json();
      beatsGrid.innerHTML = "";

      beats.forEach((beat, idx) => {
        const card = document.createElement("div");
        card.className = "apple-story-card";
        card.innerHTML = `
          <div>
            <div class="card-top-meta">
              <span class="card-beat-tag">Beat 0${beat.id}</span>
              <span class="card-time-span">${beat.start.toFixed(1)}s ~ ${beat.end.toFixed(1)}s</span>
            </div>
            <h3 class="card-beat-title">${beat.name.split(" ")[0]}</h3>
            <p class="card-beat-body">${beatDescriptions[idx] || beat.name}</p>
          </div>
          <div class="card-action-link">
            <span>跳转关键帧</span> ↗
          </div>
        `;

        card.addEventListener("click", () => {
          document.getElementById("hero").scrollIntoView({ behavior: "smooth" });
          if (isInteractiveMode) {
            interactiveT = beat.start;
            renderInteractiveFrame(interactiveT);
          } else {
            video.currentTime = beat.start;
            video.play();
          }
        });

        beatsGrid.appendChild(card);
      });
    } catch (e) {
      console.error("加载 Beat 失败", e);
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
        row.className = "artifact-row";
        row.innerHTML = `
          <div class="art-info">
            <span class="art-name">${item.name}</span>
            <span class="art-spec">${item.filename} · ${item.sizeFormatted || "就绪"}</span>
          </div>
          <a href="${item.path}" download="${item.filename}" class="apple-action-link">下载 ↗</a>
        `;
        artifactsList.appendChild(row);
      });
    } catch (e) {
      console.error("加载资产失败", e);
    }
  }

  // 6. 模态框大图核验
  cardContactSheet.addEventListener("click", () => {
    modalTitle.textContent = "编码后真实抽帧九宫格印相质检单 (来自已生成的 code3d-v3.mp4)";
    modalImg.src = "/video/contact-sheet-v3.png?" + Date.now();
    imageModal.classList.remove("hidden");
  });

  cardSpectrogram.addEventListener("click", () => {
    modalTitle.textContent = "v3.1 物理建模古琴声学频谱瀑布图 (True Physical String Acoustics)";
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
        line.className = "term-line";
        line.textContent = `[${data.time}] ${data.text}`;
        terminalLogs.appendChild(line);
        terminalLogs.scrollTop = terminalLogs.scrollHeight;
      } catch (err) {}
    };
  }

  btnClearLogs.addEventListener("click", () => {
    terminalLogs.innerHTML = "";
  });

  // 8. 全量流水线渲染触发
  async function triggerRender() {
    if (!confirm("确定要启动全量流水线渲染吗？将重新计算 V1、V2、v3.1 配乐、V3 成片并执行 MP4 抽帧质检。")) return;
    try {
      document.getElementById("studio").scrollIntoView({ behavior: "smooth" });
      const res = await fetch("/api/render", { method: "POST" });
      const data = await res.json();
      alert(data.message || "全量渲染流水线已在后台启动，可在下方终端窗口观察实时日志");
    } catch (e) {
      alert("触发失败: " + e.message);
    }
  }

  btnNavRender.addEventListener("click", triggerRender);
  btnHeroPipeline.addEventListener("click", triggerRender);
  btnRunRenderBottom.addEventListener("click", triggerRender);

  btnRecomposeAudio.addEventListener("click", async () => {
    try {
      const res = await fetch("/api/audio", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        alert("物理建模配乐重算完成！6 项客观声学门禁全部通过！");
        loadArtifacts();
      }
    } catch (e) {
      alert("重算音频失败: " + e.message);
    }
  });

  loadBeats();
  loadArtifacts();
  setupSSE();
});
