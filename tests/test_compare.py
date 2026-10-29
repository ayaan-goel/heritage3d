import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.compare import collect, level_row, write_csv


def stage(seconds, mb):
    return {"seconds": seconds, "peak_memory_mb": mb}


def fake_run(level, images):
    return {
        "level": level, "input_images": images, "input_bytes": 2 * 1024 * 1024,
        "stages": {"feature_extractor": stage(1, 2000), "exhaustive_matcher": stage(10, 1900),
                   "mapper": stage(2, 400), "image_undistorter": stage(0.5, 80),
                   "DensifyPointCloud": stage(20, 2500), "TextureMesh": stage(5, 900)},
        "sparse_models": {"0": {"registered_images": images, "points": 100, "mean_reprojection_error_px": 0.2}},
        "dense_from_model": 0,
        "outputs_bytes": {"scene_dense.ply": 1024 * 1024, "scene_dense_texture.ply": 1024 * 1024,
                          "scene_dense_texture0.png": 1024 * 1024},
    }


def fake_eval(f):
    part = {"chamfer": 0.001, "accuracy_mean": 0.001, "completeness_mean": 0.001, "hausdorff_95": 0.002,
            "fscore": {"0.002": {"f": f, "precision": f, "recall": f}}}
    return {"alignment": {"camera_error_rms": 0.0003}, "dense_cloud": part, "mesh_vertices": part}


def test_level_row_splits_sparse_and_dense_cost():
    row = level_row(fake_run("L3", 92), fake_eval(0.97))
    assert row["sparse_s"] == 13 and row["dense_s"] == 25.5 and row["total_s"] == 38.5
    assert row["matching_s"] == 10 and row["densify_s"] == 20
    assert row["peak_mb"] == 2500 and row["input_mb"] == 2 and row["textured_mesh_mb"] == 2
    assert row["cloud_f@0.002"] == 0.97 and row["registered"] == 92


def test_collect_skips_levels_without_evaluation_and_keeps_order(tmp_path):
    for level, images in (("L1", 362), ("L3", 92), ("L5", 26)):
        (tmp_path / f"art_{level}.json").write_text(json.dumps(fake_run(level, images)))
    for level in ("L5", "L1"):
        (tmp_path / f"art_{level}_eval.json").write_text(json.dumps(fake_eval(0.9)))
    rows = collect(tmp_path, "art", ["L1", "L2", "L3", "L4", "L5"])
    assert [r["level"] for r in rows] == ["L1", "L5"]
    write_csv(rows, tmp_path / "out.csv")
    with open(tmp_path / "out.csv", newline="") as f:
        assert [r["images"] for r in csv.DictReader(f)] == ["362", "26"]
