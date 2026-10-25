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

Choice to be made after [[03-Dataset-CHSD]] unknowns are answered.

## Optimization and museum

- Decimate mesh to target face counts; resize/compress textures; export GLB (glTF binary).
- Compare optimized vs unoptimized (geometric deviation, file size, load time).
- Museum: static web app with an interactive 3D viewer (rotate/zoom), artifact information, attribution and license notice.
