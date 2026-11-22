"""Poster v2 chart: each level's combined score split into its quality and saving parts
-> Deliverables/figures/score_breakdown.png (from experiments/results/tradeoff_score.csv)"""
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIG, ROOT

BG, INK, MUTED, QUAL, SAVE, GOLD = "#f7f0e1", "#3b2f2a", "#7a6a5c", "#5b3a29", "#c9a24a", "#a8492b"
rows = list(csv.DictReader(open(ROOT / "experiments/results/tradeoff_score.csv", encoding="utf-8")))
w = 0.5
plt.rcParams.update({"font.family": "Georgia", "font.size": 15, "text.color": INK, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": INK})
fig, ax = plt.subplots(figsize=(10.5, 6.2), dpi=200)
fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
for i, r in enumerate(reversed(rows)):
    q, s = w * float(r["quality"]), (1 - w) * float(r["saving"])
    best = r["level"] == "L4"
    ax.barh(i, q, color=QUAL, height=0.62, edgecolor=GOLD if best else BG, linewidth=3 if best else 0)
    ax.barh(i, s, left=q, color=SAVE, height=0.62, edgecolor=GOLD if best else BG, linewidth=3 if best else 0)
    ax.text(q + s + 0.012, i, f"{q + s:.2f}", va="center", fontsize=17, fontweight="bold" if best else "normal",
            color=GOLD if best else INK)
    if q > 0.1:
        ax.text(q / 2, i, f"{q:.2f}", va="center", ha="center", color="white", fontsize=12)
    if s > 0.1:
        ax.text(q + s / 2, i, f"{s:.2f}", va="center", ha="center", color=INK, fontsize=12)
ax.set_yticks(range(len(rows)), [f"{r['level']}  ({r['images']} images)" for r in reversed(rows)])
ax.set_xlim(0, 1.0)
ax.set_xlabel("Combined score = 0.5 × quality + 0.5 × saving")
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(MUTED)
ax.tick_params(axis="y", length=0)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=QUAL), plt.Rectangle((0, 0), 1, 1, color=SAVE)],
          labels=["Quality part", "Saving part (vs L1)"], loc="lower right", frameon=False, fontsize=13)
ax.set_title("Combined cost-effectiveness score by level", loc="left", fontsize=18, fontweight="bold", color=INK, pad=12)
fig.tight_layout()
fig.savefig(FIG / "score_breakdown.png", facecolor=BG)
print("saved")
