"""Quality against cost across subset levels: RQ2 of the project, from the rows of compare.collect().

Costs are reported side by side. On top of that, combined_score() sums them up per level as one number between
0 and 1 (half quality, half saving against L1 by default), and weight_check() shows how the ranking of the levels
moves when that split changes. A level is "sufficient" for an artifact when its F-score reaches a threshold fixed
in advance. Artifacts are paired, so levels are compared on the same objects.
"""

from statistics import median

import numpy as np
from scipy.stats import wilcoxon

COSTS = {"time": "total_s", "peak_ram": "peak_mb", "input": "input_mb", "cloud": "dense_cloud_mb", "mesh": "textured_mesh_mb"}
QUALITY = {"mesh": "mesh_f@0.002", "cloud": "cloud_f@0.002"}


def by_images(rows):
    """Rows from the fewest images (the cheapest capture) to the most."""
    return sorted(rows, key=lambda r: r["images"])


def cheapest_sufficient(rows, key, threshold):
    """Level with the fewest images whose F reaches the threshold, or None."""
    return next((r["level"] for r in by_images(rows) if r[key] >= threshold), None)


def _at(rows_by_artifact, level):
    return {a: r for a, rows in rows_by_artifact.items() for r in rows if r["level"] == level}


def level_table(rows_by_artifact, levels, threshold, base="L1"):
    """One row per level: median costs, each artifact's cost as a share of its own base level, and quality."""
    baseline = _at(rows_by_artifact, base)
    out = []
    for level in levels:
        rows = _at(rows_by_artifact, level)
        row = {"level": level, "images": next(iter(rows.values()))["images"], "artifacts": len(rows)}
        for name, key in COSTS.items():
            values = [r[key] for r in rows.values()]
            row[f"median_{key}"] = round(median(values), 1)
            shares = [rows[a][key] / baseline[a][key] for a in rows if baseline[a][key]]
            row[f"{name}_share_of_{base}"] = round(median(shares), 3)
        for name, key in QUALITY.items():
            values = sorted(r[key] for r in rows.values())
            row[f"median_{name}_f"] = round(median(values), 3)
            row[f"lowest_{name}_f"] = round(values[0], 3)
            row[f"{name}_f_reaching_{threshold}"] = sum(v >= threshold for v in values)
            row[f"{name}_f_below_0.5"] = sum(v < 0.5 for v in values)
        # runs without a dense cloud have no distances or precision, so these medians cover only runs that made one
        for key in ("cloud_precision@0.002", "cloud_recall@0.002", "cloud_chamfer", "cloud_hausdorff95", "cloud_rmse",
                    "cloud_f@0.005", "cloud_f@0.01", "mesh_f@0.005", "mesh_f@0.01"):
            values = [r[key] for r in rows.values() if r[key] is not None]
            row[f"median_{key}"] = round(median(values), 5) if values else None
        row["no_dense_cloud"] = sum(not r["dense_cloud_mb"] for r in rows.values())
        row["all_images_used"] = sum(r["registered"] == r["images"] for r in rows.values())
        out.append(row)
    return out


def sufficient_table(rows_by_artifact, thresholds):
    """One row per artifact: its cheapest sufficient level for each quality measure and threshold."""
    return [{"artifact": artifact,
             **{f"{name}_f_{t}": cheapest_sufficient(rows, key, t) or "none"
                for name, key in QUALITY.items() for t in thresholds}}
            for artifact, rows in rows_by_artifact.items()]


def policies(rows_by_artifact, levels, key, threshold):
    """What each way of working gives: one level for every artifact, or each artifact's cheapest sufficient level
    known in hindsight. Hindsight needs the reference geometry, which a real capture does not have."""
    out = []
    for level in levels:
        rows = _at(rows_by_artifact, level).values()
        out.append({"policy": f"every artifact at {level}", "artifacts_reaching": sum(r[key] >= threshold for r in rows),
                    "total_hours": round(sum(r["total_s"] for r in rows) / 3600, 1)})
    chosen = []
    for rows in rows_by_artifact.values():
        level = cheapest_sufficient(rows, key, threshold)
        chosen += [r for r in rows if r["level"] == level]
    out.append({"policy": "cheapest sufficient level, in hindsight", "artifacts_reaching": len(chosen),
                "total_hours": round(sum(r["total_s"] for r in chosen) / 3600, 1)})
    return out


def holm(p_values):
    """Holm's correction for testing several comparisons at once; keeps the input order."""
    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted, running = [0.0] * len(p_values), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[i]))
        adjusted[i] = running
    return adjusted


