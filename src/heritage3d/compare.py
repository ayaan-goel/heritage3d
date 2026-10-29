"""Collect per-level cost (run metrics) and quality (evaluation) into one table."""

import csv
import json
from pathlib import Path

SPARSE_STAGES = ("feature_extractor", "exhaustive_matcher", "mapper")
MB = 1024 * 1024


def level_row(metrics, evaluation, tau="0.002"):
    """One row of the comparison table from a run's metrics.json and evaluation.json."""
    stages = metrics["stages"]
    sparse = [s for name, s in stages.items() if name in SPARSE_STAGES]
    dense = [s for name, s in stages.items() if name not in SPARSE_STAGES]
    model = metrics["sparse_models"][str(metrics["dense_from_model"])]
    out = metrics["outputs_bytes"]
    cloud, mesh = evaluation["dense_cloud"], evaluation["mesh_vertices"]
    return {
        "level": metrics["level"],
        "images": metrics["input_images"],
        "registered": model["registered_images"],
        "sparse_points": model["points"],
        "reprojection_px": round(model["mean_reprojection_error_px"], 3),
        "sparse_s": round(sum(s["seconds"] for s in sparse), 1),
        "matching_s": stages["exhaustive_matcher"]["seconds"],
        "densify_s": stages["DensifyPointCloud"]["seconds"],
        "dense_s": round(sum(s["seconds"] for s in dense), 1),
        "total_s": round(sum(s["seconds"] for s in stages.values()), 1),
        "peak_mb": round(max(s["peak_memory_mb"] for s in stages.values())),
        "input_mb": round(metrics["input_bytes"] / MB, 1),
        "dense_cloud_mb": round(out["scene_dense.ply"] / MB, 1),
        "textured_mesh_mb": round((out["scene_dense_texture.ply"] + out["scene_dense_texture0.png"]) / MB, 1),
        "camera_rms": evaluation["alignment"]["camera_error_rms"],
        "cloud_chamfer": cloud["chamfer"],
        "cloud_accuracy": cloud["accuracy_mean"],
        "cloud_completeness": cloud["completeness_mean"],
        "cloud_hausdorff95": cloud["hausdorff_95"],
        f"cloud_f@{tau}": cloud["fscore"][tau]["f"],
        f"cloud_precision@{tau}": cloud["fscore"][tau]["precision"],
        f"cloud_recall@{tau}": cloud["fscore"][tau]["recall"],
        "mesh_chamfer": mesh["chamfer"],
        f"mesh_f@{tau}": mesh["fscore"][tau]["f"],
    }


def collect(results_dir, artifact, levels):
    """Rows for every level that has both a run and an evaluation file, in the given order."""
    rows = []
    for level in levels:
        run = Path(results_dir) / f"{artifact}_{level}.json"
        ev = Path(results_dir) / f"{artifact}_{level}_eval.json"
        if run.exists() and ev.exists():
            rows.append(level_row(json.loads(run.read_text(encoding="utf-8")),
                                  json.loads(ev.read_text(encoding="utf-8"))))
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
