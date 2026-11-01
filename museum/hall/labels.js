// Text in the hall, drawn on canvases: pedestal placards, doorway signs and the information stand.
import { canvas } from "./textures.js";

const SERIF = 'Georgia, "Times New Roman", serif';
const SANS = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
const INK = "#2b251e", MUTED = "#6c6153", BRONZE = "#8a6838";

const fmt = (x, d = 1) => Number(x).toLocaleString("en", { maximumFractionDigits: d, minimumFractionDigits: d });
const int = (x) => Number(x).toLocaleString("en");

// text shrunk until it fits maxWidth
function fit(g, text, x, y, maxWidth, size, family) {
  let px = size;
  do g.font = `${px}px ${family}`; while (g.measureText(text).width > maxWidth && --px > 10);
  g.fillText(text, x, y);
}

// centred text wrapped onto lines of at most maxWidth; returns the y after the last line
function wrap(g, text, x, y, maxWidth, lineHeight) {
  let line = "";
  for (const word of text.split(" ")) {
    if (line && g.measureText(`${line} ${word}`).width > maxWidth) {
      g.fillText(line, x, y);
      y += lineHeight;
      line = word;
    } else line = line ? `${line} ${word}` : word;
  }
  g.fillText(line, x, y);
  return y + lineHeight;
}

const range = (values, f) => {
  const lo = Math.min(...values), hi = Math.max(...values);
  return lo === hi ? f(lo) : `${f(lo)}–${f(hi)}`;
};

export function placardCanvas(entry, number) {
  const w = 768, h = 480, c = canvas(w, h), g = c.getContext("2d");
  g.fillStyle = "#f4eee2";
  g.fillRect(0, 0, w, h);
  g.strokeStyle = BRONZE;
  g.lineWidth = 8;
  g.strokeRect(12, 12, w - 24, h - 24);
  g.lineWidth = 2;
  g.strokeRect(30, 30, w - 60, h - 60);

  g.fillStyle = BRONZE;
  g.font = `600 26px ${SANS}`;
  g.letterSpacing = "4px";
  g.fillText(`NO. ${number}`, 62, 92);
  g.letterSpacing = "0px";
  g.fillStyle = INK;
  fit(g, entry.id, 62, 158, w - 124, 58, SERIF);
  g.fillStyle = MUTED;
  g.font = `28px ${SANS}`;
  g.fillText(`Digitized from ${entry.input_images} photographs (${entry.level})`, 62, 204);
  g.fillStyle = BRONZE;
  g.fillRect(62, 232, w - 124, 2);

  const rows = [
    ["Reconstruction", `${fmt(entry.reconstruction_min)} min, laptop CPU`],
    ["Museum model", `${int(entry.faces)} triangles · ${fmt(entry.glb_mb)} MB`],
    ["Accuracy F@0.002 R", fmt(entry["f@0.002"], 3)],
  ];
  rows.forEach(([label, value], i) => {
    const y = 300 + i * 60;
    g.textAlign = "left";
    g.fillStyle = MUTED;
    g.font = `32px ${SANS}`;
    g.fillText(label, 62, y);
    g.textAlign = "right";
    g.fillStyle = INK;
    g.font = `600 34px ${SANS}`;
    g.fillText(value, w - 62, y);
  });
  return c;
}

// Sign for the half-round panel above a doorway; only the upper half of the canvas is shown.
export function signCanvas(title, subtitle) {
  const c = canvas(1024), g = c.getContext("2d");
  g.fillStyle = "#e7dcc7";
  g.fillRect(0, 0, 1024, 1024);
  g.strokeStyle = BRONZE;
  g.lineWidth = 12;
  g.beginPath();
  g.arc(512, 512, 470, Math.PI, 0);
  g.stroke();
  g.textAlign = "center";
  g.fillStyle = "#6b4f2c";
  g.letterSpacing = "12px";
  fit(g, title.toUpperCase(), 512, 360, 800, 76, SERIF);
  if (subtitle) {
    g.letterSpacing = "4px";
    g.font = `46px ${SERIF}`;
    g.fillText(subtitle, 512, 450);
  }
  return c;
}

