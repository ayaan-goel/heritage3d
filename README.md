# heritage3d

A cost-effective image-based 3D digitization framework for cultural heritage artifacts.

This project studies how input-image density affects 3D reconstruction quality, computation and storage, and turns an optimized reconstruction into an interactive artifact in a web-based virtual museum.

**Status:** setup phase. No reconstruction has been run yet. See [`vault/00-Home.md`](vault/00-Home.md).

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

More folders (`experiments/`, `museum/`) are added as each milestone is built.

## Environment check

```
python scripts/check_env.py --out D:\heritage3d-data\runs\environment.json
```
Prints COLMAP/OpenMVS versions and hardware; exits with an error if a tool is not on PATH.

## Subset levels

Uniform azimuth step on every camera ring: L1 3° (600 images), L2 6° (300), L3 12° (150), L4 24° (75), L5 45° (40).

```
python scripts/create_subsets.py --artifact <name> --out D:\heritage3d-data\runs\<name> --check
```

## Dataset

Cultural Heritage Synthetic Depth Dataset (CHSD) by Arampatzakis, Arnaoutoglou, Koutsoudis & Pavlidis (2024), licensed **CC BY-NC-SA 4.0**:
- RGB: https://doi.org/10.5281/zenodo.11492154
- Depth: https://doi.org/10.5281/zenodo.11484461

The dataset is not stored in this repository.

## Team

Ayaan Goel, Kshiti Bhavsar. Mentor: Ms. Komal Singh.
