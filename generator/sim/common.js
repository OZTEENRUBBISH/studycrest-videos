// Shared low-poly world kit for the StudyCrest "What if" simulation videos.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
export { THREE };

export const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const seg = (t, a, b) => clamp((t - a) / (b - a));           // 0..1 progress of t inside [a,b]
export const smooth = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
export const easeOut = (x) => 1 - Math.pow(1 - clamp(x), 3);
export const easeIn = (x) => Math.pow(clamp(x), 3);
export const easeIO = (x) => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };

export function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function h3(x, y, z) { let n = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453; return n - Math.floor(n); }
export function noise3(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z), xf = x - xi, yf = y - yi, zf = z - zi;
  const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf), w = zf * zf * (3 - 2 * zf);
  const c = (a, b, d) => h3(xi + a, yi + b, zi + d);
  return lerp(lerp(lerp(c(0, 0, 0), c(1, 0, 0), u), lerp(c(0, 1, 0), c(1, 1, 0), u), v), lerp(lerp(c(0, 0, 1), c(1, 0, 1), u), lerp(c(0, 1, 1), c(1, 1, 1), u), v), w);
}
export function fbm(x, y, z, o = 4) { let a = 0.5, f = 1, s = 0; for (let i = 0; i < o; i++) { s += a * noise3(x * f, y * f, z * f); a *= 0.5; f *= 2.03; } return s; }

const _mats = {};
export function mat(color, opt = {}) {
  const k = color + JSON.stringify(opt);
  if (!_mats[k]) { const pbr = opt.metalness !== undefined || opt.envMap; const o = { ...opt }; if (!pbr) { delete o.roughness; } _mats[k] = pbr ? new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.9, metalness: 0, ...o }) : new THREE.MeshLambertMaterial({ color, flatShading: true, ...o }); }
  return _mats[k];
}
export function box(w, h, d, color, x = 0, y = 0, z = 0, opt) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(color, opt)); m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; return m;
}
export function shadowAll(g, cast = true, recv = true) { g.traverse(o => { if (o.isMesh) { o.castShadow = cast; o.receiveShadow = recv; } }); return g; }

