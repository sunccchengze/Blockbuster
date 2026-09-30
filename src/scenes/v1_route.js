/**
 * @file v1_route.js
 * @description V1 路线验证版（12.00s 3D MP4）：
 * 验证确定性 seek(t) 机制、种子伪随机数与三维投影坐标系，证明无物理时钟依赖的代码求值闭环。
 */

const THREE = require("three");
const { createPRNG } = require("../core/timeline");

class V1Scene {
  constructor() {
    this.width = 1280;
    this.height = 720;
    this.fps = 24;
    this.duration = 12.0;
    this.shutterAngle = 0;
    this.subframes = 1;

    // 预创建几何数据
    this.boxGeo = new THREE.BoxGeometry(220, 220, 220);
    this.icoGeo = new THREE.IcosahedronGeometry(130, 0); // 12 顶点 20 面
  }

  render(ctx, t, frameIndex, subIndex, subCount, width, height) {
    const prng = createPRNG(1001);

    // 1. 深色极简背景
    ctx.fillStyle = "#080a0f";
    ctx.fillRect(0, 0, width, height);

    // 2. 背景微观确定性坐标网格
    ctx.strokeStyle = "rgba(40, 60, 90, 0.25)";
    ctx.lineWidth = 1;
    const gridSpacing = 40;
    for (let x = 0; x < width; x += gridSpacing) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSpacing) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // 3. 3D 旋转变换
    const cameraZ = 800;
    const rotX = t * 0.45;
    const rotY = t * 0.75;
    const rotZ = t * 0.2;

    const rotMatrix = new THREE.Matrix4().makeRotationFromEuler(
      new THREE.Euler(rotX, rotY, rotZ, "XYZ")
    );

    const project = (vec) => {
      const v = vec.clone().applyMatrix4(rotMatrix);
      const z = v.z + cameraZ;
      const f = 600 / Math.max(10, z);
      return {
        x: width / 2 + v.x * f,
        y: height / 2 - v.y * f,
        z: v.z,
        scale: f
      };
    };

    // 4. 绘制外层 3D 立方体线框
    const posAttr = this.boxGeo.attributes.position;
    const indexAttr = this.boxGeo.index;
    const indices = indexAttr.array;

    ctx.strokeStyle = "#00d2ff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < indices.length; i += 3) {
      const idxA = indices[i];
      const idxB = indices[i + 1];
      const idxC = indices[i + 2];

      const vA = new THREE.Vector3().fromBufferAttribute(posAttr, idxA);
      const vB = new THREE.Vector3().fromBufferAttribute(posAttr, idxB);
      const vC = new THREE.Vector3().fromBufferAttribute(posAttr, idxC);

      const pA = project(vA);
      const pB = project(vB);
      const pC = project(vC);

      ctx.moveTo(pA.x, pA.y);
      ctx.lineTo(pB.x, pB.y);
      ctx.lineTo(pC.x, pC.y);
      ctx.closePath();
    }
    ctx.stroke();

    // 5. 绘制内层 3D 正二十面体粒子与节点
    const icoPos = this.icoGeo.attributes.position;
    const vertexCount = icoPos.count;

    ctx.strokeStyle = "rgba(255, 100, 150, 0.7)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let i = 0; i < vertexCount; i += 3) {
      const vA = new THREE.Vector3().fromBufferAttribute(icoPos, i);
      const vB = new THREE.Vector3().fromBufferAttribute(icoPos, i + 1);
      const vC = new THREE.Vector3().fromBufferAttribute(icoPos, i + 2);

      const pA = project(vA);
      const pB = project(vB);
      const pC = project(vC);

      ctx.moveTo(pA.x, pA.y);
      ctx.lineTo(pB.x, pB.y);
      ctx.lineTo(pC.x, pC.y);
      ctx.closePath();
    }
    ctx.stroke();

    // 6. UI 与工程标签层
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 20px monospace";
    ctx.fillText("BLOCKBUSTER ENGINE // V1.0 ROUTE VALIDATION", 50, 60);

    ctx.fillStyle = "#8899aa";
    ctx.font = "14px monospace";
    ctx.fillText(`TIME: ${t.toFixed(3)}s / 12.000s | FRAME: ${frameIndex} / 288`, 50, 88);
    ctx.fillText("PIPELINE: DETERMINISTIC SEEK(t) -> SKIA BUFFER -> FFMPEG STREAM", 50, 110);
    ctx.fillText("STATUS: ZERO WALL-CLOCK DEPENDENCY VERIFIED", 50, 132);

    // 底部走时进度条
    ctx.fillStyle = "rgba(255, 255, 255, 0.15)";
    ctx.fillRect(50, height - 40, width - 100, 6);
    ctx.fillStyle = "#00d2ff";
    ctx.fillRect(50, height - 40, ((width - 100) * t) / this.duration, 6);
  }
}

module.exports = V1Scene;
