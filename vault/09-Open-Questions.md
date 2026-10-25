# Open Questions and Risks

## Open

- [ ] CHSD folder structure, naming, resolution, background (needs downloaded files).
- [ ] Depth encoding and units; are camera intrinsics/distances published? (decides evaluation Option A/B/C)
- [ ] Are ±90° cameras top/bottom views? (affects subset totals)
- [ ] Contents of https://gitlab.com/VasilisAramp/chsd-dataset (generation scripts may give camera parameters).
- [ ] Are the original Virtual Hampson Museum models obtainable, and under what license?
- [ ] CPU runtime for L1 (600 images) — feasible? Decide after pilot.
- [ ] Matcher choice (exhaustive vs vocabulary tree) — fixed after pilot, same for all levels.
- [ ] Code license for the repository (separate from the CC BY-NC-SA data license).
- [ ] Kshiti's git author name/email for commits.

## Risks

- Synthetic renders may have textureless/uniform backgrounds → SfM may match background or fail; masks may be needed.
- 16 GB RAM may limit OpenMVS densify at full resolution → may need reduced resolution (recorded).
- Depth maps might be normalized 8-bit → metric 3D reference impossible → fall back to Option B.
