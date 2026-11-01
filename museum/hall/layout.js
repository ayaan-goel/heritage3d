// Floor plan of the hall, sized from the number of exhibits: a domed rotunda (its centre is the origin)
// with four galleries; the south gallery is the entrance. Metres, y up. A heading is measured from +z
// (south) towards +x (east), like THREE.CylinderGeometry's theta.

export const EYE = 1.6;              // eye height of the visitor
export const BODY = 0.35;            // visitor radius for collisions
export const ROTUNDA_R = 10;
export const WALL_H = 7.5;           // rotunda wall height; the dome starts here
export const DOOR_W = 5;             // doorway from the rotunda into a gallery
export const DOOR_H = 4.6;
export const WALL_T = 0.6;           // rotunda wall thickness at the doorways
export const GALLERY_START = ROTUNDA_R + WALL_T;
export const GALLERY_W = 8;
export const GALLERY_H = 5.2;        // gallery wall height; a barrel vault sits on top
export const PILASTER = 0.3;         // how far the wall pilasters stand out
export const PEDESTAL_TOP = 1.04;
export const STEP = 3.2;             // between pedestal pairs along a gallery
export const FIRST_PAIR = 2.6;       // from a gallery's start (and end) to its first (and last) pair
const ROW = 2.2;                     // pedestal distance from a gallery's centre line
const LOBBY = 3;                     // extra length of the entrance gallery, where visitors start
const RING_R = 6.6;                  // rotunda pedestal ring
const RING_DEG = [32, 58, 122, 148, 212, 238, 302, 328];
const PEDESTAL_R = 0.52;             // circle around a pedestal's footprint
const STAND_R = 0.75;                // information stand in the middle of the rotunda

export const GALLERIES = [
  { name: "South", heading: 0 },
  { name: "East", heading: Math.PI / 2 },
  { name: "North", heading: Math.PI },
  { name: "West", heading: Math.PI * 1.5 },
];

// gallery coordinates (s along it from the rotunda centre, v across it) -> world [x, z]
export function toWorld(heading, s, v) {
  const sin = Math.sin(heading), cos = Math.cos(heading);
  return [s * sin + v * cos, s * cos - v * sin];
}

function toGallery(heading, x, z) {
  const sin = Math.sin(heading), cos = Math.cos(heading);
  return [x * sin + z * cos, x * cos - z * sin];
}

// yaw that turns an object's front (+z) towards the direction (dx, dz)
const facing = (dx, dz) => Math.atan2(dx, dz);

export function planHall(n) {
  const ring = Math.min(n, RING_DEG.length);
  const rest = n - ring;
  const counts = GALLERIES.map((_, g) => Math.floor(rest / 4) + (g < rest % 4 ? 1 : 0));
  const pairs = Math.max(1, Math.ceil(Math.max(...counts) / 2));
  const galleries = GALLERIES.map((g, i) => {
    const length = 2 * FIRST_PAIR + (pairs - 1) * STEP + (i === 0 ? LOBBY : 0);
    return { ...g, start: GALLERY_START, end: GALLERY_START + length };
  });

  // pedestal places of a gallery, pair by pair from the rotunda outwards; fronts face the centre line
  const slots = ({ heading }) => {
    const out = [];
    for (let p = 0; p < pairs; p++) {
      for (const side of [1, -1]) {
        const [x, z] = toWorld(heading, GALLERY_START + FIRST_PAIR + p * STEP, side * ROW);
        out.push({ x, z, yaw: facing(...toWorld(heading, 0, -side)) });
      }
    }
    return out;
  };

  // exhibits are numbered in visiting order: entrance gallery, rotunda, then east, north and west
  const spots = [], zones = [];
  const add = (name, list) => {
    if (list.length) zones.push({ name, from: spots.length + 1, to: spots.length + list.length });
    spots.push(...list);
  };
  add("South gallery", slots(galleries[0]).slice(0, counts[0]).reverse());
  add("Rotunda", RING_DEG.slice(0, ring).map((deg) => {
    const a = (deg * Math.PI) / 180;
    return { x: RING_R * Math.sin(a), z: RING_R * Math.cos(a), yaw: a + Math.PI };
  }));
  for (const g of [1, 2, 3]) add(`${GALLERIES[g].name} gallery`, slots(galleries[g]).slice(0, counts[g]));

  const obstacles = [...spots.map(({ x, z }) => ({ x, z, r: PEDESTAL_R + BODY })), { x: 0, z: 0, r: STAND_R + BODY }];
  const roomR = ROTUNDA_R - PILASTER - BODY;
  const halfDoor = DOOR_W / 2 - BODY, halfGallery = GALLERY_W / 2 - PILASTER - BODY;

  function inside(x, z) {
    if (Math.hypot(x, z) <= roomR) return true;
    return galleries.some((g) => {
      const [s, v] = toGallery(g.heading, x, z);
      return (Math.abs(v) <= halfDoor && s >= ROTUNDA_R - 2 && s <= GALLERY_START + BODY + 0.05)
        || (Math.abs(v) <= halfGallery && s >= GALLERY_START + BODY && s <= g.end - BODY);
    });
  }

  // round obstacles push the visitor out sideways, so walking into a pedestal slides around it
  function pushOut(x, z) {
    for (const o of obstacles) {
      const dx = x - o.x, dz = z - o.z, d = Math.hypot(dx, dz);
      if (d < o.r && d > 1e-6) {
        x = o.x + (dx / d) * o.r;
        z = o.z + (dz / d) * o.r;
      }
    }
    return [x, z];
  }

  const free = (x, z) => inside(x, z) && obstacles.every((o) => Math.hypot(x - o.x, z - o.z) >= o.r - 1e-6);

  // one step of walking: full step, else slide along the rotunda wall, else along the x or z axis
  function move(x, z, dx, dz) {
    const tries = [[dx, dz]];
    const r = Math.hypot(x, z);
    if (r > 1e-6) {
      const nx = x / r, nz = z / r, out = dx * nx + dz * nz;
      if (out > 0) tries.push([dx - out * nx, dz - out * nz]);
    }
    tries.push([dx, 0], [0, dz]);
    for (const [ax, az] of tries) {
      const p = pushOut(x + ax, z + az);
      if (free(...p)) return p;
    }
    return [x, z];
  }

  const [sx, sz] = toWorld(0, galleries[0].end - 1.6, 0);
  return {
    spots, zones, galleries,
    spawn: { x: sx, z: sz, yaw: 0 },
    extent: Math.max(...galleries.map((g) => g.end)) + 0.5,
    move,
  };
}
