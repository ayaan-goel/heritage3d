"""Evaluate one reconstruction against the CHSD reference geometry.

The reference cloud is fused from all CHSD depth maps of the artifact (never from the
reconstruction) and cached at <runs>/<artifact>/reference.npy. The run's dense cloud and
mesh vertices are aligned through the camera centres, voxel-downsampled like the
reference, and compared. Writes <workspace>/evaluation.json and a copy to
experiments/results/runs/<artifact>_<level>_eval.json.

Usage (PowerShell):
    python scripts/evaluate_run.py --artifact Ark_HM_272_HI --level L3
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402
from heritage3d.evaluate import align_to_reference, apply, distance_metrics, read_colmap_centres  # noqa: E402
from heritage3d.pipeline import colmap_path  # noqa: E402
from heritage3d.ply import read_vertices, xyz  # noqa: E402
from heritage3d.reference import build_reference, voxel_downsample  # noqa: E402


def reference_cloud(config, artifact, rebuild):
    ev, ds = config["evaluation"], config["dataset"]
    path = Path(config["paths"]["runs"]) / artifact / "reference.npy"
    meta_path = path.with_suffix(".json")
    params = {"stride": ev["reference_stride"], "voxel": ev["voxel"], "views": "all"}
    if path.exists() and not rebuild and json.loads(meta_path.read_text())["params"] == params:
        return np.load(path)
    start = time.perf_counter()
    views = [(f, e) for e in ds["rings"] for f in range(1, 360 // ds["azimuth_step"] + 1)]
    ref = build_reference(config["paths"]["chsd_depth"], artifact, views, ev["voxel"], ev["reference_stride"])
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, ref)
    meta_path.write_text(json.dumps({"params": params, "points": len(ref),
                                     "seconds": round(time.perf_counter() - start, 1)}, indent=1))
    return ref


def sparse_text_model(ws, model):
    out = ws / "sparse_txt"
    if not (out / "images.txt").exists():
        out.mkdir(exist_ok=True)
        subprocess.run([colmap_path(), "model_converter", "--input_path", str(ws / "sparse" / model),
                        "--output_path", str(out), "--output_type", "TXT"],
                       check=True, capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return out / "images.txt"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--artifact", required=True)
    p.add_argument("--level", required=True)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--rebuild-reference", action="store_true")
    args = p.parse_args(argv)

    config = load_config(args.config)
    ev = config["evaluation"]
    ws = Path(config["paths"]["runs"]) / args.artifact / args.level
    metrics = json.loads((ws / "metrics.json").read_text(encoding="utf-8"))
    model = metrics.get("dense_from_model")
    if model is None:
        print("no dense run in this workspace", file=sys.stderr)
        return 1

    ref = reference_cloud(config, args.artifact, args.rebuild_reference)
    transform, alignment = align_to_reference(read_colmap_centres(sparse_text_model(ws, model)))
    report = {"artifact": args.artifact, "level": args.level, "units": "R (camera-to-centre distance)",
              "evaluation_config": ev, "alignment": alignment,
              "reference_extent": (ref.max(0) - ref.min(0)).tolist()}
    print(f"reference: {len(ref)} points; camera alignment rms {alignment['camera_error_rms']:.5f} R")

    for name, ply in [("dense_cloud", "scene_dense.ply"), ("mesh_vertices", "scene_dense_mesh.ply")]:
        path = ws / "mvs" / ply
        if not path.exists():
            continue
        points = voxel_downsample(apply(transform, xyz(read_vertices(path))), ev["voxel"])
        report[name] = distance_metrics(points, ref, ev["thresholds"])
        r = report[name]
        f = r["fscore"][str(ev["thresholds"][1])]
        print(f"{name}: chamfer {r['chamfer']:.5f}  accuracy med {r['accuracy_median']:.5f}  "
              f"completeness med {r['completeness_median']:.5f}  F@{ev['thresholds'][1]} {f['f']:.3f} "
              f"(P {f['precision']:.3f} R {f['recall']:.3f})")

    out = ws / "evaluation.json"
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    copy = REPO_ROOT / "experiments" / "results" / "runs" / f"{args.artifact}_{args.level}_eval.json"
    shutil.copyfile(out, copy)
    print(f"evaluation: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
