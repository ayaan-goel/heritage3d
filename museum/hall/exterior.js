// The museum seen from outside, at the end of the drive behind the main gate. Drawn from the same floor plan as
// the hall, so the wings, the stair hall and the upper gallery stand where they do inside; the portico and the
// outer dome are invented for the view. Metres, y up, in the gate scene's coordinates.
import * as THREE from "three";
import { GALLERY_H, GALLERY_W, ROTUNDA_R } from "./layout.js";

export const FRONT = -48;      // z of the entrance front
const PORCH = 3.6;             // how far the portico stands forward of it
export const PORCH_W = 13;     // its half width
export const PORCH_Y = 0.9;    // height of its floor above the ground
export const STEPS_TOP = PORCH + 0.5;     // from the front wall to the top step's edge
export const STEPS_FOOT = STEPS_TOP + 1.2;  // and to the bottom step's edge
export const COLUMN_Z = FRONT + PORCH - 0.5;
export const COLUMN_X = [-10, -6, -2, 2, 6, 10];
const WALL = 0.4;              // walls and roofs stand this far outside the rooms
const DRUM_R = ROTUNDA_R + 0.6, DRUM_H = 13;

// texture coordinates in metres
function metres(geometry, su, sv) {
  const uv = geometry.attributes.uv;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * su, uv.getY(i) * sv);
  return geometry;
}

export const EXTERIOR_MATERIALS = (std, plain, plaster) => ({
  outWall: std(plaster("#e6dcc6", 21), 0.92),
  outStone: std(plaster("#f2ecdf", 22), 0.85),
  outRoof: plain(0x8d9091, 0.8, 0.2),
  outDome: plain(0x6f9c8e, 0.65, 0.25),
  outGlass: plain(0x2d3a44, 0.25, 0.4),
  outDoor: plain(0x4a3522, 0.5, 0.3),
});

function wing(add, room, centreZ) {
  const turn = new THREE.Matrix4().makeRotationY(room.heading).setPosition(room.x ?? 0, 0, (room.z ?? 0) + centreZ);
  const put = (name, g) => add(name, g.applyMatrix4(turn));
  const W = GALLERY_W + 2 * WALL, r = W / 2, s0 = room.start, s1 = room.end, L = s1 - s0, mid = (s0 + s1) / 2;
  const H = (room.y ?? 0) + (room.height ?? GALLERY_H);

  put("outWall", metres(new THREE.BoxGeometry(W, H, L), L, H).translate(0, H / 2, mid));
  put("outRoof", new THREE.CylinderGeometry(r, r, L, 24, 1, false, Math.PI / 2, Math.PI).rotateX(Math.PI / 2).translate(0, H, mid));
  for (const side of [-1, 1]) {
    put("outStone", new THREE.BoxGeometry(0.3, 0.4, L + 0.3).translate(side * (r + 0.05), H - 0.1, mid));
    put("outStone", new THREE.BoxGeometry(0.2, 0.5, L + 0.2).translate(side * (r + 0.02), 0.25, mid));
    for (let s = s0 + 2.6; s < s1 - 1; s += 3.2) {  // a tall arched window with a pilaster beside it
      const x = side * (r + 0.02), sill = H - 3.8;
      put("outGlass", new THREE.BoxGeometry(0.08, 2.4, 1.3).translate(x, sill + 1.2, s));
      put("outGlass", new THREE.CylinderGeometry(0.65, 0.65, 0.08, 16).rotateZ(Math.PI / 2).translate(x, sill + 2.4, s));
      put("outStone", new THREE.BoxGeometry(0.14, 0.14, 1.7).translate(x, sill - 0.05, s));
      if (s + 1.6 < s1 - 0.5) put("outStone", new THREE.BoxGeometry(0.2, H - 0.8, 0.5).translate(side * (r + 0.05), (H - 0.8) / 2 + 0.4, s + 1.6));
    }
  }
}

