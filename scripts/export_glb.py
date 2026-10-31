"""Export museum models: one decimated, self-contained GLB per artifact, plus its cost and accuracy.

For each artifact at the museum level ([museum] in the config), OpenMVS TextureMesh re-textures the
run's mesh twice: at full resolution (the unoptimized model) and decimated to about `faces`
triangles with a texture of at most `texture` px (the museum model). Both are turned upright into
the CHSD frame (turntable axis up, units of R) through the run's camera alignment, packed into one
GLB with the texture embedded (PNG for full, JPEG for the museum model), and compared with the CHSD
reference on surface samples. Artifacts whose full mesh scores below `min_mesh_f` are skipped.

Writes museum/models/<artifact>.glb, museum/artifacts.json (the museum's list) and
experiments/results/museum/<artifact>_glb.json. Needs the run's workspace (mesh, scene, sparse
model) and its reference cloud (made by evaluate_run.py).

Usage (PowerShell):
    python scripts/export_glb.py --artifacts Ark_HM_272_HI Ark_HM_470_HI
    python scripts/export_glb.py --count 13        # every eligible artifact of the first 13
"""

import argparse
import io
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402
from heritage3d.evaluate import align_to_reference, apply, distance_metrics, read_colmap_centres  # noqa: E402
from heritage3d.glb import read_mesh, sample_surface, write_mesh, z_up_to_y_up  # noqa: E402
from heritage3d.pipeline import colmap_path, dense_commands  # noqa: E402
from heritage3d.reference import voxel_downsample  # noqa: E402

MUSEUM = REPO_ROOT / "museum"
RESULTS = REPO_ROOT / "experiments" / "results"
MB = 1024 * 1024
SAMPLES = 1_000_000


