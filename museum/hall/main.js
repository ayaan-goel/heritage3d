// The walkable museum hall: reads artifacts.json, builds a rotunda and galleries for that many exhibits,
// loads each model onto its pedestal (nearest first) and handles walking and the 360° close-up.
// Test aids: ?fps shows the frame rate; ?repeat=N shows the collection N times (load test for a bigger
// museum); window.hall exposes stats and a teleport for measuring.
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { buildHall } from "./building.js";
import { CHARACTERS, buildCharacter } from "./character.js";
import { buildGate } from "./gate.js";
import { buildPortal } from "./portal.js";
import { infoCanvas, placardCanvas, signCanvas, teamBoardCanvas, titleBoardCanvas, upperBoardCanvas } from "./labels.js";
import { EYE, GALLERIES, GALLERY_W, PEDESTAL_TOP, ROTUNDA_R, planHall, toWorld } from "./layout.js";

const DISPLAY = 0.46;        // largest side of an exhibit on its pedestal, m (CHSD gives no real sizes)
const WALK = 2.2, RUN = 4.4; // m/s
const LOOK = 0.0022;         // radians per pixel of mouse movement
const REACH = 2.6;           // the 360° prompt appears within this distance of an exhibit, m
const FOV = 70, CLOSE_FOV = 42;
const BEHIND = 3;            // third-person camera's distance behind the visitor, m
const PANEL_SHIFT = 180;     // px the close-up view moves left to make room for the details panel

const params = new URLSearchParams(location.search);
const $ = (id) => document.getElementById(id);
const canvas = $("scene"), menu = $("menu"), enter = $("enter"), status = $("status");
const fmt = (x, d = 1) => Number(x).toLocaleString("en", { maximumFractionDigits: d, minimumFractionDigits: d });
const int = (x) => Number(x).toLocaleString("en");

function stop(message) {
  status.innerHTML = message;
  enter.hidden = true;
  throw new Error(status.textContent);
}

if (matchMedia("(pointer: coarse)").matches && !matchMedia("(any-pointer: fine)").matches) {
  document.body.classList.add("touch");  // phones and tablets get the List view instead
}

let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
} catch {
  stop('This browser cannot show the 3D hall (WebGL is off or unavailable). The <a href="list.html">List view</a> shows every exhibit.');
}
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.shadowMap.enabled = true;    // only the gate has a shadow-casting light; drawn once, nothing there moves
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.shadowMap.autoUpdate = false;
renderer.shadowMap.needsUpdate = true;
const aniso = Math.min(8, renderer.capabilities.getMaxAnisotropy());

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1c1915);
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.5;
scene.add(new THREE.HemisphereLight(0xfff4e4, 0x806f5c, 1.5));
const sun = new THREE.DirectionalLight(0xfff0d6, 1.2);
sun.position.set(3, 20, 5);
scene.add(sun);

const camera = new THREE.PerspectiveCamera(FOV, innerWidth / innerHeight, 0.05, 400);
camera.rotation.order = "YXZ";

let artifacts;
try {
  ({ artifacts } = await (await fetch("artifacts.json")).json());
  if (!artifacts.length) throw new Error("empty collection");
} catch (err) {
  stop(`Could not load the collection (${err.message}). Serve this folder over HTTP, e.g. <code>python -m http.server</code>.`);
}

// ---- the building and its pedestals --------------------------------------------------------------

