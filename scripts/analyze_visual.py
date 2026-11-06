"""Summarize visual fidelity (RQ1 visual part, RQ3) from experiments/results/visual/*.json.

Writes:
    experiments/results/visual_levels.csv     one row per level, main set: medians and failures
    experiments/results/visual_paired.csv     level differences on the same artifacts, and museum GLB - full L3 model
    experiments/results/visual_all.csv        one row per artifact and model
    experiments/plots/visual_by_level.png     PSNR, SSIM and silhouette IoU per level
    experiments/plots/visual_museum.png       museum GLB against the full L3 model, per exhibit

Usage (PowerShell):
    python scripts/analyze_visual.py
"""

import json
import sys
from pathlib import Path
from statistics import median

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.compare import collect, write_csv  # noqa: E402
from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402
from heritage3d.tradeoff import paired_differences  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_tradeoff import BLUE, INK, LEVEL_COLOR, MUTED, setup  # noqa: E402

MEASURES = ("mean_psnr", "mean_ssim", "mean_iou", "mean_psnr_overlap")
LABEL = {"mean_psnr": "PSNR (dB)", "mean_ssim": "SSIM", "mean_iou": "Silhouette IoU", "mean_psnr_overlap": "PSNR where both show the object (dB)"}
PAIRS = [("L2", "L1"), ("L3", "L1"), ("L4", "L1"), ("L5", "L1"), ("L4", "L3")]


