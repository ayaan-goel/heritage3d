// Architecture of the hall (rotunda, dome, galleries) and the pedestals, built from the floor plan.
// Parts that share a material are merged into one mesh, so the whole building costs a few draw calls.
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import {
  DOOR_H, DOOR_W, FIRST_PAIR, GALLERIES, GALLERY_H, GALLERY_START, GALLERY_W, PEDESTAL_TOP, PILASTER,
  ROTUNDA_R as R, STEP, WALL_H,
} from "./layout.js";
import * as T from "./textures.js";

const OCULUS = 0.16;     // opening at the top of the dome, radians from the zenith
const COLUMNS = 28;      // coffer columns around the dome

// texture coordinates in metres, so a texture repeats at the same size on every surface
function metres(geometry, su, sv) {
  const uv = geometry.attributes.uv;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * su, uv.getY(i) * sv);
  return geometry;
}

function materials(aniso) {
  const tile = (c, size) => T.texture(c, aniso, [1 / size, 1 / size]);
  const std = (map, roughness, extra = {}) => new THREE.MeshStandardMaterial({ map, roughness, metalness: 0, ...extra });
  const decal = (c, extra = {}) => new THREE.MeshBasicMaterial({
    map: T.texture(c, aniso), transparent: true, depthWrite: false, toneMapped: false,
    polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, ...extra,
  });
  const light = T.marble(512, { base: "#ede6da", vein: "#b3a690", seed: 3 });
  const grey = T.marble(512, { base: "#bfb7aa", vein: "#857a6c", seed: 8 });
  const dark = T.marble(512, { base: "#4b433c", vein: "#83786c", seed: 13 });

  const dome = T.texture(T.domeCoffers(OCULUS, COLUMNS), aniso, [COLUMNS, 1]);
  dome.wrapT = THREE.ClampToEdgeWrapping;
  const vault = tile(T.vaultCoffer(256), 1);
  vault.repeat.set(8 / ((Math.PI * GALLERY_W) / 2), 1 / 1.6);   // 8 coffers across, 1.6 m long
  vault.offset.set(0, -(FIRST_PAIR - STEP / 2) / 1.6);           // coffer joints line up with the ribs

  return {
    rotundaFloor: std(T.texture(T.rotundaFloor(2048, light, grey, dark, R + 0.4), aniso), 0.4),
    floor: std(tile(T.tiles(1024, light, grey), 2), 0.42),
    wall: std(tile(T.plaster(512, "#e7dbc5", 5), 3), 0.95, { side: THREE.DoubleSide }),
    stone: std(tile(T.plaster(512, "#f0e8da", 9), 2), 0.85),
    white: std(tile(light, 1.4), 0.55),
    dark: std(tile(dark, 1.4), 0.45, { side: THREE.DoubleSide }),
    dome: std(dome, 0.95, { side: THREE.BackSide }),
    vault: std(vault, 0.95, { side: THREE.BackSide }),
    bronze: new THREE.MeshStandardMaterial({ color: 0x8f6b3e, metalness: 0.75, roughness: 0.35 }),
    sky: new THREE.MeshBasicMaterial({ color: 0xeaf3ff, toneMapped: false }),
    glass: new THREE.MeshBasicMaterial({ color: 0xdde9f4, toneMapped: false }),
    daylight: new THREE.MeshBasicMaterial({ color: 0xfff4e2, toneMapped: false }),
    shaft: decal(T.vertical(4, 256, [[0, "rgba(255,244,222,0.9)"], [1, "rgba(255,244,222,0)"]]), {
      opacity: 0.16, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, polygonOffset: false,
    }),
    pool: decal(T.radial(256, [[0, "rgba(255,240,215,0.4)"], [1, "rgba(255,240,215,0)"]]), { blending: THREE.AdditiveBlending }),
    shadow: decal(T.radial(256, [[0, "rgba(35,25,15,0.5)"], [0.5, "rgba(35,25,15,0.28)"], [1, "rgba(35,25,15,0)"]])),
  };
}