const repeat = Math.min(5, Math.max(1, Math.round(Number(params.get("repeat"))) || 1));
const repeated = Array.from({ length: repeat }, () => artifacts).flat();
const upstairs = repeated.filter((e) => e.set === "cut_off");  // the set outside the main experiment
const entries = [...repeated.filter((e) => e.set !== "cut_off"), ...upstairs];
const plan = planHall(entries.length - upstairs.length, upstairs.length);
const numbers = (z) => (z.from === z.to ? `No. ${z.from}` : `Nos. ${z.from}–${z.to}`);
const signs = GALLERIES.map((g) => {
  const zone = plan.zones.find((z) => z.name === `${g.name} gallery`);
  return signCanvas(`${g.name} Gallery`, [g.heading === 0 && "Entrance", zone && numbers(zone)].filter(Boolean).join(" · "));
});
const upperZone = plan.zones.find((z) => z.name === "Upper floor");
const logo = new Image();
logo.src = "hall/pdeu-logo.png";
const logoReady = await logo.decode().then(() => logo, () => null);  // the board still shows without it
scene.add(buildHall(plan, {
  aniso,
  placards: entries.map((e, i) => placardCanvas(e, i + 1)),
  signs,
  info: infoCanvas(artifacts, plan.zones.map((z) => `${z.name}: ${numbers(z)}`)),
  boards: plan.boards.map((b) => (b.side < 0 ? titleBoardCanvas(logoReady, artifacts.length) : teamBoardCanvas())),
  stairSign: upperZone && signCanvas("Upper Floor", `Stairs · ${numbers(upperZone)}`),
  upperBoard: upperZone && upperBoardCanvas(upstairs, numbers(upperZone)),
}));

const gate = buildGate({ logo: logoReady, aniso, environment: scene.environment, plan });
const backToGate = buildPortal({ ...plan.exit, arrowY: 2.3, arrowScale: 1.1, aniso });
scene.add(backToGate.group);

const exhibits = entries.map((entry, i) => {
  const spot = plan.spots[i];
  const holder = new THREE.Group();
  holder.position.set(spot.x, spot.y + PEDESTAL_TOP, spot.z);
  holder.rotation.y = spot.yaw;
  scene.add(holder);
  return {
    entry, spot, holder, number: i + 1, state: "waiting",
    center: new THREE.Vector3(spot.x, spot.y + PEDESTAL_TOP + DISPLAY / 2, spot.z), size: new THREE.Vector3(),
  };
});

// ---- loading the models, nearest to the entrance first --------------------------------------------

const loader = new GLTFLoader();
const readySeconds = performance.now() / 1000;
let loaded = 0, loadSeconds = null, pendingId = null;
const dist2 = (a, b) => (a.x - b.x) ** 2 + (a.z - b.z) ** 2;
const queue = [...exhibits].sort((a, b) => dist2(a.spot, plan.spawn) - dist2(b.spot, plan.spawn));

// Bounds of the model's vertices without the outer 0.5 % on each axis, so a few stray reconstruction
// fragments do not shrink or shift the exhibit.
function robustBox(model) {
  model.updateMatrixWorld(true);
  const axes = [[], [], []], v = new THREE.Vector3();
  model.traverse((o) => {
    if (!o.isMesh) return;
    const pos = o.geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i).applyMatrix4(o.matrixWorld);
      axes[0].push(v.x);
      axes[1].push(v.y);
      axes[2].push(v.z);
    }
  });
  const [lo, hi] = [new THREE.Vector3(), new THREE.Vector3()];
  axes.forEach((values, a) => {
    const sorted = Float32Array.from(values).sort(), k = Math.floor(sorted.length * 0.005);
    lo.setComponent(a, sorted[k]);
    hi.setComponent(a, sorted[sorted.length - 1 - k]);
  });
  return new THREE.Box3(lo, hi);
}

function place(ex, model) {
  model.traverse((o) => {
    const map = o.isMesh && o.material.map;
    if (map) {  // the GLBs ask for no mipmaps; from across the hall they shimmer without them
      map.minFilter = THREE.LinearMipmapLinearFilter;
      map.generateMipmaps = true;
      map.anisotropy = aniso;
      map.needsUpdate = true;
    }
  });
  const box = robustBox(model), size = box.getSize(new THREE.Vector3()), centre = box.getCenter(new THREE.Vector3());
  const scale = DISPLAY / Math.max(size.x, size.y, size.z);
  model.scale.setScalar(scale);
  model.position.set(-centre.x * scale, -box.min.y * scale, -centre.z * scale);
  ex.holder.add(model);
  ex.size.copy(size).multiplyScalar(scale);
  ex.center.y = ex.spot.y + PEDESTAL_TOP + ex.size.y / 2;
  ex.state = "ready";
  if (pendingId === ex.entry.id) {
    pendingId = null;
    goTo(ex);
  }
}

