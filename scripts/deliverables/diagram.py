"""Pipeline diagram for the report, slides and poster -> Deliverables/figures/pipeline.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

NAVY, CLAY, SAGE, INK, MUTED, BG = "#1d3557", "#b5562f", "#4f7a5a", "#1f1f1f", "#5a5a5a", "#ffffff"
boxes = [  # x, y, w, h, title, lines, colour
    (0.2, 3.1, 2.3, 1.3, "CHSD dataset", ["81 artifacts, 1,800 RGB views", "800 × 600 px, CC BY-NC-SA"], NAVY),
    (3.0, 3.1, 2.3, 1.3, "Image subsets", ["L1 362 · L2 182 · L3 92", "L4 47 · L5 26 images"], NAVY),
    (5.8, 3.1, 2.3, 1.3, "COLMAP SfM (CPU)", ["features, exhaustive matching", "camera poses, sparse points"], NAVY),
    (8.6, 3.1, 2.3, 1.3, "OpenMVS (CPU)", ["dense cloud, mesh,", "texture"], NAVY),
    (8.6, 0.9, 2.3, 1.5, "Evaluation", ["shape: F-score, Chamfer", "look: PSNR, SSIM, IoU", "cost: time, RAM, storage"], CLAY),
    (5.8, 0.9, 2.3, 1.5, "Trade-off analysis", ["paired tests, sufficiency", "combined score,", "weight check"], CLAY),
    (3.0, 0.9, 2.3, 1.5, "Web optimisation", ["L3 mesh → ~100k triangles", "JPEG texture ≤ 2048 px", "GLB file"], SAGE),
    (0.2, 0.9, 2.3, 1.5, "Virtual museum", ["three.js, static website", "44 exhibits, 2 floors", "gate scene, close-ups"], SAGE),
]
fig, ax = plt.subplots(figsize=(11.6, 4.9), dpi=200)
ax.set_xlim(0, 11.1); ax.set_ylim(0.3, 5.0); ax.axis("off"); fig.patch.set_facecolor(BG)
for x, y, w, h, t, lines, c in boxes:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc="white", ec=c, lw=2))
    ax.add_patch(FancyBboxPatch((x, y + h - 0.42), w, 0.42, boxstyle="round,pad=0.02,rounding_size=0.12", fc=c, ec=c, lw=2))
    ax.text(x + w / 2, y + h - 0.21, t, ha="center", va="center", color="white", fontsize=10.5, fontweight="bold")
    for i, l in enumerate(lines):
        ax.text(x + w / 2, y + h - 0.68 - i * 0.3, l, ha="center", va="center", color=INK, fontsize=8.6)
arrow = dict(arrowstyle="-|>", color=MUTED, lw=1.6, mutation_scale=14)
for (x1, y1), (x2, y2) in [((2.52, 3.75), (2.98, 3.75)), ((5.32, 3.75), (5.78, 3.75)), ((8.12, 3.75), (8.58, 3.75)),
                           ((9.75, 3.08), (9.75, 2.42)), ((8.58, 1.65), (8.12, 1.65)), ((5.78, 1.65), (5.32, 1.65)), ((2.98, 1.65), (2.52, 1.65))]:
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=arrow)
ax.plot([1.35, 1.35, 9.2], [3.08, 2.78, 2.78], color=CLAY, lw=1.3, ls=(0, (4, 3)))
ax.annotate("", (9.2, 2.42), (9.2, 2.8), arrowprops=dict(arrowstyle="-|>", color=CLAY, lw=1.3, mutation_scale=12))
ax.text(5.2, 2.58, "depth maps → reference geometry (evaluation only, never input)", color=CLAY, fontsize=8.6, ha="center", style="italic")
ax.text(0.2, 4.75, "Reconstruction (same frozen settings for every level, RGB only)", color=NAVY, fontsize=10, fontweight="bold")
ax.text(0.2, 0.45, "Evaluation, analysis and delivery", color=CLAY, fontsize=10, fontweight="bold")
fig.tight_layout(); fig.savefig("Deliverables/figures/pipeline.png", facecolor=BG)
