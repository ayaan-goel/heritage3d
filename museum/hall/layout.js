// Floor plan of the hall, sized from the number of exhibits: a domed rotunda (its centre is the origin)
// with four galleries; the south gallery is the entrance. A staircase past the north gallery climbs to an
// upper gallery for the artifacts outside the main set. No walkable place lies above another, so the
// visitor's height follows from where they stand (height()). Metres, y up. A heading is measured from +z
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
export const UPPER_FLOOR = 5.4;      // height of the upper floor above the ground floor
export const RISERS = 15;            // steps per flight; two flights
export const STAIR_RUN = 0.3;        // depth of one step
const FLIGHT = RISERS * STAIR_RUN;
const FOYER = 1.2;                   // floor between the north gallery's far door and the first step
const LANDING = 2;                   // half landing between the flights
const UPPER_GAP = 3.6;               // from the top of the stairs along the upper gallery to its first pair
const ROW = 2.2;                     // pedestal distance from a gallery's centre line
const LOBBY = 7.5;                   // extra length of the entrance gallery, where visitors start
const RING_R = 6.6;                  // rotunda pedestal ring
const RING_DEG = [32, 58, 122, 148, 212, 238, 302, 328];
const PEDESTAL_R = 0.52;             // circle around a pedestal's footprint
const STAND_R = 0.75;                // information stand in the middle of the rotunda
const BOARD_R = 0.75;                // entrance signboards

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

