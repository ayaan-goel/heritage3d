# Experiment Plan

## Image-input levels (decided 2026-10-25)

Levels are defined by **azimuth step**, applied uniformly on every camera ring, instead of percentages. Reasons: 6.25% of 1,800 is not an integer; consecutive 1° views are near-duplicates; uniform steps keep all-round coverage constant so only density changes.

| Level | Azimuth step | Images / ring | Total (5 rings) | Share of 1,800 |
|---|---|---|---|---|
| L1 | 3° | 120 | 600 | 33% |
| L2 | 6° | 60 | 300 | 17% |
| L3 | 12° | 30 | 150 | 8% |
| L4 | 24° | 15 | 75 | 4% |
| L5 | 45° | 8 | 40 | 2% |

- L1 ⊃ L2 ⊃ L3 ⊃ L4 (nested). L5 is not nested (45 is not a multiple of 24).
- All levels start at azimuth 0° so subsets are reproducible.
- **To verify after download:** if the ±90° cameras are top/bottom views, rotating them yields no new viewpoints → use 1 image from each of those rings; totals shrink accordingly.
- **Feasibility:** if L1 is too slow on the CPU laptop during the pilot, L2 becomes the top level. Record the decision.
- Optional: one full 1,800-image run on the pilot artifact only, as an upper reference.

## Artifacts

- Pilot: 1 artifact, start with L3 (150 images) to check registration and runtime.
- Main: a small set of artifacts chosen for variety (shape, texture), number fixed after the pilot timing.

## Metrics per run

**Quality:** Chamfer distance, Hausdorff distance, RMSE, precision/recall/F-score at threshold τ (units and τ declared), completeness/coverage, visual check of texture.
**Reconstruction health:** registered images / input images, sparse points, mean reprojection error, failure flag.
**Cost:** input image count, input bytes, wall time per stage, peak RAM, output sizes (sparse, dense cloud, mesh, texture), vertices/faces.

All metrics written to `experiments/results/*.csv` with the config used.
