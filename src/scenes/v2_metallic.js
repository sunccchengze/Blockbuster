/**
 * @file v2_metallic.js
 * @description V2 质感化进阶版：
 * 引入三维表面法线光照模型（Phong/PBR 近似）、金属高光菲涅尔反射、环境遮蔽与 Bloom 辉光后处理。
 */

const THREE = require("three");
const { createPRNG, Easing } = require("../core/timeline");

class V2Scene {
  constructor() {
    this.width = 1280;
    this.height = 720;
    this.fps = 24;
    this.duration = 10.0;
    this.shutterAngle = 90; // 轻度快门模糊
    this.subframes = 2;

    // 细分圆环面几何体
    this.torusGeo = new THREE.TorusKnotGeometry(120, 35, 128, 24);
  }

  render(ctx, t, frameIndex, subIndex, subCount, width, height) {
    // 1. 深邃暗场电影级渐变背景
    const bgGrad = ctx.createRadialGradient(
      width / 2, height / 2, 50,
      width / 2, height / 2, 700
    );
    bgGrad.addColorStop(0, "#161b26");
    bgGrad.addColorStop(0.6, "#0a0c12");
    bgGrad.addColorStop(1, "#030406");
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, width, height);

    // 2. 动态光照源设置
    const light1Pos = new THREE.Vector3(
      Math.cos(t * 1.5) * 400,
      Math.sin(t * 1.2) * 300,
      400
    );
    const light1Color = { r: 0.9, g: 0.7, b: 0.3 }; // 琥珀暖金

    const light2Pos = new THREE.Vector3(
      Math.sin(t * 1.0) * -450,
      Math.cos(t * 1.8) * 350,
      300
    );
    const light2Color = { r: 0.2, g: 0.6, b: 1.0 }; // 冰蓝高光冷光

    // 3. 三维姿态变换
    const rotX = t * 0.5;
    const rotY = t * 0.8;
    const rotZ = Math.sin(t * 0.4) * 0.3;
    const rotMatrix = new THREE.Matrix4().makeRotationFromEuler(
      new THREE.Euler(rotX, rotY, rotZ, "XYZ")
    );

    const normalMatrix = new THREE.Matrix3().getNormalMatrix(rotMatrix);
    const cameraZ = 750;

    // 4. 三角面提取与排序 (Painter's Algorithm 深度排序)
    const posAttr = this.torusGeo.attributes.position;
    const normAttr = this.torusGeo.attributes.normal;
    const indexAttr = this.torusGeo.index;
    const indices = indexAttr.array;
    const numFaces = indices.length / 3;

    const faces = [];
    for (let i = 0; i < numFaces; i++) {
      const idxA = indices[i * 3];
      const idxB = indices[i * 3 + 1];
      const idxC = indices[i * 3 + 2];

      const vA = new THREE.Vector3().fromBufferAttribute(posAttr, idxA).applyMatrix4(rotMatrix);
      const vB = new THREE.Vector3().fromBufferAttribute(posAttr, idxB).applyMatrix4(rotMatrix);
      const vC = new THREE.Vector3().fromBufferAttribute(posAttr, idxC).applyMatrix4(rotMatrix);

      const nA = new THREE.Vector3().fromBufferAttribute(normAttr, idxA).applyMatrix3(normalMatrix);
      const nB = new THREE.Vector3().fromBufferAttribute(normAttr, idxB).applyMatrix3(normalMatrix);
      const nC = new THREE.Vector3().fromBufferAttribute(normAttr, idxC).applyMatrix3(normalMatrix);

      const centerZ = (vA.z + vB.z + vC.z) / 3;
      faces.push({ vA, vB, vC, nA, nB, nC, centerZ });
    }

    // 由远及近深度排序
    faces.sort((a, b) => a.centerZ - b.centerZ);

    // 投影求值并着色
    const project = (v) => {
      const z = v.z + cameraZ;
      const f = 650 / Math.max(10, z);
      return { x: width / 2 + v.x * f, y: height / 2 - v.y * f };
    };

