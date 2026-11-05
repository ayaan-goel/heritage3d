"""Measure visual fidelity: re-texture each model, render it from held-out views, compare with the CHSD photos.

Stored run textures used OpenMVS's default seam leveling, which damages these renders (see export_glb.py), so each
mesh is first re-textured as the museum's full model is: leveling off, texture up to 8192 px. A run with no mesh
counts as an empty render. Results are per view and resumable:
    experiments/results/visual/<artifact>_<level>.json   level runs
    experiments/results/visual/<artifact>_museum.json    the exhibit's museum GLB
    experiments/plots/visual/<artifact>_<level>.jpg      photo, render and difference (with --previews)

Usage (PowerShell):
    python scripts/evaluate_visual.py --count 40 --levels L1 L2 L3 L4 L5
    python scripts/evaluate_visual.py --order configs/artifact_order_cutoff.json --count 19 --levels L3
    python scripts/evaluate_visual.py --museum
"""

import argparse
import io
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402
from heritage3d.evaluate import align_to_reference, apply, read_colmap_centres  # noqa: E402
from heritage3d.glb import read_glb, read_mesh  # noqa: E402
from heritage3d.pipeline import colmap_path, dense_commands  # noqa: E402
from heritage3d.visual import compare, holdout_views, render  # noqa: E402

RESULTS = REPO_ROOT / "experiments" / "results" / "visual"
PREVIEWS = REPO_ROOT / "experiments" / "plots" / "visual"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
EMPTY = (np.zeros((0, 3)), np.zeros((0, 2), np.float32), np.zeros((0, 3), np.int64), np.zeros((1, 1, 3)))


def retexture(ws, tmp, rgb_root, settings, model):
    """The run's mesh with the leveling off: (positions in COLMAP's frame, uv, triangles, texture)."""
    images = ws / "dense" / "images"
    regenerated = not any(images.rglob("*.png"))
    if regenerated:
        _, cmd = dense_commands(colmap_path(), ws, rgb_root, ws / "sparse" / model, settings)[0]
        subprocess.run([str(c) for c in cmd], check=True, capture_output=True, creationflags=NO_WINDOW)
    out = tmp / "model.glb"
    try:
        subprocess.run(["TextureMesh", "-w", str(ws / "mvs"), "-i", "scene_dense.mvs", "-m", "scene_dense_mesh.ply",
                        "-o", str(out), "--export-type", "glb", "--decimate", "1", "--max-texture-size", "8192",
                        "--global-seam-leveling", "0", "--local-seam-leveling", "0"],
                       check=True, capture_output=True, creationflags=NO_WINDOW)
    finally:
        if regenerated:  # keep the disk as the batch left it
            shutil.rmtree(images, ignore_errors=True)
            images.mkdir(parents=True, exist_ok=True)
    positions, uv, triangles, uri = read_mesh(out)
    return positions, uv, triangles, np.asarray(Image.open(out.parent / uri).convert("RGB"), np.float64)


def level_model(ws, tmp, config):
    """Model of one level in the reference frame, or an empty one if the run made no mesh."""
    metrics = json.loads((ws / "metrics.json").read_text(encoding="utf-8"))
    model = metrics.get("dense_from_model")
    if model is None or not (ws / "mvs" / "scene_dense_mesh.ply").exists():
        return EMPTY
    positions, uv, triangles, texture = retexture(ws, tmp, Path(config["paths"]["chsd_rgb"]), config["pipeline"], str(model))
    transform, _ = align_to_reference(read_colmap_centres(ws / "sparse_txt" / "images.txt"))
    return apply(transform, positions), uv, triangles, texture


def museum_model(path):
    """The museum GLB, turned back from y up to the reference frame, with its embedded texture."""
    positions, uv, triangles, _ = read_mesh(path)
    gltf, binary = read_glb(path)
    view = gltf["bufferViews"][gltf["images"][0]["bufferView"]]
    data = binary[view.get("byteOffset", 0):view.get("byteOffset", 0) + view["byteLength"]]
    texture = np.asarray(Image.open(io.BytesIO(data)).convert("RGB"), np.float64)
    return np.stack([positions[:, 0], -positions[:, 2], positions[:, 1]], axis=1), uv, triangles, texture