def load():
    rows = {}
    for p in (REPO_ROOT / "experiments" / "results" / "visual").glob("*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        rows.setdefault(d["artifact"], []).append({"level": d["level"], "faces": d["faces"], **{m: d[m] for m in MEASURES}})
    return rows


def main():
    config = load_config(DEFAULT_CONFIG)
    levels = list(config["levels"])
    main_set = [a["name"] for a in json.loads((REPO_ROOT / "configs" / "artifact_order.json").read_text(encoding="utf-8"))["artifacts"]]
    cutoff = [a["name"] for a in json.loads((REPO_ROOT / "configs" / "artifact_order_cutoff.json").read_text(encoding="utf-8"))["artifacts"]]
    visual = load()
    runs = REPO_ROOT / "experiments" / "results" / "runs"

    # geometry next to each visual row, for the correlation between the two
    flat = []
    for artifact, rows in visual.items():
        geometry = {r["level"]: r for r in collect(runs, artifact, levels)}
        for r in rows:
            g = geometry.get(r["level"] if r["level"] != "museum" else "L3", {})
            flat.append({"artifact": artifact, "set": "main" if artifact in main_set else "cut_off", **r,
                         "mesh_f@0.002": g.get("mesh_f@0.002"), "cloud_f@0.002": g.get("cloud_f@0.002")})
    write_csv(sorted(flat, key=lambda r: (r["set"], r["artifact"], r["level"])), REPO_ROOT / "experiments" / "results" / "visual_all.csv")

    main_rows = {a: [r for r in visual[a] if r["level"] in levels] for a in main_set}
    missing = [a for a, rows in main_rows.items() if len(rows) != len(levels)]
    if missing:
        sys.exit(f"not all levels measured for: {' '.join(missing)}")
    table = []
    for level in levels:
        rows = [r for rs in main_rows.values() for r in rs if r["level"] == level]
        row = {"level": level, "artifacts": len(rows)}
        for m in MEASURES:
            values = [r[m] for r in rows if r[m] is not None]
            row[f"median_{m}"] = round(median(values), 3)
            row[f"lowest_{m}"] = round(min(values), 3)
        row["iou_below_0.9"] = sum(r["mean_iou"] < 0.9 for r in rows)
        row["empty_render"] = sum(r["faces"] == 0 for r in rows)
        table.append(row)
    write_csv(table, REPO_ROOT / "experiments" / "results" / "visual_levels.csv")

    paired = [row for m in MEASURES[:3] for row in paired_differences(main_rows, PAIRS, m)]
    # RQ3: the museum's decimated JPEG model against the full L3 model of the same exhibit
    exhibits = {a: [r for r in visual[a] if r["level"] in ("museum", "L3")] for a in visual if any(r["level"] == "museum" for r in visual[a])}
    paired += [row for m in MEASURES[:3] for row in paired_differences(exhibits, [("museum", "L3")], m)]
    write_csv(paired, REPO_ROOT / "experiments" / "results" / "visual_paired.csv")

    main_flat = [r for r in flat if r["set"] == "main" and r["level"] in levels]
    for m in ("mean_psnr", "mean_ssim"):
        for g in ("mesh_f@0.002", "cloud_f@0.002"):
            rho = spearmanr([r[m] for r in main_flat], [r[g] for r in main_flat]).statistic
            print(f"spearman {m} vs {g}: {rho:.3f} over {len(main_flat)} runs")
    cut = [r for r in flat if r["set"] == "cut_off" and r["level"] == "L3"]
    print("cut-off L3:", len(cut), {m: round(median(r[m] for r in cut if r[m] is not None), 3) for m in MEASURES})
    shown = [r for r in cut if r["artifact"] in exhibits]
    print("cut-off L3 exhibited:", len(shown), {m: round(median(r[m] for r in shown), 3) for m in MEASURES})
    ex_main = [r for r in main_flat if r["level"] == "L3" and r["artifact"] in exhibits]
    print("main L3 exhibited:", len(ex_main), {m: round(median(r[m] for r in ex_main), 3) for m in MEASURES})
    for rows in (table, paired):
        for row in rows:
            print(row)

    plt = setup()
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    rng = np.random.default_rng(0)
    for ax, m in zip(axes, MEASURES[:3]):
        for i, level in enumerate(levels):
            values = [r[m] for rs in main_rows.values() for r in rs if r["level"] == level]
            ax.scatter(i + rng.uniform(-0.18, 0.18, len(values)), values, s=14, color=LEVEL_COLOR[level], alpha=0.45, linewidths=0)
            med = median(values)
            ax.plot([i - 0.3, i + 0.3], [med, med], color=INK, lw=2)
        medians = [median(r[m] for rs in main_rows.values() for r in rs if r["level"] == level) for level in levels]
        ax.set_xticks(range(len(levels)), [f"{lv}\n{v:.1f}" if m == "mean_psnr" else f"{lv}\n{v:.3f}" for lv, v in zip(levels, medians)])
        ax.set_title(LABEL[m])
        ax.grid(axis="x", visible=False)
    fig.suptitle("Renders from 12 held-out views against the CHSD photos, 40 artifacts. Bars are medians, dots single models.",
                 x=0.01, ha="left", fontsize=11, color=MUTED)
    fig.tight_layout()
    fig.savefig(REPO_ROOT / "experiments" / "plots" / "visual_by_level.png", dpi=150)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
    for ax, m in zip(axes, ("mean_psnr", "mean_ssim")):
        pairs = [(next(r[m] for r in rows if r["level"] == "L3"), next(r[m] for r in rows if r["level"] == "museum")) for rows in exhibits.values()]
        xs, ys = zip(*pairs)
        lo, hi = min(xs + ys), max(xs + ys)
        pad = (hi - lo) * 0.05
        ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color=MUTED, lw=1, ls=(0, (4, 3)))
        ax.scatter(xs, ys, s=22, color=BLUE, alpha=0.8, linewidths=0)
        ax.annotate("equal", (hi, hi), xytext=(-4, 6), textcoords="offset points", ha="right", fontsize=9, color=MUTED)
        ax.set_xlabel(f"Full L3 model, {LABEL[m]}")
        ax.set_ylabel(f"Museum model, {LABEL[m]}")
        ax.set_title(LABEL[m])
    fig.suptitle(f"Museum models (about 100k triangles, 2048 px JPEG) against the full L3 model, {len(exhibits)} exhibits",
                 x=0.01, ha="left", fontsize=11, color=MUTED)
    fig.tight_layout()
    fig.savefig(REPO_ROOT / "experiments" / "plots" / "visual_museum.png", dpi=150)
    return 0


if __name__ == "__main__":
    sys.exit(main())
