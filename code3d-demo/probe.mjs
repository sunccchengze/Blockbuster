import { chromium } from 'playwright';
const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-sandbox','--no-sandbox'] });
const p = await b.newPage();
p.on('console', m => console.log('[page]', m.text()));
p.on('pageerror', e => console.log('[err]', e.message));
await p.setContent(`<canvas id=c></canvas><script>
const gl = document.getElementById('c').getContext('webgl2');
const d = gl ? gl.getExtension('WEBGL_debug_renderer_info') : null;
console.log(JSON.stringify({
  webgl2: !!gl,
  renderer: d ? gl.getParameter(d.UNMASKED_RENDERER_WEBGL) : null,
  vendor: d ? gl.getParameter(d.UNMASKED_VENDOR_WEBGL) : null,
  maxTex: gl ? gl.getParameter(gl.MAX_TEXTURE_SIZE) : null
}));
<\/script>`);
await p.waitForTimeout(1500);
await b.close();
