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
