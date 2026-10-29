# Methodology

## Pipeline

```
CHSD RGB images (one artifact)
  → subset generator (L1–L5, see [[05-Experiment-Plan]])
  → COLMAP (CPU): feature extraction → matching → SfM (camera poses + sparse points)
  → COLMAP image_undistorter → OpenMVS InterfaceCOLMAP
  → OpenMVS (CPU): DensifyPointCloud → ReconstructMesh → (RefineMesh) → TextureMesh
  → evaluation: geometry vs CHSD depth reference + cost metrics
  → optimization: mesh decimation + texture resize/compression → GLB
  → web virtual museum
```

## Why COLMAP + OpenMVS

The laptop has no NVIDIA GPU. COLMAP's dense stereo (PatchMatch) requires CUDA; its SfM runs on CPU. OpenMVS provides CPU dense MVS, meshing and texturing and reads COLMAP output directly. The method is still SfM + MVS; only the MVS tool changes. (Decision 2026-10-25, [[08-Decisions]].)

## Controls (to avoid confounding)

- Same artifact, same image resolution, same tool versions and parameters at every level.
- Same matcher at every level (choice fixed after the pilot).
- Unoptimized reconstruction is kept as the evaluated output; optimization is a separate later step.
- RGB only as input.

## Evaluation against reference geometry (plan, depends on dataset findings)

A depth map gives per-pixel distance from one camera only. To build a 3D reference we need: depth encoding (units/scale), camera intrinsics, camera poses. COLMAP output has arbitrary scale/rotation/translation and must be aligned to the reference (similarity transform from camera centres, refined with ICP) before any distance metric is valid.

- **Option A (preferred if metadata allows):** back-project depth maps → fused reference point cloud → Chamfer, Hausdorff, RMSE, precision/recall/F-score at a declared threshold.
- **Option B (fallback):** render reconstruction depth at reference viewpoints → per-pixel depth error after scale alignment; coverage = fraction of valid pixels.
- **Option C:** original Hampson 3D models as ground truth, if obtainable.

### Implemented: Option A (2026-10-30, team to confirm)

The depth encoding, intrinsics and rig were decoded from the depth maps alone ([[03-Dataset-CHSD]]), so Option A is possible without using the reconstruction to build its own reference:

1. **Reference cloud** (`src/heritage3d/reference.py`): back-project every CHSD depth map of the artifact (all 1,800 views, every 2nd pixel) with the ideal rig, merge on a 0.002 R voxel grid. Cached at `<runs>/<artifact>/reference.npy`.
2. **Alignment** (`src/heritage3d/evaluate.py`): similarity transform (Umeyama) from the COLMAP camera centres to the known ideal camera centres. The residual is reported as a pose-accuracy metric. No ICP (camera alignment is already ≈ 0.0003 R; ICP would hide errors).
3. **Metrics** (`scripts/evaluate_run.py`): reconstruction voxel-downsampled to the same 0.002 R grid; nearest-neighbour distances both ways → accuracy, completeness, Chamfer (mean of both), RMSE, Hausdorff and 95th-percentile Hausdorff, precision/recall/F-score at τ = 0.002, 0.005, 0.01 R (declared before any level comparison). Evaluated on the dense cloud and on the mesh vertices.

Units: R = camera-to-centre distance (object sizes ≈ 0.3–0.8 R). Reference uses depth maps only — RGB-only input to reconstruction is unchanged.

## Optimization and museum

- Decimate mesh to target face counts; resize/compress textures; export GLB (glTF binary).
- Compare optimized vs unoptimized (geometric deviation, file size, load time).
- Museum: static web app with an interactive 3D viewer (rotate/zoom), artifact information, attribution and license notice.