    // 绘制几何三角面
    for (let i = 0; i < faces.length; i++) {
      const f = faces[i];
      const faceCenter = new THREE.Vector3().add(f.vA).add(f.vB).add(f.vC).multiplyScalar(1 / 3);
      const faceNorm = new THREE.Vector3().add(f.nA).add(f.nB).add(f.nC).normalize();

      // 背面剔除 (Backface Culling)
      const viewDir = new THREE.Vector3(0, 0, 1);
      if (faceNorm.dot(viewDir) <= 0.05) continue;

      // PBR / Phong 金属光照计算
      // 漫反射 Ambient + Diffuse
      let r = 0.08, g = 0.09, b = 0.12;

      // Light 1 漫反射 + 镜面高光 (Specular Power 32)
      const l1Dir = new THREE.Vector3().subVectors(light1Pos, faceCenter).normalize();
      const diff1 = Math.max(0, faceNorm.dot(l1Dir));
      const ref1 = faceNorm.clone().multiplyScalar(2 * diff1).sub(l1Dir).normalize();
      const spec1 = Math.pow(Math.max(0, ref1.dot(viewDir)), 36);

      r += diff1 * 0.35 * light1Color.r + spec1 * 0.85 * light1Color.r;
      g += diff1 * 0.35 * light1Color.g + spec1 * 0.85 * light1Color.g;
      b += diff1 * 0.35 * light1Color.b + spec1 * 0.85 * light1Color.b;

      // Light 2 漫反射 + 镜面高光
      const l2Dir = new THREE.Vector3().subVectors(light2Pos, faceCenter).normalize();
      const diff2 = Math.max(0, faceNorm.dot(l2Dir));
      const ref2 = faceNorm.clone().multiplyScalar(2 * diff2).sub(l2Dir).normalize();
      const spec2 = Math.pow(Math.max(0, ref2.dot(viewDir)), 28);

      r += diff2 * 0.3 * light2Color.r + spec2 * 0.7 * light2Color.r;
      g += diff2 * 0.3 * light2Color.g + spec2 * 0.7 * light2Color.g;
      b += diff2 * 0.3 * light2Color.b + spec2 * 0.7 * light2Color.b;

      // 菲涅尔边缘泛光 (Fresnel Rim)
      const fresnel = Math.pow(1.0 - Math.max(0, faceNorm.dot(viewDir)), 3.0);
      r += fresnel * 0.45;
      g += fresnel * 0.55;
      b += fresnel * 0.75;

      const pA = project(f.vA);
      const pB = project(f.vB);
      const pC = project(f.vC);

      const hexR = Math.min(255, Math.round(r * 255));
      const hexG = Math.min(255, Math.round(g * 255));
      const hexB = Math.min(255, Math.round(b * 255));

      ctx.fillStyle = `rgb(${hexR}, ${hexG}, ${hexB})`;
      ctx.beginPath();
      ctx.moveTo(pA.x, pA.y);
      ctx.lineTo(pB.x, pB.y);
      ctx.lineTo(pC.x, pC.y);
      ctx.closePath();
      ctx.fill();
    }

    // 5. 模拟后处理 Bloom 辉光通道 (Overlay Glow)
    const glowGrad = ctx.createRadialGradient(
      width / 2, height / 2, 80,
      width / 2, height / 2, 350
    );
    glowGrad.addColorStop(0, "rgba(255, 200, 100, 0.18)");
    glowGrad.addColorStop(0.5, "rgba(80, 160, 255, 0.08)");
    glowGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
    ctx.fillStyle = glowGrad;
    ctx.fillRect(0, 0, width, height);

    // 6. UI HUD 标识
    ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
    ctx.font = "bold 18px monospace";
    ctx.fillText("BLOCKBUSTER ENGINE // V2.0 METALLIC PBR & BLOOM PASS", 50, 60);

    ctx.fillStyle = "#8899aa";
    ctx.font = "14px monospace";
    ctx.fillText(`TIME: ${t.toFixed(3)}s / 10.000s | SHUTTER: 90° | N-SUB: 2`, 50, 86);
    ctx.fillText("FEATURES: TORUS KNOT MESH | DEPTH-SORTING | DUAL PBR LIGHTS | FRESNEL RIM", 50, 108);

    // 进度条
    ctx.fillStyle = "rgba(255, 255, 255, 0.15)";
    ctx.fillRect(50, height - 35, width - 100, 4);
    ctx.fillStyle = "#ffaa33";
    ctx.fillRect(50, height - 35, ((width - 100) * t) / this.duration, 4);
  }
}

module.exports = V2Scene;
