// RQ3 benchmark: for every exhibit, the museum model against the full L3 model. Timed frames are drawn into an
// offscreen 1280 x 720 target (no anti-aliasing) and each is followed by a one-pixel read, which waits for the GPU,
// so frame times are the real work and not tied to the screen's refresh. The canvas shows the last model only.
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const params = new URLSearchParams(location.search);
const MBPS = Number(params.get("mbps")) || 0;
const REPEAT = Number(params.get("repeat")) || 3;
const FRAMES = 240, BATCH = 30;
const status = document.getElementById("status");
const canvas = document.getElementById("view");

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
renderer.setPixelRatio(1);
renderer.setSize(1280, 720, false);
renderer.toneMapping = THREE.NeutralToneMapping;
const gl = renderer.getContext();
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1c1915);
scene.add(new THREE.HemisphereLight(0xfff4e4, 0x806f5c, 1.5));
const camera = new THREE.PerspectiveCamera(42, 1280 / 720, 0.01, 100);
const loader = new GLTFLoader();
const pixel = new Uint8Array(4);
const median = (xs) => { const s = [...xs].sort((a, b) => a - b); const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const target = new THREE.WebGLRenderTarget(1280, 720);
const finish = () => renderer.readRenderTargetPixels(target, 0, 0, 1, 1, pixel);
const draw = () => {
  renderer.setRenderTarget(target);
  renderer.render(scene, camera);
  finish();
  renderer.setRenderTarget(null);
};

function gpuBytes(root) {  // geometry buffers, plus textures as RGBA with a full mipmap chain
  let geometry = 0, texture = 0, triangles = 0, textureSide = 0;
  root.traverse((o) => {
    if (!o.isMesh) return;
    for (const a of Object.values(o.geometry.attributes)) geometry += a.array.byteLength;
    if (o.geometry.index) geometry += o.geometry.index.array.byteLength;
    triangles += (o.geometry.index ? o.geometry.index.count : o.geometry.attributes.position.count) / 3;
    const img = o.material.map?.image;
    if (img) {
      texture += img.width * img.height * 4 * (4 / 3);
      textureSide = Math.max(textureSide, img.width, img.height);
    }
  });
  return { geometry, texture, triangles, textureSide };
}

async function measure(url) {
  const out = {};
  let t = performance.now();
  const buffer = await (await fetch(url + (MBPS ? `?mbps=${MBPS}` : ""), { cache: "no-store" })).arrayBuffer();
  out.download_ms = performance.now() - t;
  out.bytes = buffer.byteLength;
  if (MBPS) return out;

  t = performance.now();
  const gltf = await loader.parseAsync(buffer, "");
  out.decode_ms = performance.now() - t;
  const root = gltf.scene;
  root.traverse((o) => {  // as the hall does: mipmaps on, so distant views do not shimmer
    const map = o.isMesh && o.material.map;
    if (map) {
      map.minFilter = THREE.LinearMipmapLinearFilter;
      map.generateMipmaps = true;
      map.needsUpdate = true;
    }
  });
  Object.assign(out, gpuBytes(root));
  const sphere = new THREE.Box3().setFromObject(root).getBoundingSphere(new THREE.Sphere());
  scene.add(root);
  const distance = sphere.radius / Math.sin(THREE.MathUtils.degToRad(21)) * 1.05;
  const place = (a) => {
    camera.position.set(sphere.center.x + Math.sin(a) * distance, sphere.center.y + distance * 0.3, sphere.center.z + Math.cos(a) * distance);
    camera.lookAt(sphere.center);
  };

  t = performance.now();
  place(0);
  draw();
  out.first_frame_ms = performance.now() - t;  // GPU upload, mipmaps and shader setup, then one draw

  // the browser paces each read-back to the display, so time BATCH draws per read-back and divide
  const frames = [];
  renderer.setRenderTarget(target);
  for (let i = 0; i < FRAMES / BATCH; i++) {
    t = performance.now();
    for (let k = 0; k < BATCH; k++) {
      place(((i * BATCH + k) / FRAMES) * Math.PI * 2);
      renderer.render(scene, camera);
    }
    finish();
    frames.push((performance.now() - t) / BATCH);
  }
  renderer.setRenderTarget(null);
  renderer.render(scene, camera);  // to the canvas, so the page shows what was measured
  out.frame_ms_median = median(frames);
  out.frame_ms_max = Math.max(...frames);

  scene.remove(root);
  root.traverse((o) => {
    if (!o.isMesh) return;
    o.geometry.dispose();
    o.material.map?.dispose();
    o.material.dispose();
  });
  renderer.renderLists.dispose();
  return out;
}

const ids = (await (await fetch("list")).json()).filter((id) => !params.get("only") || id === params.get("only"));
const debug = gl.getExtension("WEBGL_debug_renderer_info");
const results = {
  started: new Date().toISOString(), mbps: MBPS, repeat: REPEAT, frames: FRAMES, canvas: [1280, 720],
  gpu: debug ? gl.getParameter(debug.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER), user_agent: navigator.userAgent, models: [],
};
for (let i = 0; i < ids.length; i++) {
  for (const kind of ["museum", "full"]) {
    const url = kind === "museum" ? `museum/models/${ids[i]}.glb` : `full/${ids[i]}.glb`;
    const runs = [];
    for (let r = 0; r < REPEAT; r++) {
      status.textContent = `${i + 1} / ${ids.length} · ${ids[i]} · ${kind} · run ${r + 1} of ${REPEAT}`;
      runs.push(await measure(url));
    }
    const row = { id: ids[i], kind };
    for (const key of Object.keys(runs[0])) row[key] = median(runs.map((x) => x[key]));
    results.models.push(row);
  }
}
results.finished = new Date().toISOString();
const name = `bench_${MBPS ? `${MBPS}mbps` : "local"}${params.get("only") ? "_test" : ""}`;
await fetch(`result?name=${name}`, { method: "POST", body: JSON.stringify(results) });
status.textContent = `Done: ${results.models.length} measurements saved as ${name}.json`;
window.benchDone = true;
