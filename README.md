# heritage3d

A cost-effective image-based 3D digitization framework for cultural heritage artifacts.

This project studies how input-image density affects 3D reconstruction quality, computation and storage, and turns an optimized reconstruction into an interactive artifact in a web-based virtual museum.

**Status:** pilot phase. First reconstruction (one artifact, 92 images) done; evaluation not built yet. See [`vault/00-Home.md`](vault/00-Home.md).

## Pipeline

```
CHSD RGB images → controlled image subsets (L1–L5)
  → COLMAP SfM (CPU) → OpenMVS dense MVS → mesh → texture
  → evaluation against CHSD depth (quality) + runtime/RAM/size (cost)
  → mesh/texture optimization → GLB → web virtual museum
```

## Repository layout

| Path | Contents |
|---|---|
| `vault/` | Obsidian vault: project memory, decisions, dataset facts, session log |
| `docs/literature/` | Literature review workbook |
| `configs/` | Experiment configuration (data paths, subset levels) |
| `src/heritage3d/` | Library code |
| `scripts/` | Command-line entry points |
| `tests/` | Unit tests (`python -m pytest tests`) |
| `experiments/` | Committed metrics (`results/`), logs and plots of real runs |

A `museum/` folder is added when the virtual museum is built.

## Environment check

```
python scripts/check_env.py --out D:\heritage3d-data\runs\environment.json
```
Prints COLMAP/OpenMVS versions and hardware; exits with an error if a tool is not on PATH.

## Subset levels

Uniform azimuth step on the −45°/0°/45° rings plus one top and one bottom view: L1 3° (362 images), L2 6° (182), L3 12° (92), L4 24° (47), L5 45° (26).

```
python scripts/create_subsets.py --artifact <name> --out D:\heritage3d-data\runs\<name> --check
```

## Dataset inspection

```
python scripts/inspect_dataset.py
```

Checks every CHSD artifact for missing files, image format, depth values, framing and pole views; writes `experiments/results/dataset_inspection.json`.

## Reconstruction

```
python scripts/run_pipeline.py --artifact <name> --level L3 --stages sparse
python scripts/run_pipeline.py --artifact <name> --level L3 --stages dense
```

Sparse: COLMAP feature extraction, matching, mapping (CPU). Dense: undistortion, then OpenMVS densify, mesh, texture. Settings come from `[pipeline]` in the config and are the same for every level. Each stage's wall time and peak memory go to `experiments/results/runs/<name>_<level>.json`, logs to `experiments/logs/`. Workspaces stay in `D:\heritage3d-data\runs`.

## Evaluation

```
python scripts/evaluate_run.py --artifact <name> --level L3
```

Builds a reference point cloud from the artifact's CHSD depth maps (decoded depth + known turntable cameras, never the reconstruction), aligns the reconstruction through its camera positions, and reports accuracy, completeness, Chamfer, Hausdorff and F-scores in units of the camera distance R. Output: `experiments/results/runs/<name>_<level>_eval.json`.

## Dataset

Cultural Heritage Synthetic Depth Dataset (CHSD) by Arampatzakis, Arnaoutoglou, Koutsoudis & Pavlidis (2024), licensed **CC BY-NC-SA 4.0**:
- RGB: https://doi.org/10.5281/zenodo.11492154
- Depth: https://doi.org/10.5281/zenodo.11484461

The dataset is not stored in this repository.

## Team

Ayaan Goel, Kshiti Bhavsar. Mentor: Ms. Komal Singh.
