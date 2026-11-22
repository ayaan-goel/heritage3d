"""Charts for presentation v2 in the template's lavender/purple palette -> Deliverables/figures/
    rq1_quality_time.png   median mesh F-score and PSNR against median processing time, per level
    rq3_shares.png         museum model's cost as a share of the full model (browser measurements)
Values: experiments/results/tradeoff_levels.csv, visual_levels.csv, rq3_summary.csv."""
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIG, ROOT

PURPLE, LAV, ACCENT, INK, MUTED, GRID = "#4b2577", "#cc99ff", "#9b59d0", "#2e2238", "#7a6a8a", "#ece4f5"
plt.rcParams.update({"font.family": "Calibri", "font.size": 15, "text.color": INK, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": GRID, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "axes.axisbelow": True})
read = lambda f: list(csv.DictReader(open(ROOT / "experiments/results" / f, encoding="utf-8")))

# RQ1: quality against time
lv, vis = read("tradeoff_levels.csv"), {r["level"]: r for r in read("visual_levels.csv")}
fig, ax = plt.subplots(figsize=(8.2, 5.2), dpi=200)
x = [float(r["median_total_s"]) / 60 for r in lv]
y = [float(r["median_mesh_f"]) for r in lv]
ax.plot(x, y, color=LAV, lw=3, zorder=1)
for r, xi, yi in zip(lv, x, y):
    best = r["level"] == "L4"
    ax.scatter(xi, yi, s=260 if best else 170, color=ACCENT if best else PURPLE, edgecolor="white", linewidth=2, zorder=3)
    ax.annotate(f"{r['level']} · {r['images']} img\nPSNR {float(vis[r['level']]['median_mean_psnr']):.1f} dB", (xi, yi),
                xytext=(0, 16) if r["level"] != "L5" else (16, -6), textcoords="offset points", ha="center" if r["level"] != "L5" else "left", fontsize=12.5,
                color=ACCENT if best else INK, fontweight="bold" if best else "normal")
ax.set_xscale("log")
ax.set_xticks([1, 3, 10, 30, 60], ["1", "3", "10", "30", "60"])
ax.set_ylim(0.45, 1.13); ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
ax.set_xlabel("Median processing time per artifact (minutes, log scale)")
ax.set_ylabel("Median mesh F-score (1 = perfect)")
ax.axhline(0.95, color=MUTED, lw=1, ls=(0, (4, 3)))
ax.text(14, 0.925, "sufficiency bar F = 0.95", fontsize=11.5, color=MUTED)
fig.tight_layout(); fig.savefig(FIG / "rq1_quality_time.png", transparent=True)

# RQ3: museum as share of full
summ = {r["measure"]: r for r in read("rq3_summary.csv")}
items = [("File size", "bytes"), ("Download (20 Mbit/s)", "download_ms_at_20mbps"), ("Decoding", "decode_ms"),
         ("Drawing a frame", "frame_ms_median"), ("GPU upload + first frame", "first_frame_ms")]
shares = [float(summ[k]["museum_share_of_full_median"]) * 100 for _, k in items]
fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=200)
ys = range(len(items))[::-1]
ax.barh(list(ys), [100] * len(items), color=GRID, height=0.62)
ax.barh(list(ys), shares, color=[PURPLE if v < 50 else LAV for v in shares], height=0.62)
for yi, v in zip(ys, shares):
    ax.text(v + 1.5, yi, f"{v:.0f}%", va="center", fontsize=15, fontweight="bold", color=INK)
ax.set_yticks(list(ys), [n for n, _ in items], fontsize=14, color=INK)
ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100% of full model"])
ax.grid(axis="y", visible=False); ax.tick_params(axis="y", length=0)
fig.tight_layout(); fig.savefig(FIG / "rq3_shares.png", transparent=True)
print("saved")