function rotunda(add, M, aniso, signs, info) {
  add(new THREE.CircleGeometry(R + 0.4, 128).rotateX(-Math.PI / 2), M.rotundaFloor);

  // walls between the doorways and above them
  const half = Math.asin(DOOR_W / 2 / R);
  const arc = (from, length, y0, y1, radius, material) => {
    const g = new THREE.CylinderGeometry(radius, radius, y1 - y0, Math.ceil(length * 40), 1, true, from, length);
    add(metres(g, radius * length, y1 - y0).translate(0, (y0 + y1) / 2, 0), material);
  };
  for (const { heading } of GALLERIES) {
    const from = heading + half, length = Math.PI / 2 - 2 * half;
    arc(from, length, 0, WALL_H, R, M.wall);
    arc(from, length, 0, 0.34, R - 0.04, M.dark);               // skirting
    arc(heading - half, 2 * half, DOOR_H, WALL_H, R, M.wall);    // above the doorway
  }
  add(new THREE.TorusGeometry(R - 0.14, 0.2, 10, 160).rotateX(Math.PI / 2).translate(0, WALL_H - 0.1, 0), M.stone);
  add(new THREE.TorusGeometry(R - 0.05, 0.07, 6, 160).rotateX(Math.PI / 2).translate(0, WALL_H - 0.75, 0), M.stone);

  // pilasters, 16 around the wall minus the four doorways
  const shaftH = WALL_H - 1.15;
  for (let k = 0; k < 16; k++) {
    if (k % 4 === 0) continue;
    const a = (k * Math.PI) / 8;
    const part = (w, h, d, y) => add(new THREE.BoxGeometry(w, h, d).translate(0, y, R - d / 2).rotateY(a), M.stone);
    part(1.1, 0.5, PILASTER + 0.1, 0.25);
    part(0.9, shaftH, PILASTER, 0.5 + shaftH / 2);
    part(1.15, 0.45, PILASTER + 0.12, 0.5 + shaftH + 0.225);
  }

  // doorways: reveals, soffit, threshold, lintel, arch and the sign in the half-round panel
  const sEdge = Math.sqrt(R * R - (DOOR_W / 2) ** 2);   // where the curved wall meets the doorway sides
  GALLERIES.forEach(({ heading }, i) => {
    const turn = new THREE.Matrix4().makeRotationY(heading);
    const put = (g, material) => add(g.applyMatrix4(turn), material);
    const depth = GALLERY_START - sEdge + 0.02;
    for (const side of [-1, 1]) {
      put(metres(new THREE.PlaneGeometry(depth, DOOR_H), depth, DOOR_H)
        .rotateY((-side * Math.PI) / 2).translate((side * DOOR_W) / 2, DOOR_H / 2, sEdge + depth / 2 - 0.01), M.stone);
    }
    const soffit = new THREE.Shape()
      .moveTo(DOOR_W / 2, GALLERY_START + 0.01)
      .lineTo(DOOR_W / 2, sEdge)
      .absarc(0, 0, R, Math.atan2(sEdge, DOOR_W / 2), Math.atan2(sEdge, -DOOR_W / 2), false)
      .lineTo(-DOOR_W / 2, GALLERY_START + 0.01);
    put(new THREE.ShapeGeometry(soffit, 16).rotateX(Math.PI / 2).translate(0, DOOR_H, 0), M.stone);
    const sill = GALLERY_START - sEdge + 0.5;
    put(metres(new THREE.PlaneGeometry(DOOR_W, sill), DOOR_W, sill).rotateX(-Math.PI / 2)
      .translate(0, 0.004, sEdge - 0.4 + sill / 2), M.dark);
    put(new THREE.BoxGeometry(DOOR_W + 0.5, 0.24, 0.24).translate(0, DOOR_H, R - 0.36), M.stone);
    put(new THREE.TorusGeometry(DOOR_W / 2 + 0.08, 0.12, 8, 48, Math.PI).translate(0, DOOR_H, R - 0.36), M.stone);
    const sign = new THREE.MeshStandardMaterial({ map: T.texture(signs[i], aniso), roughness: 0.9 });
    put(new THREE.CircleGeometry(DOOR_W / 2, 48, 0, Math.PI).rotateY(Math.PI).translate(0, DOOR_H, R - 0.4), sign);
  });

  // dome with its opening, the sky above it and a soft shaft of light down to the floor
  const top = WALL_H + R * Math.cos(OCULUS), hole = R * Math.sin(OCULUS);
  add(new THREE.SphereGeometry(R, 96, 32, 0, Math.PI * 2, OCULUS, Math.PI / 2 - OCULUS).translate(0, WALL_H, 0), M.dome);
  add(new THREE.TorusGeometry(hole, 0.16, 8, 64).rotateX(Math.PI / 2).translate(0, top, 0), M.bronze);
  add(new THREE.CircleGeometry(hole + 0.5, 48).rotateX(Math.PI / 2).translate(0, top + 0.4, 0), M.sky);
  add(new THREE.CylinderGeometry(hole * 0.95, hole * 1.5, top, 48, 1, true).translate(0, top / 2, 0), M.shaft);
  add(new THREE.CircleGeometry(hole * 1.6, 48).rotateX(-Math.PI / 2).translate(0, 0.006, 0), M.pool);

  // information stand: a lectern facing the entrance
  const tilt = 0.45;
  add(new THREE.CylinderGeometry(0.3, 0.46, 0.8, 40).translate(0, 0.4, 0), M.dark);
  add(new THREE.BoxGeometry(1.32, 0.06, 0.9).rotateX(tilt).translate(0, 1.0, 0), M.bronze);
  const panel = new THREE.MeshStandardMaterial({ map: T.texture(info, aniso), roughness: 0.8, color: 0xd8d0c2 });
  add(new THREE.PlaneGeometry(1.22, 0.8).rotateX(-Math.PI / 2 + tilt)
    .translate(0, 1.0 + 0.031 * Math.cos(tilt), 0.031 * Math.sin(tilt)), panel);
}

