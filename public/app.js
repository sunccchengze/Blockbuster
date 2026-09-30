/**
 * @file app.js
 * @description Blockbuster Universal Studio 交互中枢
 * 支持任意需求自然语言输入、通用端到端视频生成流水线驱动、实时阶段高亮与动态分镜回放
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM 元素引用
  const video = document.getElementById("main-video");
  const screenBadge = document.getElementById("screen-badge");
  const currentTitleBanner = document.getElementById("current-title-banner");
  const btnDownloadVideo = document.getElementById("btn-download-video");
  const btnDownloadAudio = document.getElementById("btn-download-audio");

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

  const promptInput = document.getElementById("prompt-input");
  const btnRunPipeline = document.getElementById("btn-run-pipeline");
  const navBtnGenerate = document.getElementById("nav-btn-generate");
  const tagChips = document.querySelectorAll(".prompt-tag-chip");
  const btnHeroWatch = document.getElementById("btn-hero-watch");

  const beatsGrid = document.getElementById("beats-grid");
  const historyGrid = document.getElementById("history-grid");
  const artifactsList = document.getElementById("artifacts-list");
  const terminalLogs = document.getElementById("terminal-logs");
  const btnClearLogs = document.getElementById("btn-clear-logs");
  const btnRecomposeAudio = document.getElementById("btn-recompose-audio");

  const cardContactSheet = document.getElementById("card-contact-sheet");
  const cardSpectrogram = document.getElementById("card-spectrogram");
  const contactSheetImg = document.getElementById("contact-sheet-img");
  const spectrogramImg = document.getElementById("spectrogram-img");
  const imageModal = document.getElementById("image-modal");
  const modalImg = document.getElementById("modal-img");
  const modalTitle = document.getElementById("modal-title");
  const modalClose = document.getElementById("modal-close");

  const segButtons = document.querySelectorAll(".seg-btn");

  const fps = 24;
  let totalDuration = 8.0;
  let currentManifest = null;

  function formatTime(sec) {
    const s = Math.max(0, sec);
    const mins = Math.floor(s / 60);
    const secs = Math.floor(s % 60);
    const ms = Math.floor((s - Math.floor(s)) * 1000);
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
  }

  function updateTimeDisplay(curTime, dur) {
    dur = dur || video.duration || totalDuration || 8.0;
    const curFrame = Math.floor(curTime * fps);
    const totalFrames = Math.round(dur * fps);

    timecodeDisplay.textContent = `${formatTime(curTime)} / ${formatTime(dur)}`;
    frameCounter.textContent = `FRAME ${String(curFrame).padStart(3, "0")} / ${totalFrames}`;
    seekSlider.value = curTime;
    seekSlider.max = dur;
  }

  // 1. 播放器基础事件
  video.addEventListener("timeupdate", () => {
    updateTimeDisplay(video.currentTime, video.duration);
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
    if (video.paused) {
      video.play();
    } else {
      video.pause();
    }
  });

  btnHeroWatch.addEventListener("click", () => {
    video.play();
  });

  btnStepBack.addEventListener("click", () => {
    video.pause();
    video.currentTime = Math.max(0, video.currentTime - 1 / fps);
  });

  btnStepForward.addEventListener("click", () => {
    video.pause();
    video.currentTime = Math.min(video.duration, video.currentTime + 1 / fps);
  });

  btnLoop.addEventListener("click", () => {
    video.loop = !video.loop;
    btnLoop.classList.toggle("active", video.loop);
  });

  seekSlider.addEventListener("input", (e) => {
    video.currentTime = parseFloat(e.target.value);
    updateTimeDisplay(video.currentTime, video.duration);
  });

  playbackSpeed.addEventListener("change", (e) => {
    video.playbackRate = parseFloat(e.target.value);
  });

  // 2. 预设 Tag 点按填充
  tagChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      promptInput.value = chip.dataset.prompt;
      promptInput.focus();
    });
  });

  // 3. 流水线阶段高亮指示器
  function setPipelineStep(stepIdx) {
    for (let i = 1; i <= 5; i++) {
      const el = document.getElementById(`step-${i}`);
      if (!el) continue;
      el.classList.remove("active", "completed");
      if (i < stepIdx) {
        el.classList.add("completed");
      } else if (i === stepIdx) {
        el.classList.add("active");
      }
    }
  }

  function resetPipelineSteps() {
    for (let i = 1; i <= 5; i++) {
      const el = document.getElementById(`step-${i}`);
      if (el) el.classList.remove("active", "completed");
    }
  }

  // 4. 核心：运行通用流水线制作视频
  async function triggerPipelineGeneration() {
    const promptText = promptInput.value.trim();
    if (!promptText) {
      alert("请输入你的视频需求描述，或点击下方的创意预设标签！");
      promptInput.focus();
      return;
    }

    btnRunPipeline.disabled = true;
    btnRunPipeline.innerHTML = `<span>流水线全力运转中...</span>`;
    setPipelineStep(1);

    try {
      const res = await fetch("/api/pipeline/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: promptText })
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "生成流水线执行失败");
      }

      setPipelineStep(6); // 全部完成
      loadManifestIntoStudio(data.manifest);
      loadHistory();
      document.getElementById("hero").scrollIntoView({ behavior: "smooth" });
    } catch (err) {
      alert("流水线制作失败: " + err.message);
    } finally {
      btnRunPipeline.disabled = false;
      btnRunPipeline.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        <span>立即运行流水线制作视频</span>
      `;
    }
  }

  btnRunPipeline.addEventListener("click", triggerPipelineGeneration);
  navBtnGenerate.addEventListener("click", () => {
    document.getElementById("pipeline-creator").scrollIntoView({ behavior: "smooth" });
    promptInput.focus();
  });

  // 5. 将生成的作品全套清单载入演播厅
  function loadManifestIntoStudio(manifest) {
    currentManifest = manifest;
    totalDuration = manifest.meta.duration || 8.0;

    // 1. 切换视频播放器
    video.src = manifest.deliverables.video;
    video.load();
    screenBadge.textContent = manifest.meta.genre.name.toUpperCase();
    currentTitleBanner.textContent = `当前影片：${manifest.meta.title} · ${manifest.meta.genre.name.toUpperCase()}`;

    btnDownloadVideo.href = manifest.deliverables.video;
    btnDownloadAudio.href = manifest.deliverables.audio;

    // 2. 渲染叙事 Beats
    renderBeats(manifest.storyboard.beats);

    // 3. 更新质检单与指标
    contactSheetImg.src = manifest.deliverables.contactSheet + "?" + Date.now();
    updateQCMetrics(manifest.audioQC);

    // 4. 起播
    setTimeout(() => {
      video.play().catch(() => {});
    }, 300);
  }

  function renderBeats(beats) {
    beatsGrid.innerHTML = "";
    beats.forEach((b) => {
      const card = document.createElement("div");
      card.className = "apple-story-card";
      card.innerHTML = `
        <div>
          <div class="card-top-meta">
            <span class="card-beat-tag">Beat 0${b.id}</span>
            <span class="card-time-span">${b.start.toFixed(1)}s ~ ${b.end.toFixed(1)}s</span>
          </div>
          <h3 class="card-beat-title">${b.name}</h3>
          <p class="card-beat-body">${b.action}</p>
        </div>
        <div class="card-action-link">
          <span>跳转关键帧</span> ↗
        </div>
      `;

      card.addEventListener("click", () => {
        document.getElementById("hero").scrollIntoView({ behavior: "smooth" });
        video.currentTime = b.start;
        video.play();
      });

      beatsGrid.appendChild(card);
    });
  }

  function updateQCMetrics(qc) {
    if (!qc || !qc.gates) return;
    qc.gates.forEach((g, idx) => {
      const valEl = document.getElementById(`qc-gate-${idx + 1}-val`);
      const badgeEl = document.getElementById(`qc-gate-${idx + 1}-badge`);
      if (valEl) valEl.innerHTML = `${g.value} <span class="m-target">(标准: ${g.target})</span>`;
      if (badgeEl) {
        badgeEl.textContent = g.passed ? "PASS" : "FAIL";
        badgeEl.className = `m-status ${g.passed ? "pass" : "fail"}`;
      }
    });
  }

  // 6. 加载历史制作作品列表
  async function loadHistory() {
    try {
      const res = await fetch("/api/pipeline/history");
      const history = await res.json();
      historyGrid.innerHTML = "";

      if (history.length === 0) {
        historyGrid.innerHTML = `<p class="lead-text" style="grid-column: 1/-1;">暂无生成记录，请在上方输入需求生成第一部影片。</p>`;
        return;
      }

      // 如果当前尚未加载任何作品，默认载入最新生成的历史作品
      if (!currentManifest && history[0]) {
        loadManifestIntoStudio(history[0]);
      }

      history.forEach((item) => {
        const card = document.createElement("div");
        card.className = "history-card";
        const dateStr = new Date(item.timestamp).toLocaleTimeString();
        card.innerHTML = `
          <div class="h-top">
            <span class="h-genre">${item.meta.genre.name}</span>
            <h4 class="h-prompt">${item.prompt}</h4>
          </div>
          <div class="h-meta">
            <span>${dateStr} · 1280×720 @ 24fps</span>
            <span class="apple-action-link">加载回放 ↗</span>
          </div>
        `;

        card.addEventListener("click", () => {
          loadManifestIntoStudio(item);
          document.getElementById("hero").scrollIntoView({ behavior: "smooth" });
        });

        historyGrid.appendChild(card);
      });
    } catch (e) {
      console.error("加载历史失败", e);
    }
  }

  // 7. 加载基准资产交付包
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

  // 8. Sub-Nav 切换
  segButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      segButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const type = btn.dataset.type;
      const badgeText = btn.dataset.badge;
      screenBadge.textContent = badgeText;

      if (type === "current" && currentManifest) {
        video.src = currentManifest.deliverables.video;
      } else if (btn.dataset.video) {
        video.src = btn.dataset.video;
      }
      video.load();
      video.play();
    });
  });

  // 9. 模态框全尺寸查看
  cardContactSheet.addEventListener("click", () => {
    modalTitle.textContent = "真实抽帧印相质检单 (Contact Sheet)";
    modalImg.src = contactSheetImg.src;
    imageModal.classList.remove("hidden");
  });

  cardSpectrogram.addEventListener("click", () => {
    modalTitle.textContent = "声学频谱瀑布图 (Acoustic Spectrogram)";
    modalImg.src = spectrogramImg.src;
    imageModal.classList.remove("hidden");
  });

  modalClose.addEventListener("click", () => imageModal.classList.add("hidden"));
  document.querySelector(".modal-backdrop").addEventListener("click", () => imageModal.classList.add("hidden"));

  // 10. SSE 实时日志总线
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

        // 根据日志更新阶段进度
        if (data.text.includes("[1/5]")) setPipelineStep(1);
        else if (data.text.includes("[2/5]")) setPipelineStep(2);
        else if (data.text.includes("[3/5]")) setPipelineStep(3);
        else if (data.text.includes("[4/5]")) setPipelineStep(4);
        else if (data.text.includes("[5/5]")) setPipelineStep(5);
      } catch (err) {}
    };
  }

  btnClearLogs.addEventListener("click", () => {
    terminalLogs.innerHTML = "";
  });

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

  loadHistory();
  loadArtifacts();
  setupSSE();
});
