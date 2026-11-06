"""RQ3 costs of the museum models against the full L3 models, from the browser benchmark (bench/, bench_server.py).

Reads experiments/results/rq3/bench_local.json (decode, GPU upload, drawing, from localhost) and bench_<N>mbps.json
(downloads sent at N megabits per second). Download times at other bandwidths are calculated from the file sizes,
and the throttled run checks that calculation. Writes:
    experiments/results/rq3_models.csv     one row per exhibit and kind
    experiments/results/rq3_summary.csv    medians, museum against full
    experiments/plots/rq3_costs.png

Usage (PowerShell):
    python scripts/analyze_rq3.py
"""

import json
import re
import sys
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze_tradeoff import BLUE, INK, MUTED, ORANGE, setup  # noqa: E402
from heritage3d.compare import write_csv  # noqa: E402
from heritage3d.config import REPO_ROOT  # noqa: E402

RQ3 = REPO_ROOT / "experiments" / "results" / "rq3"
BANDWIDTHS = (10, 25, 50, 100)  # Mbit/s
MB = 2 ** 20
KEYS = ("bytes", "decode_ms", "first_frame_ms", "frame_ms_median", "triangles", "geometry", "texture", "textureSide")


def main():
    local = json.loads((RQ3 / "bench_local.json").read_text(encoding="utf-8"))
    throttled = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(RQ3.glob("bench_*mbps.json"))]
    rows = {(m["id"], m["kind"]): m for m in local["models"]}
    ids = sorted({i for i, _ in rows})
    table = []
    for i in ids:
        for kind in ("museum", "full"):
            m = rows[(i, kind)]
            row = {"id": i, "kind": kind, **{k: round(m[k], 3) for k in KEYS}, "local_download_ms": round(m["download_ms"], 1)}
            for t in throttled:
                d = next(x for x in t["models"] if x["id"] == i and x["kind"] == kind)
                row[f"download_ms_at_{t['mbps']:g}mbps"] = round(d["download_ms"], 1)
            table.append(row)
    write_csv(table, REPO_ROOT / "experiments" / "results" / "rq3_models.csv")

    summary = []
    for key in (*KEYS, "local_download_ms", *[k for k in table[0] if k.startswith("download_ms_at")]):
        museum = [r[key] for r in table if r["kind"] == "museum"]
        full = [r[key] for r in table if r["kind"] == "full"]
        ratios = [m / f for m, f in zip(museum, full) if f]
        summary.append({"measure": key, "museum_median": round(median(museum), 3), "full_median": round(median(full), 3),
                        "museum_share_of_full_median": round(median(ratios), 3) if ratios else None,
                        "museum_total": round(sum(museum), 1), "full_total": round(sum(full), 1)})
    for t in throttled:  # does the measured time match size / bandwidth?
        key = f"download_ms_at_{t['mbps']:g}mbps"
        ratio = [r[key] / (r["bytes"] * 8 / (t["mbps"] * 1e6) * 1000) for r in table]
        summary.append({"measure": f"{key} / calculated", "museum_median": None, "full_median": None,
                        "museum_share_of_full_median": round(median(ratio), 3), "museum_total": None, "full_total": None})
    for mbps in BANDWIDTHS:  # seconds for one model (median) and for all of them (total)
        seconds = {kind: [r["bytes"] * 8 / (mbps * 1e6) for r in table if r["kind"] == kind] for kind in ("museum", "full")}
        summary.append({"measure": f"calculated_download_s_at_{mbps}mbps", "museum_median": round(median(seconds["museum"]), 2),
                        "full_median": round(median(seconds["full"]), 2), "museum_share_of_full_median": None,
                        "museum_total": round(sum(seconds["museum"]), 1), "full_total": round(sum(seconds["full"]), 1)})
    write_csv(summary, REPO_ROOT / "experiments" / "results" / "rq3_summary.csv")
    for s in summary:
        print(s)
    print("gpu:", local["gpu"])

    plt = setup()
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.8))
    panels = (("bytes", "File size (MB)", MB), ("decode_ms", "Decoding (ms)", 1), ("first_frame_ms", "GPU upload and first frame (ms)", 1),
              ("frame_ms_median", "Drawing one frame (ms)", 1))
    for ax, (key, title, scale) in zip(axes, panels):
        for x, kind, color in ((0, "museum", BLUE), (1, "full", ORANGE)):
            values = [r[key] / scale for r in table if r["kind"] == kind]
            ax.scatter([x] * len(values), values, s=14, color=color, alpha=0.45, linewidths=0)
            med = median(values)
            ax.plot([x - 0.25, x + 0.25], [med, med], color=INK, lw=2)
        for i in ids:  # same exhibit joined
            a, b = rows[(i, "museum")][key] / scale, rows[(i, "full")][key] / scale
            ax.plot([0, 1], [a, b], color=MUTED, lw=0.4, alpha=0.4)
        meds = [median(r[key] / scale for r in table if r["kind"] == k) for k in ("museum", "full")]
        ax.set_xticks([0, 1], [f"Museum\n{meds[0]:.1f}" if meds[0] >= 1 else f"Museum\n{meds[0]:.2f}", f"Full\n{meds[1]:.1f}" if meds[1] >= 1 else f"Full\n{meds[1]:.2f}"])
        ax.set_xlim(-0.6, 1.6)
        ax.set_ylim(bottom=0)
        ax.set_title(title)
        ax.grid(axis="x", visible=False)
    gpu = re.sub(r"\((R|TM)\)", "", local["gpu"])
    gpu = re.search(r"(Intel [\w ]+? Graphics)", gpu)
    fig.suptitle(f"{len(ids)} exhibits in the browser on this laptop ({gpu.group(1) if gpu else 'GPU in results file'}). "
                 "Bars are medians; lines join the same exhibit.", x=0.01, ha="left", fontsize=11, color=MUTED)
    fig.tight_layout()
    fig.savefig(REPO_ROOT / "experiments" / "plots" / "rq3_costs.png", dpi=150)
    return 0


if __name__ == "__main__":
    sys.exit(main())