function gallery(add, gal, M) {
  const turn = new THREE.Matrix4().makeRotationY(gal.heading);
  const put = (g, material) => add(g.applyMatrix4(turn), material);
  const W = GALLERY_W, H = GALLERY_H, s0 = gal.start, s1 = gal.end, L = s1 - s0, mid = (s0 + s1) / 2;

  put(metres(new THREE.PlaneGeometry(W, L + 0.8), W, L + 0.8).rotateX(-Math.PI / 2).translate(0, 0, mid - 0.4), M.floor);
  for (const side of [-1, 1]) {
    put(metres(new THREE.PlaneGeometry(L, H), L, H).rotateY((-side * Math.PI) / 2).translate((side * W) / 2, H / 2, mid), M.wall);
    put(new THREE.BoxGeometry(0.06, 0.34, L).translate(side * (W / 2 - 0.03), 0.17, mid), M.dark);
    put(new THREE.BoxGeometry(0.36, 0.3, L).translate(side * (W / 2 - 0.15), H - 0.12, mid), M.stone);
  }

  // end walls, each with the vault's half-round top; the near one has the doorway cut out
  const endWall = (doorway) => {
    const s = new THREE.Shape().moveTo(-W / 2, 0);
    if (doorway) s.lineTo(-DOOR_W / 2, 0).lineTo(-DOOR_W / 2, DOOR_H).lineTo(DOOR_W / 2, DOOR_H).lineTo(DOOR_W / 2, 0);
    return new THREE.ShapeGeometry(s.lineTo(W / 2, 0).lineTo(W / 2, H).absarc(0, H, W / 2, 0, Math.PI, false).lineTo(-W / 2, 0), 24);
  };
  put(endWall(true).translate(0, 0, s0), M.wall);
  put(endWall(false).rotateY(Math.PI).translate(0, 0, s1), M.wall);
  put(metres(new THREE.CylinderGeometry(W / 2, W / 2, L, 48, 1, true, Math.PI / 2, Math.PI), (Math.PI * W) / 2, L)
    .rotateX(Math.PI / 2).translate(0, H, mid), M.vault);

  // pilasters and transverse ribs between the pedestal pairs
  for (let s = s0 + FIRST_PAIR - STEP / 2; s < s1 - 0.5; s += STEP) {
    for (const side of [-1, 1]) {
      put(new THREE.BoxGeometry(PILASTER, H - 0.3, 0.6).translate(side * (W / 2 - PILASTER / 2), (H - 0.3) / 2, s), M.stone);
    }
    put(new THREE.TorusGeometry(W / 2 - 0.05, 0.15, 8, 40, Math.PI).translate(0, H, s), M.stone);
  }

  if (gal.heading === 0) {  // entrance: daylight through the open doors
    put(new THREE.PlaneGeometry(3.2, 3.9).rotateY(Math.PI).translate(0, 1.95, s1 - 0.02), M.daylight);
    for (const side of [-1, 1]) put(new THREE.BoxGeometry(0.35, 4.2, 0.2).translate(side * 1.775, 2.1, s1 - 0.1), M.stone);
    put(new THREE.BoxGeometry(4.0, 0.4, 0.24).translate(0, 4.1, s1 - 0.12), M.stone);
  } else {                  // tall arched window
    put(new THREE.PlaneGeometry(2.4, 3).rotateY(Math.PI).translate(0, 2.5, s1 - 0.02), M.glass);
    put(new THREE.CircleGeometry(1.2, 32, 0, Math.PI).rotateY(Math.PI).translate(0, 4, s1 - 0.02), M.glass);
    const bar = (w, h, x, y) => put(new THREE.BoxGeometry(w, h, 0.06).translate(x, y, s1 - 0.05), M.bronze);
    for (const x of [-1.2, 0, 1.2]) bar(0.07, 3, x, 2.5);
    for (const y of [1, 2.5, 4]) bar(2.47, 0.07, 0, y);
    put(new THREE.TorusGeometry(1.2, 0.04, 6, 32, Math.PI).translate(0, 4, s1 - 0.05), M.bronze);
    put(new THREE.BoxGeometry(2.9, 0.12, 0.32).translate(0, 0.94, s1 - 0.16), M.stone);
  }
}