// Information stand in the middle of the rotunda; `zones` lists where each run of numbers stands.
export function infoCanvas(artifacts, zones) {
  const w = 1280, h = 840, c = canvas(w, h), g = c.getContext("2d");
  g.fillStyle = "#f3ece0";
  g.fillRect(0, 0, w, h);
  g.strokeStyle = BRONZE;
  g.lineWidth = 10;
  g.strokeRect(16, 16, w - 32, h - 32);

  g.textAlign = "center";
  g.fillStyle = INK;
  g.font = `76px ${SERIF}`;
  g.fillText("heritage3d Virtual Museum", w / 2, 140);
  g.fillStyle = INK;
  g.font = `32px ${SANS}`;
  let y = wrap(g, `${artifacts.length} cultural heritage artifacts, digitized from ordinary photographs, reconstructed on a laptop CPU with open-source photogrammetry and optimized for the web.`, w / 2, 210, w - 240, 44);
  g.fillStyle = INK;
  g.font = `600 30px ${SANS}`;
  y = wrap(g, `Every exhibit: ${range(artifacts.map((a) => a.input_images), int)} photographs · about ${int(Math.round(Math.max(...artifacts.map((a) => a.faces)) / 1000) * 1000)} triangles · ${range(artifacts.map((a) => a.glb_mb), (x) => fmt(x))} MB`, w / 2, y + 16, w - 240, 42);

  g.fillStyle = BRONZE;
  g.fillRect(w / 2 - 300, y + 4, 600, 2);
  g.font = `34px ${SERIF}`;
  g.fillStyle = INK;
  y += 64;
  const half = Math.ceil(zones.length / 2);  // two columns
  zones.forEach((zone, i) => g.fillText(zone, w / 2 + (i < half ? -280 : 280), y + (i % half) * 48));
  y += half * 48;
  g.fillStyle = MUTED;
  g.font = `italic 30px ${SERIF}`;
  g.fillText("Walk up to an exhibit and press E for a 360° view.", w / 2, Math.min(y + 24, h - 120));
  g.font = `22px ${SANS}`;
  wrap(g, "Source images: CHSD (Arampatzakis, Arnaoutoglou, Koutsoudis & Pavlidis, 2024), rendered from models of the Virtual Hampson Museum · CC BY-NC-SA 4.0", w / 2, h - 72, w - 200, 30);
  return c;
}

// Entrance signboards (portrait, 800 × 1100 px): the exhibition title under the university's name and
// logo, and the project team.
function board(draw) {
  const w = 800, h = 1100, c = canvas(w, h), g = c.getContext("2d");
  g.fillStyle = "#f4eee2";
  g.fillRect(0, 0, w, h);
  g.strokeStyle = BRONZE;
  g.lineWidth = 12;
  g.strokeRect(18, 18, w - 36, h - 36);
  g.lineWidth = 2;
  g.strokeRect(40, 40, w - 80, h - 80);
  g.textAlign = "center";
  draw(g, w, h);
  return c;
}

const rule = (g, w, y) => {
  g.fillStyle = BRONZE;
  g.fillRect(w / 2 - 160, y, 320, 3);
};

export function titleBoardCanvas(logo, count) {
  return board((g, w, h) => {
    if (logo) {
      const lh = 300, lw = (logo.width / logo.height) * lh;
      g.drawImage(logo, (w - lw) / 2, 80, lw, lh);
    }
    g.fillStyle = "#8a2a22";
    g.font = `600 40px ${SERIF}`;
    g.fillText("Pandit Deendayal Energy University", w / 2, 450);
    g.font = `34px ${SERIF}`;
    g.fillText("(PDEU)", w / 2, 498);
    rule(g, w, 540);
    g.fillStyle = BRONZE;
    g.font = `600 30px ${SANS}`;
    g.letterSpacing = "8px";
    g.fillText("HERITAGE3D", w / 2, 620);
    g.letterSpacing = "0px";
    g.fillStyle = INK;
    g.font = `84px ${SERIF}`;
    g.fillText("Virtual Heritage", w / 2, 720);
    g.fillText("Exhibition", w / 2, 815);
    g.fillStyle = MUTED;
    g.font = `30px ${SANS}`;
    wrap(g, `${count} cultural heritage artifacts digitized from ordinary photographs`, w / 2, 900, w - 180, 42);
    g.font = `italic 30px ${SERIF}`;
    g.fillText("Welcome", w / 2, h - 90);
  });
}

export function teamBoardCanvas() {
  return board((g, w, h) => {
    const name = (text, y) => {
      g.fillStyle = INK;
      g.font = `60px ${SERIF}`;
      g.fillText(text, w / 2, y);
    };
    const heading = (text, y) => {
      g.fillStyle = BRONZE;
      g.font = `600 30px ${SANS}`;
      g.letterSpacing = "8px";
      g.fillText(text, w / 2, y);
      g.letterSpacing = "0px";
    };
    g.fillStyle = INK;
    g.font = `64px ${SERIF}`;
    g.fillText("Project Team", w / 2, 170);
    rule(g, w, 215);
    heading("CREATED BY", 330);
    name("Ayaan Goel", 420);
    name("Kshiti Bhavsar", 510);
    rule(g, w, 590);
    heading("MENTOR", 690);
    name("Prof. Komal Singh", 780);
    g.fillStyle = MUTED;
    g.font = `30px ${SANS}`;
    wrap(g, "Image-based 3D digitization of cultural heritage artifacts for a web-based virtual museum", w / 2, 860, w - 180, 42);
    g.fillStyle = "#8a2a22";
    g.font = `600 30px ${SERIF}`;
    g.fillText("Pandit Deendayal Energy University", w / 2, h - 90);
  });
}