const loadingEl = $("loading");
function loadNext() {
  const ex = queue.shift();
  if (!ex) return;
  ex.state = "loading";
  loader.loadAsync(ex.entry.model)
    .then((gltf) => place(ex, gltf.scene))
    .catch((err) => {
      ex.state = "failed";
      console.warn(`${ex.entry.id}: ${err.message}`);
    })
    .finally(() => {
      loaded++;
      loadingEl.querySelector("span").textContent = `${loaded} / ${exhibits.length}`;
      loadingEl.querySelector("i").style.width = `${(100 * loaded) / exhibits.length}%`;
      if (loaded === exhibits.length) {
        loadSeconds = performance.now() / 1000;
        loadingEl.classList.add("done");
      }
      loadNext();
    });
}

// ---- walking ---------------------------------------------------------------------------------------

const me = { x: gate.spawn.x, z: gate.spawn.z, yaw: gate.spawn.yaw, pitch: gate.spawn.pitch, vx: 0, vz: 0 };
const keys = new Set();
let mode = "menu";  // menu | walk | fly | closeup | fade
let outside = true; // at the main gate; false once inside the museum
document.body.classList.add("outside");
let entered = false, dragLook = false, target = null, current = null, saved = null;

function walk(dt) {
  const held = (...codes) => (codes.some((c) => keys.has(c)) ? 1 : 0);
  const f = held("KeyW", "ArrowUp") - held("KeyS", "ArrowDown");
  const r = held("KeyD", "ArrowRight") - held("KeyA", "ArrowLeft");
  let tx = 0, tz = 0;
  if (f || r) {
    const speed = (held("ShiftLeft", "ShiftRight") ? RUN : WALK) / Math.hypot(f, r);
    const sin = Math.sin(me.yaw), cos = Math.cos(me.yaw);
    tx = (-sin * f + cos * r) * speed;   // forward is (-sin, -cos), right is (cos, -sin)
    tz = (-cos * f - sin * r) * speed;
  }
  const k = 1 - Math.exp(-10 * dt);    // ease in and out of walking
  me.vx += (tx - me.vx) * k;
  me.vz += (tz - me.vz) * k;
  [me.x, me.z] = (outside ? gate : plan).move(me.x, me.z, me.vx * dt, me.vz * dt);
}

// ---- from the main gate into the museum --------------------------------------------------------------

const fade = $("fade");
const FADE_MS = 500;

function placeInHall() {
  outside = false;
  document.body.classList.remove("outside");
  Object.assign(me, { x: plan.spawn.x, z: plan.spawn.z, yaw: plan.spawn.yaw, pitch: -0.06, vx: 0, vz: 0 });
}

function placeAtGate() {
  outside = true;
  document.body.classList.add("outside");
  Object.assign(me, { ...gate.spawn, vx: 0, vz: 0 });
}

function travel(place) {
  mode = "fade";
  fade.classList.add("on");
  setTimeout(() => {
    place();
    behind = 0;
    fade.classList.remove("on");
    if (document.pointerLockElement === canvas || dragLook) mode = "walk";
    else showMenu();
  }, FADE_MS);
}

const floorAt = (x, z) => (outside ? 0 : plan.height(x, z));

