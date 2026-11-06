# Results

Measured results only, each with date, artifact, level, config and log path.

## Pilot — `Ark_HM_272_HI`, L3 (92 images), sparse SfM — 2026-10-30

Config: `configs/experiment.toml` as of this run (`SIMPLE_PINHOLE`, single camera, `exhaustive_matcher`, CPU). Metrics: `experiments/results/runs/Ark_HM_272_HI_L3.json`; logs: `experiments/logs/Ark_HM_272_HI/L3/`. Laptop: i7-1255U, 12 logical CPUs, 15.72 GB RAM, COLMAP 4.2.1 (no GPU).

| Stage | Wall time | Peak memory (process tree, committed) |
|---|---|---|
| feature_extractor | 11.7 s | 2,033 MB |
| exhaustive_matcher | 283.4 s | 1,961 MB |
| mapper | 51.9 s | 480 MB |
| **Sparse total** | **347 s (5.8 min)** | **2.0 GB** |

| Sparse model | Value |
|---|---|
| Models produced | 1 |
| Registered images | **92 / 92** |
| 3D points | 35,995 |
| Mean track length | 7.71 views per point |
| Mean observations per image | 3,018 |
| Mean reprojection error | **0.19 px** |

- Matching dominates sparse time (exhaustive: 4,186 image pairs). Expect it to grow ~quadratically with image count (L1 362 images ≈ 15× the pairs) — **(hypothesis, to measure)**.
- One shared camera model fits all five rings with 0.19 px error → supports the single-lens assumption for this artifact. Estimated focal length 998.8 px (≈ 43.7° horizontal field of view at 800 px).

## Pilot — `Ark_HM_272_HI`, L3, dense (OpenMVS, CPU) — 2026-10-30

Same workspace and metrics file as above; OpenMVS 2.4.0, `DensifyPointCloud --resolution-level 1` (images stayed at 800×600 because of the 640 px minimum).

| Stage | Wall time | Peak memory |
|---|---|---|
| image_undistorter | 0.4 s | 82 MB |
| InterfaceCOLMAP | 0.2 s | 12 MB |
| DensifyPointCloud | 546.9 s | 1,206 MB |
| ReconstructMesh | 83.8 s | 650 MB |
| TextureMesh | 110.7 s | 1,137 MB |
| **Dense total** | **742 s (12.4 min)** | **1.2 GB** |
| **Whole pipeline (sparse + dense)** | **1,089 s (18.2 min)** | **2.0 GB** (feature extraction) |

| Output | Value |
|---|---|
| Depth maps | 91 / 92 — none for `0001_90_.png` (the single top view; no neighbouring view close enough) |
| Dense points | 1,194,573 |
| Mesh | 240,838 vertices, 481,612 faces |
| Texture | one 4.8 MB PNG atlas |
| Sizes | input images 36.3 MB; sparse 13.2 MB; dense cloud 98.0 MB; mesh 9.2 MB; textured mesh 21.2 MB |

- Visual check (`experiments/plots/Ark_HM_272_HI_L3_dense.jpg`): the pot is clearly reconstructed — ribbing, rim, base with the catalogue label, surface colour. Not yet a metric; geometric accuracy needs the evaluation step.
- Peak memory measured with a Windows job object agrees with OpenMVS's own report (ReconstructMesh: 650 MB vs `PeakPagefileUsage` 649 MB).
- **Interpretation (hypothesis):** at L3 the CPU pipeline is cheap (18 min, 2 GB); RAM is not the constraint at 800×600, time is (matching, densify).

## Pilot — `Ark_HM_272_HI`, L3, geometric evaluation — 2026-10-30

Method: [[04-Methodology]] Option A. Units: R (camera-to-centre distance); object extent 0.50 × 0.50 × 0.39 R (diagonal 0.81 R). Reference: 306,000 points from all 1,800 depth maps (build 352 s, cached). File: `experiments/results/runs/Ark_HM_272_HI_L3_eval.json`.

| Metric | Dense cloud | Mesh vertices |
|---|---|---|
| Camera alignment RMS / max | 0.00025 / 0.00057 R (92 cameras) | same |
| Points after 0.002 R voxel grid | 227,961 | — |
| Accuracy median / mean | 0.00057 / 0.00075 R | 0.00066 / — R |
| Completeness median / mean | 0.00069 / 0.00076 R | 0.00092 / — R |
| Chamfer | **0.00075 R** (≈ 0.09 % of object diagonal) | 0.00082 R |
| RMSE (accuracy) | 0.00112 R | — |
| Hausdorff / 95th percentile | 0.0137 / 0.0019 R | — |
| F-score @ 0.002 R (P / R) | **0.974** (0.952 / 0.997) | — |
| F-score @ 0.005 R | 0.995 | 1.000 |
| F-score @ 0.01 R | 1.000 | — |

- L3 is close to the measurement floor (median errors below the 0.002 R voxel). F @ 0.002 R and Chamfer are the discriminating numbers.

## Pilot — `Ark_HM_272_HI`, all levels L1–L5, cost — 2026-10-30

Same config and laptop as L3 (CPU only). Metrics: `experiments/results/runs/Ark_HM_272_HI_<level>.json`; logs: `experiments/logs/Ark_HM_272_HI/<level>/`; previews: `experiments/plots/Ark_HM_272_HI_<level>_dense.jpg`; table: `experiments/results/Ark_HM_272_HI_levels.csv`.
L5 and L4 were re-run (`--overwrite`) on an idle machine because their first runs overlapped other work; the first runs were 5–15 % slower. L1, L2, L3 ran with nothing else heavy running.

| Level | Images | Registered | Sparse points | Reproj. error | Matching | Densify | Total time | Peak RAM | Dense cloud file | Textured mesh files |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 362 | 362 | 67,944 | 0.24 px | 80.4 min | 36.3 min | **135.2 min** | **4.7 GB** | 320 MB | 27.9 MB |
| L2 | 182 | 182 | 51,488 | 0.22 px | 19.7 min | 18.1 min | **45.1 min** | 2.4 GB | 179 MB | 26.5 MB |
| L3 | 92 | 92 | 35,995 | 0.19 px | 4.7 min | 9.1 min | **18.1 min** | 2.0 GB | 93 MB | 24.8 MB |
| L4 | 47 | 47 | 22,176 | 0.16 px | 1.3 min | 4.4 min | **7.9 min** | 2.0 GB | 46 MB | 21.9 MB |
| L5 | 26 | 26 | 7,119 | 0.17 px | 0.5 min | 1.7 min | **3.4 min** | 2.0 GB | 19 MB | 16.3 MB |

Dense points (before evaluation voxel grid): L1 4,117,294; L2 2,201,830; L3 1,194,573; L4 680,823; L5 305,185.

- Every level registered every image; SfM did not fail even with 26 images (45° steps).
- Matching grows about quadratically with image count (exhaustive): ×4.1 per doubling L2→L1, ×4.2 L3→L2. Densify grows about linearly (×2.0 per doubling). At L1 matching is 60 % of the time.
- Peak RAM is ~2 GB up to L3 (set by feature extraction), then rises with densify: 2.4 GB at L2, 4.7 GB at L1. Fits in 16 GB at 800×600.
- The textured mesh (what the museum would load) changes little in size (16–28 MB); the dense cloud scales with images.

## Pilot — `Ark_HM_272_HI`, all levels, quality vs cost — 2026-10-30

Method: [[04-Methodology]] Option A (thresholds fixed before this comparison). Files: `experiments/results/runs/Ark_HM_272_HI_<level>_eval.json`, `experiments/results/Ark_HM_272_HI_levels.csv`, plot `experiments/plots/Ark_HM_272_HI_levels.png` (`scripts/compare_levels.py`). Units: R; object diagonal 0.81 R.

| Level | Images | Total time | Camera RMS | Cloud Chamfer | Cloud F@0.002 (P / R) | Cloud Hausdorff95 | Mesh Chamfer | Mesh F@0.002 |
|---|---|---|---|---|---|---|---|---|
| L1 | 362 | 135.2 min | 0.00033 | 0.00103 | 0.905 (0.829 / 0.995) | 0.0051 | 0.00089 | 0.988 |
| L2 | 182 | 45.1 min | 0.00031 | 0.00088 | 0.942 (0.894 / 0.996) | 0.0040 | 0.00085 | 0.988 |
| L3 | 92 | 18.1 min | 0.00025 | 0.00075 | 0.974 (0.952 / 0.997) | 0.0019 | 0.00082 | 0.993 |
| **L4** | **47** | **7.9 min** | 0.00032 | **0.00072** | **0.991** (0.985 / 0.997) | 0.0015 | 0.00082 | **0.994** |
| L5 | 26 | 3.4 min | 0.00053 | 0.00102 | 0.959 (0.994 / 0.926) | 0.0025 | 0.00109 | 0.950 |

