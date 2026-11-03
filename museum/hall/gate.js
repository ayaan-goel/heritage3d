// The university's main gate, where a visit starts: a small outdoor scene of its own, modelled by hand from
// reference photos (sizes estimated from them, not surveyed). Walking into the yellow arrow enters the museum.
// Visitors stand south of the gate (+z) and look north (-z). Metres, y up, the gate line is z = 0.
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { BODY } from "./layout.js";
import * as T from "./textures.js";

const SERIF = 'Georgia, "Times New Roman", serif';
const HALF_W = 8;         // canopy half width
const CANOPY = { y0: 4.7, y1: 5.8, depth: 2.2 };
const BLOCK = { w: 1.2, h: 2.1 };   // half width and height of the centre block with the university's name
const PIER_X = 5.5;       // inner face of the piers carrying the canopy
const PORTAL = { x: 0, z: 3.2, r: 1.1 };  // the arrow; stepping inside this circle enters the museum
const ARROW_Y = 3;        // height of the arrow's centre: above the block, against the open sky
const WALK = { x: 16.2, zMin: 1.85, zMax: 24 };
const ROAD = { z0: 18, z1: 25 };

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

const sharedAttributes = (g) => {
  const out = g.index ? g.toNonIndexed() : g;
  if (!out.attributes.color) {
    out.setAttribute("color", new THREE.BufferAttribute(new Float32Array(out.attributes.position.count * 3).fill(1), 3));
  }
  return out;
};