// ---------- blocky person. pose: 'stand' | 'sit' | 'walk' ; call person.userData.pose(phase) to animate limbs
const SKIN = [0xf1c9a5, 0xe0ac7e, 0xc68642, 0x8d5524, 0xffdbac, 0x6b4423];
const SHIRT = [0xe6e6e6, 0x2f56d6, 0xf2c94c, 0xe2574c, 0x2bb673, 0xf2994a, 0x9b59b6, 0x34495e, 0xff7eb6, 0x1abc9c];
const PANTS = [0x2c3e50, 0x1e3aa8, 0x8a6d3b, 0x444444, 0xc0392b, 0x16a085, 0xf5f5f5];
const HAIR = [0x2b1b12, 0x5a3825, 0xd8b06a, 0x111111, 0x8e4a2a, 0xbfbfbf];
export function person(R, kind = 'stand', cols = {}) {
  const g = new THREE.Group(), pick = a => a[Math.floor(R() * a.length)];
  const skin = cols.skin ?? pick(SKIN), shirt = cols.shirt ?? pick(SHIRT), pants = cols.pants ?? pick(PANTS), hair = cols.hair ?? pick(HAIR), s = 0.9 + R() * 0.25;
  const hips = new THREE.Group(); g.add(hips);
  const torso = box(0.46, 0.62, 0.26, shirt, 0, 0.31, 0); hips.add(torso);
  const head = box(0.26, 0.28, 0.26, skin, 0, 0.8, 0); hips.add(head);
  hips.add(box(0.28, 0.1, 0.28, hair, 0, 0.97, 0)); hips.add(box(0.045, 0.05, 0.02, 0x1a1a1a, -0.065, 0.83, 0.131)); hips.add(box(0.045, 0.05, 0.02, 0x1a1a1a, 0.065, 0.83, 0.131)); hips.add(box(0.48, 0.2, 0.28, pants, 0, 0.06, 0)); hips.add(box(0.28, 0.16, 0.08, hair, 0, 0.86, -0.12));
  const limb = (w, h, col, x, y) => { const p = new THREE.Group(); p.position.set(x, y, 0); p.add(box(w, h, w, col, 0, -h / 2, 0)); hips.add(p); return p; };
  const aL = limb(0.13, 0.6, cols.sleeve ?? skin, -0.3, 0.6), aR = limb(0.13, 0.6, cols.sleeve ?? skin, 0.3, 0.6);
  const shorts = cols.shorts ?? (R() < 0.6), legC = shorts ? skin : pants; const lL = limb(0.17, 0.82, legC, -0.12, 0.0), lR = limb(0.17, 0.82, legC, 0.12, 0.0);
  for (const l of [lL, lR]) { if (shorts) l.add(box(0.19, 0.3, 0.19, pants, 0, -0.15, 0)); l.add(box(0.19, 0.09, 0.3, cols.shoe ?? (shorts ? 0xe8d9b8 : 0x222222), 0, -0.79, 0.05)); } for (const a of [aL, aR]) a.add(box(0.15, 0.16, 0.15, shirt, 0, -0.08, 0));
  g.scale.setScalar(s); g.userData = { kind, hips, aL, aR, lL, lR, seed: R() * 100,
    pose(ph, mode) {
      mode = mode || kind;
      if (mode === 'sit') { hips.position.y = 0.14; lL.rotation.x = lR.rotation.x = -1.5; aL.rotation.x = aR.rotation.x = -0.5; hips.rotation.x = -0.12; }
      else if (mode === 'walk' || mode === 'run') { const a = mode === 'run' ? 1.05 : 0.5, sw = Math.sin(ph) * a; hips.position.y = 0.82 + Math.abs(Math.cos(ph)) * (mode === 'run' ? 0.09 : 0.03);
        lL.rotation.x = sw; lR.rotation.x = -sw; aL.rotation.x = -sw * (mode === 'run' ? 1.2 : 0.8); aR.rotation.x = sw * (mode === 'run' ? 1.2 : 0.8); hips.rotation.x = mode === 'run' ? 0.22 : 0; }
      else if (mode === 'float') { hips.position.y = 0.82; lL.rotation.x = 0.5 + Math.sin(ph) * 0.4; lR.rotation.x = -0.3 + Math.cos(ph * 0.8) * 0.4; aL.rotation.x = -2.2 + Math.sin(ph * 0.7) * 0.5; aR.rotation.x = -1.6 + Math.cos(ph * 0.9) * 0.5; aL.rotation.z = -0.5; aR.rotation.z = 0.5; hips.rotation.x = 0; }
      else { hips.position.y = 0.82; lL.rotation.x = lR.rotation.x = 0; aL.rotation.x = Math.sin(ph) * 0.06; aR.rotation.x = -Math.sin(ph) * 0.06; aL.rotation.z = aR.rotation.z = 0; hips.rotation.x = 0; }
    } };
  g.userData.pose(0); return shadowAll(g);
}

