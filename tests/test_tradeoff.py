import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.tradeoff import cheapest_sufficient, holm, level_table, paired_differences, policies, sufficient_table, time_exponent

IMAGES = {"L1": 362, "L3": 92, "L5": 26}


def row(level, mesh, cloud=None, seconds=None):
    images = IMAGES[level]
    return {"level": level, "images": images, "registered": images, "total_s": seconds or images * 10.0, "peak_mb": images * 2.0,
            "input_mb": images / 4, "dense_cloud_mb": images / 2, "textured_mesh_mb": 20.0,
            "mesh_f@0.002": mesh, "cloud_f@0.002": mesh if cloud is None else cloud, "cloud_precision@0.002": 0.9,
            "cloud_recall@0.002": 0.9, "cloud_chamfer": 0.001, "cloud_hausdorff95": 0.002, "cloud_rmse": 0.001,
            "cloud_f@0.005": 0.95, "cloud_f@0.01": 0.97, "mesh_f@0.005": 0.96, "mesh_f@0.01": None}


def data():
    return {"good": [row("L1", 0.97), row("L3", 0.98), row("L5", 0.96)],
            "needs_many": [row("L1", 0.96), row("L3", 0.90), row("L5", 0.20)],
            "never": [row("L1", 0.60), row("L3", 0.70), row("L5", 0.10)]}


def test_cheapest_sufficient_takes_fewest_images_and_ignores_row_order():
    rows = data()
    assert cheapest_sufficient(rows["good"], "mesh_f@0.002", 0.95) == "L5"
    assert cheapest_sufficient(rows["needs_many"], "mesh_f@0.002", 0.95) == "L1"
    assert cheapest_sufficient(rows["never"], "mesh_f@0.002", 0.95) is None


def test_level_table_shares_are_per_artifact_and_counts_are_right():
    table = {r["level"]: r for r in level_table(data(), ["L1", "L3", "L5"], 0.95)}
    assert table["L1"]["time_share_of_L1"] == 1
    assert table["L3"]["time_share_of_L1"] == pytest.approx(92 / 362, abs=0.001)
    assert table["L1"]["mesh_f_reaching_0.95"] == 2 and table["L5"]["mesh_f_reaching_0.95"] == 1
    assert table["L5"]["mesh_f_below_0.5"] == 2 and table["L5"]["no_dense_cloud"] == 0


def test_level_table_skips_missing_distances_and_counts_failed_clouds():
    rows = data()
    failed = rows["never"][2]
    failed.update(cloud_chamfer=None, cloud_hausdorff95=None, cloud_rmse=None, dense_cloud_mb=0)
    table = {r["level"]: r for r in level_table(rows, ["L1", "L3", "L5"], 0.95)}
    assert table["L5"]["no_dense_cloud"] == 1 and table["L5"]["median_cloud_chamfer"] == 0.001


def test_sufficient_table_marks_artifacts_that_never_reach():
    table = {r["artifact"]: r for r in sufficient_table(data(), [0.9, 0.95])}
    assert table["never"]["mesh_f_0.95"] == "none" and table["needs_many"]["mesh_f_0.9"] == "L3"


def test_policies_add_up_time_and_hindsight_leaves_out_what_never_reaches():
    out = {p["policy"]: p for p in policies(data(), ["L1", "L3"], "mesh_f@0.002", 0.95)}
    assert out["every artifact at L1"]["artifacts_reaching"] == 2
    assert out["every artifact at L1"]["total_hours"] == round(3 * 3620 / 3600, 1)
    hindsight = out["cheapest sufficient level, in hindsight"]
    assert hindsight["artifacts_reaching"] == 2 and hindsight["total_hours"] == round((260 + 3620) / 3600, 1)


def test_holm_scales_by_rank_keeps_order_and_caps_at_one():
    assert holm([0.04, 0.01, 0.5]) == pytest.approx([0.08, 0.03, 0.5])
    assert holm([0.9, 0.9]) == pytest.approx([1.0, 1.0])


def test_paired_differences_on_same_artifacts():
    rows = {f"a{i}": [row("L1", 0.90 + i / 1000), row("L3", 0.95 + i / 1000)] for i in range(12)}
    out = paired_differences(rows, [("L3", "L1"), ("L1", "L1")], "mesh_f@0.002")
    assert out[0]["median_difference"] == 0.05 and out[0]["a_higher"] == 12 and out[0]["ci95_low"] == 0.05
    assert out[0]["p_wilcoxon"] < 0.01
    assert out[1]["median_difference"] == 0 and out[1]["p_wilcoxon"] == 1


def test_time_exponent_of_a_known_power_law():
    rows = {"a": [row(l, 0.9, seconds=3 * IMAGES[l] ** 1.5) for l in IMAGES]}
    assert time_exponent(rows, ["L1", "L3", "L5"]) == 1.5
