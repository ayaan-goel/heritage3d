// Loads artifacts.json (written by scripts/export_glb.py) and shows one model at a time.
const viewer = document.getElementById("viewer");
const info = document.getElementById("info");
const gallery = document.getElementById("gallery");
const progress = document.getElementById("progress");

const fmt = (x, d = 1) => Number(x).toLocaleString(undefined, { maximumFractionDigits: d, minimumFractionDigits: d });
const int = (x) => Number(x).toLocaleString();

function show(entry, button) {
  viewer.src = entry.model;
  viewer.alt = `3D model of ${entry.id}`;
  gallery.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === button)));
  info.innerHTML = `
    <h3>${entry.id}</h3>
    <p class="tag">Captured from ${entry.input_images} photographs (${entry.level})</p>
    <dl>
      <dt>Reconstruction</dt><dd>${fmt(entry.reconstruction_min)} min, laptop CPU</dd>
      <dt>Museum model</dt><dd>${int(entry.faces)} triangles</dd>
      <dt>Download size</dt><dd>${fmt(entry.glb_mb)} MB</dd>
      <dt>Full model</dt><dd>${int(entry.full_faces)} tri, ${fmt(entry.full_glb_mb)} MB</dd>
      <dt>Accuracy F@0.002 R</dt><dd>${fmt(entry["f@0.002"], 3)}</dd>
      <dt>Full model F@0.002 R</dt><dd>${fmt(entry["full_f@0.002"], 3)}</dd>
    </dl>`;
  history.replaceState(null, "", `#${encodeURIComponent(entry.id)}`);
}

viewer.addEventListener("progress", (e) => {
  progress.style.width = `${e.detail.totalProgress * 100}%`;
  progress.style.opacity = e.detail.totalProgress >= 1 ? "0" : "1";
});

fetch("artifacts.json")
  .then((r) => r.json())
  .then(({ artifacts }) => {
    if (!artifacts.length) throw new Error("empty collection");
    const buttons = artifacts.map((entry) => {
      const li = document.createElement("li");
      const b = document.createElement("button");
      b.type = "button";
      b.innerHTML = `<span class="name">${entry.id}</span>
        <span class="meta">${entry.input_images} photos · ${fmt(entry.glb_mb)} MB · F ${fmt(entry["f@0.002"], 2)}</span>`;
      b.addEventListener("click", () => show(entry, b));
      li.append(b);
      gallery.append(li);
      return b;
    });
    const wanted = decodeURIComponent(location.hash.slice(1));
    const i = Math.max(0, artifacts.findIndex((e) => e.id === wanted));
    show(artifacts[i], buttons[i]);
  })
  .catch((err) => {
    info.innerHTML = `<p class="muted">Could not load the collection (${err.message}). Serve this folder over HTTP, e.g. <code>python -m http.server</code>.</p>`;
  });