export function palm(R) {
  const g = new THREE.Group(), h = 5.5 + R() * 3, lean = (R() - 0.5) * 0.5; let px = 0, py = 0; const n = 6;
  const top = new THREE.Group();
  for (let i = 0; i < n; i++) { const sh = h / n, t = new THREE.Mesh(new THREE.CylinderGeometry(0.16 - i * 0.012, 0.2 - i * 0.012, sh * 1.05, 6), mat(0x8b6b45)); px += lean * sh * (i / n); t.position.set(px, py + sh / 2, 0); t.rotation.z = -lean * (i / n); py += sh; g.add(t); }
  top.position.set(px, py, 0);
  for (let i = 0; i < 8; i++) { const f = new THREE.Group(), L = 2.6 + R() * 0.8; const geo = new THREE.ConeGeometry(0.42, L, 4); geo.translate(0, L / 2, 0); geo.scale(1, 1, 0.22);
    const m = new THREE.Mesh(geo, mat(i % 2 ? 0x2e8b4a : 0x3fa35a)); m.rotation.z = Math.PI / 2 + 0.55 + R() * 0.3; f.add(m); f.rotation.y = i / 8 * Math.PI * 2 + R() * 0.3; top.add(f); }
  g.add(top); g.userData.top = top; return shadowAll(g);
}
export function umbrella(R) {
  const g = new THREE.Group(), cols = [[0xe2574c, 0xffffff], [0x2f56d6, 0xffffff], [0xf2c94c, 0xffffff], [0x2bb673, 0xfdf6e3]][Math.floor(R() * 4)];
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 2.3, 6), mat(0xdddddd)); pole.position.y = 1.15; g.add(pole);
  for (let i = 0; i < 8; i++) { const geo = new THREE.ConeGeometry(1.5, 0.55, 8, 1, true, i / 8 * Math.PI * 2, Math.PI / 4); const m = new THREE.Mesh(geo, mat(cols[i % 2], { side: THREE.DoubleSide })); m.position.y = 2.35; g.add(m); }
  g.rotation.z = (R() - 0.5) * 0.25; return shadowAll(g);
}
export function windowTex(R, cols, rows, base, night) {
  const c = document.createElement('canvas'); c.width = cols * 16; c.height = rows * 16; const x = c.getContext('2d');
  x.fillStyle = base; x.fillRect(0, 0, c.width, c.height);
  for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) { const r = R(); x.fillStyle = r < 0.18 ? '#ffe9a8' : (r < 0.55 ? '#9fc3e8' : '#5f7fa6'); if (night) x.fillStyle = r < 0.3 ? '#ffd98a' : '#141a26'; x.fillRect(i * 16 + 3, j * 16 + 4, 10, 9); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.magFilter = THREE.NearestFilter; return t;
}
export function building(R, w, h, d) {
  const g = new THREE.Group(), bases = ['#c9c2b8', '#9aa3ad', '#b7a58f', '#7d8794', '#d8d2c6', '#8c7b6e', '#a9b4bf'], base = bases[Math.floor(R() * bases.length)];
  const tex = windowTex(R, Math.max(3, Math.round(w / 2.2)), Math.max(4, Math.round(h / 3)), base), tex2 = windowTex(R, Math.max(3, Math.round(d / 2.2)), Math.max(4, Math.round(h / 3)), base);
  const side = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.8 }), side2 = new THREE.MeshStandardMaterial({ map: tex2, roughness: 0.8 }), roof = mat(new THREE.Color(base).multiplyScalar(0.7).getHex());
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), [side2, side2, roof, roof, side, side]); m.position.y = h / 2; m.castShadow = true; m.receiveShadow = true; g.add(m);
  if (R() < 0.5) g.add(box(w * 0.5, h * 0.12, d * 0.5, new THREE.Color(base).multiplyScalar(0.8).getHex(), 0, h + h * 0.06, 0));
  if (R() < 0.3) g.add(box(0.3, h * 0.25, 0.3, 0x888888, 0, h + h * 0.24, 0));
  g.userData = { h, w, d }; return g;
}
export function cloud(R) {
  const g = new THREE.Group(), n = 4 + Math.floor(R() * 3);
  for (let i = 0; i < n; i++) { const s = 6 + R() * 7, m = new THREE.Mesh(new THREE.IcosahedronGeometry(s, 1), mat(0xffffff, { roughness: 1, emissive: 0xd6e4f5, emissiveIntensity: 0.62 })); m.position.set((i - n / 2) * 7 + R() * 3, R() * 3, R() * 5); m.scale.y = 0.55; g.add(m); }
  return g;
}
export function skyDome(top, mid, bot) {
  const geo = new THREE.SphereGeometry(900, 32, 16);
  const m = new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false, uniforms: { top: { value: new THREE.Color(top) }, mid: { value: new THREE.Color(mid) }, bot: { value: new THREE.Color(bot) } },
    vertexShader: 'varying vec3 p; void main(){ p = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: 'varying vec3 p; uniform vec3 top; uniform vec3 mid; uniform vec3 bot; void main(){ float h = normalize(p).y; vec3 c = h > 0.0 ? mix(mid, top, pow(h, 0.55)) : mix(mid, bot, pow(-h, 0.4)); gl_FragColor = vec4(c, 1.0); }' });
  return new THREE.Mesh(geo, m);
}
export function stars(R, n = 2500, rad = 700) {
  const p = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const u = R() * 2 - 1, a = R() * Math.PI * 2, s = Math.sqrt(1 - u * u); p[i * 3] = rad * s * Math.cos(a); p[i * 3 + 1] = rad * u; p[i * 3 + 2] = rad * s * Math.sin(a); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3));
  return new THREE.Points(g, new THREE.PointsMaterial({ color: 0xffffff, size: 2.2, sizeAttenuation: false, fog: false, transparent: true, opacity: 0.9 }));
}
// ---------- low-poly Earth with continents from noise
export function globe(radius = 10, detail = 24) {
  const geo = new THREE.IcosahedronGeometry(radius, detail).toNonIndexed(), pos = geo.attributes.position, col = new Float32Array(pos.count * 3), c = new THREE.Color();
  for (let i = 0; i < pos.count; i += 3) {
    const x = (pos.getX(i) + pos.getX(i + 1) + pos.getX(i + 2)) / 3 / radius, y = (pos.getY(i) + pos.getY(i + 1) + pos.getY(i + 2)) / 3 / radius, z = (pos.getZ(i) + pos.getZ(i + 1) + pos.getZ(i + 2)) / 3 / radius;
    const n = fbm(x * 1.7 + 3.1, y * 1.7 + 1.7, z * 1.7 + 5.3, 5), lat = Math.abs(y);
    if (lat > 0.9 + (n - 0.5) * 0.2) c.set(0xf4f8fb); else if (n > 0.53) { const e = (n - 0.53) / 0.2; c.set(e > 0.55 ? 0x8a7a5a : (lat > 0.62 ? 0x5d8a54 : (e > 0.25 ? 0x4f9a4a : 0x79b356))); if (lat < 0.35 && n > 0.6 && fbm(x * 5, y * 5, z * 5, 2) > 0.52) c.set(0xd9c08a); }
    else c.set(n > 0.49 ? 0x2f86c9 : (n > 0.4 ? 0x1f6bb3 : 0x154f96));
    for (let k = 0; k < 3; k++) { col[(i + k) * 3] = c.r; col[(i + k) * 3 + 1] = c.g; col[(i + k) * 3 + 2] = c.b; }
  }
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3)); geo.computeVertexNormals();
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, flatShading: true, roughness: 0.85 }));
  const atm = new THREE.Mesh(new THREE.SphereGeometry(radius * 1.09, 48, 32), new THREE.ShaderMaterial({ side: THREE.BackSide, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: { k: { value: 1 } },
    vertexShader: 'varying vec3 n; varying vec3 v; void main(){ n = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position,1.0); v = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }',
    fragmentShader: 'varying vec3 n; varying vec3 v; uniform float k; void main(){ float f = pow(clamp(1.0 + dot(n, v) * 1.6, 0.0, 1.0), 2.4); gl_FragColor = vec4(0.35, 0.62, 1.0, 1.0) * f * 0.95 * k; }' }));
  const g = new THREE.Group(); g.add(m); g.add(atm); g.userData = { mesh: m, atm }; return g;
}
export function arrow(len, color, w = 0.16) {
  const g = new THREE.Group(), m = new THREE.MeshBasicMaterial({ color, transparent: true });
  const s = new THREE.Mesh(new THREE.CylinderGeometry(w, w, len * 0.68, 8), m); s.position.y = len * 0.34; const h = new THREE.Mesh(new THREE.ConeGeometry(w * 2.6, len * 0.32, 10), m); h.position.y = len * 0.84; g.add(s); g.add(h); g.userData.mat = m; return g;
}