function skyTexture(aniso) {
  const c = T.vertical(1024, 512, [[0, "#2f6fc4"], [0.3, "#5f9ade"], [0.44, "#a4c9ea"], [0.5, "#d3e4ef"], [1, "#d3e4ef"]]);
  const g = c.getContext("2d"), rand = random(21);
  for (let i = 0; i < 26; i++) {  // clouds: clusters of soft white puffs above the horizon
    const x = rand() * 1024, y = 95 + rand() * 120, size = 16 + rand() * 40;
    for (let k = 0; k < 7; k++) {
      const px = x + (rand() - 0.5) * size * 2.6, py = y + (rand() - 0.5) * size * 0.6, r = size * (0.5 + rand() * 0.5);
      const puff = g.createRadialGradient(px, py, 0, px, py, r);
      puff.addColorStop(0, "rgba(255,255,255,0.42)");
      puff.addColorStop(1, "rgba(255,255,255,0)");
      g.fillStyle = puff;
      g.fillRect(px - r, py - r, r * 2, r * 2);
    }
  }
  const t = T.texture(c, aniso);
  t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

// largest font of this family at which the text stays within maxWidth
function fitFont(g, text, maxWidth, size, style = "") {
  let px = size;
  do g.font = `${style} ${px}px ${SERIF}`; while (g.measureText(text).width > maxWidth && --px > 10);
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
  scene.add(new THREE.HemisphereLight(0xdbe9ff, 0x9a8d78, 1.05));
  const sun = new THREE.DirectionalLight(0xfff1dc, 1.7);
  sun.position.set(-30, 40, 14);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -42, right: 42, top: 42, bottom: -42, near: 1, far: 130 });
  sun.shadow.camera.updateProjectionMatrix();
  sun.shadow.bias = -0.0006;
  sun.shadow.normalBias = 0.03;
  scene.add(sun);

  const tile = (c, size = 1) => T.texture(c, aniso, [size, size]);
  const std = (map, roughness, extra = {}) => new THREE.MeshStandardMaterial({ map, roughness, metalness: 0, ...extra });
  const seams = T.plaster(512, "#a8a092", 11);
  const sg = seams.getContext("2d");
  sg.strokeStyle = "rgba(70, 62, 50, 0.55)";
  sg.lineWidth = 4;
  sg.strokeRect(0, 0, 512, 512);
  const M = {
    beige: std(tile(T.plaster(512, "#c9a878", 5)), 0.9),
    pale: std(tile(T.plaster(512, "#c9c0ae", 7)), 0.9),
    block: std(tile(T.plaster(512, "#cdb48c", 9)), 0.9),
    concrete: std(tile(seams), 0.95),
    asphalt: std(tile(T.plaster(512, "#55524f", 4)), 0.95),
    grass: std(tile(T.plaster(512, "#6d8f45", 6)), 1),
    hedge: std(tile(T.plaster(512, "#47702f", 3)), 1),
    white: new THREE.MeshStandardMaterial({ color: 0xece8df, roughness: 0.8 }),
    maroon: new THREE.MeshStandardMaterial({ color: 0x6d2b2a, roughness: 0.55, metalness: 0.15 }),
    dark: new THREE.MeshStandardMaterial({ color: 0x31363a, roughness: 0.3, metalness: 0.2 }),
    steel: new THREE.MeshStandardMaterial({ color: 0x8c9092, roughness: 0.5, metalness: 0.5 }),
    blue: new THREE.MeshStandardMaterial({ color: 0x173f73, roughness: 0.5 }),
    pot: new THREE.MeshStandardMaterial({ color: 0xb4623a, roughness: 0.85 }),
    trunk: new THREE.MeshStandardMaterial({ color: 0x5b4a39, roughness: 1 }),
    leaves: new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 1, flatShading: true }),
  };
  const parts = new Map();
  const add = (name, geometry) => {
    if (!parts.has(name)) parts.set(name, []);
    parts.get(name).push(sharedAttributes(geometry));
  };

  // ground: forecourt, road, the drive beyond the gate, grass everywhere else
  add("grass", slab(-130, 130, -130, 130, -0.03, 6));
  add("concrete", slab(-17, 17, -1, ROAD.z0, 0, 5));
  add("concrete", slab(-PIER_X, PIER_X, -80, -1, 0, 5));
  add("asphalt", slab(-130, 130, ROAD.z0, ROAD.z1, 0.005, 4));
  for (const z of [ROAD.z0 + 0.3, ROAD.z1 - 0.3]) add("white", box(-130, 130, 0, 0.012, z - 0.06, z + 0.06));
  for (const side of [-1, 1]) {
    add("white", box(side * PIER_X - 0.15, side * PIER_X + 0.15, 0, 0.14, -80, -1));
    add("hedge", box(side * 17 - 0.45, side * 17 + 0.45, 0, 1.2, 0.5, ROAD.z0 - 0.6, 2));
    add("hedge", box(side * 7.2 - 0.5, side * 7.2 + 0.5, 0, 1, -60, -3, 2));
  }

  // the gate: two piers, canopy, centre block
  add("beige", box(-HALF_W, HALF_W, CANOPY.y0, CANOPY.y1, -CANOPY.depth, CANOPY.depth));
  add("pale", box(-HALF_W + 0.15, HALF_W - 0.15, CANOPY.y0 - 0.02, CANOPY.y0, -CANOPY.depth + 0.15, CANOPY.depth - 0.15));
  for (const side of [-1, 1]) {
    const [x0, x1] = side < 0 ? [-HALF_W + 0.4, -PIER_X] : [PIER_X, HALF_W - 0.4];
    add("beige", box(x0, x1, 0, CANOPY.y0, -1.5, 1.5));
    add("steel", box(side * 6.4 - 0.32, side * 6.4 + 0.32, CANOPY.y1, CANOPY.y1 + 0.26, 1.3, 1.7));  // floodlights
    for (const x of [2.2, 4.2]) {
      const light = new THREE.CircleGeometry(0.1, 16).rotateX(Math.PI / 2).translate(side * x, CANOPY.y0 - 0.025, 0.9);
      add("white", light);
    }
    // closed sliding gates either side of the block: maroon frame with vertical bars
    const a = side < 0 ? -PIER_X : BLOCK.w, b = side < 0 ? -BLOCK.w : PIER_X;
    add("maroon", box(a, b, 0.08, 0.2, -0.05, 0.05));
    add("maroon", box(a, b, 1.95, 2.07, -0.05, 0.05));
    add("maroon", box(a, b, 1.02, 1.08, -0.04, 0.04));
    add("maroon", box(a, a + 0.1, 0.08, 2.07, -0.05, 0.05));
    add("maroon", box(b - 0.1, b, 0.08, 2.07, -0.05, 0.05));
    for (let x = a + 0.2; x < b - 0.1; x += 0.13) add("maroon", box(x - 0.012, x + 0.012, 0.2, 1.95, -0.012, 0.012));
    // boundary wall running off to both sides
    add("pale", box(side < 0 ? -130 : 10.8, side < 0 ? -11.8 : 130, 0, 2.4, -0.2, 0.2));
  }
  add("block", box(-BLOCK.w, BLOCK.w, 0, BLOCK.h, -0.3, 0.3));

  // guard room on the west side, with a striped awning; service block on the east
  add("beige", box(-11.8, -7.6, 0, 3.2, -2, 1));
  add("pale", box(-11.95, -7.5, 3.2, 3.42, -2.1, 1.1));
  add("maroon", box(-8.75, -7.85, 0, 2.2, 1, 1.05));
  add("dark", box(-10.1, -9.1, 1, 2.3, 1, 1.03));
  add("steel", box(-10.2, -9, 0.92, 2.38, 0.98, 1.015));
  add("pale", box(10.5 - 3, 10.8, 0, 4.2, -1.5, 1.1));
  add("blue", box(8.4, 10.6, 3, 4, 1.1, 1.17));

  // low clay pots with plants along the closed gates
  const rand = random(5);
  for (const side of [-1, 1]) {
    for (let x = 1.7; x < 5.2; x += 0.58) {
      const px = side * x, pz = 0.95;
      add("pot", new THREE.CylinderGeometry(0.23, 0.17, 0.3, 12).translate(px, 0.15, pz));
      const leaf = new THREE.IcosahedronGeometry(0.27, 1).scale(1, 0.75, 1).translate(px, 0.44, pz);
      const colors = new Float32Array(leaf.attributes.position.count * 3);
      const tone = 0.75 + rand() * 0.35;
      for (let i = 0; i < colors.length; i += 3) colors.set([0.25 * tone, 0.52 * tone, 0.2 * tone], i);
      leaf.setAttribute("color", new THREE.BufferAttribute(colors, 3));
      add("leaves", leaf);
    }
  }

  // campus block seen over the guard room: floors of dark window bands between pale slabs
  add("pale", box(-44, -13, 0, 11, -40, -26));
  for (const y of [1.2, 4.6, 8]) add("dark", box(-43.5, -13.5, y, y + 1.9, -26.05, -25.95));
  for (let x = -43; x < -13; x += 3) add("pale", box(x - 0.25, x + 0.25, 0, 11, -25.92, -25.75));

  // lamp posts along the drive
  for (let z = -8; z > -60; z -= 13) {
    for (const side of [-1, 1]) {
      const x = side * (PIER_X + 0.55);
      add("white", new THREE.CylinderGeometry(0.05, 0.08, 5.5, 8).translate(x, 2.75, z));
      add("steel", box(x - 0.35, x + 0.35, 5.45, 5.55, z - 0.08, z + 0.08));
    }
  }

  // trees: a trunk under a few rough blobs of leaves, each tree its own green
  const tree = (x, z, size) => {
    add("trunk", new THREE.CylinderGeometry(0.1 * size, 0.2 * size, 3 * size, 8).translate(x, 1.5 * size, z));
    const tone = 0.72 + rand() * 0.45, warm = rand() * 0.12;
    for (let i = 0; i < 6; i++) {
      const a = rand() * Math.PI * 2, d = i ? (0.8 + rand()) * size : 0, r = (1.1 + rand() * 0.8) * size;
      const blob = new THREE.IcosahedronGeometry(r, 2)
        .scale(1, 0.8, 1)
        .translate(x + Math.cos(a) * d, (3.6 + rand() * 1.2) * size, z + Math.sin(a) * d);
      const colors = new Float32Array(blob.attributes.position.count * 3);
      for (let k = 0; k < colors.length; k += 3) {
        const v = tone * (0.85 + rand() * 0.3);
        colors.set([(0.27 + warm) * v, 0.47 * v, 0.17 * v], k);
      }
      blob.setAttribute("color", new THREE.BufferAttribute(colors, 3));
      add("leaves", blob);
    }
  };
  for (let i = 0; i < 40; i++) {  // behind the gate, along both sides of the drive
    const side = i % 2 ? 1 : -1;
    const x = side * (9 + rand() * 40), z = -7 - rand() * 62;
    if (x > -46 && x < -11 && z > -42 && z < -24) continue;  // not inside the campus block
    tree(x, z, 1 + rand() * 0.9);
  }
  for (const side of [-1, 1]) {
    for (let z = 3; z < 17; z += 4.5) tree(side * (20 + rand() * 6), z, 0.9 + rand() * 0.6);
  }
  for (let x = -60; x < 60; x += 7 + rand() * 5) tree(x, ROAD.z1 + 7 + rand() * 18, 1 + rand() * 0.9);

  const building = new THREE.Group();
  for (const [name, geometries] of parts) {
    const mesh = new THREE.Mesh(mergeGeometries(geometries), M[name]);
    mesh.castShadow = name !== "grass" && name !== "concrete" && name !== "asphalt";
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
  const awning = decal(awningTexture(), 3.4, 1.05, -9.8, 2.75, 1.45, { transparent: false, side: THREE.DoubleSide });
  awning.rotation.x = 0.5;
  awning.castShadow = true;

  scene.add(new THREE.Mesh(
    new THREE.SphereGeometry(220, 32, 16),
    new THREE.MeshBasicMaterial({ map: skyTexture(aniso), side: THREE.BackSide, toneMapped: false, fog: false }),
  ));

  // the arrow, a glowing ring on the ground and a faint column of light above the ring
  const yellow = new THREE.MeshStandardMaterial({ color: 0xffd21f, emissive: 0xc89400, roughness: 0.45 });
  const arrow = new THREE.Mesh(arrowGeometry(), yellow);
  arrow.position.set(PORTAL.x, ARROW_Y, PORTAL.z);
  arrow.scale.setScalar(1.45);
  scene.add(arrow);
  const glow = { color: 0xffd21f, transparent: true, depthWrite: false, toneMapped: false };
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

  const free = (x, z) => [Math.max(-WALK.x, Math.min(WALK.x, x)), Math.max(WALK.zMin, Math.min(WALK.zMax, z))];
  return {
    scene,
    portal: PORTAL,
    spawn: { x: 0, z: 15, yaw: 0, pitch: 0.08 },
    move: (x, z, dx, dz) => free(x + dx, z + dz),
    atPortal: (x, z) => Math.hypot(x - PORTAL.x, z - PORTAL.z) < PORTAL.r - BODY * 0.4,
    distance: (x, z) => Math.hypot(x - PORTAL.x, z - PORTAL.z),
    animate,
  };
}
