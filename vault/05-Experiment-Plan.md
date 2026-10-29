# Experiment Plan

## Image-input levels (decided 2026-10-25)

Levels are defined by **azimuth step**, applied uniformly on every camera ring, instead of percentages. Reasons: 6.25% of 1,800 is not an integer; consecutive 1° views are near-duplicates; uniform steps keep all-round coverage constant so only density changes.

| Level | Azimuth step | Images / turning ring | Total (3 turning rings + 2 pole views) | Share of 1,800 |
|---|---|---|---|---|
| L1 | 3° | 120 | 362 | 20% |
| L2 | 6° | 60 | 182 | 10% |
| L3 | 12° | 30 | 92 | 5% |
| L4 | 24° | 15 | 47 | 2.6% |
| L5 | 45° | 8 | 26 | 1.4% |

- L1 ⊃ L2 ⊃ L3 ⊃ L4 (nested). L5 is not nested (45 is not a multiple of 24).
- All levels start at azimuth 0° (file frame 0001) so subsets are reproducible.
- **Verified 2026-10-29:** the ±90° views are the same picture spun in the image plane (no new viewpoint), so each pole ring contributes one image (frame 0001). Totals above reflect this (the 2026-10-25 plan had 600/300/150/75/40).
- **Feasibility:** if L1 is too slow on the CPU laptop during the pilot, L2 becomes the top level. Record the decision.
- Optional: one full 1,800-image run on the pilot artifact only, as an upper reference.

## Artifacts

- Pilot: 1 artifact, start with L3 (92 images) to check registration and runtime. Proposed pilot: `Ark_HM_272_HI` (centred, never cut off by the frame in the sample views, strongly textured pot) — to confirm with the team.
- Avoid for now: artifacts cut off by the image frame in some views (41 of 81, listed in `experiments/results/dataset_inspection.json`).
- Main: a small set of artifacts chosen for variety (shape, texture), number fixed after the pilot timing.

## Metrics per run

**Quality:** Chamfer distance, Hausdorff distance, RMSE, precision/recall/F-score at threshold τ (units and τ declared), completeness/coverage, visual check of texture.
**Reconstruction health:** registered images / input images, sparse points, mean reprojection error, failure flag.
**Cost:** input image count, input bytes, wall time per stage, peak RAM, output sizes (sparse, dense cloud, mesh, texture), vertices/faces.

All metrics written to `experiments/results/*.csv` with the config used.