// ---------- 2D overlay (brand badge, HUD, captions, title). All positions in the 1080x1920 frame.
export const LOGO_SVG = '<svg viewBox="5 5 90 90" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3A63E6"/><stop offset="1" stop-color="#1E3AA8"/></linearGradient></defs><rect x="5" y="5" width="90" height="90" rx="21" fill="url(#lg)"/><polygon points="30,40 30,24 40,32 50,20 60,32 70,24 70,40" fill="#fff"/><polyline points="30,60 44,73 70,48" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>';
export function overlay() {
  const css = `
  html,body{margin:0;background:#000;overflow:hidden}
  #stage{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter,Arial,sans-serif;color:#fff}
  #stage canvas{position:absolute;left:0;top:0}
  .ov{position:absolute;left:0;top:0;width:1080px;height:1920px;pointer-events:none}
  #vig{background:radial-gradient(ellipse at 50% 46%,rgba(0,0,0,0) 52%,rgba(0,0,0,.42) 100%),linear-gradient(180deg,rgba(0,0,0,.38) 0,rgba(0,0,0,0) 16%,rgba(0,0,0,0) 70%,rgba(0,0,0,.5) 100%)}
  #badge{position:absolute;left:44px;top:168px;display:flex;align-items:center;gap:16px;padding:12px 22px 12px 12px;border-radius:26px;background:rgba(10,14,34,.62);border:1.5px solid rgba(255,255,255,.2)}
  #badge svg{width:76px;height:76px;display:block}
  #badge .n{font-weight:800;font-size:33px;letter-spacing:-.4px;line-height:1.05}
  #badge .o{font-weight:600;font-size:23.5px;color:#cfe0ff;margin-top:5px;line-height:1.1}
  #badge .o b{color:#ffd64a;font-weight:800}
  #title{position:absolute;left:70px;width:940px;top:420px;text-align:center;font-family:Lora,serif;font-weight:600;font-size:86px;line-height:1.12;letter-spacing:-1px;text-shadow:0 4px 34px rgba(0,0,0,.9),0 0 6px rgba(0,0,0,.75),0 0 60px rgba(0,0,20,.6)}
  #title em{font-style:normal;color:#b9d2ff;text-shadow:0 0 34px rgba(100,150,255,.9),0 4px 30px rgba(0,0,0,.7)}
  #hud{position:absolute;left:64px;top:860px;padding-left:22px;border-left:5px solid #5b86ff;text-shadow:0 2px 14px rgba(0,0,0,.85)}
  #hud .l{font-weight:700;font-size:25px;letter-spacing:5px;text-transform:uppercase}
  #hud .v{font-family:Lora,serif;font-weight:500;font-size:78px;line-height:1.05;font-variant-numeric:tabular-nums;margin-top:2px}
  #hud .s{font-weight:600;font-size:21px;letter-spacing:3.5px;text-transform:uppercase;color:#d5e2ff;margin-top:10px;white-space:pre-line;line-height:1.5}
  #cap{position:absolute;left:80px;width:920px;top:1210px;text-align:center;font-family:Lora,serif;font-style:italic;font-weight:500;font-size:55px;line-height:1.22;text-shadow:0 3px 22px rgba(0,0,0,.95),0 0 5px rgba(0,0,0,.8)}
  #cap em{font-style:italic;color:#9cc0ff}
  #chip{position:absolute;left:0;width:1080px;top:330px;text-align:center}
  #chip span{display:inline-block;padding:14px 30px;border-radius:999px;font-weight:800;font-size:31px;letter-spacing:4px;text-transform:uppercase;background:rgba(10,14,34,.7);border:2px solid rgba(255,255,255,.55)}
  .lab{position:absolute;font-weight:700;font-size:25px;letter-spacing:3px;text-transform:uppercase;text-shadow:0 2px 12px rgba(0,0,0,.9);white-space:pre-line;line-height:1.35}
  .lab b{display:block;font-family:Lora,serif;font-weight:600;font-size:46px;letter-spacing:0;text-transform:none}
  #end{position:absolute;left:0;top:0;width:1080px;height:1920px;background:rgba(6,9,26,.78);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
  #end svg{width:190px;height:190px}
  #end .n{font-weight:800;font-size:70px;margin-top:26px;letter-spacing:-1px}
  #end .f{font-family:Lora,serif;font-style:italic;font-size:62px;margin-top:44px}
  #end .o{font-weight:700;font-size:36px;margin-top:40px;color:#cfe0ff;line-height:1.4}
  #end .o b{color:#ffd64a}
  `;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
  const stage = document.getElementById('stage');
  const add = (id, html = '', cls = 'ov') => { const d = document.createElement('div'); d.id = id; if (cls) d.className = cls; d.innerHTML = html; stage.appendChild(d); return d; };
  const o = { stage };
  o.tint = add('tint'); o.vig = add('vig'); o.flash = add('flash'); o.glitch = add('glitch');
  o.labels = add('labels');
  o.title = add('title', '', ''); o.chip = add('chip', '<span></span>', ''); o.hud = add('hud', '<div class="l"></div><div class="v"></div><div class="s"></div>', ''); o.cap = add('cap', '', '');
  o.end = add('end', LOGO_SVG + '<div class="n">StudyCrest</div><div class="f">Follow for more.</div><div class="o">The study app that checks your working.<br><b>Free for 30 days</b> · promo code in bio</div>', '');
  o.badge = add('badge', LOGO_SVG + '<div><div class="n">StudyCrest</div><div class="o">Try it <b>free for 30 days</b><br>Promo code in bio</div></div>', '');
  o.set = (el, html) => { if (el._h !== html) { el._h = html; (el === o.chip ? el.firstChild : el).innerHTML = html; } };
  o.show = (el, a) => { el.style.opacity = a; el.style.visibility = a <= 0.001 ? 'hidden' : 'visible'; };
  o.hudSet = (l, v, s) => { const k = l + '|' + v + '|' + s; if (o.hud._k === k) return; o.hud._k = k; o.hud.children[0].textContent = l; o.hud.children[1].textContent = v; o.hud.children[2].textContent = s; };
  return o;
}
// captions: [[start, end, html], ...] -> html + alpha at time t
export function capAt(caps, t) { for (const c of caps) if (t >= c[0] && t < c[1]) return [c[2], Math.min(seg(t, c[0], c[0] + 0.18), 1 - seg(t, c[1] - 0.15, c[1]))]; return ['', 0]; }

