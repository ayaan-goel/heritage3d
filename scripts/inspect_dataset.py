"""Inspect the extracted CHSD dataset and write a JSON report.

For every artifact: checks that RGB and Z folders hold the full frame x ring grid,
reads image headers and depth values on sample frames, compares the RGB foreground
with depth > 0, and tests whether each ring's views are only in-plane spins of each
other (pole views that add no new viewpoint).

Usage (PowerShell):
    python scripts/inspect_dataset.py
    python scripts/inspect_dataset.py --artifacts Ark_HM_110_HI shell_bead_HI --out <file>
"""

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402
from heritage3d.dataset import (  # noqa: E402
    depth_stats,
    foreground_rgb,
    image_header,
    in_plane_rotation_iou,
    iou,
    load,
    scan_folder,
    touches_border,
)

SAMPLE_FRAMES = [1, 91, 181, 271]
SPIN_OFFSETS = [30, 90, 180]  # degrees of turntable rotation compared with frame 1


def inspect_artifact(name, rgb_root, depth_root, rings, frames):
    rgb_dir, depth_dir = rgb_root / name / "RGB", depth_root / name / "Z"
    report = {"rgb": scan_folder(rgb_dir, rings, frames), "depth": scan_folder(depth_dir, rings, frames)}
    file = lambda d, f, e: d / f"{f:04d}_{e}_.png"  # noqa: E731

    headers = Counter()
    cut_off, coverage = [], []
    for f in SAMPLE_FRAMES:
        for e in rings:
            headers["rgb " + json.dumps(image_header(file(rgb_dir, f, e)))] += 1
            headers["depth " + json.dumps(image_header(file(depth_dir, f, e)))] += 1
            mask = load(file(depth_dir, f, e)) > 0
            cut_off.append(touches_border(mask))
            coverage.append(mask.mean())
    report["headers"] = dict(headers)
    # Framing on the sample views: share cut off by the image edge, object size in the image.
    report["cut_off_fraction"] = round(sum(cut_off) / len(cut_off), 3)
    report["foreground_fraction_range"] = [round(float(min(coverage)), 4), round(float(max(coverage)), 4)]

    report["frame1"] = {}
    for e in rings:
        depth = load(file(depth_dir, 1, e))
        report["frame1"][e] = {
            "depth": depth_stats(depth),
            "rgb_vs_depth_mask_iou": round(iou(foreground_rgb(load(file(rgb_dir, 1, e))), depth > 0), 4),
        }

    report["spin_iou"] = {}
    for e in rings:
        ref = load(file(depth_dir, 1, e)) > 0
        scores = [in_plane_rotation_iou(ref, load(file(depth_dir, 1 + k, e)) > 0, k) for k in SPIN_OFFSETS]
        report["spin_iou"][e] = round(min(scores), 4)
    return report


def summarize(per_artifact, rings):
    reps = per_artifact.values()
    frame1 = [r["frame1"][e] for r in reps for e in rings]
    depths = [x["depth"] for x in frame1 if "max" in x["depth"]]
    return {
        "artifacts": len(per_artifact),
        "rgb_files": sum(r["rgb"]["files"] for r in reps),
        "depth_files": sum(r["depth"]["files"] for r in reps),
        "artifacts_with_missing_or_unexpected": sorted(
            n for n, r in per_artifact.items()
            if any(r[k]["missing"] or r[k]["unexpected"] for k in ("rgb", "depth"))
        ),
        "header_variants": sorted({h for r in reps for h in r["headers"]}),
        "depth_dtypes": sorted({d["dtype"] for d in depths}),
        "depth_min_nonzero": min(d["min"] for d in depths),
        "depth_max": max(d["max"] for d in depths),
        "depth_distinct_values_range": [min(d["distinct_values"] for d in depths),
                                        max(d["distinct_values"] for d in depths)],
        "depth_min_gap": min(d["min_gap"] for d in depths if d["min_gap"] is not None),
        "depth_median_gap_range": [min(d["median_gap"] for d in depths if d["median_gap"] is not None),
                                   max(d["median_gap"] for d in depths if d["median_gap"] is not None)],
        "rgb_vs_depth_mask_iou_min": min(x["rgb_vs_depth_mask_iou"] for x in frame1),
        "spin_iou_min_per_ring": {e: min(r["spin_iou"][e] for r in reps) for e in rings},
        "spin_iou_max_per_ring": {e: max(r["spin_iou"][e] for r in reps) for e in rings},
        "artifacts_never_cut_off": sum(r["cut_off_fraction"] == 0 for r in reps),
        "artifacts_cut_off_in_some_views": sorted(n for n, r in per_artifact.items() if r["cut_off_fraction"] > 0),
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--artifacts", nargs="*", help="default: every artifact folder")
    p.add_argument("--out", type=Path, default=REPO_ROOT / "experiments" / "results" / "dataset_inspection.json")
    args = p.parse_args(argv)

    config = load_config(args.config)
    ds = config["dataset"]
    rgb_root, depth_root = Path(config["paths"]["chsd_rgb"]), Path(config["paths"]["chsd_depth"])
    rings = ds["rings"]
    frames = range(1, 360 // ds["azimuth_step"] + 1)
    names = args.artifacts or sorted(d.name for d in rgb_root.iterdir() if d.is_dir())
    depth_only = sorted({d.name for d in depth_root.iterdir() if d.is_dir()} - set(names))

    start = time.perf_counter()
    per_artifact = {}
    for i, name in enumerate(names, 1):
        per_artifact[name] = inspect_artifact(name, rgb_root, depth_root, rings, frames)
        print(f"[{i}/{len(names)}] {name}", file=sys.stderr)

    summary = summarize(per_artifact, rings)
    if not args.artifacts:
        summary["depth_folders_without_rgb"] = depth_only
    report = {
        "config": str(args.config),
        "rgb_root": str(rgb_root),
        "depth_root": str(depth_root),
        "sample_frames": SAMPLE_FRAMES,
        "spin_offsets_deg": SPIN_OFFSETS,
        "seconds": round(time.perf_counter() - start, 1),
        "summary": summary,
        "artifacts": per_artifact,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"report: {args.out}", file=sys.stderr)
    return 1 if summary["artifacts_with_missing_or_unexpected"] else 0


if __name__ == "__main__":
    sys.exit(main())