def paired_differences(rows_by_artifact, pairs, key, seed=0, resamples=10000):
    """F of level a minus F of level b on the same artifacts: median, bootstrap 95 % interval, Wilcoxon test."""
    rng = np.random.default_rng(seed)
    out = []
    for a, b in pairs:
        at_a, at_b = _at(rows_by_artifact, a), _at(rows_by_artifact, b)
        diff = np.array([at_a[n][key] - at_b[n][key] for n in at_a if n in at_b])
        samples = rng.choice(diff, size=(resamples, len(diff)))
        low, high = np.percentile(np.median(samples, axis=1), [2.5, 97.5])
        p = 1.0 if not np.any(diff) else float(wilcoxon(diff).pvalue)
        out.append({"measure": key, "compare": f"{a} - {b}", "artifacts": len(diff), "median_difference": round(float(np.median(diff)), 4),
                    "ci95_low": round(float(low), 4), "ci95_high": round(float(high), 4),
                    "a_higher": int(np.sum(diff > 0)), "b_higher": int(np.sum(diff < 0)), "p_wilcoxon": p})
    for row, adjusted in zip(out, holm([r["p_wilcoxon"] for r in out])):
        row["p_wilcoxon"] = round(row["p_wilcoxon"], 5)
        row["p_holm"] = round(adjusted, 5)
    return out


def storage_mb(row):
    """Disk a run takes: its input images, dense cloud and textured mesh."""
    return row["input_mb"] + (row["dense_cloud_mb"] or 0) + (row["textured_mesh_mb"] or 0)


def score_inputs(rows_by_artifact, ssim, levels, threshold, base="L1"):
    """Per level, the parts of the combined score, each between 0 and 1.

    Quality: median mesh F, median SSIM (ssim maps (artifact, level) to the mean SSIM over the held-out views)
    and the share of artifacts whose mesh F reaches the threshold, so a cheap level that fails often scores low.
    Cost: median share of the same artifact's base-level time, peak RAM and storage."""
    baseline = _at(rows_by_artifact, base)
    costs = {"time": lambda r: r["total_s"], "peak_ram": lambda r: r["peak_mb"], "storage": storage_mb}
    out = []
    for level in levels:
        rows = _at(rows_by_artifact, level)
        row = {"level": level, "images": next(iter(rows.values()))["images"],
               "median_mesh_f": median(r["mesh_f@0.002"] for r in rows.values()),
               "median_ssim": median(ssim[(a, level)] for a in rows),
               "share_sufficient": sum(r["mesh_f@0.002"] >= threshold for r in rows.values()) / len(rows)}
        for name, cost in costs.items():
            row[f"{name}_share"] = median(cost(rows[a]) / cost(baseline[a]) for a in rows)
        out.append(row)
    return out


QUALITY_PARTS = ("median_mesh_f", "median_ssim", "share_sufficient")
COST_PARTS = ("time_share", "peak_ram_share", "storage_share")


def combined_score(inputs, quality_weight=0.5):
    """score = w * quality + (1 - w) * saving, where quality is the mean of QUALITY_PARTS and saving is 1 minus the
    mean of COST_PARTS (0 at the base level, near 1 for a nearly free one). Equal weights inside each side."""
    out = []
    for row in inputs:
        quality = sum(row[k] for k in QUALITY_PARTS) / len(QUALITY_PARTS)
        saving = 1 - sum(row[k] for k in COST_PARTS) / len(COST_PARTS)
        out.append({**row, "quality": quality, "saving": saving, "score": quality_weight * quality + (1 - quality_weight) * saving})
    return out


def weight_check(inputs, weights):
    """For each quality weight, the levels from best to worst score."""
    out = []
    for w in weights:
        ranked = sorted(combined_score(inputs, w), key=lambda r: -r["score"])
        out.append({"quality_weight": w, "ranking": " > ".join(r["level"] for r in ranked), "best": ranked[0]["level"],
                    **{f"score_{r['level']}": round(r["score"], 3) for r in combined_score(inputs, w)}})
    return out


def time_exponent(rows_by_artifact, levels):
    """b in time = c * images^b, fitted over the given levels to each artifact; returns the median b.
    b near 1 means time grows in step with the images; above 1, faster."""
    slopes = []
    for rows in rows_by_artifact.values():
        used = [r for r in rows if r["level"] in levels]
        slopes.append(np.polyfit(np.log([r["images"] for r in used]), np.log([r["total_s"] for r in used]), 1)[0])
    return round(float(np.median(slopes)), 2)