// project a world point to pixel coordinates in the 1080x1920 frame
export function proj(v, cam) { const p = v.clone().project(cam); return [(p.x * 0.5 + 0.5) * 1080, (-p.y * 0.5 + 0.5) * 1920]; }

// ---------- render pipeline: supersampling + ambient occlusion + bloom + film grade. One per scene.
const _Q = new URLSearchParams(location.search); export const SS = +(_Q.get('ss') || 1.5); const _AO = _Q.get('ao') !== '0';
const GradeShader = { uniforms: { tDiffuse: { value: null }, sat: { value: 1.12 }, con: { value: 1.06 }, vig: { value: 0.0 }, warm: { value: 0.0 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
  fragmentShader: 'uniform sampler2D tDiffuse; uniform float sat; uniform float con; uniform float vig; uniform float warm; varying vec2 vUv; void main(){ vec4 c = texture2D(tDiffuse, vUv); float l = dot(c.rgb, vec3(0.2126,0.7152,0.0722)); c.rgb = mix(vec3(l), c.rgb, sat); c.rgb = (c.rgb - 0.5) * con + 0.5; c.rgb *= vec3(1.0 + warm, 1.0 + warm * 0.35, 1.0 - warm); gl_FragColor = c; }' };
export function makePost(renderer, scene, cam, opt = {}) {
  const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(1080 * SS, 1920 * SS, { type: THREE.HalfFloatType, samples: +(_Q.get('msaa') ?? 0) })); composer.setPixelRatio(SS); composer.setSize(1080, 1920);
  composer.addPass(new RenderPass(scene, cam)); let ao = null;
  if (opt.ao === true && _AO) { ao = new GTAOPass(scene, cam, 1080 * SS, 1920 * SS); ao.updateGtaoMaterial({ radius: opt.aoRadius ?? 0.9, distanceExponent: 1.4, thickness: 1.2, scale: opt.aoScale ?? 1.25, samples: 12, screenSpaceRadius: false }); ao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 6, rings: 2, samples: 12 }); ao.blendIntensity = opt.aoIntensity ?? 1.0; composer.addPass(ao); }
  const bloom = new UnrealBloomPass(new THREE.Vector2(1080, 1920), opt.bloom ?? 0.22, opt.bloomRadius ?? 0.6, opt.bloomThreshold ?? 0.92); if (_Q.get('bloom') !== '0' && opt.bloom !== 0) composer.addPass(bloom);
  composer.addPass(new OutputPass()); const grade = new ShaderPass(GradeShader); grade.uniforms.sat.value = opt.sat ?? 1.12; grade.uniforms.con.value = opt.con ?? 1.06; grade.uniforms.warm.value = opt.warm ?? 0.0; composer.addPass(grade);
  return { composer, bloom, ao, grade, render() { composer.render(); } };
}
export function skyEnv(renderer, top, mid, bot) { const s = new THREE.Scene(); s.add(skyDome(top, mid, bot)); const p = new THREE.PMREMGenerator(renderer); const t = p.fromScene(s, 0, 1, 2000).texture; p.dispose(); return t; }

