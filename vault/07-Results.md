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
