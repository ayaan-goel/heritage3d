// Procedural textures drawn on canvases (marble, plaster, coffers, floors), so the hall needs no image
// files of its own.
import * as THREE from "three";

export function canvas(w, h = w) {
  const c = document.createElement("canvas");
  c.width = w;
  c.height = h;
  return c;
}

const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
const mix = (a, b, t) => `rgb(${rgb(a).map((v, i) => Math.round(v + (rgb(b)[i] - v) * t)).join(",")})`;
const smooth = (t) => t * t * (3 - 2 * t);
const BRONZE = "#9b7b4b";

function random(seed) {  // mulberry32
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Tileable fractal value noise in [0, 1); `cells` lattice cells across the tile at the first octave.
function noise(size, cells, octaves, seed) {
  const out = new Float32Array(size * size), rand = random(seed);
  let amp = 1, sum = 0;
  for (let o = 0; o < octaves; o++, amp *= 0.5) {
    const p = cells << o, lattice = new Float32Array(p * p).map(() => rand());
    for (let y = 0; y < size; y++) {
      const fy = (y * p) / size, y0 = fy | 0, ty = smooth(fy - y0), r0 = y0 * p, r1 = ((y0 + 1) % p) * p;
      for (let x = 0; x < size; x++) {
        const fx = (x * p) / size, x0 = fx | 0, tx = smooth(fx - x0), x1 = (x0 + 1) % p;
        const a = lattice[r0 + x0], b = lattice[r0 + x1], c = lattice[r1 + x0], d = lattice[r1 + x1];
        out[y * size + x] += amp * (a + (b - a) * tx + (c - a) * ty + (a - b - c + d) * tx * ty);
      }
    }
    sum += amp;
  }
  return out.map((v) => v / sum);
}

function pixels(size, shade) {  // canvas filled pixel by pixel: shade(i) -> [r, g, b]
  const c = canvas(size), g = c.getContext("2d"), img = g.createImageData(size, size);
  for (let i = 0; i < size * size; i++) {
    const [r, gr, b] = shade(i);
    img.data.set([r, gr, b, 255], i * 4);
  }
  g.putImageData(img, 0, 0);
  return c;
}

// Marble: wavy diagonal veins over a slightly clouded base.
export function marble(size, { base, vein, seed }) {
  const warp = noise(size, 3, 5, seed), cloud = noise(size, 2, 4, seed + 7);
  const [r0, g0, b0] = rgb(base), [r1, g1, b1] = rgb(vein);
  return pixels(size, (i) => {
    const x = i % size, y = (i / size) | 0;
    const phase = ((x + y) / size) * Math.PI * 2 + warp[i] * 10;
    const k = Math.min(1, (1 - Math.abs(Math.sin(phase))) ** 14 + Math.max(0, cloud[i] - 0.55) * 0.9);
    const shade = 0.96 + (cloud[i] - 0.5) * 0.1;
    return [(r0 + (r1 - r0) * k) * shade, (g0 + (g1 - g0) * k) * shade, (b0 + (b1 - b0) * k) * shade];
  });
}

export function plaster(size, color, seed) {
  const n = noise(size, 6, 5, seed), rand = random(seed + 1), [r, g, b] = rgb(color);
  return pixels(size, (i) => {
    const k = 0.94 + n[i] * 0.1 + (rand() - 0.5) * 0.025;
    return [r * k, g * k, b * k];
  });
}

// Gallery floor: 2 × 2 checker of light and grey marble slabs with thin joints.
export function tiles(size, light, grey) {
  const c = canvas(size), g = c.getContext("2d"), h = size / 2;
  [[light, 0, 0], [grey, h, 0], [grey, 0, h], [light, h, h]].forEach(([img, x, y]) => g.drawImage(img, x, y, h, h));
  g.fillStyle = "rgba(70, 58, 45, 0.5)";
  for (const p of [0, h]) {
    g.fillRect(p, 0, 2, size);
    g.fillRect(0, p, size, 2);
  }
  return c;
}

// Rotunda floor, seen from above: a compass star, a ring of wedges and bands; `radius` is the metres
// from the centre to the canvas edge.
export function rotundaFloor(size, light, grey, dark, radius) {
  const c = canvas(size), g = c.getContext("2d"), h = size / 2, px = (m) => (m / radius) * h;
  const [lightP, greyP, darkP] = [light, grey, dark].map((img) => g.createPattern(img, "repeat"));
  const ring = (r0, r1, fill) => {
    g.beginPath();
    g.arc(h, h, px(r1), 0, Math.PI * 2);
    g.arc(h, h, px(r0), 0, Math.PI * 2, true);
    g.fillStyle = fill;
    g.fill();
  };
  g.fillStyle = lightP;
  g.fillRect(0, 0, size, size);
  ring(9.2, radius * 1.5, darkP);       // under the wall and pilasters
  ring(8.95, 9.2, BRONZE);
  ring(7.9, 8.1, greyP);
  for (let k = 0; k < 32; k += 2) {     // wedges between the inner bands
    const a0 = (k / 32) * Math.PI * 2, a1 = ((k + 1) / 32) * Math.PI * 2;
    g.beginPath();
    g.arc(h, h, px(4.6), a0, a1);
    g.arc(h, h, px(2.6), a1, a0, true);
    g.fillStyle = greyP;
    g.fill();
  }
  ring(4.6, 4.8, BRONZE);
  ring(2.4, 2.6, BRONZE);
  for (let k = 0; k < 16; k++) {        // 16-point star, each point split into a dark and a grey half
    const a = (k / 16) * Math.PI * 2, d = Math.PI / 16;
    const pt = (angle, m) => [h + Math.cos(angle) * px(m), h + Math.sin(angle) * px(m)];
    for (const [side, fill] of [[-d, darkP], [d, greyP]]) {
      g.beginPath();
      g.moveTo(h, h);
      g.lineTo(...pt(a + side, 1.0));
      g.lineTo(...pt(a, k % 2 ? 1.7 : 2.3));
      g.fillStyle = fill;
      g.fill();
    }
  }
  ring(0, 0.5, darkP);
  return c;
}

// One recessed coffer: stepped frames getting darker inwards, a gilded rosette in the middle.
function coffer(g, x, y, w, h, depth) {
  const stone = "#ebe2d1", shadow = "#b4a387";
  g.fillStyle = stone;
  g.fillRect(x, y, w, h);
  for (let k = 0; k < 3; k++) {
    const ix = w * (0.1 + 0.07 * k), iy = h * (0.1 + 0.07 * k);
    g.fillStyle = mix(stone, shadow, ((k + 1) / 3) * depth);
    g.fillRect(x + ix, y + iy, w - 2 * ix, h - 2 * iy);
    g.fillStyle = "rgba(60, 45, 30, 0.2)";
    g.fillRect(x + ix, y + iy, w - 2 * ix, Math.max(1.5, h * 0.025));
  }
  g.fillStyle = "#b8955a";
  g.beginPath();
  g.arc(x + w / 2, y + h / 2, Math.min(w, h) * 0.06, 0, Math.PI * 2);
  g.fill();
}

export function vaultCoffer(size) {
  const c = canvas(size);
  coffer(c.getContext("2d"), 0, 0, size, size, 0.8);
  return c;
}

// One column of the dome, from its opening (top of the canvas) down to the cornice: a plain upper dome
// and five rows of coffers that shrink upwards so they stay square, as in the Pantheon.
export function domeCoffers(oculus, columns) {
  const w = 256, h = 1024, c = canvas(w, h), g = c.getContext("2d");
  const y = (theta) => ((theta - oculus) / (Math.PI / 2 - oculus)) * h;
  const sky = g.createLinearGradient(0, 0, 0, h);
  sky.addColorStop(0, "#f7f1e6");
  sky.addColorStop(1, "#e2d6c1");
  g.fillStyle = sky;
  g.fillRect(0, 0, w, h);
  let lower = 1.48;  // radians from the zenith
  for (let row = 0; row < 5; row++) {
    const upper = 2 * Math.atan(Math.tan(lower / 2) * Math.exp((-2 * Math.PI) / columns));
    coffer(g, 0, y(upper), w, y(lower) - y(upper), 0.9);
    lower = upper;
  }
  g.fillStyle = "#b8955a";
  g.fillRect(0, y(1.5), w, 6);
  return c;
}

export function radial(size, stops) {
  const c = canvas(size), g = c.getContext("2d"), grad = g.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  stops.forEach(([at, color]) => grad.addColorStop(at, color));
  g.fillStyle = grad;
  g.fillRect(0, 0, size, size);
  return c;
}

export function vertical(w, h, stops) {
  const c = canvas(w, h), g = c.getContext("2d"), grad = g.createLinearGradient(0, 0, 0, h);
  stops.forEach(([at, color]) => grad.addColorStop(at, color));
  g.fillStyle = grad;
  g.fillRect(0, 0, w, h);
  return c;
}

export function texture(c, aniso, repeat = [1, 1]) {
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(...repeat);
  t.anisotropy = aniso;
  return t;
}
