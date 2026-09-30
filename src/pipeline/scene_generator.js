/**
 * @file scene_generator.js
 * @description 程序化视觉合成器：将任意分镜规格编译为确定性渲染函数
 */

const { createPRNG } = require("../core/timeline");

/**
 * 创建三维点投影器
 */
function project3D(x, y, z, cx, cy, fov = 450) {
  const depth = z + 600;
  if (depth <= 10) return null;
  const scale = fov / depth;
  return {
    px: cx + x * scale,
    py: cy + y * scale,
    scale,
    depth
  };
}

/**
 * 编译生成确定性场景渲染逻辑
 */
function createProceduralScene(storyboard) {
  const { meta, beats } = storyboard;
  const { genre, title, duration, width, height } = meta;
  const palette = genre.palette;

  // 预生成伪随机粒子集合 (纯函数，无副作用)
  const prng = createPRNG(20260930);
  const particleCount = 260;
  const particles = [];
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: (prng() - 0.5) * 1600,
      y: (prng() - 0.5) * 1200,
      z: (prng() - 0.5) * 1400,
      vx: (prng() - 0.5) * 40,
      vy: (prng() - 0.5) * 40,
      vz: (prng() - 0.5) * 40,
      size: 1.5 + prng() * 3.5,
      hueOffset: prng() * 0.4 - 0.2
    });
  }

  // 渲染函数 f(t, ctx, canvas)
  return function renderFrame(t, ctx, canvas) {
    const cx = width / 2;
    const cy = height / 2;

    // 1. 背景铺陈
    const bgGrad = ctx.createRadialGradient(cx, cy, 50, cx, cy, Math.max(cx, cy) * 1.2);
    bgGrad.addColorStop(0, palette.bg === "#efe8d8" ? "#fbf8f0" : "#0d1424");
    bgGrad.addColorStop(1, palette.bg);
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, width, height);

    // 2. 判定当前所属 Beat
    let currentBeat = beats[0];
    for (const b of beats) {
      if (t >= b.start && t < b.end) {
        currentBeat = b;
        break;
      }
    }

    // 3. 动态粒子云与空间流形
    for (let i = 0; i < particleCount; i++) {
      const p = particles[i];
      // 依时间演进
      let px = p.x + p.vx * t;
      let py = p.y + p.vy * t;
      let pz = p.z + p.vz * t;

      // 在高潮与奔涌阶段产生引力牵引
      if (t >= 2.8 && t < 6.0) {
        const pull = Math.sin((t - 2.8) * 1.5);
        px *= 1 - pull * 0.35;
        py *= 1 - pull * 0.35;
        pz -= pull * 400 * ((t - 2.8) / 3.2);
      }

      // 循环卷绕
      px = ((px + 1000) % 2000) - 1000;
      py = ((py + 800) % 1600) - 800;
      pz = ((pz + 800) % 1600) - 800;

      const pt = project3D(px, py, pz, cx, cy);
      if (pt) {
        const alpha = Math.max(0.1, Math.min(0.85, (1000 - pt.depth) / 1000));
        ctx.fillStyle = palette.primary;
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.arc(pt.px, pt.py, p.size * pt.scale, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    ctx.globalAlpha = 1.0;

    // 4. 三维晶格与几何环 (Lattice & Orbital Rings)
    const rotSpeed = 0.8 * t;
    const ringCount = 4;
    for (let r = 1; r <= ringCount; r++) {
      const radius = 100 + r * 55;
      const ringAngle = rotSpeed * (r % 2 === 0 ? 1 : -1) + (r * Math.PI) / 4;

      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(ringAngle * 0.3);
      ctx.scale(1.0, 0.45);

      ctx.strokeStyle = r % 2 === 0 ? palette.primary : palette.accent;
      ctx.lineWidth = 1.5 + (ringCount - r) * 0.8;
      ctx.globalAlpha = 0.35 + 0.3 * Math.sin(t * 3 + r);
      ctx.beginPath();
      ctx.arc(0, 0, radius * (0.8 + 0.2 * Math.sin(t * 2)), 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
    ctx.globalAlpha = 1.0;

    // 5. 核心图腾显现 (Hero Geometric Emblem / Core)
    if (t >= 1.4) {
      const coreT = Math.min(1.0, (t - 1.4) / 1.5);
      const easeCore = 1 - Math.pow(1 - coreT, 3);
      const coreRadius = (45 + 15 * Math.sin(t * 4)) * easeCore;

      // 辉光核心
      const glow = ctx.createRadialGradient(cx, cy, 5, cx, cy, coreRadius * 2.5);
      glow.addColorStop(0, palette.primary);
      glow.addColorStop(0.5, palette.secondary);
      glow.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(cx, cy, coreRadius * 2.5, 0, Math.PI * 2);
      ctx.fill();

      // 内层几何多边形
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      const sides = 6;
      for (let s = 0; s <= sides; s++) {
        const ang = (s * 2 * Math.PI) / sides + t * 1.5;
        const gx = cx + Math.cos(ang) * coreRadius;
        const gy = cy + Math.sin(ang) * coreRadius;
        if (s === 0) ctx.moveTo(gx, gy);
        else ctx.lineTo(gx, gy);
      }
      ctx.stroke();
    }

    // 6. 冲击波扩散 (Shockwave)
    if (t >= 4.4 && t < 5.8) {
      const shockT = (t - 4.4) / 1.4;
      const shockR = shockT * (width * 0.7);
      const shockAlpha = (1 - shockT) * 0.8;

      ctx.strokeStyle = palette.accent;
      ctx.lineWidth = 4 * (1 - shockT);
      ctx.globalAlpha = shockAlpha;
      ctx.beginPath();
      ctx.arc(cx, cy, shockR, 0, Math.PI * 2);
      ctx.stroke();
      ctx.globalAlpha = 1.0;
    }

    // 7. 电影级排版与标题定格 (Typography & Hero Manifest)
    if (t >= 5.2) {
      const textT = Math.min(1.0, (t - 5.2) / 0.8);
      const easeAlpha = textT * textT;
      const tracking = 12 + (1 - textT) * 20;

      ctx.save();
      ctx.globalAlpha = easeAlpha;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      // 主标题
      ctx.fillStyle = palette.text;
      ctx.font = `600 44px -apple-system, "SF Pro Display", sans-serif`;
      ctx.fillText(title.toUpperCase(), cx, cy - 25);

      // 副标与流派标签
      ctx.fillStyle = palette.primary;
      ctx.font = `500 15px -apple-system, "SF Pro Text", monospace`;
      ctx.fillText(`${genre.name.toUpperCase()} · PROCEDURAL CINEMA`, cx, cy + 32);

      // 下划装饰线
      const lineWidth = 180 * textT;
      ctx.strokeStyle = palette.primary;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(cx - lineWidth / 2, cy + 50);
      ctx.lineTo(cx + lineWidth / 2, cy + 50);
      ctx.stroke();

      ctx.restore();
    }

    // 8. 实时 HUD 与电影画幅遮罩 (Cinematic 2.39:1 Letterbox)
    const letterboxH = 50;
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, width, letterboxH);
    ctx.fillRect(0, height - letterboxH, width, letterboxH);

    // 顶栏 HUD 极简时间码
    ctx.fillStyle = "rgba(255, 255, 255, 0.45)";
    ctx.font = "11px monospace";
    ctx.textAlign = "left";
    ctx.fillText(`BLOCKBUSTER PIPELINE // SCENE: ${currentBeat.subtitle} // T: ${t.toFixed(3)}s`, 24, 30);
    ctx.textAlign = "right";
    ctx.fillText(`${width}x${height} 24FPS // SEED DETERMINISTIC`, width - 24, 30);
  };
}

module.exports = {
  createProceduralScene
};
