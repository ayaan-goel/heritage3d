# Open Questions and Risks

## Open

- [ ] CHSD folder structure, naming, resolution, background (needs downloaded files).
- [ ] Depth encoding and units; are camera intrinsics/distances published? (decides evaluation Option A/B/C)
- [ ] Are ±90° cameras top/bottom views? (affects subset totals)
- [ ] Companion paper: Arampatzakis, Arnaoutoglou, Koutsoudis & Pavlidis, "Deep Learning-Based Monocular Depth Estimation in Cultural Heritage", CAA-GR 2024 proceedings (Springer), doi 10.1007/978-3-032-06389-2_15 (to verify: does it describe camera setup and depth encoding?). Team to check access via university library.
- [ ] Are the original Virtual Hampson Museum models obtainable, and under what license?
- [ ] CPU runtime for L1 (600 images) — feasible? Decide after pilot.
- [ ] Matcher choice (exhaustive vs vocabulary tree) — fixed after pilot, same for all levels.
- [ ] Code license for the repository (separate from the CC BY-NC-SA data license).

## Closed

- [x] Authors' GitLab repo https://gitlab.com/VasilisAramp/chsd-dataset → 404 for the team on 2026-10-25 (private or removed). Not a usable source.

- [x] Kshiti's git author identity → `Kshiti Bhavsar <kshitibhavsar@gmail.com>`, GitHub Kshitii05 (2026-10-25).

## Risks

- Synthetic renders may have textureless/uniform backgrounds → SfM may match background or fail; masks may be needed.
- 16 GB RAM may limit OpenMVS densify at full resolution → may need reduced resolution (recorded).
- Depth maps might be normalized 8-bit (hypothesis: the companion paper's abstract reports mean RMSE 37.35, a scale that fits 0–255 pixel values rather than metres) → metric 3D reference impossible → fall back to Option B.
