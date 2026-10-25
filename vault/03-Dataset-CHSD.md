# Dataset — CHSD

Cultural Heritage Synthetic Depth Dataset. Primary and only dataset for the core project.

## Verified (from the Zenodo record pages, screenshots shared 2026-10-25)

| Item | RGB record | Depth record |
|---|---|---|
| DOI | 10.5281/zenodo.11492154 | 10.5281/zenodo.11484461 |
| File | `CHSDD_RGB.zip` | `CHSDD_depth.zip` |
| Size | 46.2 GB | 7.9 GB |
| License | CC BY-NC-SA 4.0 | CC BY-NC-SA 4.0 |

- Authors: Arampatzakis, V., Arnaoutoglou, F., Koutsoudis, A., & Pavlidis, G. (2024).
- Venue: Computer Applications and Quantitative Methods in Archaeology (CAA-GR), Serres, Greece, 17 April 2024 (Springer).
- Keywords: cultural heritage, synthetic image dataset, **monocular depth estimation** (the dataset was built for depth estimation, not photogrammetry).
- Linked software repo: https://gitlab.com/VasilisAramp/chsd-dataset (not reachable from the cloud session; team to check).
- File names use **CHSDD**, not CHSD.

## Stated in the Zenodo description, not yet checked on the files (to verify)

- 81 artifacts, 3D models from the Virtual Hampson Museum.
- 145,800 RGB images and 145,800 depth maps.
- Five virtual cameras at −90°, −45°, 0°, 45°, 90° relative to the object; rotation in 1° steps → 1,800 images per object (5 × 360).

## Unknown — must be answered from the files

- Folder structure and file naming (per artifact? per camera?).
- Image resolution and format; background (transparent/solid?).
- Depth encoding: metric or normalized; bit depth; near/far; z-depth vs ray distance.
- Camera intrinsics (focal length, sensor) and distance to object — provided anywhere?
- Whether the ±90° cameras are top/bottom views (rotation would then give no new viewpoints).
- Are the original Hampson 3D models obtainable (best ground truth)? Their license?

## License implications

CC BY-NC-SA 4.0: attribution required, **non-commercial only**, and derivatives (our reconstructions and museum models) must be shared under the same license. The virtual museum must show attribution to the dataset authors and the Virtual Hampson Museum.

## Role in the project

- RGB images → reconstruction input.
- Depth maps → evaluation reference only, never input to reconstruction (see [[08-Decisions]]).
