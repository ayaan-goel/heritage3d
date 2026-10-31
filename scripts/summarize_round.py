"""Summarize quality vs cost across artifacts for the main experiment.

For the first --count artifacts of configs/artifact_order.json, collects every evaluated level and
writes:
    experiments/results/<name>_all.csv      one row per artifact and level
    experiments/results/<name>_summary.csv  one row per level (medians, worst case, broken count)
    experiments/plots/<name>_summary.png    F-score and time per level for every artifact

Usage (PowerShell):
    python scripts/summarize_round.py --count 13 --name round1
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.compare import collect, level_summary, write_csv  # noqa: E402
from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402

TAU = "0.002"


def plot(rows_by_artifact, levels, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x = {lv: i for i, lv in enumerate(levels)}
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    panels = ((f"cloud_f@{TAU}", f"Dense cloud F@{TAU} R"), (f"mesh_f@{TAU}", f"Mesh F@{TAU} R"),
              ("total_s", "Total time (min, log scale)"))
    for ax, (key, title) in zip(axes, panels):
        for artifact, rows in rows_by_artifact.items():
            ys = [r[key] / 60 if key == "total_s" else r[key] for r in rows]
            ax.plot([x[r["level"]] for r in rows], ys, "o-", lw=1, ms=3, alpha=0.8, label=artifact)
        ax.set_title(title)
        ax.set_xticks(range(len(levels)), levels)
        ax.grid(alpha=0.3)
    axes[2].set_yscale("log")
    axes[0].set_ylabel("F-score")
    axes[2].legend(fontsize=7, loc="upper right")
    fig.suptitle(f"{len(rows_by_artifact)} artifacts: quality and cost by subset level")
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--count", type=int, required=True, help="use the first N artifacts of the fixed order")
    p.add_argument("--name", default="round1")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--order", type=Path, default=REPO_ROOT / "configs" / "artifact_order.json")
    args = p.parse_args(argv)

    levels = list(load_config(args.config)["levels"])
    order = [a["name"] for a in json.loads(args.order.read_text(encoding="utf-8"))["artifacts"]][:args.count]
    runs = REPO_ROOT / "experiments" / "results" / "runs"
    rows_by_artifact = {a: rows for a in order if (rows := collect(runs, a, levels))}
    missing = [a for a in order if a not in rows_by_artifact]
    if missing:
        print(f"no evaluated levels for: {' '.join(missing)}", file=sys.stderr)

    results = REPO_ROOT / "experiments" / "results"
    write_csv([{"artifact": a, **r} for a, rows in rows_by_artifact.items() for r in rows],
              results / f"{args.name}_all.csv")
    summary = level_summary(rows_by_artifact, levels, TAU)
    write_csv(summary, results / f"{args.name}_summary.csv")
    plot(rows_by_artifact, levels, REPO_ROOT / "experiments" / "plots" / f"{args.name}_summary.png")
    for s in summary:
        print(", ".join(f"{k} {v}" for k, v in s.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