const fwd = new THREE.Vector3(), toward = new THREE.Vector3();
function findTarget() {  // the exhibit in reach that the visitor is looking at
  camera.getWorldDirection(fwd);
  let best = null, bestScore = Infinity;
  for (const ex of exhibits) {
    const d = Math.hypot(ex.center.x - me.x, ex.center.z - me.z);
    if (d > REACH) continue;
    toward.set(ex.center.x - me.x, ex.center.y - floorAt(me.x, me.z) - EYE, ex.center.z - me.z).normalize();
    const angle = Math.acos(Math.min(1, fwd.dot(toward)));
    if (angle > (d < 1.3 ? 0.8 : 0.45)) continue;
    if (angle + d * 0.2 < bestScore) {
      best = ex;
      bestScore = angle + d * 0.2;
    }
  }
  return best;
}

const promptEl = $("prompt");
let promptKey = "", hint = "";
function showPrompt() {
  const key = target ? `${target.number}:${target.state}` : hint;
  if (key === promptKey) return;
  promptKey = key;
  promptEl.hidden = !key;
  if (!target) {
    promptEl.textContent = hint;
    return;
  }
  const name = `No. ${target.number} · ${target.entry.id}`;
  promptEl.innerHTML = {
    ready: `<kbd>E</kbd> 360° view <span>${name}</span>`,
    failed: `${name} could not be loaded`,
  }[target.state] ?? `${name} is loading…`;
}

// ---- menu and pointer lock ---------------------------------------------------------------------------

function showMenu() {
  mode = "menu";
  keys.clear();
  enter.textContent = entered ? "Resume" : "Start at the main gate";
  toGate.hidden = outside || !entered;
  menu.hidden = false;
}

function hideMenu() {
  menu.hidden = true;
  entered = true;
}

let lockPending = false, lockFailures = 0;
function requestLock() {
  lockPending = true;
  try {
    canvas.requestPointerLock()?.catch?.(lockFailed);
  } catch {
    lockFailed();
  }
}

// Some pages (embedded previews, sandboxed frames) never grant pointer lock; after the first entry fails,
// or a second request does, the hall switches to looking around by dragging with the mouse.
function lockFailed() {
  if (!lockPending || dragLook) return;  // browsers may report one failure twice
  lockPending = false;
  if (mode === "fly") {                  // returning from a close-up: the flight's end shows the menu
    lockFailures++;
    return;
  }
  if (entered && ++lockFailures < 2) return showMenu();
  dragLook = true;
  document.body.classList.add("drag");
  hideMenu();
  mode = "walk";
}

enter.addEventListener("click", () => {
  if (!dragLook) return requestLock();
  hideMenu();
  mode = "walk";
});

const toGate = $("to-gate");
toGate.addEventListener("click", () => {
  placeAtGate();
  if (!dragLook) return requestLock();
  hideMenu();
  mode = "walk";
});

document.addEventListener("pointerlockchange", () => {
  const locked = document.pointerLockElement === canvas;
  document.body.classList.toggle("locked", locked);
  if (locked) {
    lockPending = false;
    lockFailures = 0;
    hideMenu();
    if (mode === "menu") mode = "walk";
  } else if (mode === "walk") showMenu();
});
document.addEventListener("pointerlockerror", lockFailed);

addEventListener("mousemove", (e) => {
  if (mode !== "walk" || (document.pointerLockElement !== canvas && !(dragLook && e.buttons & 1))) return;
  const clamp = (x) => Math.max(-150, Math.min(150, x));  // browsers sometimes report a jump on lock
  me.yaw -= clamp(e.movementX) * LOOK;
  me.pitch = Math.max(-1.3, Math.min(1.3, me.pitch - clamp(e.movementY) * LOOK));
});

canvas.addEventListener("click", () => {
  if (mode === "walk" && target && !dragLook) openCloseup(target);
});

