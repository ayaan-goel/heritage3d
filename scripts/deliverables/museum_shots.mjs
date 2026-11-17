// Screenshots of the virtual museum with headless Chrome (CDP), for the report, slides and poster.
// Usage: node scripts/deliverables/museum_shots.mjs   (museum served on http://localhost:8765)
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const OUT = "D:/heritage3d/Deliverables/figures/";
const chrome = spawn(CHROME, ["--headless=new", "--remote-debugging-port=9333", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
  "--window-size=1600,900", "--user-data-dir=" + process.env.TEMP + "/h3d-shots", "about:blank"]);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
await sleep(2500);
const targets = await (await fetch("http://127.0.0.1:9333/json")).json();
const ws = new WebSocket(targets.find((t) => t.type === "page").webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const wait = new Map();
ws.addEventListener("message", (e) => { const m = JSON.parse(e.data); if (wait.has(m.id)) { wait.get(m.id)(m); wait.delete(m.id); } });
const send = (method, params = {}) => new Promise((r) => { wait.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
const run = async (expr) => (await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result?.result?.value;
const snap = async (name) => { await sleep(4000); const r = await send("Page.captureScreenshot", { format: "jpeg", quality: 90 }); writeFileSync(OUT + name + ".jpg", Buffer.from(r.result.data, "base64")); console.log("saved", name); };
await send("Emulation.setDeviceMetricsOverride", { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: "http://localhost:8765/" });
for (let i = 0; i < 90; i++) { await sleep(1000); const s = await run("window.hall && hall.stats().loaded"); if (s >= 44) break; }
console.log(await run("JSON.stringify(hall.stats())"));
await run("document.getElementById('enter').click()");
await run("document.querySelectorAll('.hint,#hint').forEach(e=>e.style.display='none')");
await snap("museum_gate");
const views = JSON.parse(process.argv[2] || "[]");
for (const v of views) { await run(v.js); await snap(v.name); }
ws.close(); chrome.kill();
