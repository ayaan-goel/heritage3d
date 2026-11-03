// The university's main gate and the street in front of it, where a visit starts: an outdoor scene of its own,
// modelled by hand from reference photos (sizes estimated from them, not surveyed; no photo is used as a
// texture). Walking into the yellow arrow enters the museum.
// Visitors stand south of the gate (+z) and look north (-z). Metres, y up, the gate line is z = 0. From the gate
// southwards: granite forecourt, cobbled plaza where the road passes, service road, median, main road, footpath
// and fence, open scrub, and the elevated metro viaduct.
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { BODY } from "./layout.js";
import * as T from "./textures.js";

const SERIF = 'Georgia, "Times New Roman", serif';
const SANS = 'system-ui, "Segoe UI", Roboto, sans-serif';
const HALF_W = 8;         // canopy half width
const CANOPY = { y0: 4.7, y1: 5.8, depth: 2.2 };
const BLOCK = { w: 1.2, h: 2.1 };   // half width and height of the centre block with the university's name
const PIER_X = 5.5;       // inner face of the piers carrying the canopy
const PORTAL = { x: 0, z: 3.2, r: 1.1 };  // the arrow; stepping inside this circle enters the museum
const ARROW_Y = 3;        // height of the arrow's centre: above the block, against the open sky
const FAR = 150;          // how far the street runs either way

const PLAZA_X = 26;       // half width of the forecourt and the cobbled plaza
const FORECOURT = 7;      // forecourt ends, plaza and service road start
const MEDIAN = [14.5, 16];
const FOOTPATH = 24;      // main road ends, footpath starts
const FENCE = 28;
const VIADUCT = { z0: 56, z1: 66, y0: 9.5, y1: 11 };
const WALK = { x: 58, zGate: 1.85, zBikes: 3.1, zMax: FENCE - 0.4 };

function random(seed) {
  let s = seed;
  return () => {
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// a ground slab with its texture tiling every `tile` metres
function slab(x0, x1, z0, z1, y, tile) {
  const g = new THREE.PlaneGeometry(x1 - x0, z1 - z0).rotateX(-Math.PI / 2).translate((x0 + x1) / 2, y, (z0 + z1) / 2);
  const uv = g.attributes.uv;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, (uv.getX(i) * (x1 - x0)) / tile, (uv.getY(i) * (z1 - z0)) / tile);
  return g;
}

function box(x0, x1, y0, y1, z0, z1, tile = 3) {
  const w = x1 - x0, h = y1 - y0, d = z1 - z0;
  const g = new THREE.BoxGeometry(w, h, d).translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
  const uv = g.attributes.uv;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, (uv.getX(i) * Math.max(w, d)) / tile, (uv.getY(i) * h) / tile);
  return g;
}

const post = (x, z, r0, r1, h, y = 0) => new THREE.CylinderGeometry(r1, r0, h, 12).translate(x, y + h / 2, z);

const sharedAttributes = (g) => {
  const out = g.index ? g.toNonIndexed() : g;
  if (!out.attributes.color) {
    out.setAttribute("color", new THREE.BufferAttribute(new Float32Array(out.attributes.position.count * 3).fill(1), 3));
  }
  return out;
};