addEventListener("keydown", (e) => {
  if (e.code.startsWith("Arrow") || e.code === "Space") e.preventDefault();
  if (e.repeat) return;
  keys.add(e.code);
  if (e.code === "KeyE") {
    if (mode === "walk" && target) openCloseup(target);
    else if (mode === "closeup") closeCloseup(true);
  } else if (e.code === "Escape") {
    if (mode === "closeup") closeCloseup(false);
    else if (mode === "walk" && dragLook) showMenu();
  } else if (e.code === "KeyM") {
    map.hidden = !map.hidden;
  } else if (mode === "walk" && e.code === "KeyV") {
    third = !third;
    showWho();
  } else if (mode === "walk" && e.code === "KeyC") {
    wearing = (wearing + 1) % CHARACTERS.length;
    figure.wear(CHARACTERS[wearing]);
    showWho();
  }
});
addEventListener("keyup", (e) => keys.delete(e.code));
addEventListener("blur", () => keys.clear());

// ---- first or third person, and who the visitor is ---------------------------------------------------

const figure = buildCharacter();
let third = false, wearing = 0, behind = 0;
figure.wear(CHARACTERS[wearing]);
const whoEl = $("who");
function showWho() {
  whoEl.textContent = `${CHARACTERS[wearing].name} · ${third ? "third" : "first"} person`;
}
showWho();

// Distance the camera can stand behind (x, z) before a wall or an obstacle gets in its way.
function roomBehind(x, z, yaw, pitch) {
  const world = outside ? gate : plan;
  const dx = Math.sin(yaw) * Math.cos(pitch), dz = Math.cos(yaw) * Math.cos(pitch);
  let room = 0;
  for (let d = 0.25; d <= BEHIND; d += 0.25) {
    const [ax, az] = world.move(x, z, dx * d, dz * d);
    if (Math.hypot(ax - (x + dx * d), az - (z + dz * d)) > 0.02) break;
    room = d;
  }
  return room;
}

function viewFrom(x, z, yaw, pitch, distance) {
  const cx = x + Math.sin(yaw) * Math.cos(pitch) * distance, cz = z + Math.cos(yaw) * Math.cos(pitch) * distance;
  return new THREE.Vector3(
    cx,
    Math.max(floorAt(cx, cz) + 0.35, floorAt(x, z) + EYE + (distance > 0 ? 0.2 : 0) - Math.sin(pitch) * distance),
    cz,
  );
}

// ---- 360° close-up -----------------------------------------------------------------------------------

const orbit = new OrbitControls(camera, canvas);
orbit.enabled = false;
orbit.enableDamping = true;
orbit.autoRotateSpeed = 1.5;
orbit.minPolarAngle = 0.05;
orbit.maxPolarAngle = Math.PI * 0.62;
orbit.addEventListener("start", () => { orbit.autoRotate = false; });

let flight = null, shift = 0;
const eased = (t) => (t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2);
const lookAt = (from, at) => new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().lookAt(from, at, THREE.Object3D.DEFAULT_UP));

function setShift(f) {  // 0..1 of PANEL_SHIFT: centres the exhibit in the space left of the panel
  shift = f;
  const px = innerWidth > 640 ? f * PANEL_SHIFT : 0;
  if (px > 0.5) camera.setViewOffset(innerWidth, innerHeight, px, 0, innerWidth, innerHeight);
  else camera.clearViewOffset();
  camera.updateProjectionMatrix();
}

function fly(pos, quat, fov, toShift, seconds, done) {
  flight = {
    from: { pos: camera.position.clone(), quat: camera.quaternion.clone(), fov: camera.fov, shift },
    to: { pos, quat, fov, shift: toShift }, t: 0, seconds, done,
  };
}

function stepFlight(dt) {
  flight.t = Math.min(1, flight.t + dt / flight.seconds);
  const e = eased(flight.t), { from, to } = flight;
  camera.position.lerpVectors(from.pos, to.pos, e);
  camera.quaternion.slerpQuaternions(from.quat, to.quat, e);
  camera.fov = from.fov + (to.fov - from.fov) * e;
  setShift(from.shift + (to.shift - from.shift) * e);
  if (flight.t === 1) {
    const { done } = flight;
    flight = null;
    done();
  }
}

