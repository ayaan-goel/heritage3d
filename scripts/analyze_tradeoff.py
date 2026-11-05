"""Quality against cost for the main set (RQ1, RQ2, H1, H2), from the stored runs; nothing is reconstructed.

Writes:
    experiments/results/tradeoff_levels.csv      one row per level: costs, shares of L1, quality, failures
    experiments/results/tradeoff_sufficient.csv  one row per artifact: its cheapest sufficient level
    experiments/results/tradeoff_policies.csv    one level for every artifact, against hindsight
    experiments/results/tradeoff_paired.csv      level differences on the same artifacts, with tests
    experiments/plots/tradeoff_quality_vs_time.png, tradeoff_cost_by_level.png, tradeoff_sufficient.png

Usage (PowerShell):
    python scripts/analyze_tradeoff.py
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.compare import collect, write_csv  # noqa: E402
from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402
from heritage3d.tradeoff import QUALITY, level_table, paired_differences, policies, sufficient_table, time_exponent  # noqa: E402

THRESHOLDS = (0.90, 0.95, 0.98)
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
LEVEL_COLOR = {"L1": "#0d366b", "L2": "#1c5cab", "L3": "#2a78d6", "L4": "#5598e7", "L5": "#86b6ef"}
BLUE, ORANGE, NEUTRAL = "#2a78d6", "#eb6834", "#b9b8b2"
PAIRS = [("L2", "L1"), ("L3", "L1"), ("L4", "L1"), ("L5", "L1"), ("L4", "L3")]


def setup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "font.size": 10,
        "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": GRID,
        "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 11, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    })
    return plt


def plot_quality_vs_time(rows_by_artifact, table, levels, threshold, path):
    plt = setup()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True, sharex=True)
    for ax, (name, key), title in zip(axes, QUALITY.items(), ("Final mesh", "Dense point cloud")):
        for level in levels:
            points = [(r["total_s"] / 60, r[key]) for rows in rows_by_artifact.values() for r in rows if r["level"] == level]
            ax.scatter(*zip(*points), s=16, color=LEVEL_COLOR[level], alpha=0.35, linewidths=0)
        for row in table:
            x, y = row["median_total_s"] / 60, row[f"median_{name}_f"]
            ax.scatter(x, y, s=95, color=LEVEL_COLOR[row["level"]], edgecolors=SURFACE, linewidths=2, zorder=3)
            ax.annotate(row["level"], (x, y), xytext=(0, -18 if name == "mesh" or row["level"] == "L5" else 9), textcoords="offset points",
                        ha="center", fontsize=9, fontweight="bold", color=INK, zorder=4)
        ax.axhline(threshold, color=MUTED, lw=1, ls=(0, (4, 3)))
        ax.annotate(f"F = {threshold}", (0.01, threshold), xycoords=("axes fraction", "data"), xytext=(0, -13), textcoords="offset points",
                    ha="left", fontsize=9, color=MUTED)
        ax.set_xscale("log")
        ax.set_xticks([1, 3, 10, 30, 100], ["1", "3", "10", "30", "100"])
        ax.set_xlabel("Total reconstruction time (minutes, log scale)")
        ax.set_title(title)
    axes[0].set_ylabel("F@0.002 R (1 is perfect)")
    axes[0].set_ylim(-0.03, 1.05)
    fig.suptitle(f"Quality against time: {len(rows_by_artifact)} artifacts × 5 levels. Large marks are medians, small marks single runs.",
                 x=0.01, ha="left", fontsize=11, color=MUTED)
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def plot_cost_by_level(table, path):
    plt = setup()
    panels = (("time_share_of_L1", "Time"), ("peak_ram_share_of_L1", "Peak RAM"), ("input_share_of_L1", "Input images, MB"),
              ("cloud_share_of_L1", "Dense cloud, MB"), ("mesh_share_of_L1", "Textured mesh, MB"))
    fig, axes = plt.subplots(1, 5, figsize=(13, 3.5), sharey=True)
    names = [r["level"] for r in table]
    for ax, (key, title) in zip(axes, panels):
        values = [r[key] * 100 for r in table]
        bars = ax.bar(names, values, color=BLUE, width=0.72)
        ax.bar_label(bars, [f"{v:.0f}" if v >= 10 else f"{v:.1f}" for v in values], padding=2, fontsize=9, color=INK)
        ax.set_title(title)
        ax.grid(axis="x", visible=False)
        ax.set_ylim(0, 118)
    axes[0].set_ylabel("Median share of the same\nartifact's L1 cost (%)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def plot_sufficient(table, sufficient, levels, threshold, path):
    plt = setup()
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    width = 0.38
    xs = range(len(levels))
    for offset, name, color, label in ((-width / 2 - 0.01, "mesh", BLUE, "Final mesh"), (width / 2 + 0.01, "cloud", ORANGE, "Dense cloud")):
        reach = [r[f"{name}_f_reaching_{threshold}"] for r in table]
        bars = left.bar([x + offset for x in xs], reach, width, color=color, label=label)
        left.bar_label(bars, padding=2, fontsize=9, color=INK)
        first = [sum(s[f"{name}_f_{threshold}"] == level for s in sufficient) for level in levels[::-1]]
        never = sum(s[f"{name}_f_{threshold}"] == "none" for s in sufficient)
        bars = right.bar([x + offset for x in range(len(levels) + 1)], first + [never], width, color=color, label=label)
        right.bar_label(bars, padding=2, fontsize=9, color=INK)
    left.set_xticks(list(xs), levels)
    left.set_title(f"Artifacts reaching F ≥ {threshold} when all use one level")
    left.set_ylabel(f"Artifacts, of {len(sufficient)}")
    right.set_xticks(range(len(levels) + 1), [*levels[::-1], "Never"])
    right.set_title("Fewest photos that reach it, per artifact")
    for ax in (left, right):
        ax.grid(axis="x", visible=False)
        ax.legend(frameon=False, loc="upper left", ncols=2)
    left.set_ylim(0, len(sufficient) * 1.2)
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--order", type=Path, default=REPO_ROOT / "configs" / "artifact_order.json")
    args = p.parse_args(argv)

    config = load_config(args.config)
    levels, threshold = list(config["levels"]), config["museum"]["min_mesh_f"]
    results, plots = REPO_ROOT / "experiments" / "results", REPO_ROOT / "experiments" / "plots"
    names = [a["name"] for a in json.loads(args.order.read_text(encoding="utf-8"))["artifacts"]]
    rows_by_artifact = {a: collect(results / "runs", a, levels) for a in names}
    incomplete = [a for a, rows in rows_by_artifact.items() if len(rows) != len(levels)]
    if incomplete:
        sys.exit(f"not all levels are evaluated for: {' '.join(incomplete)}")

    table = level_table(rows_by_artifact, levels, threshold)
    sufficient = sufficient_table(rows_by_artifact, THRESHOLDS)
    plans = [{"quality": name, **row} for name, key in QUALITY.items() for row in policies(rows_by_artifact, levels, key, threshold)]
    paired = [row for key in QUALITY.values() for row in paired_differences(rows_by_artifact, PAIRS, key)]
    write_csv(table, results / "tradeoff_levels.csv")
    write_csv(sufficient, results / "tradeoff_sufficient.csv")
    write_csv(plans, results / "tradeoff_policies.csv")
    write_csv(paired, results / "tradeoff_paired.csv")
    plot_quality_vs_time(rows_by_artifact, table, levels, threshold, plots / "tradeoff_quality_vs_time.png")
    plot_cost_by_level(table, plots / "tradeoff_cost_by_level.png")
    plot_sufficient(table, sufficient, levels, threshold, plots / "tradeoff_sufficient.png")

    for rows in (table, plans, paired):
        for row in rows:
            print(row)
    print("time exponent L1-L4:", time_exponent(rows_by_artifact, levels[:4]))
    for t in THRESHOLDS:
        for name in QUALITY:
            print(t, name, {level: sum(s[f"{name}_f_{t}"] == level for s in sufficient) for level in [*levels, "none"]})
    return 0


if __name__ == "__main__":
    sys.exit(main())