def texture_mesh(ws, out, decimate, max_texture):
    """Run TextureMesh on the run's mesh; returns seconds. Output: out (.glb) + out_0.png.

    Seam leveling is off: on the CHSD renders (object on pure black) OpenMVS's global and local
    seam leveling each turn the faces black (checked 2026-10-31 on Ark_HM_470_HI L3: 91-100 % of
    face centres black with either on, 0.2 % with both off).
    """
    start = time.perf_counter()
    subprocess.run(["TextureMesh", "-w", str(ws / "mvs"), "-i", "scene_dense.mvs", "-m", "scene_dense_mesh.ply",
                    "-o", str(out), "--export-type", "glb", "--decimate", f"{decimate:.6f}",
                    "--max-texture-size", str(max_texture),
                    "--global-seam-leveling", "0", "--local-seam-leveling", "0"],
                   check=True, capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return time.perf_counter() - start


def ensure_images(ws, rgb_root, model, settings):
    """TextureMesh reads the undistorted images; regenerate them if a cleanup removed them."""
    if not any((ws / "dense" / "images").rglob("*.png")):
        name, cmd = dense_commands(colmap_path(), ws, rgb_root, ws / "sparse" / model, settings)[0]
        subprocess.run([str(c) for c in cmd], check=True, capture_output=True)


def pack(raw_glb, transform, out, jpeg_quality=None):
    """Upright, texture-embedded GLB from an OpenMVS export. Returns (positions, triangles, bytes)."""
    positions, texcoords, triangles, uri = read_mesh(raw_glb)
    positions = apply(transform, positions)  # CHSD frame, units of R
    texture = raw_glb.parent / uri
    if jpeg_quality is None:
        image, mime = texture.read_bytes(), "image/png"
    else:
        buf = io.BytesIO()
        Image.open(texture).convert("RGB").save(buf, "JPEG", quality=jpeg_quality, optimize=True)
        image, mime = buf.getvalue(), "image/jpeg"
    size = write_mesh(out, z_up_to_y_up(positions), texcoords, triangles, image, mime)
    return positions, triangles, size


def surface_metrics(positions, triangles, reference, voxel, thresholds):
    points = voxel_downsample(sample_surface(positions, triangles, SAMPLES), voxel)
    return distance_metrics(points, reference, thresholds)


def mesh_faces(ply):
    with open(ply, "rb") as f:
        for line in f:
            if line.startswith(b"element face"):
                return int(line.split()[2])
            if line.startswith(b"end_header"):
                break
    raise ValueError(f"no faces in {ply}")


def export(artifact, config, models_dir):
    m = config["museum"]
    level, ev = m["level"], config["evaluation"]
    ws = Path(config["paths"]["runs"]) / artifact / level
    metrics = json.loads((ws / "metrics.json").read_text(encoding="utf-8"))
    evaluation = json.loads((ws / "evaluation.json").read_text(encoding="utf-8"))
    tau = str(ev["thresholds"][0])
    mesh_f = evaluation["mesh_vertices"]["fscore"][tau]["f"]
    if mesh_f < m["min_mesh_f"]:
        print(f"{artifact} {level}: mesh F@{tau} {mesh_f:.3f} < {m['min_mesh_f']}: not exhibited")
        return None
    model = str(metrics["dense_from_model"])
    transform, _ = align_to_reference(read_colmap_centres(ws / "sparse_txt" / "images.txt"))
    reference = np.load(Path(config["paths"]["runs"]) / artifact / "reference.npy")
    ensure_images(ws, Path(config["paths"]["chsd_rgb"]), model, config["pipeline"])
    faces = mesh_faces(ws / "mvs" / "scene_dense_mesh.ply")
    decimate = min(1.0, m["faces"] / faces)

    report = {"artifact": artifact, "level": level, "input_images": metrics["input_images"], "museum": m}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for name, dec, tex, quality in (("full", 1.0, 8192, None),
                                        ("museum", decimate, m["texture"], m["jpeg_quality"])):
            seconds = texture_mesh(ws, tmp / f"{name}.glb", dec, tex)
            out = tmp / f"{name}_packed.glb" if name == "full" else models_dir / f"{artifact}.glb"
            positions, triangles, size = pack(tmp / f"{name}.glb", transform, out, quality)
            report[name] = {"faces": len(triangles), "vertices": len(positions), "glb_bytes": size,
                            "texture_seconds": round(seconds, 1),
                            "surface": surface_metrics(positions, triangles, reference, ev["voxel"], ev["thresholds"])}
            s = report[name]["surface"]
            print(f"{artifact} {name}: {len(triangles)} faces, {size / MB:.1f} MB, "
                  f"surface F@{tau} {s['fscore'][tau]['f']:.3f}, chamfer {s['chamfer']:.5f} R")
    (RESULTS / "museum").mkdir(parents=True, exist_ok=True)
    (RESULTS / "museum" / f"{artifact}_glb.json").write_text(json.dumps(report, indent=1), encoding="utf-8")

    full, small = report["full"], report["museum"]
    return {
        "id": artifact,
        "model": f"models/{artifact}.glb",
        "level": level,
        "input_images": metrics["input_images"],
        "reconstruction_min": round(sum(s["seconds"] for s in metrics["stages"].values()) / 60, 1),
        "faces": small["faces"],
        "glb_mb": round(small["glb_bytes"] / MB, 2),
        "full_faces": full["faces"],
        "full_glb_mb": round(full["glb_bytes"] / MB, 2),
        f"f@{tau}": round(small["surface"]["fscore"][tau]["f"], 3),
        f"full_f@{tau}": round(full["surface"]["fscore"][tau]["f"], 3),
        "chamfer_r": round(small["surface"]["chamfer"], 5),
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--artifacts", nargs="+")
    g.add_argument("--count", type=int, help="every eligible artifact among the first N of the fixed order")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--order", type=Path, default=REPO_ROOT / "configs" / "artifact_order.json")
    args = p.parse_args(argv)

    config = load_config(args.config)
    order = [a["name"] for a in json.loads(args.order.read_text(encoding="utf-8"))["artifacts"]]
    artifacts = args.artifacts or order[:args.count]
    models_dir = MUSEUM / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = MUSEUM / "artifacts.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"artifacts": []}
    entries = {e["id"]: e for e in manifest["artifacts"]}
    for artifact in artifacts:
        entry = export(artifact, config, models_dir)
        if entry:
            entries[artifact] = entry
    rank = {a: i for i, a in enumerate(order)}
    manifest["artifacts"] = sorted(entries.values(), key=lambda e: rank.get(e["id"], len(rank)))
    manifest_path.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(f"-> {manifest_path} ({len(manifest['artifacts'])} artifacts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