const panel = $("panel"), panelBody = $("panel-body");
$("back").addEventListener("click", () => closeCloseup(true));

function openCloseup(ex) {
  if (ex.state !== "ready") return;
  current = ex;
  saved = { x: me.x, z: me.z, yaw: me.yaw, pitch: me.pitch };
  mode = "fly";
  if (document.pointerLockElement) document.exitPointerLock();
  const radius = Math.max(ex.size.x, ex.size.y, ex.size.z) / 2;
  const distance = Math.max(0.8, radius * 5.2);  // fills most of the narrower close-up lens
  const away = new THREE.Vector3(me.x - ex.center.x, 0, me.z - ex.center.z).normalize();
  const pos = ex.center.clone().addScaledVector(away, distance).setY(ex.center.y + distance * 0.3);

  const e = ex.entry;
  panelBody.innerHTML = `
    <p class="no">No. ${ex.number}</p>
    <h2>${e.id}</h2>
    <p class="tag">Digitized from ${e.input_images} photographs (${e.level})</p>
    <dl>
      <dt>Reconstruction</dt><dd>${fmt(e.reconstruction_min)} min, laptop CPU</dd>
      <dt>Museum model</dt><dd>${int(e.faces)} triangles</dd>
      <dt>Download size</dt><dd>${fmt(e.glb_mb)} MB</dd>
      <dt>Full model</dt><dd>${int(e.full_faces)} tri, ${fmt(e.full_glb_mb)} MB</dd>
      <dt>Accuracy F@0.002 R</dt><dd>${fmt(e["f@0.002"], 3)}</dd>
      <dt>Full model F@0.002 R</dt><dd>${fmt(e["full_f@0.002"], 3)}</dd>
      ${e.set === "cut_off" ? `<dt>Touches the frame</dt><dd>${Math.round(e.cut_off_fraction * 100)}% of sample views</dd>` : ""}
    </dl>`;
  panel.hidden = false;
  document.body.classList.add("closeup");
  history.replaceState(null, "", `#${encodeURIComponent(e.id)}`);

  fly(pos, lookAt(pos, ex.center), CLOSE_FOV, 1, 0.8, () => {
    mode = "closeup";
    orbit.target.copy(ex.center);
    orbit.minDistance = radius * 1.4;
    orbit.maxDistance = Math.max(1.6, radius * 6);
    orbit.enabled = true;
    orbit.autoRotate = true;
    orbit.update();
  });
}

function closeCloseup(relock) {
  if (mode !== "closeup") return;
  mode = "fly";
  orbit.enabled = false;
  orbit.autoRotate = false;
  panel.hidden = true;
  document.body.classList.remove("closeup");
  history.replaceState(null, "", location.pathname + location.search);
  if (relock && !dragLook) requestLock();
  const quat = new THREE.Quaternion().setFromEuler(new THREE.Euler(saved.pitch, saved.yaw, 0, "YXZ"));
  const room = third ? roomBehind(saved.x, saved.z, saved.yaw, saved.pitch) : 0;
  fly(viewFrom(saved.x, saved.z, saved.yaw, saved.pitch, room), quat, FOV, 0, 0.6, () => {
    behind = room;
    Object.assign(me, saved, { vx: 0, vz: 0 });
    current = null;
    if (document.pointerLockElement === canvas || dragLook) mode = "walk";
    else showMenu();
  });
}

function keepTarget() {  // panning may move the pivot a little, but not away from the exhibit
  const off = orbit.target.clone().sub(current.center);
  if (off.length() > 0.2) orbit.target.copy(current.center).add(off.setLength(0.2));
}