function rotunda(add, z) {
  const at = (g) => g.translate(0, 0, z);
  add("outWall", at(metres(new THREE.CylinderGeometry(DRUM_R, DRUM_R, DRUM_H, 64), 66, DRUM_H).translate(0, DRUM_H / 2, 0)));
  add("outStone", at(new THREE.CylinderGeometry(DRUM_R + 0.3, DRUM_R + 0.3, 0.45, 64).translate(0, DRUM_H + 0.1, 0)));
  for (let k = 0; k < 20; k++) {  // high windows above the gallery roofs, with pilasters between them
    const a = (k * Math.PI) / 10;
    add("outGlass", at(new THREE.BoxGeometry(1.1, 0.95, 0.1).translate(0, DRUM_H - 0.95, DRUM_R + 0.02).rotateY(a)));
    add("outGlass", at(new THREE.CylinderGeometry(0.55, 0.55, 0.1, 14).rotateX(Math.PI / 2).translate(0, DRUM_H - 0.5, DRUM_R + 0.02).rotateY(a)));
    add("outStone", at(new THREE.BoxGeometry(0.4, DRUM_H, 0.25).translate(0, DRUM_H / 2, DRUM_R).rotateY(a + Math.PI / 20)));
  }
  const dome = DRUM_H + 0.3, R = DRUM_R - 0.2, squash = 0.85, top = dome + R * squash;
  add("outDome", at(new THREE.SphereGeometry(R, 48, 16, 0, Math.PI * 2, 0, Math.PI / 2).scale(1, squash, 1).translate(0, dome, 0)));
  for (let k = 0; k < 16; k++) {
    add("outStone", at(new THREE.TorusGeometry(R + 0.03, 0.09, 6, 24, Math.PI / 2).scale(1, squash, 1).translate(0, dome, 0).rotateY((k * Math.PI) / 8)));
  }
  // the lantern over the dome's opening
  add("outStone", at(new THREE.CylinderGeometry(1.75, 1.95, 0.5, 24).translate(0, top - 0.1, 0)));
  add("outGlass", at(new THREE.CylinderGeometry(1.3, 1.3, 1.7, 16).translate(0, top + 1, 0)));
  for (let k = 0; k < 8; k++) add("outStone", at(new THREE.BoxGeometry(0.22, 1.7, 0.22).translate(0, top + 1, 1.32).rotateY((k * Math.PI) / 4)));
  add("outStone", at(new THREE.CylinderGeometry(1.6, 1.6, 0.22, 24).translate(0, top + 1.95, 0)));
  add("outDome", at(new THREE.SphereGeometry(1.45, 20, 8, 0, Math.PI * 2, 0, Math.PI / 2).scale(1, 0.8, 1).translate(0, top + 2.05, 0)));
  add("outStone", at(new THREE.CylinderGeometry(0.03, 0.09, 1, 8).translate(0, top + 3.6, 0)));
}

function portico(add, box, post) {
  const zf = FRONT + PORCH, plinth = PORCH_Y, shaft = 5.6, beamTop = plinth + shaft + 1.1;
  for (let i = 0; i < 3; i++) {  // steps up to the columns
    const y = plinth - (i * plinth) / 3, out = STEPS_TOP + i * 0.6;
    add("outStone", box(-PORCH_W - 0.4 - i * 0.6, PORCH_W + 0.4 + i * 0.6, 0, y, FRONT, FRONT + out));
  }
  for (const x of COLUMN_X) {
    add("outStone", post(x, COLUMN_Z, 0.48, 0.38, shaft, plinth));
    add("outStone", box(x - 0.6, x + 0.6, plinth, plinth + 0.3, zf - 1.1, zf + 0.1));
  }
  add("outStone", box(-PORCH_W, PORCH_W, plinth + shaft, beamTop, FRONT, zf));
  add("outWall", box(-PORCH_W, PORCH_W, 0, beamTop, FRONT - 1, FRONT));

  const gable = new THREE.Shape().moveTo(-PORCH_W - 0.4, 0).lineTo(PORCH_W + 0.4, 0).lineTo(0, 2.2).lineTo(-PORCH_W - 0.4, 0);
  add("outStone", new THREE.ExtrudeGeometry(gable, { depth: PORCH + 1.2, bevelEnabled: false }).translate(0, beamTop, FRONT - 1));

  // the doors, open to the same lobby the visitor walks into, and windows either side
  add("outDoor", box(-1.9, 1.9, plinth, plinth + 4.6, FRONT, FRONT + 0.08));
  add("outStone", box(-2.2, 2.2, plinth + 4.6, plinth + 5, FRONT, FRONT + 0.14));
  for (const x of [-8, 8]) {
    add("outGlass", box(x - 1, x + 1, plinth + 1, plinth + 4.6, FRONT, FRONT + 0.06));
    add("outStone", box(x - 1.25, x + 1.25, plinth + 4.6, plinth + 4.9, FRONT, FRONT + 0.12));
  }
}

// The whole building as parts for the gate scene's add(name, geometry); box and post are its helpers.
export function buildExterior(add, plan, box, post) {
  const centreZ = FRONT - plan.galleries[0].end;
  for (const room of plan.rooms) wing(add, room, centreZ);
  rotunda(add, centreZ);
  portico(add, box, post);
  return { centreZ, nameY: 0.9 + 5.6 + 0.55, nameZ: FRONT + PORCH + 0.005, nameW: 21, nameH: 1.05 };
}
