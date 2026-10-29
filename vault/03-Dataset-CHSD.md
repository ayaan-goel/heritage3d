# Dataset — CHSD

Cultural Heritage Synthetic Depth Dataset. Primary and only dataset for the core project.

## Verified (from the Zenodo record pages, screenshots shared 2026-10-25)

| Item | RGB record | Depth record |
|---|---|---|
| DOI | 10.5281/zenodo.11492154 | 10.5281/zenodo.11484461 |
| File | `CHSDD_RGB.zip` | `CHSDD_depth.zip` |
| Size | 46.2 GB | 7.9 GB |
| License | CC BY-NC-SA 4.0 | CC BY-NC-SA 4.0 |
| Exact size (Zenodo API, 2026-10-29) | 46,153,386,865 bytes | 7,903,200,369 bytes |
| MD5 (Zenodo API) | `a84ed62feae438b467d6ffc654bd6762` | `4e0dd27e6445fd06520e795918638370` |

- Downloaded zips (`C:\Users\goel3\Downloads\`, 2026-10-26) match the exact sizes above, and their MD5s match (checked 2026-10-29 with `Get-FileHash -Algorithm MD5`).
- Extracted with 7-Zip (2026-10-29): `D:\heritage3d-data\chsd\depth\CHSDD_depth\` → **145,800 files** (7.4 GiB); `D:\heritage3d-data\chsd\rgb\CHSDD_RGB\` → **145,800 files** (43.1 GiB). Each zip has one top-level folder. The file count matches the Zenodo description (81 artifacts × 5 cameras × 360 frames).

- Authors: Arampatzakis, V., Arnaoutoglou, F., Koutsoudis, A., & Pavlidis, G. (2024).
- Venue: Computer Applications and Quantitative Methods in Archaeology (CAA-GR), Serres, Greece, 17 April 2024 (Springer).
- Keywords: cultural heritage, synthetic image dataset, **monocular depth estimation** (the dataset was built for depth estimation, not photogrammetry).
- Linked software repo: https://gitlab.com/VasilisAramp/chsd-dataset → returns 404 (checked by team 2026-10-25).
- Companion paper (to verify that it is the dataset paper): "Deep Learning-Based Monocular Depth Estimation in Cultural Heritage", CAA-GR 2024, doi 10.1007/978-3-032-06389-2_15.
- File names use **CHSDD**, not CHSD.

## Verified on the extracted files (2026-10-29, `scripts/inspect_dataset.py`, report `experiments/results/dataset_inspection.json`)

- **81 artifacts**, one folder each, same 81 names in RGB and depth (e.g. `Ark_HM_272_HI`, `shell_bead_HI`, `LR_41638k_HI`; case of the `_HI` suffix varies: `_Hi`, `_hi`).
- Layout: `CHSDD_RGB/<artifact>/RGB/<frame>_<elevation>_.png` and `CHSDD_depth/<artifact>/Z/<frame>_<elevation>_.png`. Frame `0001`–`0360`, elevation `-90`, `-45`, `0`, `45`, `90` (note the trailing underscore).
- Every artifact has the full 360 × 5 grid in both folders: 145,800 RGB + 145,800 depth, nothing missing, no extra files.
- **RGB:** PNG, 8-bit RGB (no alpha), **800 × 600**, **black background** (≈0–1). Rendered in Blender (PNG metadata: `depthmaps.blend`, render dates Nov 2023).
- PNG metadata field `Camera` says `Camera_-90_` on every file regardless of elevation → **stale, do not use**; trust the file name.
- **Depth:** PNG, **16-bit grayscale** (`I;16`), 800 × 600, **0 = background**. Depth > 0 matches the RGB foreground (mask IoU ≥ 0.98 except badly framed views).
- Depth values are quantized: distinct values are 31–32 apart (sometimes 64) → about **2,048 effective levels** (≈11 bits) despite 16-bit storage. 80–909 distinct values per image.
- **Larger value = closer to the camera** (bowl interiors are low, near rims are high). Range of foreground values across the dataset: 960–65535. Max varies per image (e.g. 38,463 vs 53,919), so values are **not normalized per image** (hypothesis: one fixed near/far mapping for the whole dataset; units unknown). 65535 reached on `Ark_HM_1279_Hi` (likely clipped where the object comes too close).
- **±90° are pole views:** the views at ±90° for frame k are the frame-1 view spun in the image plane by (k−1)°. Silhouette IoU after spinning ≥ 0.991 on all 40 well-framed artifacts (0° ring: 0.0–0.80, i.e. genuinely new views). −90° looks at the bottom, +90° looks down into the object. → `pole_rings = [-90, 90]`.
- **Framing problem:** in 41 of 81 artifacts the object touches/leaves the image edge in some of the 20 sample views (frames 1/91/181/271 × 5 rings); some are badly off-centre (e.g. `Ark_HM_1279_Hi`, `LR_41638k_HI`, `Ark_HM_484_HI` swing partly out of the picture). 40 artifacts are never cut off in the sample.
- Object size in the image (well-framed artifacts): 2–53 % of pixels.

## Assumptions

- Frame `0001` = azimuth 0°, frame k = (k−1)° (assumption: only relative angles matter; rotation direction unknown).

## Still unknown

- Depth units / near-far mapping (metric or normalized?); z-depth vs ray distance. Needed for a 3D reference (Option A).
- Camera intrinsics (focal length, sensor) and camera distance — not in the files (PNG metadata only has render info).
- Are the original Hampson 3D models obtainable (best ground truth)? Their license?

## License implications

CC BY-NC-SA 4.0: attribution required, **non-commercial only**, and derivatives (our reconstructions and museum models) must be shared under the same license. The virtual museum must show attribution to the dataset authors and the Virtual Hampson Museum.

## Role in the project

- RGB images → reconstruction input.
- Depth maps → evaluation reference only, never input to reconstruction (see [[08-Decisions]]).
