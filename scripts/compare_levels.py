"""Compare quality vs cost across subset levels for one artifact.

Reads experiments/results/runs/<artifact>_<level>.json (cost) and <artifact>_<level>_eval.json
(quality), writes experiments/results/<artifact>_levels.csv and a quality-vs-cost plot
experiments/plots/<artifact>_levels.png.

Usage (PowerShell):
    python scripts/compare_levels.py --artifact Ark_HM_272_HI
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.compare import collect, write_csv  # noqa: E402
from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402


def plot(rows, artifact, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    images = [r["images"] for r in rows]
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    ax = axes[0]
    ax.plot(images, [r["total_s"] / 60 for r in rows], "o-", label="total")
    ax.plot(images, [r["matching_s"] / 60 for r in rows], "s--", label="matching")
    ax.plot(images, [r["densify_s"] / 60 for r in rows], "^--", label="densify")
    ax.set(xlabel="input images", ylabel="wall time (min)", title="Time")
    ax.legend()
    ax = axes[1]
    ax.plot(images, [r["peak_mb"] for r in rows], "o-", label="peak RAM")
    ax.plot(images, [r["dense_cloud_mb"] for r in rows], "s--", label="dense cloud file")
    ax.plot(images, [r["textured_mesh_mb"] for r in rows], "^--", label="textured mesh files")
    ax.set(xlabel="input images", ylabel="MB", title="Memory and storage")
    ax.legend()
    ax = axes[2]
    tau = next(k for k in rows[0] if k.startswith("cloud_f@")).split("@")[1]
    ax.plot(images, [r[f"cloud_f@{tau}"] for r in rows], "o-", label=f"dense cloud F@{tau} R")
    ax.plot(images, [r[f"mesh_f@{tau}"] for r in rows], "s--", label=f"mesh F@{tau} R")
    ax.set(xlabel="input images", ylabel="F-score", title="Quality")
    ax.legend()
    for row in rows:
        ax.annotate(row["level"], (row["images"], row[f"cloud_f@{tau}"]), textcoords="offset points",
                    xytext=(4, -10), fontsize=8)
    for ax in axes:
        ax.set_xticks(images, [str(i) for i in images])
        ax.grid(alpha=0.3)
    fig.suptitle(f"{artifact}: quality vs cost by subset level")
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--artifact", required=True)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = p.parse_args(argv)

    levels = list(load_config(args.config)["levels"])
    rows = collect(REPO_ROOT / "experiments" / "results" / "runs", args.artifact, levels)
    if not rows:
        print("no level has both a run and an evaluation", file=sys.stderr)
        return 1
    csv_path = REPO_ROOT / "experiments" / "results" / f"{args.artifact}_levels.csv"
    write_csv(rows, csv_path)
    plot_path = REPO_ROOT / "experiments" / "plots" / f"{args.artifact}_levels.png"
    plot(rows, args.artifact, plot_path)
    for r in rows:
        print(f"{r['level']}: {r['images']} images, {r['total_s'] / 60:.1f} min, peak {r['peak_mb']} MB, "
              f"chamfer {r['cloud_chamfer']:.5f} R, F {r['cloud_f@0.002']:.3f}")
    print(f"-> {csv_path}\n-> {plot_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