// Pedestal: dark plinth, white marble shaft and cap, soft shadows, and the placard on its front (+z).
function pedestal(add, spot, M, placard, aniso) {
  const at = new THREE.Matrix4().makeRotationY(spot.yaw).setPosition(spot.x, 0, spot.z);
  const put = (g, material) => add(g.applyMatrix4(at), material);
  put(new THREE.BoxGeometry(0.76, 0.12, 0.76).translate(0, 0.06, 0), M.dark);
  put(new THREE.BoxGeometry(0.6, 0.86, 0.6).translate(0, 0.55, 0), M.white);
  put(new THREE.BoxGeometry(0.7, 0.06, 0.7).translate(0, PEDESTAL_TOP - 0.03, 0), M.white);
  put(new THREE.PlaneGeometry(1.5, 1.5).rotateX(-Math.PI / 2).translate(0, 0.003, 0), M.shadow);
  put(new THREE.PlaneGeometry(0.62, 0.62).rotateX(-Math.PI / 2).translate(0, PEDESTAL_TOP + 0.002, 0), M.shadow);
  put(new THREE.BoxGeometry(0.5, 0.33, 0.025).rotateX(-0.2).translate(0, 0.62, 0.316), M.bronze);
  const label = new THREE.MeshStandardMaterial({ map: T.texture(placard, aniso), roughness: 0.75, color: 0xd8d0c2 });
  put(new THREE.PlaneGeometry(0.46, 0.29).rotateX(-0.2).translate(0, 0.62, 0.331), label);
}

// Freestanding signboard on two bronze posts; the panel (1.6 × 2.2 m) faces the board's front (+z).
function signboard(add, spot, M, picture, aniso) {
  const at = new THREE.Matrix4().makeRotationY(spot.yaw).setPosition(spot.x, 0, spot.z);
  const put = (g, material) => add(g.applyMatrix4(at), material);
  for (const side of [-1, 1]) {
    put(new THREE.BoxGeometry(0.07, 2.75, 0.07).translate(side * 0.72, 1.375, -0.06), M.bronze);
    put(new THREE.BoxGeometry(0.12, 0.05, 0.5).translate(side * 0.72, 0.025, -0.06), M.bronze);
  }
  put(new THREE.BoxGeometry(1.72, 2.32, 0.05).translate(0, 1.55, 0), M.dark);
  put(new THREE.PlaneGeometry(1.8, 1.8).rotateX(-Math.PI / 2).translate(0, 0.003, 0), M.shadow);
  const face = new THREE.MeshStandardMaterial({ map: T.texture(picture, aniso), roughness: 0.8, color: 0xd8d0c2 });
  put(new THREE.PlaneGeometry(1.6, 2.2).translate(0, 1.55, 0.026), face);
}

// The whole building as one group: placards[i] belongs to plan.spots[i], signs[i] to GALLERIES[i] and
// boards[i] to plan.boards[i].
export function buildHall(plan, { aniso, placards, signs, info, boards }) {
  const M = materials(aniso);
  const parts = new Map();
  const add = (geometry, material) => (parts.get(material) ?? parts.set(material, []).get(material)).push(geometry);
  rotunda(add, M, aniso, signs, info);
  for (const gal of plan.galleries) gallery(add, gal, M);
  plan.spots.forEach((spot, i) => pedestal(add, spot, M, placards[i], aniso));
  plan.boards.forEach((spot, i) => signboard(add, spot, M, boards[i], aniso));

  const group = new THREE.Group();
  for (const [material, list] of parts) {
    const mesh = new THREE.Mesh(list.length > 1 ? mergeGeometries(list) : list[0], material);
    if (material.transparent) mesh.renderOrder = 1;
    group.add(mesh);
  }
  return group;
}