// n exhibits on the ground floor, upper on the upper floor (numbered after them)
export function planHall(n, upper = 0) {
  const ring = Math.min(n, RING_DEG.length);
  const rest = n - ring;
  const counts = GALLERIES.map((_, g) => Math.floor(rest / 4) + (g < rest % 4 ? 1 : 0));
  const pairs = Math.max(1, Math.ceil(Math.max(...counts) / 2));
  const galleries = GALLERIES.map((g, i) => {
    const length = 2 * FIRST_PAIR + (pairs - 1) * STEP + (i === 0 ? LOBBY : 0);
    return { ...g, start: GALLERY_START, end: GALLERY_START + length };
  });

  // the staircase, in the north gallery's coordinates, and the upper gallery across its top
  const north = galleries[2];
  const stairs = upper ? { foot: north.end + FOYER, flight: FLIGHT, landing: LANDING } : null;
  const rooms = [...galleries];
  let top = 0, loft = null;
  if (upper) {
    north.farEnd = "door";
    top = stairs.foot + 2 * FLIGHT + LANDING;
    stairs.top = top;
    const wing = Math.max(1, Math.ceil(Math.ceil(upper / 2) / 2));
    const half = UPPER_GAP + (wing - 1) * STEP + FIRST_PAIR;
    const ribs = [];
    for (let s = UPPER_GAP - STEP / 2; s < half - 0.5; s += STEP) ribs.push(s, -s);
    loft = {
      name: "Upper", heading: Math.PI / 2, x: 0, y: UPPER_FLOOR, z: -(top + GALLERY_W / 2), start: -half, end: half,
      nearEnd: "window", farEnd: "window", floorBack: 0, opening: -1, ribs,
    };
    rooms.push({
      name: "Stairs", heading: Math.PI, start: north.end + 0.04, end: top, height: UPPER_FLOOR + GALLERY_H,
      nearEnd: "door", farEnd: "upperDoor", floorBack: 0, windows: true,
    }, loft);
  }

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
    spots.push(...list.map((spot) => ({ y: 0, ...spot })));
  };
  add("South gallery", slots(galleries[0]).slice(0, counts[0]).reverse());
  add("Rotunda", RING_DEG.slice(0, ring).map((deg) => {
    const a = (deg * Math.PI) / 180;
    return { x: RING_R * Math.sin(a), z: RING_R * Math.cos(a), yaw: a + Math.PI };
  }));
  for (const g of [1, 2, 3]) add(`${GALLERIES[g].name} gallery`, slots(galleries[g]).slice(0, counts[g]));
  if (upper) {  // from the top of the stairs outwards, the east wing and then the west wing
    const places = [];
    for (const dir of [1, -1]) {
      const inWing = dir > 0 ? Math.ceil(upper / 2) : Math.floor(upper / 2);
      for (let i = 0; i < inWing; i++) {
        const side = i % 2 ? -1 : 1, s = dir * (UPPER_GAP + Math.floor(i / 2) * STEP);
        const [x, z] = toWorld(loft.heading, s, side * ROW);
        places.push({ x: loft.x + x, y: UPPER_FLOOR, z: loft.z + z, yaw: facing(...toWorld(loft.heading, 0, -side)) });
      }
    }
    add("Upper floor", places);
  }

  // the circle leading outside beside the entrance doors, then where visitors start, then two signboards
  // either side of the aisle, turned towards the start
  const entrance = galleries[0].end, start = toWorld(0, entrance - 3.4, 0);
  const [exitX, exitZ] = toWorld(0, entrance - 1.6, -2.4);  // off the aisle, clear of a third-person camera
  const boards = [-1, 1].map((side) => {
    const [x, z] = toWorld(0, entrance - 6.6, side * 2.4);
    return { x, z, yaw: facing(start[0] - x, start[1] - z), side };
  });

  const obstacles = [
    ...spots.map(({ x, z }) => ({ x, z, r: PEDESTAL_R + BODY })),
    { x: 0, z: 0, r: STAND_R + BODY },
    ...boards.map(({ x, z }) => ({ x, z, r: BOARD_R + BODY })),
  ];
  const roomR = ROTUNDA_R - PILASTER - BODY;
  const halfDoor = DOOR_W / 2 - BODY, halfGallery = GALLERY_W / 2 - PILASTER - BODY;

  function inside(x, z) {
    if (Math.hypot(x, z) <= roomR) return true;
    return galleries.some((g) => {
      const [s, v] = toGallery(g.heading, x, z);
      return (Math.abs(v) <= halfDoor && s >= ROTUNDA_R - 2 && s <= GALLERY_START + BODY + 0.05)
        || (Math.abs(v) <= halfGallery && s >= GALLERY_START + BODY && s <= g.end - BODY);
    }) || (upper > 0 && insideUpstairs(x, z));
  }

  function insideUpstairs(x, z) {
    const [s, v] = toGallery(north.heading, x, z);
    if (Math.abs(v) <= halfDoor && s >= north.end - BODY - 0.1 && s <= top + PILASTER + BODY + 0.1) return true;
    const [along, across] = toGallery(loft.heading, x - loft.x, z - loft.z);
    return Math.abs(along) <= loft.end - BODY && Math.abs(across) <= halfGallery;
  }

  // floor height under (x, z). The flights are slopes; the small bulge keeps feet on the step tops.
  function height(x, z) {
    if (!upper) return 0;
    const s = toGallery(north.heading, x, z)[0], rise = UPPER_FLOOR / 2;
    const flight = (t, base) => base + t * rise + 0.09 * Math.sin(Math.PI * t);
    if (s <= stairs.foot) return 0;
    if (s >= top) return UPPER_FLOOR;
    const up = s - stairs.foot;
    if (up < FLIGHT) return flight(up / FLIGHT, 0);
    if (up < FLIGHT + LANDING) return rise;
    return flight((up - FLIGHT - LANDING) / FLIGHT, rise);
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

  return {
    spots, zones, galleries, rooms, stairs, boards,
    exit: { x: exitX, z: exitZ, r: 0.9 },
    spawn: { x: start[0], z: start[1], yaw: 0 },
    extent: Math.max(...galleries.map((g) => g.end), upper ? top + GALLERY_W : 0, loft ? loft.end : 0) + 0.5,
    move, height,
  };
}