**Measured on this one artifact:**
- Quality is **not** monotonic in image count. The best numbers are at L4 (47 images, 8 min); L1 costs 17× the time and 2.3× the RAM and scores lower.
- Recall (completeness) saturates by L4 (0.997); only L5 loses coverage (0.926), so L5 → L4 is the one step where more images clearly help.
- Above L4 the dense cloud's **precision** falls steadily (0.985 → 0.952 → 0.894 → 0.829) and its Hausdorff95 grows: more views add more stray points ("noise") within 0.002–0.005 R of the surface, not missing geometry.
- The mesh hides most of this: mesh F@0.002 stays 0.988–0.994 from L4 to L1; meshing filters the extra noise.

**Interpretation (hypothesis, to verify):**
- With fixed OpenMVS settings, more neighbouring views per depth map means more small depth errors fused into the cloud (OpenMVS's fusion/filtering was tuned for fewer, wider-baseline views). Testing this would need a densify-parameter study, which is outside the frozen scope unless agreed.
- One artifact is not a result. Needs repeating on more artifacts (well-framed ones from the inspection list) before any general claim.
- For the museum, L4-level capture (47 images) gives a mesh as good as L1 at ~6 % of the time on this CPU laptop.

## `Ark_HM_1260B_HI`, L5 (batch test) — 2026-10-30

Smallest well-framed object (8 % of the frame; extent 0.09 × 0.50 × 0.18 R). Files: `experiments/results/runs/Ark_HM_1260B_HI_L5.json`, `_L5_eval.json`.
- SfM: **7 / 26 images registered**, 273 points, 0.20 px. Total pipeline 5 s.
- Densify: every registered image paired with 0 neighbour views → 0 depth maps, **no dense cloud** (F = 0).
- Mesh (from the 273 sparse points): F@0.005 R 0.144 (precision 0.934, recall 0.078) — what exists is in the right place, but 92 % of the object is missing.
- First measured case where a level **fails**: 45° steps are too sparse for a small, plain object. (Hypothesis: size × texture decide the lowest workable level — round 1 tests this.)

## Round 1 — pilot + ranks 1–12 (13 artifacts × 5 levels) — 2026-10-31

Frozen config (see [[08-Decisions]]), same laptop, run by `run_batch.py --count 13 --clean` from 2026-10-30 10:59 to 2026-10-31 15:01 with the condition guard (no level counted that slept or ran on battery; 470 L4 and L3 were redone after charger removals). 65 / 65 level runs evaluated. Files: `experiments/results/runs/<artifact>_<level>{,_eval}.json`, per artifact `experiments/results/<artifact>_levels.csv` + `experiments/plots/<artifact>_levels.png`, all rows `experiments/results/round1_all.csv`, per level `experiments/results/round1_summary.csv`, plot `experiments/plots/round1_summary.png` (`scripts/summarize_round.py --count 13`).

Dense-cloud F@0.002 R; in brackets, images in the densified SfM model / input images when not all:

| Artifact | L1 | L2 | L3 | L4 | L5 | L1 time | Best |
|---|---|---|---|---|---|---|---|
| `Ark_HM_272_HI` | 0.905 | 0.942 | 0.974 | 0.991 | 0.959 | 135 min | L4 |
| `Ark_HM_1260B_HI` | 0.062 (350/362) | 0.051 (98/182) | 0.151 (30/92) | 0.209 (14/47) | 0.000 (7/26) | 18 min | L4 |
| `Ark_HM_470_HI` | 0.937 | 0.967 | 0.988 | 0.995 | 0.997 | 136 min | L5 |
| `Ark_HM_795_HI` | 0.842 | 0.786 (121/182) | 0.823 (61/92) | 0.777 (31/47) | 0.295 (17/26) | 48 min | L1 |
| `Ark_HM_714_HI` | 0.933 | 0.966 | 0.990 | 0.997 | 0.995 | 150 min | L4 |
| `Ark_HM_341_HI` | 0.633 (241/362) | 0.651 (121/182) | 0.663 (61/92) | 0.666 (31/47) | 0.651 (17/26) | 44 min | L4 |
| `Ark_HM_654_HI` | 0.878 | 0.931 | 0.971 | 0.967 | 0.345 (24/26) | 52 min | L3 |
| `Ark_HM_725_HI` | 0.883 | 0.915 | 0.961 | 0.986 | 0.852 | 64 min | L4 |
| `RL_907_HI` | 0.797 (360/362) | 0.845 (180/182) | 0.907 (90/92) | 0.273 (25/47) | 0.000 (5/26) | 23 min | L3 |
| `Ark_HM_321_HI` | 0.914 | 0.943 | 0.969 | 0.820 (31/47) | 0.790 (17/26) | 78 min | L3 |
| `Ark_HM_31_HI` | 0.649 (241/362) | 0.615 (121/182) | 0.669 (61/92) | 0.335 (20/47) | 0.000 (7/26) | 26 min | L3 |
| `Ark_HM_809_HI` | 0.914 | 0.945 | 0.972 | 0.990 | 0.789 | 79 min | L4 |
| `Ark_HM_797_hi` | 0.837 (241/362) | 0.850 (121/182) | 0.834 (61/92) | 0.662 (20/47) | 0.000 (9/26) | 27 min | L2 |

Per level across the 13 (`round1_summary.csv`):

| Level | Images | Median total time (max) | Median peak RAM | Median cloud F (min) | Median mesh F | Cloud F < 0.5 |
|---|---|---|---|---|---|---|
| L1 | 362 | 52.0 min (150.1) | 4.4 GB | 0.878 (0.062) | 0.983 | 1 / 13 |
| L2 | 182 | 22.5 min (55.4) | 2.3 GB | 0.915 (0.051) | 0.981 | 1 / 13 |
| L3 | 92 | 9.8 min (18.1) | 2.0 GB | **0.961** (0.151) | 0.983 | 1 / 13 |
| L4 | 47 | 3.3 min (8.1) | 2.0 GB | 0.820 (0.209) | 0.821 | 3 / 13 |
| L5 | 26 | 1.4 min (4.2) | 2.0 GB | 0.651 (0.000) | 0.653 | 6 / 13 |

**Measured:**
- Six artifacts reconstruct as one complete model at L1–L4 (272, 470, 714, 654, 725, 809). For them the pilot pattern repeats: cloud F rises from L1 to L3/L4 (precision falls with more images) and the mesh stays ≥ 0.97 from L4 up; best level L4 for four, L5 for 470, L3 for 654. At L5 three of the six lose quality (654 0.345, 809 0.789, 725 0.852).
- **SfM splits into two models** in 7 artifacts at some level: all images register, but into two disconnected models, and the pipeline densifies only the larger one (`dense_from_model` = most registered images). At L1 in 341, 31 and 797 the split is exactly **one elevation ring plus its pole** (341: the +45° ring + top view; 31 and 797: the −45° ring + bottom view; checked from the COLMAP models, 2026-10-31) — that side of the object is never densified, hence F ≈ 0.63–0.84 flat across levels. 795 splits the same way from L2 down, 321 from L4, RL_907 at L4.
- Hard failures (F = 0, no dense cloud): L5 of 1260B, RL_907, 31, 797 (5–9 / 26 images registered). Three of them crashed TextureMesh after 0-point densify; evaluated afterwards as failed reconstructions.
- `Ark_HM_1260B_HI` (smallest, flat, plain, specular object) registers 350/362 at L1 in one model but is poorly placed: camera RMS 0.018 R (pilot 0.0003), cloud F@0.002 0.062, F@0.005 0.217, **F@0.01 0.912** — the shape is roughly right but off by ~0.5–1 % R.
- Cost scales as in the pilot: median L1 52 min, L3 10 min, L5 1.4 min; L1 ranges 18–150 min depending on the object (matching dominates). Peak RAM ≤ 4.7 GB everywhere.
- L3 (92 images, 12°) is the lowest level with no new breakdown on any artifact (its F < 0.5 case is 1260B, which fails at every level).

**Interpretation (hypotheses, to verify):**
- The split-model loss is a pipeline limitation (taking only the largest model), not missing coverage: merging or densifying both models would likely recover most of the missing side. Fixing it changes the frozen pipeline → team decision ([[09-Open-Questions]]).
- Rings fail to connect when the object looks very different from above and below (plain or symmetric surfaces), so cross-ring matches are few; fewer images per ring make it worse (more splits at L4/L5).
- τ = 0.002 R is harsh for small objects (1260B fills 8 % of the frame); a tolerance relative to object size may be fairer for them.

## Round 2 — ranks 13–19 (7 artifacts × 5 levels) — 2026-11-01

Same frozen config, `run_batch.py --count 20 --clean` in-session from 2026-10-31 16:54 to 2026-11-01 07:37 → `batch done: 35 ok, 0 failed`. Charger removed three times (1303 L1, 299 L2 twice): the guard stopped each level and redid it; nothing slept or was set aside. Files as in round 1; all 20 artifacts: `experiments/results/round2_all.csv`, `round2_summary.csv`, `experiments/plots/round2_summary.png` (`summarize_round.py --count 20 --name round2`).

Dense-cloud F@0.002 R; in brackets, images in the densified SfM model / input images when not all:

| Artifact | L1 | L2 | L3 | L4 | L5 | L1 time | Best |
|---|---|---|---|---|---|---|---|
| `Ark_HM_1304_HI` | 0.890 | 0.928 | 0.964 | 0.986 | 0.724 | 56 min | L4 |
| `Ark_HM_1303_HI` | 0.884 | 0.920 | 0.963 | 0.984 | 0.678 (17/26) | 60 min | L4 |
| `Ark_HM_314_HI` | 0.869 | 0.911 | 0.963 | 0.989 | 0.723 | 79 min | L4 |
| `Ark_HM_299_HI` | 0.877 | 0.919 | 0.966 | 0.988 | 0.817 | 123 min | L4 |
| `Ark_HM_38_HI` | 0.175 (121/362) | 0.326 (61/182) | 0.494 (31/92) | 0.000 (2/47) | 0.000 (4/26) | 15 min | L3 |
| `Ark_HM_747_HI` | 0.894 | 0.929 | 0.966 | 0.975 | 0.679 | 86 min | L4 |
| `Ark_HM_11_HI` | 0.896 | 0.927 | 0.965 | 0.984 | 0.578 (17/26) | 52 min | L4 |

Per level across all 20 artifacts (`round2_summary.csv`):

| Level | Images | Median total time (max) | Median peak RAM | Median cloud F (min) | Median mesh F | Cloud F < 0.5 |
|---|---|---|---|---|---|---|
| L1 | 362 | 58.2 min (150.1) | 4.4 GB | 0.881 (0.062) | 0.980 | 2 / 20 |
| L2 | 182 | 23.3 min (55.4) | 2.3 GB | 0.920 (0.051) | 0.980 | 2 / 20 |
| L3 | 92 | 9.8 min (18.1) | 2.0 GB | 0.963 (0.151) | 0.986 | 2 / 20 |
| L4 | 47 | 3.8 min (8.1) | 2.0 GB | **0.980** (0.000) | 0.983 | 4 / 20 |
| L5 | 26 | 1.4 min (4.2) | 2.0 GB | 0.679 (0.000) | 0.687 | 7 / 20 |

**Measured:**
- Six of the seven round-2 artifacts behave like the pilot: one complete model at L1–L4, cloud F rising L1 → L4 (0.87–0.90 → 0.975–0.989), mesh F ≥ 0.97, best level L4 for all six; L5 drops to 0.58–0.82. Clean artifacts across both rounds: 12 / 20.
- With them the **median best level moves from L3 (round 1) to L4** (0.980 vs 0.963), but L4 breaks down on more artifacts (4 vs 2 with F < 0.5): L4 is better when it works, L3 is the lowest level with no breakdown beyond the two artifacts that fail at every level (1260B, 38).
- `Ark_HM_38_HI` fails at every level: SfM splits into 2–4 small models (L1: 121 + 121 + 53 + 52 images, 1,816 points in the largest; pilot ~35,000), L4/L5 register 2–4 images and the dense stage crashes (scored F = 0). The object is a smooth, plain round vessel: pixel colour std inside the object ≈ 8 / 255 (view 0001, −45°). Low texture → too few feature matches (hypothesis; consistent with 1260B).
- Split models at L5 only in 1303, 747, 11 (two overlapping models; 747 densified a 26-image model and still scored 0.679).
- Cost unchanged: median L1 58 min, L3 10 min, L5 1.4 min across 20; peak RAM ≤ 4.7 GB.

## Museum models — optimized vs full (round-1 exhibits) — 2026-10-31

`scripts/export_glb.py --count 13`, config `[museum]` (L3, ~100k triangles, texture ≤ 2048 px JPEG q85, seam leveling off). 8 of 13 artifacts pass the exhibit rule (full-mesh F@0.002 R ≥ 0.95 at L3); not exhibited: 1260B (0.128), 795 (0.830), 341 (0.667), 31 (0.665), 797 (0.854). Both versions re-textured by OpenMVS from the same L3 mesh, aligned into the CHSD frame, packed as one GLB (full: PNG texture ≤ 8192 px; museum: JPEG); accuracy from 1,000,000 surface samples voxelized at 0.002 R vs the CHSD reference. Files: `museum/models/*.glb`, `museum/artifacts.json`, `experiments/results/museum/<artifact>_glb.json`.

| Artifact | Full mesh | Full GLB | Museum GLB | Size ratio | Surface F@0.002 full → museum | Chamfer museum |
|---|---|---|---|---|---|---|
| `Ark_HM_272_HI` | 481,612 tri | 18.21 MB | 3.09 MB | 17 % | 0.9853 → 0.9851 | 0.00078 R |
| `Ark_HM_470_HI` | 487,210 tri | 22.27 MB | 3.82 MB | 17 % | 0.9986 → 0.9987 | 0.00056 R |
| `Ark_HM_714_HI` | 406,484 tri | 16.34 MB | 3.13 MB | 19 % | 0.9738 → 0.9736 | 0.00145 R |
| `Ark_HM_654_HI` | 456,782 tri | 16.22 MB | 2.83 MB | 17 % | 0.9782 → 0.9783 | 0.00119 R |
| `Ark_HM_725_HI` | 419,517 tri | 15.24 MB | 2.92 MB | 19 % | 0.9804 → 0.9802 | 0.00084 R |
| `RL_907_HI` | 133,138 tri | 5.01 MB | 2.79 MB | 56 % | 0.9801 → 0.9799 | 0.00090 R |
| `Ark_HM_321_HI` | 325,530 tri | 12.52 MB | 2.99 MB | 24 % | 0.9847 → 0.9846 | 0.00085 R |
| `Ark_HM_809_HI` | 521,125 tri | 18.88 MB | 2.91 MB | 15 % | 0.9876 → 0.9877 | 0.00075 R |

**Measured:** median file 16.3 MB → 3.0 MB (all 8 exhibits 24.5 MB), surface F@0.002 changes by ≤ 0.0003 and Chamfer by < 1 % — decimating to 100k triangles costs no measurable accuracy at this tolerance; reconstruction error, not tessellation, dominates. Supports H3 on these 8 artifacts (load time / rendering cost not measured yet).
- Found while exporting: OpenMVS seam leveling turns faces black on CHSD renders, so the pipeline's own textured meshes (`scene_dense_texture*`) are black. Does not affect any evaluation (geometry only); museum export turns it off ([[08-Decisions]]).

## Museum models — round-2 exhibits — 2026-11-01

`export_glb.py` for the 7 round-2 artifacts, same `[museum]` config. 6 pass the exhibit rule; not exhibited: `Ark_HM_38_HI` (L3 mesh F 0.486). Museum now **14 exhibits, 43 MB in all**.

| Artifact | Full mesh | Full GLB | Museum GLB | Surface F@0.002 full → museum | Chamfer museum |
|---|---|---|---|---|---|
| `Ark_HM_1304_HI` | 278,552 tri | 11.3 MB | 2.9 MB | 0.948 → 0.948 | 0.00226 R |
| `Ark_HM_1303_HI` | 283,373 tri | 10.7 MB | 2.9 MB | 0.985 → 0.985 | 0.00076 R |
| `Ark_HM_314_HI` | 471,306 tri | 18.6 MB | 3.0 MB | 0.966 → 0.966 | 0.00156 R |
| `Ark_HM_299_HI` | 474,849 tri | 17.9 MB | 3.1 MB | 0.985 → 0.985 | 0.00082 R |
| `Ark_HM_747_HI` | 505,461 tri | 18.2 MB | 2.9 MB | 0.973 → 0.972 | 0.00088 R |
| `Ark_HM_11_HI` | 426,382 tri | 15.4 MB | 2.9 MB | 0.969 → 0.969 | 0.00132 R |

(MB as printed by the script, 1 decimal; exact bytes in `experiments/results/museum/<artifact>_glb.json`.)

**Measured:** decimation again costs ≤ 0.001 surface F. Surface-sampled F is below the vertex-based mesh F used for the exhibit rule (1304: 0.948 vs 0.993; round 1 714: 0.974 vs 0.999) — surface sampling also counts large faces, e.g. hole fills, that have few vertices (hypothesis for the gap). Checked 1304 and 11 in the browser: textured and upright.

## Round 3 — ranks 20–22 (3 artifacts × 5 levels) — 2026-11-01

Same frozen config (still the strict power guard), `run_batch.py --count 23 --clean` in-session 2026-11-01 08:48 → 14:49, `batch done: 15 ok, 0 failed`, no charger removal or sleep. Team chose a 3-artifact round (briefly 2, then back to 3). All 23: `experiments/results/round3_all.csv`, `round3_summary.csv`, `experiments/plots/round3_summary.png`.

| Artifact | L1 | L2 | L3 | L4 | L5 | L1 time | Best |
|---|---|---|---|---|---|---|---|
| `Ark_HM_746_HI` | 0.881 | 0.927 | 0.967 | 0.988 | 0.915 | 100 min | L4 |
| `Ark_HM_522_HI` | 0.909 | 0.946 | 0.978 | 0.991 | 0.896 | 69 min | L4 |
| `BEY_1415_HI` | 0.902 | 0.905 (181/182) | 0.627 (44/92) | 0.582 (20/47) | 0.547 (10/26) | 42 min | L2 |

Per level across all 23 artifacts (`round3_summary.csv`):

| Level | Images | Median total time (max) | Median peak RAM | Median cloud F (min) | Median mesh F | Cloud F < 0.5 |
|---|---|---|---|---|---|---|
| L1 | 362 | 60.0 min (150.1) | 4.4 GB | 0.883 (0.062) | 0.983 | 2 / 23 |
| L2 | 182 | 24.1 min (55.4) | 2.3 GB | 0.920 (0.051) | 0.981 | 2 / 23 |
| L3 | 92 | 9.9 min (18.1) | 2.0 GB | 0.964 (0.151) | 0.988 | 2 / 23 |
| L4 | 47 | 3.9 min (8.1) | 2.0 GB | **0.984** (0.000) | 0.990 | 4 / 23 |
| L5 | 26 | 1.4 min (4.2) | 2.0 GB | 0.679 (0.000) | 0.689 | 7 / 23 |

**Measured:**
- 746 and 522 are clean at every level (one model, all images) and best at L4; both keep F ≈ 0.90–0.92 at L5, among the best L5 results so far. Clean artifacts: 14 / 23.
- `BEY_1415_HI` (first artifact from the BEY collection) is complete at L1/L2 (F ≈ 0.90) but from L3 down SfM registers only part of the images, into two models at L3/L4 (44 + 31, 20 + 15) → F 0.55–0.63. Its breakdown point is 12° steps (L3); others broke from L2 (795), from L4 (321, RL_907) or at every level (1260B, 38).
- Per-level medians barely move from 20 to 23 artifacts; L4 remains best when it works (0.984), L3 the lowest level without extra breakdowns.

## Museum models — round-3 exhibits — 2026-11-01

`export_glb.py --artifacts Ark_HM_746_HI Ark_HM_522_HI BEY_1415_HI`; not exhibited: `BEY_1415_HI` (L3 mesh F 0.593). Museum now **16 exhibits, 49 MB**.

| Artifact | Full mesh | Full GLB | Museum GLB | Surface F@0.002 full → museum | Chamfer museum |
|---|---|---|---|---|---|
| `Ark_HM_746_HI` | 433,507 tri | 15.8 MB | 2.9 MB | 0.982 → 0.981 | 0.00092 R |
| `Ark_HM_522_HI` | 354,525 tri | 13.1 MB | 2.9 MB | 0.991 → 0.991 | 0.00073 R |

Checked both in the browser: textured, upright.

## Round 4 — ranks 23–26 (4 artifacts × 5 levels) — 2026-11-02

Same frozen config, `run_batch.py --count 27 --clean` in-session 2026-11-01 20:28 → 2026-11-02 04:02 (7.6 h), `batch done: 20 ok, 0 failed`, no charger removal or sleep (first round under the 15-min unplug grace). Sized to end before 06:30 (team). All 27: `experiments/results/round4_all.csv`, `round4_summary.csv`, `experiments/plots/round4_summary.png`.

| Artifact | L1 | L2 | L3 | L4 | L5 | L1 time | Best |
|---|---|---|---|---|---|---|---|
| `Ark_HM_192_HI` | 0.922 | 0.960 | 0.985 | 0.987 | 0.000 (6/26) | 55 min | L4 |
| `Ark_HM_711_HI` | 0.920 | 0.944 | 0.973 | 0.988 | 0.560 | 83 min | L4 |
| `Ark_HM_1286_HI` | 0.918 | 0.956 | 0.983 | 0.996 | 0.588 | 66 min | L4 |
| `Ark_HM_1299_Hi` | 0.893 | 0.928 | 0.965 | 0.973 | 0.594 (25/26) | 53 min | L4 |

Per level across all 27 artifacts (`round4_summary.csv`):

| Level | Images | Median total time (max) | Median peak RAM | Median cloud F (min) | Median mesh F | Cloud F < 0.5 |
|---|---|---|---|---|---|---|
| L1 | 362 | 60.0 min (150.1) | 4.4 GB | 0.890 (0.062) | 0.986 | 2 / 27 |
| L2 | 182 | 24.1 min (55.4) | 2.3 GB | 0.927 (0.051) | 0.983 | 2 / 27 |
| L3 | 92 | 9.9 min (18.1) | 2.0 GB | 0.965 (0.151) | 0.989 | 2 / 27 |
| L4 | 47 | 3.9 min (8.1) | 2.0 GB | **0.984** (0.000) | 0.990 | 4 / 27 |
| L5 | 26 | 1.4 min (4.2) | 2.0 GB | 0.651 (0.000) | 0.653 | 8 / 27 |

**Measured:**
- All four are clean from L1 to L4 (one model, all or all-but-one images) and best at L4, with the usual pattern: F rises as images drop from 362 to 47, then collapses at 26.
- `Ark_HM_192_HI` L5: only 6 / 26 images registered, dense step produced no points (2 s) → recorded as failed, F 0. The other three register 25–26 / 26 at L5 but reach only F 0.56–0.59 (chamfer 0.008–0.038 R, 10–50× L4).
- Per-level medians stay put from 23 to 27 artifacts (L4 0.984, L3 0.965); L5 failures 8 / 27.

## Round 5 — rank 27 (1 artifact × 5 levels) — 2026-11-02

`run_batch.py --count 28 --clean` in-session 04:02 → 04:23 (21 min), `batch done: 5 ok, 0 failed`. Started because round 4 ended before 04:30 (team rule). All 28: `experiments/results/round5_all.csv`, `round5_summary.csv`, `experiments/plots/round5_summary.png`.

| Level | Images | Registered | Total time | Cloud F@0.002 R |
|---|---|---|---|---|
| L1 | 362 | 153 | 11.8 min | 0.070 |
| L2 | 182 | 56 | 4.6 min | 0.082 |
| L3 | 92 | 26 | 1.9 min | 0.050 |
| L4 | 47 | 12 | 1.1 min | 0.632 |
| L5 | 26 | 6 | 0.1 min | 0.000 (no dense cloud) |

**Measured:**
- `Ark_HM_1260C_HI` fails at every level: SfM registers only 25–42 % of the images (L1–L4), so the clouds cover a fraction of the object. Same pattern as its sibling `Ark_HM_1260B_HI` (batch test / round 1); together with `Ark_HM_38_HI` the third artifact that fails at all levels **(hypothesis: small, plain, low-texture surface — not checked)**. Not exhibited (L3 mesh F 0.045).
- Per level across 28 (`round5_summary.csv`): median cloud F L1 0.887, L2 0.927, L3 0.965, **L4 0.984**, L5 0.622; cloud F < 0.5: 3 / 3 / 3 / 4 / 9 of 28.

## Round 6 — ranks 28–34 (7 artifacts × 5 levels) — 2026-11-03

Same frozen config, `run_batch.py --count 35 --clean` in-session 2026-11-02 23:07 → 2026-11-03 07:29 (8.4 h; estimate was ~15 h), `batch done: 35 ok, 0 failed`, no charger removal or sleep. The team called this "round 5"; files use `round6` because `round5_*` already holds `Ark_HM_1260C_HI`. All 35: `experiments/results/round6_all.csv`, `round6_summary.csv`, `experiments/plots/round6_summary.png`.

| Artifact | L1 | L2 | L3 | L4 | L5 | L1 time | Best |
|---|---|---|---|---|---|---|---|
| `Ark_HM_557_HI` | 0.870 | 0.907 | 0.956 | 0.969 (43/47) | 0.000 (10/26) | 30 min | L4 |
| `Ark_HM_792_hi` | 0.677 | 0.658 | 0.479 | 0.598 (29/47) | 0.000 (11/26) | 38 min | L1 |
| `Ark_HM_703_HI` | 0.773 (241/362) | 0.798 (121/182) | 0.840 (61/92) | 0.795 (29/47) | 0.000 (12/26) | 27 min | L3 |
| `Ark_HM_498_HI` | 0.916 | 0.955 | 0.983 | 0.994 | 0.000 (16/26) | 48 min | L4 |
| `Ark_HM_596_Hi` | 0.900 | 0.934 | 0.975 | 0.987 | 0.000 (12/26) | 65 min | L4 |
| `Ark_HM_259_HI` | 0.879 | 0.908 | 0.958 | 0.985 | 0.627 (14/26) | 58 min | L4 |
| `Ark_HM_611_HI` | 0.876 | 0.910 | 0.951 | 0.969 (45/47) | 0.000 (11/26) | 28 min | L4 |

Per level across all 35 artifacts (`round6_summary.csv`):

| Level | Images | Median total time (max) | Median peak RAM | Median cloud F (min) | Median mesh F | Cloud F < 0.5 |
|---|---|---|---|---|---|---|
| L1 | 362 | 54.5 min (150.1) | 4.4 GB | 0.883 (0.062) | 0.983 | 3 / 35 |
| L2 | 182 | 22.5 min (55.4) | 2.3 GB | 0.920 (0.051) | 0.981 | 3 / 35 |
| L3 | 92 | 9.7 min (18.1) | 2.0 GB | 0.964 (0.050) | 0.986 | 4 / 35 |
| L4 | 47 | 3.8 min (8.1) | 2.0 GB | **0.984** (0.000) | 0.984 | 4 / 35 |
| L5 | 26 | 1.0 min (4.2) | 2.0 GB | 0.578 (0.000) | 0.570 | 15 / 35 |

**Measured:**
- L5 yields no dense cloud on 6 / 7 artifacts this round (10–16 / 26 images in the model used; 259 is the exception at 0.627, still partial). Across 35, L5 failures rose from 9 / 28 to 15 / 35. No config or code change between rounds. These seven have texture scores of 16–29 (`artifact_order.json`), and low-texture artifacts also failed at L5 earlier; whether texture is the cause is **(hypothesis, not tested)**.
- `Ark_HM_703_HI`: SfM splits into two models at every level L1–L4 (241 + 121 at L1, 121 + 61 at L2, 61 + 31 at L3), only the larger is densified → F 0.77–0.84. Same split seen in earlier rounds.
- `Ark_HM_792_hi`: every image registers at L1–L3, but F is low and falls with fewer images (0.677 → 0.479 at L3). Cause not investigated.
- 498, 596, 259 are clean L1–L4 and best at L4; 557 and 611 are best at L4 with a few images lost there (43/47, 45/47).

## Museum models — round-6 exhibits — 2026-11-03

`export_glb.py --artifacts <the 7>` → exit 0; not exhibited: `Ark_HM_792_hi` (L3 mesh F 0.459), `Ark_HM_703_HI` (0.842). Museum now **25 exhibits, 75 MB**.

| Artifact | Full mesh | Full GLB | Museum GLB | Surface F@0.002 full → museum | Chamfer museum |
|---|---|---|---|---|---|
| `Ark_HM_557_HI` | 286,702 tri | 10.4 MB | 2.8 MB | 0.953 → 0.953 | 0.00143 R |
| `Ark_HM_498_HI` | 507,176 tri | 18.4 MB | 2.9 MB | 0.997 → 0.997 | 0.00065 R |
| `Ark_HM_596_Hi` | 458,351 tri | 16.3 MB | 2.9 MB | 0.986 → 0.986 | 0.00085 R |
| `Ark_HM_259_HI` | 413,680 tri | 15.0 MB | 2.9 MB | 0.982 → 0.982 | 0.00081 R |
| `Ark_HM_611_HI` | 238,631 tri | 8.8 MB | 2.8 MB | 0.959 → 0.959 | 0.00159 R |

Checked all five in the 3D hall (browser pane): textured, upright, placards No. 21–25, no console errors. Layout with 25: South 1–5, Rotunda 6–13, East 14–17, North 18–21, West 22–25. `Ark_HM_611_HI` shows a catalogue sticker on its surface (it is in the source images).

## Museum models — round-4 exhibits — 2026-11-02

`export_glb.py --artifacts Ark_HM_192_HI Ark_HM_711_HI Ark_HM_1286_HI Ark_HM_1299_Hi` → exit 0; all four pass the rule (L3 mesh-vertex F ≥ 0.95). Museum now **20 exhibits, 60 MB**.

| Artifact | Full mesh | Full GLB | Museum GLB | Surface F@0.002 full → museum | Chamfer museum |
|---|---|---|---|---|---|
| `Ark_HM_192_HI` | 500,880 tri | 17.6 MB | 2.8 MB | 0.983 → 0.983 | 0.00113 R |
| `Ark_HM_711_HI` | 509,047 tri | 18.2 MB | 2.9 MB | 0.985 → 0.985 | 0.00086 R |
| `Ark_HM_1286_HI` | 476,704 tri | 17.4 MB | 2.9 MB | 0.984 → 0.984 | 0.00107 R |
| `Ark_HM_1299_Hi` | 302,374 tri | 12.3 MB | 2.9 MB | 0.924 → 0.924 | 0.00236 R |

- `Ark_HM_1299_Hi` passes the exhibit rule (which uses the evaluation's mesh-vertex F) but its surface-sample F (0.924) is the lowest of any exhibit so far. It is a joined double pot; the narrow gap between the two bodies is a likely cause **(hypothesis)**.
- Checked all four in the 3D hall (browser pane): textured, upright, placards No. 17–20.

## Round 7, part 1 — rank 35 (`Ark_HM_658_HI`) — 2026-11-03

Same frozen config, `run_batch.py --count 40 --clean` from 08:43; stopped by the team at 12:38, so the round is incomplete. Finished in part 2 below. The medians in this section are for the first 36 only.

| Level | Images | Registered | Total time | Peak RAM | Cloud F@0.002 R | Chamfer |
|---|---|---|---|---|---|---|
| L1 | 362 | 362 | 70.8 min | 3.0 GB | 0.937 | 0.00073 R |
| L2 | 182 | 182 | 22.4 min | 2.3 GB | 0.963 | 0.00067 R |
| L3 | 92 | 92 | 9.7 min | 2.0 GB | 0.987 | 0.00059 R |
| L4 | 47 | 47 | 4.7 min | 2.0 GB | **0.997** | 0.00060 R |
| L5 | 26 | 26 | 1.9 min | 2.0 GB | 0.952 | 0.00094 R |

**Measured:** clean at every level and best at L4. One of the few artifacts that stays above 0.95 at L5. Medians across 36: L1 0.883, L2 0.924, L3 0.965, **L4 0.984**, L5 0.583; cloud F < 0.5 on 3 / 3 / 4 / 4 / 15 of 36.

Museum model (L3): 418,355 → 99,999 triangles, 15.7 → 2.9 MB, surface F 0.994 → 0.994, chamfer 0.00064 R. Checked in the 3D hall as No. 26: textured, upright, no console errors. Museum now **26 exhibits, 77 MB**.

## Round 7, part 2 — ranks 36–39, main set complete — 2026-11-04

Same frozen config, `run_batch.py --count 40 --clean`, 00:51–06:14 (5 h 23 min), 16 / 16 runs ok. `Ark_HM_393_HI` L2–L5 ran on 2026-11-03, its L1 was redone here. All 40: `experiments/results/round7_all.csv`, `round7_summary.csv`, `experiments/plots/round7_summary.png`.

| Artifact | Level | Images | Registered | Total time | Peak RAM | Cloud F@0.002 R | Chamfer |
|---|---|---|---|---|---|---|---|
| `Ark_HM_393_HI` | L1 | 362 | 362 | 71.0 min | 4.6 GB | 0.881 | 0.00103 R |
| | L2 | 182 | 182 | 34.0 min | 2.3 GB | 0.924 | 0.00091 R |
| | L3 | 92 | 92 | 13.8 min | 2.0 GB | 0.967 | 0.00078 R |
| | L4 | 47 | 47 | 8.1 min | 2.0 GB | **0.985** | 0.00076 R |
| | L5 | 26 | 26 | 1.7 min | 2.0 GB | 0.876 | 0.00138 R |
| `Ark_HM_1292_HI` | L1 | 362 | 362 | 35.2 min | 4.4 GB | 0.853 | 0.00135 R |
| | L2 | 182 | 182 | 14.9 min | 2.2 GB | 0.907 | 0.00108 R |
| | L3 | 92 | 92 | 6.6 min | 2.0 GB | 0.952 | 0.00092 R |
| | L4 | 47 | 47 | 2.2 min | 2.0 GB | **0.979** | 0.00084 R |
| | L5 | 26 | 13 | 0.1 min | 2.0 GB | 0.000 (no dense cloud) | – |
| `Ark_HM_1288_HI` | L1 | 362 | 362 | 57.6 min | 4.6 GB | 0.944 | 0.00065 R |
| | L2 | 182 | 182 | 23.6 min | 2.4 GB | 0.972 | 0.00057 R |
| | L3 | 92 | 92 | 11.0 min | 2.0 GB | 0.990 | 0.00055 R |
| | L4 | 47 | 47 | 6.4 min | 2.0 GB | **0.997** | 0.00056 R |
| | L5 | 26 | 26 | 2.7 min | 2.0 GB | 0.993 | 0.00069 R |
| `Ark_HM_209_HI` | L1 | 362 | 362 | 48.4 min | 4.6 GB | 0.903 | 0.00096 R |
| | L2 | 182 | 182 | 20.7 min | 2.3 GB | 0.937 | 0.00086 R |
| | L3 | 92 | 92 | 9.6 min | 2.0 GB | 0.968 | 0.00081 R |
| | L4 | 47 | 47 | 4.2 min | 2.0 GB | **0.991** | 0.00071 R |
| | L5 | 26 | 26 | 1.0 min | 2.0 GB | 0.558 | 0.01853 R |

All four are best at L4. In `Ark_HM_1292_HI` L5, SfM split the images into models of 9 and 13 and no dense cloud was produced (`preview_cloud.py` raised FileNotFoundError; the batch carried on as designed).

**Measured, all 40 artifacts:**

| Level | Images | Median total time | Median peak RAM | Median cloud F@0.002 R | Median mesh F@0.002 R | Cloud F < 0.5 |
|---|---|---|---|---|---|---|
| L1 | 362 | 55.4 min | 4.4 GB | 0.883 | 0.984 | 3 / 40 |
| L2 | 182 | 22.4 min | 2.3 GB | 0.925 | 0.982 | 3 / 40 |
| L3 | 92 | 9.7 min | 2.0 GB | 0.965 | 0.989 | 4 / 40 |
| L4 | 47 | 3.9 min | 2.0 GB | **0.984** | 0.988 | 4 / 40 |
| L5 | 26 | 1.0 min | 2.0 GB | 0.583 | 0.580 | 16 / 40 |

Museum models (L3), full → about 100,000 triangles:

| No. | Artifact | Full triangles | Size | Surface F (full → museum) | Chamfer |
|---|---|---|---|---|---|
| 27 | `Ark_HM_393_HI` | 421,764 | 15.5 → 2.9 MB | 0.985 → 0.984 | 0.00078 R |
| 28 | `Ark_HM_1292_HI` | 271,806 | 10.0 → 2.9 MB | 0.979 → 0.979 | 0.00084 R |
| 29 | `Ark_HM_1288_HI` | 519,552 | 19.0 → 2.9 MB | 0.991 → 0.991 | 0.00073 R |
| 30 | `Ark_HM_209_HI` | 463,004 | 17.8 → 2.9 MB | 0.965 → 0.965 | 0.00176 R |

Museum now **30 of the 40 main-set artifacts, 88.5 MB**. Not exhibited (L3 mesh F < 0.95): 1260B, 795, 341, 31, 797, 38, BEY_1415, 1260C, 792, 703. Checked in the browser pane: 30 / 30 loaded in 2.7 s, page ready 1.2 s, no console errors, Nos. 27–30 textured and upright. Seen from straight above, No. 27 shows a small gap inside the bottom of the pot beside its white label, where the plinth colour shows through (to verify in a normal browser).

## Quality against cost — all 40 main-set artifacts — 2026-11-05

`python scripts/analyze_tradeoff.py`, from the stored runs, nothing reconstructed. Files: `experiments/results/tradeoff_levels.csv`, `tradeoff_sufficient.csv`, `tradeoff_policies.csv`, `tradeoff_paired.csv`; plots `experiments/plots/tradeoff_quality_vs_time.png`, `tradeoff_cost_by_level.png`, `tradeoff_sufficient.png`. Rules in [[08-Decisions]]. Mesh F is measured on mesh vertices.

Median cost, with the median share of the same artifact's L1 cost in brackets:

| Level | Images | Time | Peak RAM | Input | Dense cloud | Textured mesh |
|---|---|---|---|---|---|---|
| L1 | 362 | 55.4 min | 4,437 MB | 103.7 MB | 260.2 MB | 23.9 MB |
| L2 | 182 | 22.4 min (40%) | 2,316 MB (51%) | 52.2 MB (50%) | 147.2 MB (56%) | 22.9 MB (95%) |
| L3 | 92 | 9.7 min (17%) | 2,024 MB (46%) | 26.4 MB (26%) | 73.5 MB (28%) | 21.4 MB (88%) |
| L4 | 47 | 3.9 min (6.3%) | 2,021 MB (46%) | 13.6 MB (13%) | 28.2 MB (12%) | 18.1 MB (76%) |
| L5 | 26 | 1.0 min (1.7%) | 2,015 MB (45%) | 7.5 MB (7.2%) | 5.8 MB (2.5%) | 5.4 MB (27%) |

L5's costs are low partly because 14 of its 40 runs made no dense cloud and skipped those stages.

Quality and reliability:

| Level | Median mesh F | Median cloud F | Cloud precision | Cloud recall | Cloud F at 0.005 R / 0.01 R | Mesh F >= 0.95 | Cloud F >= 0.95 | Mesh F < 0.5 | No dense cloud | Hours for all 40 |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 0.984 | 0.883 | 0.795 | 0.996 | 0.968 / 0.998 | 31 | 0 | 3 | 0 | 40.1 |
| L2 | 0.982 | 0.925 | 0.868 | 0.994 | 0.981 / 0.999 | 31 | 7 | 3 | 0 | 15.5 |
| L3 | 0.989 | 0.965 | 0.938 | 0.994 | 0.994 / 1.000 | 30 | 29 | 4 | 0 | 6.3 |
| L4 | 0.988 | 0.984 | 0.981 | 0.988 | 0.998 / 1.000 | 28 | 28 | 4 | 1 | 2.7 |
| L5 | 0.580 | 0.583 | 0.996 | 0.413 | 0.662 / 0.687 | 5 | 5 | 16 | 14 | 0.8 |

Precision and the distances cover only runs that made a dense cloud.

Cheapest level reaching mesh F >= 0.95, per artifact: L5 5, L4 23, L3 2, L2 1, L1 0, never 9. In hindsight that would take 2.6 h for the 31 that can reach it, but choosing it needs reference geometry, which a real capture does not have. The 30 artifacts sufficient at L3 or below are the 30 exhibits, as they should be, since the exhibit rule is the same test. The threshold changes little: at mesh F 0.90 L4 is cheapest for 22, at 0.98 for 20.

Paired differences on the same 40 artifacts (median, bootstrap 95% interval, Wilcoxon p with Holm's correction):

| Compare | Mesh F | p | Cloud F | p |
|---|---|---|---|---|
| L2 − L1 | 0.0000 (−0.0020, 0.0011) | 0.75 | +0.0342 (0.0297, 0.0371) | < 0.001 |
| L3 − L1 | +0.0028 (0.0007, 0.0042) | 0.039 | +0.0693 (0.0604, 0.0752) | < 0.001 |
| L4 − L1 | +0.0011 (−0.0061, 0.0043) | 0.75 | +0.0806 (0.0645, 0.0887) | 0.028 |
| L5 − L1 | −0.3245 (−0.4396, −0.1969) | < 0.001 | −0.2331 (−0.3572, −0.1248) | < 0.001 |
| L4 − L3 | −0.0002 (−0.0045, 0.0006) | 0.50 | +0.0131 (0.0074, 0.0185) | 0.087 |

Across L1–L4 time grows as about images^1.34 (median per artifact), so doubling the images takes about 2.5 times as long.

**Measured, for this set under this setup:**

- **H1 supported at the cost end, with a limit:** time, input and cloud size fall steadily with fewer images, but peak RAM stops falling below L3 (about 2 GB) and mesh size falls little until L5. Quality collapses only at L5: recall falls to 0.41 and 14 runs make no cloud.
- **More images did not improve quality:** from L4 to L1 cloud precision falls from 0.981 to 0.795 at the tight 0.002 R tolerance, with recall about level. Why is not established (hypothesis: extra views add slightly misplaced points). This is an effect at fine tolerance: at 0.01 R L1 to L4 all score 0.998 or more. The mesh is not affected, and no level from L1 to L4 is meaningfully better on mesh F.
- **H2 supported:** L3 uses 25% of L1's images and 17% of its time, and L4 13% and 6.3%, with median mesh F within 0.003 of L1 and interval limits within 0.0061. No equivalence margin was set in advance, so this is stated as measured differences, not as a formal equivalence test.
- **The real trade-off is reliability against time:** L4 costs 2.7 h for all 40 and 28 reach mesh F 0.95; L3 costs 6.3 h for 30; L2 15.5 h for 31; L1 40.1 h for 31. L4 has the better median, but L3 is not significantly worse and loses fewer artifacts. L4 is the most economical choice, L3 the safer one, and nothing past L2 gained anything here.
- **More photos do not rescue the hardest objects:** 9 of 40 never reach mesh F 0.95 at any level, including L1.

**Limits:** synthetic CHSD renders, one pipeline, a laptop CPU, one set of 40 artifacts chosen as never cut off in the sample views, and an evaluation method (Option A) the team has yet to confirm. Time and memory are single runs per level, not repeated. Visual and texture quality have no measurement here, so RQ1 is answered for geometry only. Final GLB size exists only for the L3 exhibits. Point density is not computed, because the evaluation's point counts are after downsampling; dense cloud size stands in for it.

## Visual fidelity — method pilot only — 2026-11-05

`scripts/evaluate_visual.py`, `src/heritage3d/visual.py`. Each model is rendered from 12 held-out views (azimuths 7, 97, 187, 277° × elevations −45, 0, 45°, used by no level) with the ideal CHSD cameras and compared with the CHSD photo, over the union of the two silhouettes, so missing parts count against the model. Files: `experiments/results/visual/`, comparison images in `experiments/plots/visual/`.

| Artifact | Model | Faces | PSNR (dB) | SSIM | Silhouette IoU | PSNR where both have the object (dB) | Time |
|---|---|---|---|---|---|---|---|
| `Ark_HM_658_HI` | L1 | 448,476 | 29.51 | 0.943 | 0.997 | 32.94 | 814 s |
| `Ark_HM_658_HI` | L4 | 400,085 | 29.01 | 0.949 | 0.997 | 32.64 | 82 s |
| `Ark_HM_658_HI` | L5 | 289,288 | 27.74 | 0.926 | 0.996 | 31.24 | 62 s |
| `Ark_HM_658_HI` | Museum GLB (from L3) | 99,999 | 29.72 | 0.943 | 0.998 | 32.68 | 41 s |
| `Ark_HM_1260B_HI` | L5, run that failed | 452 | 8.03 | 0.188 | 0.352 | 16.69 | 12 s |

**Checked:** in the comparison images for `Ark_HM_658_HI` L4 and the museum GLB, the renders line up with the photos, and differences sit mainly at the outlines. The failed run scores far lower, as it should. **This only shows the method works.** Two artifacts say nothing about RQ1 or RQ3: L2, L3 and the other 38 are not measured. L3 itself has not been re-textured and measured, so full-against-museum at L3 is not available yet.

**Found while building it:** the batch runs textured with OpenMVS's default seam leveling, which damages these renders (`export_glb.py`), so this measurement re-textures with it off. The stored `scene_dense_texture*` files and the `textured_mesh_mb` cost column come from the leveled versions. Geometry and F-scores do not use the texture.

**Full run:** done, next section.

## Visual fidelity — all levels, cut-off set and museum models — 2026-11-06

Ran 2026-11-05 21:41 to 2026-11-06 06:15 (8.8 h, 263 measurements, no errors; log `experiments/logs/visual_full.log`): 40 main-set artifacts × 5 levels, the 19 cut-off artifacts at L3, the 44 museum GLBs. Summary by `python scripts/analyze_visual.py`: `experiments/results/visual_levels.csv`, `visual_paired.csv`, `visual_all.csv`; plots `experiments/plots/visual_by_level.png`, `visual_museum.png`. Method as in the pilot above.

Main set, medians over 40 artifacts (each artifact's value is its mean over the 12 held-out views):

| Level | PSNR (dB) | SSIM | Silhouette IoU | PSNR where both show the object (dB) | IoU below 0.9 | Empty render |
|---|---|---|---|---|---|---|
| L1 | 29.55 | 0.918 | 0.995 | 32.41 | 2 | 0 |
| L2 | 29.03 | 0.919 | 0.995 | 32.42 | 2 | 0 |
| L3 | 29.25 | 0.924 | 0.995 | 32.42 | 2 | 0 |
| L4 | 29.20 | 0.922 | 0.995 | 32.49 | 6 | 1 |
| L5 | 14.39 | 0.595 | 0.791 | 25.61 | 25 | 4 |

Paired differences on the same 40 artifacts (median, bootstrap 95% interval, Wilcoxon p with Holm's correction):

| Compare | PSNR (dB) | p | SSIM | p |
|---|---|---|---|---|
| L2 − L1 | −0.34 (−0.58, −0.16) | < 0.001 | −0.0006 (−0.0036, 0.0010) | 0.92 |
| L3 − L1 | −0.41 (−0.75, 0.04) | 0.065 | +0.0035 (−0.0001, 0.0059) | 0.49 |
| L4 − L1 | −0.47 (−1.57, 0.07) | 0.065 | +0.0048 (−0.0066, 0.0087) | 1.0 |
| L5 − L1 | −12.72 (−16.27, −8.72) | < 0.001 | −0.283 (−0.438, −0.194) | < 0.001 |
| L4 − L3 | +0.06 (−0.32, 0.40) | 0.69 | +0.0019 (−0.0036, 0.0042) | 1.0 |
| Museum GLB − full L3 (44 exhibits) | −0.20 (−0.24, −0.16) | < 0.001 | −0.0047 (−0.0051, −0.0043) | < 0.001 |

Over the 200 main-set models, the visual measures rank models much as geometry does: Spearman ρ 0.80 (PSNR) and 0.87 (SSIM) against mesh F, 0.75 and 0.83 against cloud F. The weakest renders from L1 to L4 are the artifacts that fail on geometry (`Ark_HM_1260B_HI`, `Ark_HM_1260C_HI`, `Ark_HM_31_HI`, and `Ark_HM_38_HI` at L4 with no model). Cut-off set at L3: median PSNR 28.71 dB, SSIM 0.926 over 19; the 14 exhibited ones 30.32 dB and 0.929, against 29.88 dB and 0.930 for the 30 exhibited main-set artifacts at L3.

**Measured, for this set under this setup:**

- **RQ1 visual part:** appearance follows the same pattern as geometry. L2 to L4 look as good as L1 to within half a decibel of PSNR, with no significant SSIM difference and the same silhouettes; L5 collapses (median 14.4 dB, silhouette IoU 0.79, 4 empty renders). L1 is slightly ahead on PSNR, by 0.34 to 0.47 dB in median, significant only against L2 after correction. Why is not established: texture size could play a part, since TextureMesh picks the atlas size itself (stored textures seen at 2048 and 4096 px, at L3 as well as L1), but the re-textured sizes were not recorded (hypothesis, not tested). SSIM, which weighs structure rather than exact colour, shows no such lead.
- **H2 holds visually too:** L3 and L4 match L1 within these margins, at 17% and 6.3% of its time.
- **RQ3:** the museum models lose 0.20 dB PSNR and 0.005 SSIM against the full L3 model, consistently on 43 and 44 of 44 exhibits, at 19% of the file size. That loss is smaller than the gap between L1 and L3, and about a sixty-fifth of L5's (12.7 dB). Rendering cost and download time: next section.
- **The cut-off set looks as good as the main set** at L3 on these measures, with the same framing caveat as its F-scores.

**Limits:** the renders are unlit, like the museum models, and the CHSD photos are renders too, so these measure agreement with the dataset's own images, not with a real object's look. PSNR and SSIM are pixel measures; no perceptual or user study was done (out of scope). The textures here are the re-textured ones with seam leveling off, not the batch's stored ones. Texture size is chosen by TextureMesh per model and was not recorded, so it is part of what each model delivers here.

## RQ3 — museum models against full models in the browser — 2026-11-06

Full L3 models of the 44 exhibits exported outside the repo (`scripts/export_full_glb.py`, `D:\heritage3d-data\full_glb`, 670 MB, done 07:30, log `experiments/logs/export_full_glb.log`). Measured with `bench/` served by `scripts/bench_server.py`, in the app's browser pane, visible, on this laptop (Intel Iris Xe, Chrome 152 through ANGLE/Direct3D 11): `experiments/results/rq3/bench_local.json` (localhost, 3 runs per model, median) and `bench_20mbps.json` (each model sent at 20 Mbit/s, 1 run). Summary by `python scripts/analyze_rq3.py`: `experiments/results/rq3_models.csv`, `rq3_summary.csv`, plot `experiments/plots/rq3_costs.png`. Drawing is timed offscreen at 1280 × 720 without anti-aliasing, 30 draws per GPU read-back: timing each draw on its own was tied to the 60 Hz display (every model read 16.6 ms), so that method was dropped.

Medians over 44 exhibits:

| Measure | Museum model | Full model | Museum as share of full |
|---|---|---|---|
| File size | 2.9 MB | 15.7 MB | 19% |
| Triangles | 100,000 | 424,073 | 24% |
| Decoding in the browser | 19.8 ms | 66.8 ms | 31% |
| GPU upload and first frame | 29.9 ms | 34.7 ms | 85% |
| Drawing one frame | 0.56 ms | 1.19 ms | 43% |
| Download at 20 Mbit/s, measured | 1.53 s | 6.62 s | 23% |
| GPU memory, estimated (geometry + RGBA textures with mipmaps) | 2.5 + 21.3 MB | 10.9 + 21.3 MB | |

All 44 together: 129.6 MB against 669 MB; download at 20 Mbit/s measured 68 s against 281 s. Calculated from size at 10 / 25 / 50 / 100 Mbit/s: museum 109 / 43 / 22 / 11 s, full 561 / 225 / 112 / 56 s; one median museum model 2.5 / 1.0 / 0.5 / 0.25 s. The measured 20 Mbit/s times were a median 1.10 × the calculated ones (transfer overhead). Estimated GPU memory for the whole hall: about 1.0 GB museum, 2.0 GB full.

Over all 44 exhibits the museum model's surface F@0.002 R differs from the full model's by at most 0.0003 (median −0.00002) and its Chamfer by at most 0.3% (from `experiments/results/museum/*_glb.json`, checked 2026-11-06).

**Measured, for this laptop:**

- **RQ3 answered:** the museum model downloads in about a quarter of the time, decodes in a third, draws in under half and keeps the same texture, at a visual cost of 0.20 dB PSNR and 0.005 SSIM (previous section) and no measurable geometric cost ([[07-Results]] museum sections). **H3 supported.**
- **Texture dominates GPU memory:** both kinds mostly carry a 2048 px texture (21.3 MB on the GPU), so decimation cuts geometry memory by 77% but total GPU memory far less. 10 full models had 4096 px textures, and those are the slow first frames (110–153 ms); one museum model has 1024 px.
- **Download is the real cost of the hall:** about 109 s for the whole collection at 10 Mbit/s, against 9 min for full models. The hall loads the nearest exhibits first, so the first ones appear after a few seconds (calculated, not measured on a hosted site).

**Limits:** one laptop and one browser; local network with a simulated bandwidth and no latency; no hosting yet. GPU memory is calculated from the decoded sizes, not read from the driver. The hall itself was not re-measured full-screen.

## Cut-off trial — `Ark_HM_640_HI` at L3 — 2026-11-04

Outside the 40-artifact main set, same frozen config. Cut off by the frame in 30% of the 20 sample views, the most of the 19 artifacts cut off in at most 30%.

| Images | Registered | Total time | Peak RAM | Cloud F@0.002 R | Mesh-vertex F@0.002 R | Cloud chamfer |
|---|---|---|---|---|---|---|
| 92 | 92 | 8.5 min | 2.0 GB | 0.952 | 0.970 | 0.00091 R |

**Measured:** one model, all images registered, above the museum rule (mesh F ≥ 0.95). The preview looks complete by eye. One artifact at one level only. The reference comes from depth maps with the same framing, so F may not fully penalise parts outside the frame (hypothesis). Not exported to the museum.

## Cut-off set at L3 — 19 artifacts — 2026-11-05

Outside the 40-artifact main set, same frozen config, L3 (92 images), order in `configs/artifact_order_cutoff.json`. Batch 2026-11-04 22:52 to 2026-11-05 01:52 (18 runs, 0 failed), plus the trial above. Files: `experiments/results/cutoff_l3_all.csv`, `cutoff_l3_summary.csv`, `experiments/plots/cutoff_l3_summary.png`.

| Artifact | Cut-off views | Images in dense model | Total time | Cloud F@0.002 R | Mesh F@0.002 R | Exhibit rule (≥ 0.95) |
|---|---|---|---|---|---|---|
| `Ark_HM_388_HI` | 5% | 92 | 11.8 min | 0.957 | 0.972 | Pass |
| `Ark_HM_724_HI` | 5% | 92 | 10.9 min | 0.960 | 0.982 | Pass |
| `Ark_HM_758_HI` | 5% | 92 | 12.1 min | 0.950 | 0.974 | Pass |
| `Ark_HM_1247_HI` | 10% | 42 of 92 (models 42 + 38) | 2.2 min | 0.657 | 0.652 | **Fail** |
| `Ark_HM_1282_HI` | 10% | 92 | 9.8 min | 0.968 | 0.992 | Pass |
| `Ark_HM_173_HI` | 10% | 92 | 9.2 min | 0.953 | 0.990 | Pass |
| `Ark_HM_217_HI` | 10% | 92 | 9.0 min | 0.928 | 0.945 | **Fail** |
| `Ark_HM_501_HI` | 10% | 55 of 92 (models 55 + 31) | 2.7 min | 0.571 | 0.552 | **Fail** |
| `Ark_HM_539_HI` | 10% | 92 | 9.3 min | 0.945 | 0.990 | Pass |
| `Ark_HM_706_HI` | 10% | 92 | 9.0 min | 0.953 | 0.989 | Pass |
| `SV_4337_HI` | 10% | 92 | 6.8 min | 0.969 | 0.994 | Pass |
| `Ark_HM_110_HI` | 15% | 92 | 4.6 min | 0.955 | 0.992 | Pass |
| `Ark_HM_688_HI` | 15% | 92 | 12.8 min | 0.977 | 0.993 | Pass |
| `Ark_HM_358_HI` | 20% | 92 | 12.2 min | 0.958 | 0.986 | Pass |
| `pipe1_HI` | 20% | 59 of 92 (models 59 + 31) | 2.9 min | 0.921 | 0.929 | **Fail** |
| `shell_bead_HI` | 20% | 90 of 92 | 3.6 min | 0.878 | 0.899 | **Fail** |
| `Ark_HM_791_HI` | 25% | 92 | 11.9 min | 0.979 | 0.993 | Pass |
| `Ark_HM_XXb_HI` | 25% | 92 | 8.8 min | 0.983 | 0.997 | Pass |
| `Ark_HM_640_HI` | 30% | 92 | 8.5 min | 0.952 | 0.970 | Pass |

**Measured:** 14 of 19 pass the rule. The five failures do not track the cut-off share: three split into two SfM models, and the failures sit at 10–20% while everything at 25–30% passes. Previews checked by eye. The hole in `Ark_HM_388_HI` and the broken rim of `Ark_HM_758_HI` are in the source photos, not reconstruction damage. The same caveat as the trial applies: the reference shares the framing, so F may not fully penalise parts outside the frame (hypothesis). L3 only, so no quality-vs-level comparison for this set. The 14 are now in the museum, on the upper floor (next section).

## Museum upper floor — 44 exhibits — 2026-11-05

The 14 passing cut-off artifacts exported at L3 (`export_glb.py`, run 2026-11-05), numbered 31–44. Museum models: 2.81–3.09 MB, about 100k triangles, surface F@0.002 R 0.958–0.998. The five failures were skipped by the exporter's own rule. Museum total: 44 exhibits, 129.6 MB.

Measured in the app's browser pane on this laptop, pane visible, 746 × 630 px, pixel ratio 1.25:

| View | Frame rate | Triangles drawn | Draw calls |
|---|---|---|---|
| Upper floor, looking along a wing | 60 fps | 0.74 M | 23 |
| Top of the stairs, looking down | 60 fps | 3.05 M | 89 |
| Foot of the stairs, looking up | 60 fps | 1.44 M | 38 |
| Rotunda | 60 fps | 2.35 M | 64 |
| South lobby, looking in | 60 fps | 4.25 M | 108 |

Hall ready in 1.54 s and all 44 models loaded in 4.82 s, from localhost with files already in the browser cache; **not** a real download time. With the pane hidden the page read about 20 fps in every view whatever it drew, so that number is the hidden pane's limit, not a measurement. A full-screen window has not been measured.

Checked: a simulated walk over `planHall(30, 14)` from the entrance up the stairs to both ends of the upper gallery (never stuck, height changes smoothly) and five wall tests (all blocked); live in the pane, the W key climbs the stairs, third person follows on the steps, the close-up on No. 31 opens at the right height with its panel, list view shows 44. Not checked: walking with real pointer lock in a normal browser.

## Museum building seen through the gate — rendering cost — 2026-11-05

The gate scene now shows the museum's exterior at the end of the drive (`museum/hall/exterior.js`). Measured in the app's browser pane, visible, 746 × 630 px: 60 fps from the start spot (0.31 M triangles, 51 draw calls), close to the gate and from along the street. A full-screen window has not been measured.

Later the same day the gates were opened and the drive made walkable, with the arrow moved to the museum's doors. Triangles drawn are unchanged (0.31 M), but the frame rate was **not** re-measured, because the browser pane was hidden for that test (it dropped to about 5 fps). Start spot to doors is about 63 m: about 29 s walking and 14 s with Shift, calculated from the walking speeds, not timed.

## Museum gate scene — rendering cost — 2026-11-03

Browser pane, 800×675, pixel ratio 1.25, batch running at the same time: first gate-only version 60 fps, 67,368 triangles. **With the street: 60 fps, 43 draw calls, 246,406 triangles at the start point**; page ready 3.3 s, 25 exhibits loaded in 6.9 s (cached). Full-screen not measured. Page-ready time varies with the batch: 3.0–3.3 s in most loads, once 17 s while a dense step was using the CPU, 1.4 s with no batch running.

## Museum hall — rendering cost on the team laptop — 2026-11-01

Measured in the Claude desktop app's browser pane (Chromium) on the HP Envy x360 (Intel Iris Xe), pane 800 × 675 px, pixel ratio 1.25, display capped at 60 fps; models served from `localhost`. `?repeat=3` shows the 16 exhibits three times (stress test for a ~40–50-exhibit museum).

| Exhibits | Hall ready | All models loaded | View | Triangles drawn | Draw calls | fps |
|---|---|---|---|---|---|---|
| 16 | 0.9–1.0 s | 3.6 s | entrance, looking in | 1.43 M | 48 | 60 |
| 48 | 0.8 s | 7.9 s | entrance, looking in | 4.64 M | 113 | 59 |
| 48 | | | rotunda | 1.74 M | 51 | 60 |
| 48 | | | east gallery | 0.83 M | 25 | 60 |

- The building itself (merged by material) is a few draw calls; each exhibit is one draw call plus its placard.
- Not measured yet: full-screen at the laptop's native resolution, a normal browser window, or loading over the internet (to measure with the hosting decision). Frame rate at full screen may be lower (to verify).