// a link to list.html#<id> or index.html#<id> opens that exhibit's close-up
function goTo(ex) {
  const fx = Math.sin(ex.spot.yaw), fz = Math.cos(ex.spot.yaw);
  placeInHall();
  Object.assign(me, { x: ex.spot.x + fx * 1.5, z: ex.spot.z + fz * 1.5, yaw: Math.atan2(fx, fz), pitch: -0.25 });
  camera.position.set(me.x, floorAt(me.x, me.z) + EYE, me.z);
  camera.rotation.set(me.pitch, me.yaw, 0);
  hideMenu();
  openCloseup(ex);
}

function followHash() {
  const ex = exhibits.find((x) => x.entry.id === decodeURIComponent(location.hash.slice(1)));
  if (!ex || ex === current) return;
  if (ex.state === "ready") return goTo(ex);
  pendingId = ex.entry.id;  // opened by place() once loaded; load it next
  const i = queue.indexOf(ex);
  if (i > 0) queue.unshift(...queue.splice(i, 1));
}
addEventListener("hashchange", () => {
  if (mode === "menu" || mode === "walk") followHash();
});

// ---- map ---------------------------------------------------------------------------------------------

const map = $("map"), MAP = 176, mapScale = (MAP / 2 - 8) / plan.extent, dpr = Math.min(2, devicePixelRatio);
const mapCtx = map.getContext("2d");
map.width = map.height = MAP * dpr;
const toMap = (x, z) => [MAP / 2 + x * mapScale, MAP / 2 + z * mapScale];
const mapBase = (() => {
  const c = document.createElement("canvas"), g = c.getContext("2d");
  c.width = c.height = MAP * dpr;
  g.scale(dpr, dpr);
  g.fillStyle = "rgba(243, 233, 214, 0.18)";
  g.strokeStyle = "rgba(243, 233, 214, 0.6)";
  for (const gal of plan.rooms) {
    const corners = [[gal.start, -1], [gal.end, -1], [gal.end, 1], [gal.start, 1]].map(([s, v]) => {
      const [x, z] = toWorld(gal.heading, s, (v * GALLERY_W) / 2);
      return toMap(x + (gal.x ?? 0), z + (gal.z ?? 0));
    });
    g.beginPath();
    corners.forEach(([x, y]) => g.lineTo(x, y));
    g.closePath();
    g.fill();
    g.stroke();
  }
  g.beginPath();
  g.arc(MAP / 2, MAP / 2, ROTUNDA_R * mapScale, 0, Math.PI * 2);
  g.fill();
  g.stroke();
  g.fillStyle = "rgba(224, 169, 109, 0.95)";
  for (const s of plan.spots) {
    const [x, y] = toMap(s.x, s.z);
    g.fillRect(x - 1.5, y - 1.5, 3, 3);
  }
  const [exitX, exitY] = toMap(plan.exit.x, plan.exit.z);
  g.fillStyle = "#ffd21f";
  g.beginPath();
  g.arc(exitX, exitY, 3, 0, Math.PI * 2);
  g.fill();
  return c;
})();

function drawMap() {
  if (map.hidden) return;
  mapCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
  mapCtx.clearRect(0, 0, MAP, MAP);
  mapCtx.drawImage(mapBase, 0, 0, MAP, MAP);
  const near = target ?? current;
  if (near) {
    const [x, y] = toMap(near.spot.x, near.spot.z);
    mapCtx.strokeStyle = "#fff";
    mapCtx.beginPath();
    mapCtx.arc(x, y, 4.5, 0, Math.PI * 2);
    mapCtx.stroke();
  }
  const [x, y] = toMap(me.x, me.z), dx = -Math.sin(me.yaw), dy = -Math.cos(me.yaw);
  mapCtx.fillStyle = "#fff";
  mapCtx.beginPath();
  mapCtx.moveTo(x + dx * 7, y + dy * 7);
  mapCtx.lineTo(x - dx * 4 - dy * 4, y - dy * 4 + dx * 4);
  mapCtx.lineTo(x - dx * 4 + dy * 4, y - dy * 4 - dx * 4);
  mapCtx.fill();
}