function skyTexture(aniso) {
  const c = T.vertical(1024, 512, [[0, "#6a86ad"], [0.3, "#8ea4c0"], [0.45, "#c3c8cb"], [0.5, "#dcd8cc"], [1, "#dcd8cc"]]);
  const g = c.getContext("2d"), rand = random(21);
  for (let i = 0; i < 16; i++) {  // thin high haze
    const x = rand() * 1024, y = 110 + rand() * 110, size = 24 + rand() * 50;
    for (let k = 0; k < 6; k++) {
      const px = x + (rand() - 0.5) * size * 3.4, py = y + (rand() - 0.5) * size * 0.4, r = size * (0.5 + rand() * 0.5);
      for (const wrap of [-1024, 0, 1024]) {  // drawn again across the edge, so the sky has no seam
        const puff = g.createRadialGradient(px + wrap, py, 0, px + wrap, py, r);
        puff.addColorStop(0, "rgba(255,255,255,0.22)");
        puff.addColorStop(1, "rgba(255,255,255,0)");
        g.fillStyle = puff;
        g.fillRect(px + wrap - r, py - r, r * 2, r * 2);
      }
    }
  }
  const t = T.texture(c, aniso);
  t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

// the plaza: small dark setts with bands of pale stone curling across them
function cobbles(widthM, depthM) {
  const px = 40, w = widthM * px, h = depthM * px;
  const c = T.canvas(w, h), g = c.getContext("2d"), rand = random(17);
  g.fillStyle = "#3f3d3a";
  g.fillRect(0, 0, w, h);
  const stone = 7;
  for (let y = 0; y < h; y += stone) {
    for (let x = (y / stone) % 2 ? 0 : stone / 2; x < w; x += stone) {
      const v = 78 + rand() * 42;
      g.fillStyle = `rgb(${v}, ${v * 0.98}, ${v * 0.94})`;
      g.fillRect(x, y, stone - 1.5, stone - 1.5);
    }
  }
  g.strokeStyle = "rgba(160, 155, 142, 0.85)";
  g.lineCap = "round";
  g.lineWidth = 0.34 * px;
  for (let row = 0; row * 5.2 < depthM + 3; row++) {
    for (let col = 0; col * 9 < widthM + 5; col++) {
      const x = (col * 9 + (row % 2) * 4.5 + (rand() - 0.5)) * px, y = (row * 5.2 + 1.5 + (rand() - 0.5)) * px;
      const rx = (3 + rand()) * px, ry = rx * (0.48 + rand() * 0.12);
      const start = rand() * Math.PI * 2;
      g.beginPath();
      g.ellipse(x, y, rx, ry, 0, start, start + Math.PI * (1.5 + rand() * 0.5));
      g.stroke();
      g.beginPath();
      g.ellipse(x, y, rx * 0.5, ry * 0.5, 0, start + 1, start + 1 + Math.PI * (1.2 + rand() * 0.8));
      g.stroke();
    }
  }
  return c;
}

function pavers(color, joint, seed, n = 4) {  // square paving with thin joints
  const c = T.plaster(512, color, seed), g = c.getContext("2d");
  g.strokeStyle = joint;
  g.lineWidth = 3;
  for (let i = 0; i <= n; i++) {
    const at = (i * 512) / n;
    g.beginPath();
    g.moveTo(at, 0);
    g.lineTo(at, 512);
    g.moveTo(0, at);
    g.lineTo(512, at);
    g.stroke();
  }
  return c;
}

function bands(stops) {  // a post painted in horizontal bands, top first
  const c = T.canvas(16, 96), g = c.getContext("2d");
  stops.forEach((color, i) => {
    g.fillStyle = color;
    g.fillRect(0, (i * 96) / stops.length, 16, 96 / stops.length + 1);
  });
  return c;
}

// largest font of this family at which the text stays within maxWidth
function fitFont(g, text, maxWidth, size, style = "", family = SERIF) {
  let px = size;
  do g.font = `${style} ${px}px ${family}`; while (g.measureText(text).width > maxWidth && --px > 10);
}

function fasciaLetters() {
  const c = T.canvas(2048, 140), g = c.getContext("2d");
  g.textAlign = "center";
  g.textBaseline = "middle";
  g.letterSpacing = "9px";
  fitFont(g, "PANDIT DEENDAYAL ENERGY UNIVERSITY", 1940, 84, "bold");
  g.fillStyle = "rgba(60, 50, 38, 0.65)";  // the letters stand off the wall and cast a thin shadow
  g.fillText("PANDIT DEENDAYAL ENERGY UNIVERSITY", 1027, 77);
  g.fillStyle = "#eef0f0";
  g.fillText("PANDIT DEENDAYAL ENERGY UNIVERSITY", 1024, 73);
  return c;
}

function blockPlate(logo) {
  const c = T.canvas(640, 560), g = c.getContext("2d");
  if (logo) {
    g.fillStyle = "#2c2a28";
    g.fillRect(250, 60, 140, 140);
    const h = 112, w = (logo.width / logo.height) * h;
    g.drawImage(logo, 320 - w / 2, 74, w, h);
  }
  g.textAlign = "center";
  g.fillStyle = "#4e4638";
  g.letterSpacing = "2px";
  fitFont(g, "ENERGY UNIVERSITY", 560, 56, "600");
  g.fillText("PANDIT DEENDAYAL", 320, 300);
  g.fillText("ENERGY UNIVERSITY", 320, 372);
  return c;
}

function instituteSign() {
  const c = T.canvas(640, 256), g = c.getContext("2d");
  g.textAlign = "center";
  g.fillStyle = "#3e3a32";
  fitFont(g, "SCHOOL OF TECHNOLOGY", 560, 46, "600", SANS);
  g.fillText("SCHOOL OF TECHNOLOGY", 320, 90);
  fitFont(g, "RESEARCH AND MANAGEMENT INSTITUTE", 580, 36, "600", SANS);
  g.fillText("GUJARAT ENERGY", 320, 150);
  g.fillText("RESEARCH AND MANAGEMENT INSTITUTE", 320, 196);
  return c;
}

function bankSign() {
  const c = T.canvas(512, 128), g = c.getContext("2d");
  g.fillStyle = "#2c2c78";
  g.fillRect(0, 0, 512, 128);
  g.textAlign = "center";
  g.textBaseline = "middle";
  g.fillStyle = "#f4f4fa";
  g.font = `700 72px ${SANS}`;
  g.fillText("SBI", 150, 68);
  g.font = `500 54px ${SANS}`;
  g.fillText("ATM", 340, 70);
  return c;
}

function awningTexture() {
  const c = T.canvas(256, 64), g = c.getContext("2d");
  for (let i = 0; i < 16; i++) {
    g.fillStyle = i % 2 ? "#f0e6cf" : "#8c5a33";
    g.fillRect(i * 16, 0, 16, 64);
  }
  return c;
}

function arrowGeometry() {  // points down
  const s = new THREE.Shape();
  [[-0.17, 0.62], [0.17, 0.62], [0.17, 0.08], [0.44, 0.08], [0, -0.62], [-0.44, 0.08], [-0.17, 0.08]]
    .forEach(([x, y], i) => (i ? s.lineTo(x, y) : s.moveTo(x, y)));
  s.closePath();
  return new THREE.ExtrudeGeometry(s, { depth: 0.14, bevelEnabled: true, bevelSize: 0.025, bevelThickness: 0.025, bevelSegments: 2 }).center();
}

export function buildGate({ logo, aniso, environment }) {
  const scene = new THREE.Scene();
  scene.environment = environment;
  scene.environmentIntensity = 0.35;
  scene.fog = new THREE.Fog(0xd8d4c8, 70, 260);  // the afternoon haze over the far end of the street
  scene.add(new THREE.HemisphereLight(0xd9e2ef, 0x8f8676, 1.1));
  const sun = new THREE.DirectionalLight(0xfff0da, 1.75);
  sun.position.set(-60, 90, 34);
  sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  Object.assign(sun.shadow.camera, { left: -85, right: 85, top: 85, bottom: -85, near: 1, far: 260 });
  sun.shadow.camera.updateProjectionMatrix();
  sun.shadow.bias = -0.0006;
  sun.shadow.normalBias = 0.05;
  scene.add(sun);

  const tile = (c, size = 1) => T.texture(c, aniso, [size, size]);
  const std = (map, roughness, extra = {}) => new THREE.MeshStandardMaterial({ map, roughness, metalness: 0, ...extra });
  const plain = (color, roughness = 0.8, metalness = 0) => new THREE.MeshStandardMaterial({ color, roughness, metalness });
  const painted = (stops) => {
    const map = T.texture(bands(stops), aniso);
    map.wrapS = map.wrapT = THREE.ClampToEdgeWrapping;
    return std(map, 0.7);
  };
  const cobbleMap = T.texture(cobbles(PLAZA_X * 2, FOOTPATH - FORECOURT), aniso);
  cobbleMap.wrapS = cobbleMap.wrapT = THREE.ClampToEdgeWrapping;
  const M = {
    beige: std(tile(T.plaster(512, "#c9a878", 5)), 0.9),
    pale: std(tile(T.plaster(512, "#c9c0ae", 7)), 0.9),
    wall: std(tile(T.plaster(512, "#c8bb9f", 12)), 0.92),
    block: std(tile(T.plaster(512, "#cdb48c", 9)), 0.9),
    granite: std(tile(pavers("#a8a398", "rgba(70, 66, 58, 0.5)", 11)), 0.92),
    cobbles: std(cobbleMap, 0.95),
    road: std(tile(pavers("#a3a096", "rgba(70, 66, 58, 0.45)", 4, 1)), 0.95),
    pink: std(tile(pavers("#a9806f", "rgba(70, 48, 38, 0.45)", 13, 6)), 0.95),
    footpath: std(tile(pavers("#8f8c84", "rgba(50, 48, 42, 0.5)", 14, 8)), 0.95),
    soil: std(tile(T.plaster(512, "#6d5b3f", 15)), 1),
    grass: std(tile(T.plaster(512, "#8b8c50", 6)), 1),
    lawn: std(tile(T.plaster(512, "#64803f", 8)), 1),
    hedge: std(tile(T.plaster(512, "#47702f", 3)), 1),
    concrete: std(tile(T.plaster(512, "#a8a59d", 16)), 0.95),
    tricolour: painted(["#d8742a", "#ece8df", "#2f8146"]),
    hazard: painted(["#1e1e1e", "#e5b714", "#1e1e1e", "#e5b714", "#1e1e1e", "#e5b714", "#1e1e1e"]),
    white: plain(0xece8df),
    marking: plain(0xe8e6dd),
    maroon: plain(0x6d2b2a, 0.55, 0.15),
    dark: plain(0x31363a, 0.3, 0.2),
    black: plain(0x202326, 0.6, 0.3),
    steel: plain(0x8c9092, 0.5, 0.5),
    pole: plain(0x9a9d9e, 0.55, 0.4),
    blue: plain(0x2a4f8a, 0.5),
    slate: plain(0x5e646a, 0.7),
    yellow: plain(0xd8b43a, 0.7),
    wood: plain(0xb08f62, 0.85),
    pot: plain(0xb4623a, 0.85),
    orange: plain(0xc96a26, 0.7),
    sail: plain(0xe2d9c0, 0.9),
    trunk: plain(0x5b4a39, 1),
    tower: plain(0xbdb7aa, 0.9),
    leaves: new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 1, flatShading: true }),
  };
  M.sail.side = THREE.DoubleSide;
  const FLAT = new Set(["grass", "lawn", "granite", "cobbles", "road", "pink", "footpath", "soil", "marking"]);
  const parts = new Map();
  const add = (name, geometry) => {
    if (!parts.has(name)) parts.set(name, []);
    parts.get(name).push(sharedAttributes(geometry));
  };
  const obstacles = [];
  const solid = (x, z, r) => obstacles.push({ x, z, r: r + BODY });
  const rand = random(5);
  const painted3d = (geometry, r, g, b) => {
    const colors = new Float32Array(geometry.attributes.position.count * 3);
    for (let k = 0; k < colors.length; k += 3) {
      const v = 0.85 + rand() * 0.3;
      colors.set([r * v, g * v, b * v], k);
    }
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    return geometry;
  };

  // ---- ground --------------------------------------------------------------------------------------------
  add("grass", slab(-260, 260, FENCE, 260, -0.03, 8));
  add("lawn", slab(-260, 260, -260, 1, -0.03, 6));
  add("granite", slab(-PLAZA_X, PLAZA_X, -1, FORECOURT, 0, 3));
  add("road", slab(-PIER_X, PIER_X, -90, -1, 0, 6));
  add("cobbles", new THREE.PlaneGeometry(PLAZA_X * 2, FOOTPATH - FORECOURT).rotateX(-Math.PI / 2).translate(0, 0, (FORECOURT + FOOTPATH) / 2));
  add("footpath", slab(-260, 260, FOOTPATH, FENCE, 0.03, 2));
  add("white", box(-260, 260, 0, 0.16, FOOTPATH - 0.14, FOOTPATH + 0.04));  // kerb
  for (const side of [-1, 1]) {
    const span = (a, b) => (side < 0 ? [-b, -a] : [a, b]);
    const [x0, x1] = span(PLAZA_X, 260);
    add("pink", slab(x0, x1, 1, FORECOURT - 0.1, 0.02, 2.4));
    add("road", slab(x0, x1, FORECOURT - 0.1, MEDIAN[0], 0, 6));
    add("road", slab(x0, x1, MEDIAN[1], FOOTPATH, 0, 6));
    add("soil", slab(x0, x1, MEDIAN[0], MEDIAN[1], 0.14, 3));
    add("white", box(x0, x1, 0, 0.14, MEDIAN[0] - 0.12, MEDIAN[0] + 0.03));
    add("white", box(x0, x1, 0, 0.14, MEDIAN[1] - 0.03, MEDIAN[1] + 0.12));
    add("white", box(x0, x1, 0, 0.14, FORECOURT - 0.14, FORECOURT + 0.02));
    // lane dashes
    for (let d = PLAZA_X + 3; d < 200; d += 7) {
      const [a, b] = span(d, d + 2.5);
      add("marking", box(a, b, 0, 0.02, 19.9, 20.1));
      add("marking", box(a, b, 0, 0.02, 10.6, 10.8));
    }
    // tricolour columns and saplings along the median and the footpath's kerb
    for (let d = PLAZA_X + 4; d < 200; d += 10) {
      const x = side * d;
      add("tricolour", post(x, (MEDIAN[0] + MEDIAN[1]) / 2, 0.36, 0.36, 2.4, 0.1));
      solid(x, (MEDIAN[0] + MEDIAN[1]) / 2, 0.36);
      add("tricolour", post(x + side * 5, FOOTPATH + 0.45, 0.32, 0.32, 2.1, 0.03));
      solid(x + side * 5, FOOTPATH + 0.45, 0.32);
      add("trunk", post(x + side * 5, (MEDIAN[0] + MEDIAN[1]) / 2, 0.02, 0.03, 0.9, 0.12));
      add("leaves", painted3d(new THREE.IcosahedronGeometry(0.28, 1).translate(x + side * 5, 1.15, (MEDIAN[0] + MEDIAN[1]) / 2), 0.27, 0.46, 0.17));
    }
    // black and yellow posts with a blue disc where the median meets the plaza
    const nose = side * (PLAZA_X + 0.8);
    add("hazard", post(nose, (MEDIAN[0] + MEDIAN[1]) / 2, 0.2, 0.2, 1, 0.1));
    add("blue", new THREE.CylinderGeometry(0.19, 0.19, 0.05, 20).rotateX(Math.PI / 2).translate(nose, 1.32, (MEDIAN[0] + MEDIAN[1]) / 2));
    solid(nose, (MEDIAN[0] + MEDIAN[1]) / 2, 0.2);
    // double-armed street lights on the median
    for (let d = PLAZA_X + 9; d < 230; d += 30) {
      const x = side * d, z = (MEDIAN[0] + MEDIAN[1]) / 2;
      add("pole", post(x, z, 0.13, 0.08, 10.5, 0.1));
      add("pole", box(x - 0.05, x + 0.05, 10.4, 10.5, z - 2, z + 2));
      for (const at of [z - 2, z + 2]) add("dark", box(x - 0.14, x + 0.14, 10.32, 10.42, at - 0.3, at + 0.3));
      solid(x, z, 0.14);
    }
    // the kerbed hedges along the drive behind the gate
    add("white", box(side * PIER_X - 0.15, side * PIER_X + 0.15, 0, 0.14, -90, -1));
    add("hedge", box(side * 7.2 - 0.5, side * 7.2 + 0.5, 0, 1.1, -70, -3, 2));
    // lamp posts along the drive
    for (let z = -8; z > -80; z -= 13) {
      const x = side * (PIER_X + 0.55);
      add("white", post(x, z, 0.08, 0.05, 5.5));
      add("steel", box(x - 0.35, x + 0.35, 5.45, 5.55, z - 0.08, z + 0.08));
    }
  }

  // ---- the gate ------------------------------------------------------------------------------------------
  add("beige", box(-HALF_W, HALF_W, CANOPY.y0, CANOPY.y1, -CANOPY.depth, CANOPY.depth));
  add("pale", box(-HALF_W + 0.15, HALF_W - 0.15, CANOPY.y0 - 0.02, CANOPY.y0, -CANOPY.depth + 0.15, CANOPY.depth - 0.15));
  for (const side of [-1, 1]) {
    const [x0, x1] = side < 0 ? [-HALF_W + 0.4, -PIER_X] : [PIER_X, HALF_W - 0.4];
    add("beige", box(x0, x1, 0, CANOPY.y0, -1.5, 1.5));
    add("steel", box(side * 6.4 - 0.32, side * 6.4 + 0.32, CANOPY.y1, CANOPY.y1 + 0.26, 1.3, 1.7));  // floodlights
    for (const x of [2.2, 4.2]) {
      add("white", new THREE.CircleGeometry(0.1, 16).rotateX(Math.PI / 2).translate(side * x, CANOPY.y0 - 0.025, 0.9));
    }
    // closed sliding gates either side of the block: maroon frame with vertical bars
    const a = side < 0 ? -PIER_X : BLOCK.w, b = side < 0 ? -BLOCK.w : PIER_X;
    add("maroon", box(a, b, 0.08, 0.2, -0.05, 0.05));
    add("maroon", box(a, b, 1.95, 2.07, -0.05, 0.05));
    add("maroon", box(a, b, 1.02, 1.08, -0.04, 0.04));
    add("maroon", box(a, a + 0.1, 0.08, 2.07, -0.05, 0.05));
    add("maroon", box(b - 0.1, b, 0.08, 2.07, -0.05, 0.05));
    for (let x = a + 0.2; x < b - 0.1; x += 0.13) add("maroon", box(x - 0.012, x + 0.012, 0.2, 1.95, -0.012, 0.012));
  }
  add("block", box(-BLOCK.w, BLOCK.w, 0, BLOCK.h, -0.3, 0.3));

  // ---- west of the gate: guard room running into a long low building ---------------------------------------
  add("beige", box(-25, -7.6, 0, 3.2, -2, 1));
  add("pale", box(-25.15, -7.5, 3.2, 3.42, -2.1, 1.1));
  add("maroon", box(-8.75, -7.85, 0, 2.2, 1, 1.05));
  add("dark", box(-10.1, -9.1, 1, 2.3, 1, 1.03));
  add("steel", box(-10.2, -9, 0.92, 2.38, 0.98, 1.015));
  add("slate", box(-17.2, -13.4, 1, 2.5, 1, 1.05));
  add("blue", box(-12.4, -11.6, 1, 1.6, 1, 1.04));
  add("yellow", box(-11.3, -10.5, 1, 1.6, 1, 1.04));
  // the institute's low sign wall, then a closed side gate and the boundary wall
  add("wall", box(-31, -25, 0, 1.7, 0.4, 0.8));
  add("maroon", box(-36, -31, 0.1, 1.9, 0.55, 0.65));
  add("wall", box(-260, -36, 0, 2.2, 0.3, 0.7));
  // white bollards, planter box and pot along the edge of the forecourt
  for (let x = -25; x < -13; x += 1.7) {
    add("white", post(x, FORECOURT - 0.9, 0.13, 0.12, 0.75));
    solid(x, FORECOURT - 0.9, 0.13);
  }
  add("wood", box(-16.5, -15.6, 0, 0.6, FORECOURT - 2, FORECOURT - 1.4));
  solid(-16, FORECOURT - 1.7, 0.55);
  add("pot", post(-26.8, FORECOURT - 0.9, 0.24, 0.34, 0.55));
  solid(-26.8, FORECOURT - 0.9, 0.34);

  // ---- east of the gate: ATM booth, the long wall and the row of parked motorbikes --------------------------
  add("white", box(7.6, 11.4, 0, 3, -1.6, 1));
  add("dark", box(8.5, 10.5, 0.3, 2.5, 1, 1.03));
  add("white", box(7.6, 11.4, 3, 3.1, -1.6, 1.2));
  add("granite", box(8.1, 10.9, 0, 0.15, 1, 1.45));
  add("granite", box(8.3, 10.7, 0.15, 0.3, 1, 1.25));
  add("wall", box(11.4, 13, 0, 2.6, -0.8, 0.4));
  add("wall", box(13, 260, 0, 2.4, -0.2, 0.3));
  const bikeBody = (x) => {
    const lean = 0.08 * (rand() - 0.5);
    for (const dz of [-0.62, 0.62]) add("black", new THREE.CylinderGeometry(0.3, 0.3, 0.09, 16).rotateX(Math.PI / 2).rotateY(Math.PI / 2 + lean).translate(x, 0.3, 1.55 + dz));
    add("black", box(x - 0.13, x + 0.13, 0.42, 0.75, 1.05, 2));
    add(rand() < 0.5 ? "black" : "maroon", box(x - 0.14, x + 0.14, 0.75, 0.9, 1.25, 1.95));
    add("steel", box(x - 0.34, x + 0.34, 1.02, 1.05, 2.03, 2.07));
    add("steel", box(x - 0.025, x + 0.025, 0.5, 1.05, 2.03, 2.1));
  };
  for (let x = 14; x < 52; x += 0.88 + rand() * 0.25) bikeBody(x);
  // bollards and a planter where the forecourt meets the pink footpath
  for (let z = FORECOURT - 2.4; z < FORECOURT + 0.2; z += 0.55) {
    const x = 13.6 - (z - FORECOURT) * 0.6;
    add("white", post(x, z, 0.15, 0.14, 0.75));
    solid(x, z, 0.15);
  }
  add("pot", post(15, FORECOURT - 1.2, 0.24, 0.34, 0.55));
  solid(15, FORECOURT - 1.2, 0.34);
  add("wood", box(12.4, 13, 0, 0.75, 2.4, 3));
  solid(12.7, 2.7, 0.42);
  add("slate", box(16.6, 16.85, 0, 2.6, 4.9, 5.35));   // the tall sign post on the footpath
  solid(16.7, 5.1, 0.28);

  // ---- south of the road: fence, scrub, shade sail, pipes, viaduct --------------------------------------------
  add("white", box(-260, 260, 0, 0.45, FENCE - 0.1, FENCE + 0.1));
  add("black", box(-260, 260, 1.5, 1.56, FENCE - 0.025, FENCE + 0.025));
  add("black", box(-260, 260, 0.5, 0.56, FENCE - 0.025, FENCE + 0.025));
  for (let x = -130; x < 130; x += 0.24) {
    if (Math.round(x / 0.24) % 12 === 0) add("black", box(x - 0.04, x + 0.04, 0.3, 1.6, FENCE - 0.04, FENCE + 0.04));
    else add("black", box(x - 0.01, x + 0.01, 0.5, 1.5, FENCE - 0.01, FENCE + 0.01));
  }
  for (let x = -FAR; x < FAR; x += 18) {  // single lamps along the footpath
    add("pole", post(x, FENCE - 1, 0.07, 0.05, 6.4));
    add("dark", box(x - 0.09, x + 0.09, 6.35, 6.48, FENCE - 1.3, FENCE - 0.7));
    solid(x, FENCE - 1, 0.07);
  }
  // the fabric shade over the path and the orange bin next to it
  add("white", post(-7, FENCE - 1.4, 0.07, 0.06, 5.2));
  solid(-7, FENCE - 1.4, 0.07);
  const sail = new THREE.PlaneGeometry(1, 1, 1, 1);
  [[-7, 4.2, FENCE - 1.4], [-3, 3.1, FENCE + 2.4], [-11.5, 3.2, FENCE + 1.6], [-7, 5.4, FENCE - 4]]
    .forEach(([x, y, z], i) => sail.attributes.position.setXYZ([1, 0, 3, 2][i], x, y, z));
  sail.computeVertexNormals();
  add("sail", sail);
  add("orange", post(-5.4, FENCE - 0.5, 0.33, 0.36, 1.05, 0.03));
  solid(-5.4, FENCE - 0.5, 0.36);
  add("wood", box(-2.6, -1.8, 0.03, 0.6, FENCE - 1.3, FENCE - 0.6));
  solid(-2.2, FENCE - 0.95, 0.5);
  // concrete pipes lying in the scrub, a red construction strip and the road under the viaduct
  for (const [x, z, turn] of [[3, 36, 0.3], [6.2, 37.5, 1.1], [-22, 40, 0.8]]) {
    add("concrete", new THREE.CylinderGeometry(0.6, 0.6, 2.4, 16).rotateZ(Math.PI / 2).rotateY(turn).translate(x, 0.56, z));
  }
  add("orange", box(-120, 120, 0, 0.1, 46, 46.5));
  add("road", slab(-260, 260, 49, 56, 0, 6));
  add("road", slab(-260, 260, 66, 74, 0, 6));
  // the viaduct: deck, side parapets with a rail, Y-headed piers
  add("concrete", box(-260, 260, VIADUCT.y0, VIADUCT.y1, VIADUCT.z0, VIADUCT.z1));
  for (const z of [VIADUCT.z0, VIADUCT.z1]) {
    add("concrete", box(-260, 260, VIADUCT.y1, VIADUCT.y1 + 0.5, z - 0.1, z + 0.1));
    add("pole", box(-260, 260, VIADUCT.y1 + 1.05, VIADUCT.y1 + 1.1, z - 0.03, z + 0.03));
    for (let x = -200; x < 200; x += 2.4) add("pole", box(x - 0.03, x + 0.03, VIADUCT.y1 + 0.5, VIADUCT.y1 + 1.05, z - 0.03, z + 0.03));
  }
  const midZ = (VIADUCT.z0 + VIADUCT.z1) / 2;
  for (let x = -210; x < 215; x += 34) {
    add("concrete", post(x, midZ, 1.15, 1.05, VIADUCT.y0 - 1.5));
    add("concrete", new THREE.CylinderGeometry(4.2, 1.05, 1.5, 4, 1).rotateY(Math.PI / 4).scale(0.6, 1, 1).translate(x, VIADUCT.y0 - 0.75, midZ));
  }
  // far apartment towers where the street meets the haze
  for (const [x, z, h, w] of [[175, -35, 34, 11], [192, -10, 42, 12], [176, 20, 28, 10], [-178, -28, 30, 11], [-192, 8, 38, 12], [205, 40, 30, 14]]) {
    add("tower", box(x - w / 2, x + w / 2, 0, h, z - w / 2, z + w / 2));
  }
  // campus blocks seen above the trees, north-west of the gate
  add("pale", box(-44, -13, 0, 11, -40, -26));
  for (const y of [1.2, 4.6, 8]) add("dark", box(-43.5, -13.5, y, y + 1.9, -26.05, -25.95));
  for (let x = -43; x < -13; x += 3) add("pale", box(x - 0.25, x + 0.25, 0, 11, -25.92, -25.75));
  add("wall", box(-36, -25, 11, 17, -38, -28));
  add("pale", box(-36.2, -24.8, 17, 17.25, -38.2, -27.8));
  add("pole", post(-24, -28, 0.05, 0.05, 3, 17));

  // ---- trees ---------------------------------------------------------------------------------------------
  const clump = (radius, x, y, z, r, g, b, crownY, crownH) => {
    const leaf = new THREE.IcosahedronGeometry(radius, 1), pos = leaf.attributes.position;
    const push = new Map();  // corners shared by faces move together, so the clump stays closed
    for (let i = 0; i < pos.count; i++) {
      const key = `${pos.getX(i).toFixed(3)},${pos.getY(i).toFixed(3)},${pos.getZ(i).toFixed(3)}`;
      if (!push.has(key)) push.set(key, 0.72 + rand() * 0.5);
      const k = push.get(key);
      pos.setXYZ(i, pos.getX(i) * k + x, pos.getY(i) * k * 0.85 + y, pos.getZ(i) * k + z);
    }
    const colors = new Float32Array(pos.count * 3);
    for (let i = 0; i < pos.count; i += 3) {  // one tone per face, darker low in the crown
      const light = (0.5 + 0.75 * Math.max(0, Math.min(1, (pos.getY(i) - crownY) / crownH))) * (0.82 + rand() * 0.42);
      for (let v = 0; v < 3; v++) colors.set([r * light, g * light, b * light], (i + v) * 3);
    }
    leaf.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    add("leaves", leaf);
  };
  const tree = (x, z, size, clumps, r, g, b) => {
    const height = 3 * size, crownH = 3.6 * size, spread = 2.5 * size;
    add("trunk", new THREE.CylinderGeometry(0.1 * size, 0.22 * size, height + 1, 7).translate(x, (height + 1) / 2, z));
    const tone = 0.8 + rand() * 0.35;
    for (let i = 0; i < clumps; i++) {
      const a = rand() * Math.PI * 2, d = Math.sqrt(rand()) * spread, up = rand();
      const narrow = 1 - up * 0.55;  // crown narrows towards the top
      clump((0.62 + rand() * 0.5) * size, x + Math.cos(a) * d * narrow, height + up * crownH, z + Math.sin(a) * d * narrow,
        r * tone, g * tone, b * tone, height, crownH);
    }
  };
  // the big dark trees that stand behind the walls and over the campus
  for (let i = 0; i < 130; i++) {
    const side = i % 2 ? 1 : -1, x = side * (8.6 + rand() * 140), z = -3.5 - rand() * 34;
    if (x > -46 && x < -11 && z > -42 && z < -24) continue;  // not inside the campus block
    tree(x, z, 1.5 + rand() * 1.1, Math.abs(x) < 60 ? 22 : 11, 0.2, 0.38, 0.14);
  }
  for (let i = 0; i < 26; i++) {  // along the drive, further in
    tree((i % 2 ? 1 : -1) * (9 + rand() * 7), -40 - rand() * 45, 1.2 + rand() * 0.8, 10, 0.22, 0.4, 0.15);
  }
  for (let i = 0; i < 46; i++) {  // thin, young trees in the scrub south of the fence
    tree(-125 + rand() * 250, FENCE + 1.5 + rand() * 16, 0.55 + rand() * 0.5, 9, 0.33, 0.47, 0.17);
  }

  const building = new THREE.Group();
  for (const [name, geometries] of parts) {
    const mesh = new THREE.Mesh(mergeGeometries(geometries), M[name]);
    mesh.castShadow = !FLAT.has(name);
    mesh.receiveShadow = true;
    building.add(mesh);
  }
  scene.add(building);

  // lettering and the awning are pictures on planes
  const decal = (c, w, h, x, y, z, extra = {}) => {
    const map = T.texture(c, aniso);
    map.wrapS = map.wrapT = THREE.ClampToEdgeWrapping;
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({
      map, transparent: true, roughness: 0.6, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, ...extra,
    }));
    mesh.position.set(x, y, z);
    scene.add(mesh);
    return mesh;
  };
  // the canopy's shade on the ground, fading out in front of the gate
  const shade = T.texture(T.vertical(4, 128, [[0, "rgba(30,26,20,0.42)"], [0.7, "rgba(30,26,20,0.38)"], [1, "rgba(30,26,20,0)"]]), aniso);
  shade.wrapT = THREE.ClampToEdgeWrapping;
  const shadeOnGround = new THREE.Mesh(new THREE.PlaneGeometry(HALF_W * 2, 6.2).rotateX(-Math.PI / 2),
    new THREE.MeshBasicMaterial({ map: shade, transparent: true, depthWrite: false, toneMapped: false }));
  shadeOnGround.position.set(0, 0.012, 0.9);
  scene.add(shadeOnGround);

  decal(fasciaLetters(), 14.6, 1, 0, (CANOPY.y0 + CANOPY.y1) / 2, CANOPY.depth + 0.005);
  decal(blockPlate(logo), BLOCK.w * 2, (BLOCK.w * 2 * 560) / 640, 0, BLOCK.h / 2 + 0.05, 0.305);
  decal(instituteSign(), 5.4, 1.5, -28, 0.86, 0.805);
  decal(bankSign(), 3.8, 0.95, 9.5, 3.5, 1.22, { transparent: false });
  const awning = decal(awningTexture(), 3.4, 1.05, -9.8, 2.75, 1.45, { transparent: false, side: THREE.DoubleSide });
  awning.rotation.x = 0.5;
  awning.castShadow = true;

  scene.add(new THREE.Mesh(
    new THREE.SphereGeometry(320, 32, 16),
    new THREE.MeshBasicMaterial({ map: skyTexture(aniso), side: THREE.BackSide, toneMapped: false, fog: false }),
  ));

  // the arrow, a glowing ring on the ground and a faint column of light above the ring
  const yellow = new THREE.MeshStandardMaterial({ color: 0xffd21f, emissive: 0xc89400, roughness: 0.45 });
  const arrow = new THREE.Mesh(arrowGeometry(), yellow);
  arrow.position.set(PORTAL.x, ARROW_Y, PORTAL.z);
  arrow.scale.setScalar(1.45);
  scene.add(arrow);
  const glow = { color: 0xffd21f, transparent: true, depthWrite: false, toneMapped: false, fog: false };
  const ring = new THREE.Mesh(new THREE.RingGeometry(PORTAL.r - 0.14, PORTAL.r, 64).rotateX(-Math.PI / 2),
    new THREE.MeshBasicMaterial({ ...glow, opacity: 0.95, side: THREE.DoubleSide }));
  ring.position.set(PORTAL.x, 0.03, PORTAL.z);
  scene.add(ring);
  const fadeUp = T.texture(T.vertical(4, 64, [[0, "rgba(255,255,255,0)"], [1, "rgba(255,255,255,0.28)"]]), aniso);
  fadeUp.wrapT = THREE.ClampToEdgeWrapping;
  const column = new THREE.Mesh(new THREE.CylinderGeometry(PORTAL.r - 0.05, PORTAL.r - 0.05, 1.5, 64, 1, true),
    new THREE.MeshBasicMaterial({ ...glow, map: fadeUp, side: THREE.DoubleSide }));
  column.position.set(PORTAL.x, 0.75, PORTAL.z);
  scene.add(column);

  function animate(t) {
    arrow.rotation.y = t * 1.9;
    arrow.position.y = ARROW_Y + Math.sin(t * 2.2) * 0.12;
    ring.scale.setScalar(1 + Math.sin(t * 3) * 0.03);
  }

  // the street is open ground bounded by the gate line, the parked bikes, the fence and the ends of the view;
  // posts and bollards push the visitor out sideways, as the pedestals do in the hall
  function move(x, z, dx, dz) {
    let nx = Math.max(-WALK.x, Math.min(WALK.x, x + dx)), nz = z + dz;
    for (const o of obstacles) {
      const ox = nx - o.x, oz = nz - o.z, d = Math.hypot(ox, oz);
      if (d < o.r && d > 1e-6) {
        nx = o.x + (ox / d) * o.r;
        nz = o.z + (oz / d) * o.r;
      }
    }
    const zMin = nx > 11.6 ? WALK.zBikes : WALK.zGate;
    return [Math.max(-WALK.x, Math.min(WALK.x, nx)), Math.max(zMin, Math.min(WALK.zMax, nz))];
  }

  return {
    scene,
    portal: PORTAL,
    spawn: { x: 0, z: 19, yaw: 0, pitch: 0.06 },
    move,
    atPortal: (x, z) => Math.hypot(x - PORTAL.x, z - PORTAL.z) < PORTAL.r - BODY * 0.4,
    distance: (x, z) => Math.hypot(x - PORTAL.x, z - PORTAL.z),
    animate,
  };
}
