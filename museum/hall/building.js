// Architecture of the hall (rotunda, dome, galleries) and the pedestals, built from the floor plan.
// Parts that share a material are merged into one mesh, so the whole building costs a few draw calls.
import * as THREE from "three";
import { mergeGeometries, mergeVertices } from "three/addons/utils/BufferGeometryUtils.js";
import {
  DOOR_H, DOOR_W, FIRST_PAIR, GALLERIES, GALLERY_H, GALLERY_START, GALLERY_W, PEDESTAL_TOP, PILASTER, RISERS,
  ROTUNDA_R as R, STAIR_RUN, STEP, UPPER_FLOOR, WALL_H,
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

// Stone frame and dark sill for a doorway in an end wall at s, its floor at height y.
function doorFrame(put, M, s, y) {
  for (const side of [-1, 1]) put(new THREE.BoxGeometry(0.3, DOOR_H, 0.34).translate(side * (DOOR_W / 2 + 0.15), y + DOOR_H / 2, s), M.stone);
  put(new THREE.BoxGeometry(DOOR_W + 0.6, 0.3, 0.34).translate(0, y + DOOR_H + 0.15, s), M.stone);
  put(metres(new THREE.PlaneGeometry(DOOR_W, 0.7), DOOR_W, 0.7).rotateX(-Math.PI / 2).translate(0, y + 0.004, s), M.dark);
}

// Tall arched window in an end wall at s; dir is +1 when the room lies towards larger s.
function endWindow(put, M, s, dir) {
  const turned = (g) => (dir < 0 ? g.rotateY(Math.PI) : g);
  const inner = s + dir * 0.02, bars = s + dir * 0.05;
  put(turned(new THREE.PlaneGeometry(2.4, 3)).translate(0, 2.5, inner), M.glass);
  put(turned(new THREE.CircleGeometry(1.2, 32, 0, Math.PI)).translate(0, 4, inner), M.glass);
  const bar = (w, h, x, y) => put(new THREE.BoxGeometry(w, h, 0.06).translate(x, y, bars), M.bronze);
  for (const x of [-1.2, 0, 1.2]) bar(0.07, 3, x, 2.5);
  for (const y of [1, 2.5, 4]) bar(2.47, 0.07, 0, y);
  put(new THREE.TorusGeometry(1.2, 0.04, 6, 32, Math.PI).translate(0, 4, bars), M.bronze);
  put(new THREE.BoxGeometry(2.9, 0.12, 0.32).translate(0, 0.94, s + dir * 0.16), M.stone);
}

function gallery(add, gal, M) {
  const turn = new THREE.Matrix4().makeRotationY(gal.heading).setPosition(gal.x ?? 0, gal.y ?? 0, gal.z ?? 0);
  const put = (g, material) => add(g.applyMatrix4(turn), material);
  const W = GALLERY_W, H = gal.height ?? GALLERY_H, s0 = gal.start, s1 = gal.end, L = s1 - s0, mid = (s0 + s1) / 2;
  const back = gal.floorBack ?? 0.8;  // how far the floor runs on under the near doorway
  const open = DOOR_W / 2;            // half width of a doorway in a side wall (gal.opening is that wall's side)

  put(metres(new THREE.PlaneGeometry(W, L + back), W, L + back).rotateX(-Math.PI / 2).translate(0, 0, mid - back / 2), M.floor);
  for (const side of [-1, 1]) {
    const wall = (a, b, y0, y1) => put(metres(new THREE.PlaneGeometry(b - a, y1 - y0), b - a, y1 - y0)
      .rotateY((-side * Math.PI) / 2).translate((side * W) / 2, (y0 + y1) / 2, (a + b) / 2), M.wall);
    const skirting = (a, b) => put(new THREE.BoxGeometry(0.06, 0.34, b - a).translate(side * (W / 2 - 0.03), 0.17, (a + b) / 2), M.dark);
    if (gal.opening === side) {
      wall(s0, -open, 0, H);
      wall(open, s1, 0, H);
      wall(-open, open, DOOR_H, H);
      skirting(s0, -open);
      skirting(open, s1);
      for (const s of [-1, 1]) put(new THREE.BoxGeometry(0.34, DOOR_H, 0.3).translate((side * W) / 2, DOOR_H / 2, s * (open + 0.15)), M.stone);
      put(new THREE.BoxGeometry(0.34, 0.3, DOOR_W + 0.6).translate((side * W) / 2, DOOR_H + 0.15, 0), M.stone);
      put(metres(new THREE.PlaneGeometry(0.7, DOOR_W), 0.7, DOOR_W).rotateX(-Math.PI / 2).translate(side * (W / 2 - 0.1), 0.004, 0), M.dark);
    } else {
      wall(s0, s1, 0, H);
      skirting(s0, s1);
    }
    put(new THREE.BoxGeometry(0.36, 0.3, L).translate(side * (W / 2 - 0.15), H - 0.12, mid), M.stone);
  }

  // end walls, each with the vault's half-round top; a doorway is cut out at the floor or, at the top of the
  // stairs, at the upper floor
  const endWall = (kind) => {
    const s = new THREE.Shape().moveTo(-W / 2, 0);
    if (kind === "door") s.lineTo(-DOOR_W / 2, 0).lineTo(-DOOR_W / 2, DOOR_H).lineTo(DOOR_W / 2, DOOR_H).lineTo(DOOR_W / 2, 0);
    s.lineTo(W / 2, 0).lineTo(W / 2, H).absarc(0, H, W / 2, 0, Math.PI, false).lineTo(-W / 2, 0);
    if (kind === "upperDoor") {
      s.holes.push(new THREE.Path().moveTo(-DOOR_W / 2, UPPER_FLOOR).lineTo(DOOR_W / 2, UPPER_FLOOR)
        .lineTo(DOOR_W / 2, UPPER_FLOOR + DOOR_H).lineTo(-DOOR_W / 2, UPPER_FLOOR + DOOR_H).lineTo(-DOOR_W / 2, UPPER_FLOOR));
    }
    return new THREE.ShapeGeometry(s, 24);
  };
  const nearEnd = gal.nearEnd ?? "door", farEnd = gal.farEnd ?? (gal.heading === 0 ? "daylight" : "window");
  put(endWall(nearEnd).translate(0, 0, s0), M.wall);
  put(endWall(farEnd).rotateY(Math.PI).translate(0, 0, farEnd === "upperDoor" ? s1 - 0.02 : s1), M.wall);
  put(metres(new THREE.CylinderGeometry(W / 2, W / 2, L, 48, 1, true, Math.PI / 2, Math.PI), (Math.PI * W) / 2, L)
    .rotateX(Math.PI / 2).translate(0, H, mid), M.vault);

  // pilasters and transverse ribs between the pedestal pairs
  const ribs = gal.ribs ?? [];
  if (!gal.ribs) for (let s = s0 + FIRST_PAIR - STEP / 2; s < s1 - 0.5; s += STEP) ribs.push(s);
  for (const s of ribs) {
    for (const side of [-1, 1]) {
      if (gal.opening === side && Math.abs(s) < open + 0.6) continue;
      put(new THREE.BoxGeometry(PILASTER, H - 0.3, 0.6).translate(side * (W / 2 - PILASTER / 2), (H - 0.3) / 2, s), M.stone);
    }
    put(new THREE.TorusGeometry(W / 2 - 0.05, 0.15, 8, 40, Math.PI).translate(0, H, s), M.stone);
  }

  if (nearEnd === "window") endWindow(put, M, s0, 1);
  if (farEnd === "daylight") {  // entrance: daylight through the open doors
    put(new THREE.PlaneGeometry(3.2, 3.9).rotateY(Math.PI).translate(0, 1.95, s1 - 0.02), M.daylight);
    for (const side of [-1, 1]) put(new THREE.BoxGeometry(0.35, 4.2, 0.2).translate(side * 1.775, 2.1, s1 - 0.1), M.stone);
    put(new THREE.BoxGeometry(4.0, 0.4, 0.24).translate(0, 4.1, s1 - 0.12), M.stone);
  } else if (farEnd === "window") {
    endWindow(put, M, s1, -1);
  } else if (farEnd === "door") {
    doorFrame(put, M, s1, 0);
  } else if (farEnd === "upperDoor") {
    doorFrame(put, M, s1 - 0.17, UPPER_FLOOR);
  }

  if (gal.windows) {  // high windows either side of a stair hall
    for (let s = s0 + FIRST_PAIR; s < s1 - 1; s += STEP) {
      for (const side of [-1, 1]) {
        const x = side * (W / 2 - 0.02), turned = (g) => g.rotateY((-side * Math.PI) / 2);
        put(turned(new THREE.PlaneGeometry(1.6, 2.6)).translate(x, 6.3, s), M.glass);
        put(turned(new THREE.CircleGeometry(0.8, 24, 0, Math.PI)).translate(x, 7.6, s), M.glass);
        put(new THREE.BoxGeometry(0.2, 0.1, 1.9).translate(side * (W / 2 - 0.1), 4.96, s), M.stone);
      }
    }
  }
}

// Two flights with a half landing between low stone walls topped by a bronze rail, and the signs at each end.
function staircase(add, plan, M, aniso, sign, board) {
  const { foot, flight, landing, top } = plan.stairs;
  const turn = new THREE.Matrix4().makeRotationY(Math.PI);  // the north gallery's direction
  const put = (g, material) => add(g.applyMatrix4(turn), material);
  const rise = UPPER_FLOOR / 2 / RISERS, half = UPPER_FLOOR / 2, W = DOOR_W, RAIL = 1;

  for (const [start, base] of [[foot, 0], [foot + flight + landing, half]]) {
    for (let i = 0; i < RISERS; i++) {
      const z = start + i * STAIR_RUN, y = base + (i + 1) * rise;
      put(metres(new THREE.BoxGeometry(W, rise, STAIR_RUN), W, STAIR_RUN).translate(0, y - rise / 2, z + STAIR_RUN / 2), M.white);
      put(new THREE.BoxGeometry(W, 0.025, 0.05).translate(0, y - 0.012, z + 0.025), M.dark);  // step edge
    }
  }
  put(metres(new THREE.BoxGeometry(W, 0.1, landing), W, landing).translate(0, half - 0.05, foot + flight + landing / 2), M.floor);

  const line = [[foot, 0], [foot + flight, half], [foot + flight + landing, half], [top, UPPER_FLOOR]];
  const wall = new THREE.Shape().moveTo(foot - 0.3, 0).lineTo(foot - 0.3, RAIL).lineTo(foot, RAIL);
  for (const [s, y] of line.slice(1)) wall.lineTo(s, y + RAIL);
  wall.lineTo(top, 0).lineTo(foot - 0.3, 0);
  for (const side of [-1, 1]) {
    const x = side > 0 ? W / 2 + 0.24 : -W / 2;
    put(mergeVertices(new THREE.ExtrudeGeometry(wall, { depth: 0.24, bevelEnabled: false })).rotateY(-Math.PI / 2).translate(x, 0, 0), M.stone);
    for (let i = 0; i < line.length - 1; i++) {
      const [s0, y0] = line[i], [s1, y1] = line[i + 1], ds = s1 - s0, dy = y1 - y0;
      put(new THREE.BoxGeometry(0.1, 0.06, Math.hypot(ds, dy)).rotateX(-Math.atan2(dy, ds))
        .translate(side * (W / 2 + 0.12), (y0 + y1) / 2 + RAIL + 0.03, (s0 + s1) / 2), M.bronze);
    }
    put(new THREE.BoxGeometry(0.42, RAIL + 0.2, 0.42).translate(side * (W / 2 + 0.12), (RAIL + 0.2) / 2, foot - 0.15), M.stone);
  }

  // over the door at the foot of the stairs, seen from the north gallery
  const lunette = new THREE.MeshStandardMaterial({ map: T.texture(sign, aniso), roughness: 0.9 });
  const end = plan.galleries[2].end;
  put(new THREE.CircleGeometry(W / 2, 48, 0, Math.PI).rotateY(Math.PI).translate(0, DOOR_H + 0.3, end - 0.18), lunette);

  // on the north wall, facing the top of the stairs
  const at = new THREE.Matrix4().setPosition(0, UPPER_FLOOR, -(top + GALLERY_W - 0.04));
  const face = new THREE.MeshStandardMaterial({ map: T.texture(board, aniso), roughness: 0.8, color: 0xd8d0c2 });
  add(new THREE.BoxGeometry(3.1, 2.1, 0.03).translate(0, 2.3, -0.015).applyMatrix4(at), M.dark);
  add(new THREE.PlaneGeometry(3, 2).translate(0, 2.3, 0.002).applyMatrix4(at), face);
}

// Pedestal: dark plinth, white marble shaft and cap, soft shadows, and the placard on its front (+z).
function pedestal(add, spot, M, placard, aniso) {
  const at = new THREE.Matrix4().makeRotationY(spot.yaw).setPosition(spot.x, spot.y, spot.z);
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
// boards[i] to plan.boards[i]; stairSign and upperBoard are only used when the plan has a staircase.
export function buildHall(plan, { aniso, placards, signs, info, boards, stairSign, upperBoard }) {
  const M = materials(aniso);
  const parts = new Map();
  const add = (geometry, material) => (parts.get(material) ?? parts.set(material, []).get(material)).push(geometry);
  rotunda(add, M, aniso, signs, info);
  for (const room of plan.rooms) gallery(add, room, M);
  if (plan.stairs) staircase(add, plan, M, aniso, stairSign, upperBoard);
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