def measure(artifact, model, views, config, preview=None):
    rgb_dir = Path(config["paths"]["chsd_rgb"]) / artifact / "RGB"
    depth_dir = Path(config["paths"]["chsd_depth"]) / artifact / "Z"
    rows, panels = [], []
    for frame, elevation in views:
        photo = np.asarray(Image.open(rgb_dir / f"{frame:04d}_{elevation}_.png").convert("RGB"), np.float64)
        mask = np.asarray(Image.open(depth_dir / f"{frame:04d}_{elevation}_.png")) > 0
        rendered, coverage = render(model[0], model[1], model[2], model[3], frame, elevation)
        rows.append({"frame": frame, "elevation": elevation, **compare(rendered, coverage, photo, mask)})
        if preview and len(panels) < 3 and frame == views[0][0]:
            panels.append(np.vstack([photo, rendered, np.clip(np.abs(rendered - photo) * 3, 0, 255)]))
    if preview:
        PREVIEWS.mkdir(parents=True, exist_ok=True)
        Image.fromarray(np.hstack(panels).astype(np.uint8)).resize((1200, 1350)).save(preview, quality=88)
    return rows


def summary(rows):
    out = {}
    for key in ("psnr", "ssim", "iou", "psnr_overlap"):
        values = [r[key] for r in rows if r[key] is not None]
        out[f"mean_{key}"] = round(float(np.mean(values)), 4) if values else None
    return out


def run_one(artifact, level, config, views, previews):
    name = f"{artifact}_{level or 'museum'}"
    out = RESULTS / f"{name}.json"
    if out.exists():
        return None
    start = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmp:
        if level:
            model = level_model(Path(config["paths"]["runs"]) / artifact / level, Path(tmp), config)
        else:
            model = museum_model(REPO_ROOT / "museum" / "models" / f"{artifact}.glb")
        texture_s = time.perf_counter() - start
        rows = measure(artifact, model, views, config, PREVIEWS / f"{name}.jpg" if previews else None)
    report = {"artifact": artifact, "level": level or "museum", "faces": len(model[2]), "views": rows, **summary(rows),
              "texture_seconds": round(texture_s, 1), "total_seconds": round(time.perf_counter() - start, 1)}
    RESULTS.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--artifacts", nargs="+")
    p.add_argument("--count", type=int, help="the first N artifacts of --order")
    p.add_argument("--order", type=Path, default=REPO_ROOT / "configs" / "artifact_order.json")
    p.add_argument("--levels", nargs="+", default=[])
    p.add_argument("--museum", action="store_true", help="measure the museum GLBs of every exhibit (or of --artifacts)")
    p.add_argument("--previews", action="store_true")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = p.parse_args(argv)

    config = load_config(args.config)
    views = holdout_views(tuple(config["levels"].values()))
    jobs = []
    artifacts = args.artifacts or [a["name"] for a in json.loads(args.order.read_text(encoding="utf-8"))["artifacts"]][:args.count or None]
    # cheapest levels first across the set, so early results come quickly
    for level in sorted(args.levels, reverse=True):
        jobs += [(a, level) for a in artifacts]
    if args.museum:
        exhibits = [e["id"] for e in json.loads((REPO_ROOT / "museum" / "artifacts.json").read_text(encoding="utf-8"))["artifacts"]]
        jobs += [(a, None) for a in (args.artifacts or exhibits)]
    for i, (artifact, level) in enumerate(jobs, 1):
        report = run_one(artifact, level, config, views, args.previews)
        if report:
            print(f"[{i}/{len(jobs)}] {artifact} {report['level']}: psnr {report['mean_psnr']}, ssim {report['mean_ssim']}, iou {report['mean_iou']}, "
                  f"overlap {report['mean_psnr_overlap']}, faces {report['faces']}, texture {report['texture_seconds']} s, total {report['total_seconds']} s", flush=True)
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
