"""Poster hero chart: combined score by level, large text, no title (the caption sits under it)
-> Deliverables/figures/score_breakdown_poster.png (from experiments/results/tradeoff_score.csv)"""
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIG, ROOT

INK, MUTED, QUAL, SAVE, BEST, GRID = "#2e2238", "#6e5f7e", "#4b2577", "#cc99ff", "#9b59d0", "#ece4f5"
rows = list(csv.DictReader(open(ROOT / "experiments/results/tradeoff_score.csv", encoding="utf-8")))
plt.rcParams.update({"font.family": "Calibri", "font.size": 20, "text.color": INK, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": INK})
fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=220)
for i, r in enumerate(reversed(rows)):
    q, s = 0.5 * float(r["quality"]), 0.5 * float(r["saving"])
    best = r["level"] == "L4"
    kw = dict(height=0.66, edgecolor=BEST if best else "white", linewidth=3.5 if best else 0)
    ax.barh(i, q, color=QUAL, **kw)
    ax.barh(i, s, left=q, color=SAVE, **kw)
    ax.text(q + s + 0.015, i, f"{q + s:.2f}", va="center", fontsize=24, fontweight="bold", color=BEST if best else INK)
    ax.text(q / 2, i, f"{q:.2f}", va="center", ha="center", color="white", fontsize=16)
    if s > 0.08:
        ax.text(q + s / 2, i, f"{s:.2f}", va="center", ha="center", color=INK, fontsize=16)
ax.set_yticks(range(len(rows)), [f"{r['level']} · {r['images']} photos" for r in reversed(rows)], fontsize=19)
ax.set_xlim(0, 1.0); ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_xlabel("Score = 0.5 × quality + 0.5 × saving against L1", fontsize=18)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID); ax.tick_params(axis="y", length=0)
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=QUAL), plt.Rectangle((0, 0), 1, 1, color=SAVE)],
          labels=["Quality part", "Saving part"], loc="upper right", frameon=False, fontsize=17, ncols=1,
          bbox_to_anchor=(1.02, 1.04))
fig.tight_layout()
fig.savefig(FIG / "score_breakdown_poster.png", transparent=True)
print("saved")