// ---- main loop ---------------------------------------------------------------------------------------

const fpsEl = $("fps");
fpsEl.hidden = !params.has("fps");
let frames = 0, fps = 0, fpsSince = performance.now();

addEventListener("resize", () => {
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth / innerHeight;
  setShift(shift);
});

const clock = new THREE.Clock();
renderer.setAnimationLoop(() => {
  const dt = Math.min(clock.getDelta(), 0.05);
  if (mode === "walk") walk(dt);
  if (mode === "walk" || mode === "menu") {
    const room = third ? roomBehind(me.x, me.z, me.yaw, me.pitch) : 0;
    behind = room < behind ? room : behind + (room - behind) * Math.min(1, dt * 6);  // in at once, out gently
    camera.position.copy(viewFrom(me.x, me.z, me.yaw, me.pitch, behind));
    camera.rotation.set(me.pitch, me.yaw, 0);
  }
  const world = outside ? gate.scene : scene;
  if (figure.group.parent !== world) world.add(figure.group);
  figure.group.visible = third && behind > 1 && (mode === "walk" || mode === "menu");
  figure.pose(me.x, me.z, me.yaw, Math.hypot(me.vx, me.vz), dt, floorAt(me.x, me.z));
  if (flight) stepFlight(dt);
  if (mode === "closeup") {
    orbit.update(dt);
    keepTarget();
  }
  hint = "";
  if (outside) {
    gate.animate(clock.elapsedTime);
    if (mode === "walk" && gate.atPortal(me.x, me.z)) travel(placeInHall);
    else if (mode === "walk" && gate.distance(me.x, me.z) < 9) hint = "Walk into the yellow arrow to enter the museum";
  } else {
    backToGate.animate(clock.elapsedTime);
    const away = Math.hypot(me.x - plan.exit.x, me.z - plan.exit.z);
    if (mode === "walk" && away < plan.exit.r - 0.14) travel(placeAtGate);
    else if (mode === "walk" && away < 3.5) hint = "Walk into the yellow arrow to go back to the main gate";
  }
  target = mode === "walk" && !outside ? findTarget() : null;
  showPrompt();
  if (!outside) drawMap();
  renderer.render(outside ? gate.scene : scene, camera);

  frames++;
  const now = performance.now();
  if (now - fpsSince >= 1000) {
    fps = (frames * 1000) / (now - fpsSince);
    frames = 0;
    fpsSince = now;
    fpsEl.textContent = `${fps.toFixed(0)} fps`;
  }
});

window.hall = {
  plan,
  stats: () => ({
    fps: Math.round(fps), exhibits: exhibits.length, loaded,
    readySeconds: +readySeconds.toFixed(2), loadSeconds: loadSeconds && +loadSeconds.toFixed(2),
    drawCalls: renderer.info.render.calls, triangles: renderer.info.render.triangles,
    textures: renderer.info.memory.textures, pixelRatio: renderer.getPixelRatio(),
  }),
  gate,
  where: () => (outside ? "gate" : "hall"),
  view: () => ({ third, behind: +behind.toFixed(2), wearing: CHARACTERS[wearing].name, figure: figure.group.visible }),
  teleport(x, z, yaw = me.yaw, pitch = me.pitch) {
    placeInHall();
    Object.assign(me, { x, z, yaw, pitch, vx: 0, vz: 0 });
  },
  teleportGate(x, z, yaw = me.yaw, pitch = me.pitch) {
    Object.assign(me, { x, z, yaw, pitch, vx: 0, vz: 0 });
  },
  closeup: (n) => openCloseup(exhibits[n - 1]),
};

followHash();
for (let i = 0; i < 3; i++) loadNext();
status.textContent = `${exhibits.length} exhibits in a domed rotunda, four galleries${upstairs.length ? " and an upper floor" : ""}, past the main gate.`;
enter.disabled = false;