// ---------- detailed city buildings
const _tiles = {};
function tileTex(style, night, seedR) {
  const k = style + night + Math.floor(seedR() * 4); if (_tiles[k]) return _tiles[k];
  const c = document.createElement('canvas'); c.width = 512; c.height = 512; const x = c.getContext('2d'), R = seedR, N = 8, cw = 512 / N;
  const P = { glass: ['#5f86ad', '#86b4dc', '#3f6690', '#a9d2f2'], glassg: ['#4f8f88', '#86cfc4', '#35706a', '#b5ece2'], office: ['#b9b2a6', '#7fa3c4', '#55708c', '#d9d2c6'], sand: ['#d6c3a0', '#8fb0cb', '#5c7890', '#efe0c0'], brick: ['#a5644c', '#9bb8cf', '#5b7488', '#c98a6e'], white: ['#e9e6df', '#8db3d6', '#56779a', '#ffffff'], dark: ['#4a505a', '#7d9cba', '#39506a', '#676f7c'] }[style];
  x.fillStyle = P[0]; x.fillRect(0, 0, 512, 512);
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) { const X = i * cw, Y = j * cw, r = R(); const lit = night ? r < 0.32 : r < 0.1; const col = lit ? (night ? ['#ffd98a', '#ffe9b8', '#ffc66a'][Math.floor(R() * 3)] : '#fff0c4') : (night ? '#10151f' : (style.startsWith('glass') ? (r < 0.8 ? P[1] : P[3]) : (r < 0.55 ? P[1] : P[2])));
    if (style.startsWith('glass')) { x.fillStyle = col; x.fillRect(X + 2, Y + 2, cw - 4, cw - 4); if (!night) { const g = x.createLinearGradient(X, Y, X + cw, Y + cw); g.addColorStop(0, 'rgba(255,255,255,.28)'); g.addColorStop(0.5, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(X + 2, Y + 2, cw - 4, cw - 4); } }
    else { x.fillStyle = col; x.fillRect(X + 12, Y + 14, cw - 24, cw - 30); x.fillStyle = 'rgba(0,0,0,.25)'; x.fillRect(X + 12, Y + cw - 16, cw - 24, 4); if (!night) { x.fillStyle = 'rgba(255,255,255,.2)'; x.fillRect(X + 12, Y + 14, (cw - 24) / 2, 8); } if (style === 'white' || style === 'sand') { x.fillStyle = P[3]; x.fillRect(X + 6, Y + cw - 12, cw - 12, 7); } } }
  if (!style.startsWith('glass')) { x.fillStyle = 'rgba(0,0,0,.10)'; for (let j = 0; j <= N; j++) x.fillRect(0, j * cw - 1, 512, 2); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; _tiles[k] = t; return t;
}
const STYLES = ['glass', 'glassg', 'office', 'sand', 'brick', 'white', 'dark', 'glass', 'office', 'white'];
export function tower(R, w, h, d, opt = {}) {
  const g = new THREE.Group(), style = opt.style || STYLES[Math.floor(R() * STYLES.length)], night = !!opt.night, glass = style.startsWith('glass'), base = tileTex(style, night, R), fl = 3.4, ww = 3.0;
  const sideMat = (len, hh) => { const t = base.clone(); t.needsUpdate = true; t.repeat.set(Math.max(1, Math.round(len / ww)) / 8, Math.max(1, Math.round(hh / fl)) / 8); t.offset.set(Math.floor(R() * 8) / 8, Math.floor(R() * 8) / 8);
    if (!glass) return new THREE.MeshLambertMaterial({ map: t, emissive: night ? 0xffffff : 0x000000, emissiveMap: night ? t : null, emissiveIntensity: night ? 0.9 : 0 });
    return new THREE.MeshStandardMaterial({ map: t, roughness: 0.2, metalness: 0.5, envMap: opt.env || null, envMapIntensity: 1.1, emissive: night ? 0xffffff : 0x000000, emissiveMap: night ? t : null, emissiveIntensity: night ? 0.9 : 0 }); };
  const roofC = glass ? 0x59626e : [0x8d8a84, 0x6f6c68, 0xa39c90][Math.floor(R() * 3)], roof = mat(roofC);
  const seg = (sw, sh, sd, y) => { const a = sideMat(sw, sh), b = sideMat(sd, sh), m = new THREE.Mesh(new THREE.BoxGeometry(sw, sh, sd), [b, b, roof, roof, a, a]); m.position.y = y + sh / 2; m.castShadow = true; m.receiveShadow = true; g.add(m); g.add(box(sw + 0.5, 0.5, sd + 0.5, roofC, 0, y + sh + 0.25, 0)); };
  const tiers = h > 40 && R() < 0.7 ? (h > 80 && R() < 0.5 ? 3 : 2) : 1; let y = 0, sw = w, sd = d;
  for (let i = 0; i < tiers; i++) { const sh = tiers === 1 ? h : (i === 0 ? h * (0.5 + R() * 0.15) : (h - y) * (i === tiers - 1 ? 1 : 0.6)); seg(sw, sh, sd, y); y += sh; sw *= 0.68 + R() * 0.12; sd *= 0.68 + R() * 0.12; }
  const tw = sw / 0.74, td = sd / 0.74;
  if (R() < 0.75) g.add(box(tw * 0.35, 1.8, td * 0.3, 0x9a9da3, (R() - 0.5) * tw * 0.3, y + 1.4, (R() - 0.5) * td * 0.3));
  if (R() < 0.5) { const wt = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 2.2, 8), mat(0x7a5a3c)); wt.position.set(tw * 0.25, y + 2.6, -td * 0.2); wt.castShadow = true; g.add(wt); g.add(box(0.15, 1.5, 0.15, 0x555555, tw * 0.25, y + 0.9, -td * 0.2)); }
  if (h > 55 && R() < 0.6) { g.add(box(0.35, h * 0.16, 0.35, 0xd0d0d0, 0, y + h * 0.08 + 0.5, 0)); if (night) { const l = new THREE.Mesh(new THREE.SphereGeometry(0.6, 6, 5), new THREE.MeshBasicMaterial({ color: 0xff3020 })); l.position.y = y + h * 0.16 + 0.8; g.add(l); } }
  g.userData = { h, w, d }; return g;
}
export function lamp() { const g = new THREE.Group(); g.add(box(0.14, 5, 0.14, 0x3a3f47, 0, 2.5, 0)); g.add(box(1.1, 0.1, 0.14, 0x3a3f47, 0.5, 5, 0)); g.add(box(0.5, 0.12, 0.26, 0xfff2c8, 0.95, 4.92, 0)); return shadowAll(g); }
