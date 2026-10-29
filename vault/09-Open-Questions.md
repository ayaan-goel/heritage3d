# Open Questions and Risks

## Open

- [ ] Depth units / near-far mapping: 16-bit, ~2,048 levels, larger = nearer, not per-image normalized (verified) — but metric scale unknown. Are camera intrinsics/distances published? (decides evaluation Option A/B/C)
- [ ] Pilot artifact: proposed `Ark_HM_272_HI` (centred, textured) — team to confirm.
- [ ] Black background: will COLMAP find features on the background or edges only on the object? Check in the pilot (masks may not be needed since background is uniform black).
- [ ] Companion paper: Arampatzakis, Arnaoutoglou, Koutsoudis & Pavlidis, "Deep Learning-Based Monocular Depth Estimation in Cultural Heritage", CAA-GR 2024 proceedings (Springer), doi 10.1007/978-3-032-06389-2_15 (to verify: does it describe camera setup and depth encoding?). Team to check access via university library.
- [ ] Are the original Virtual Hampson Museum models obtainable, and under what license?
- [ ] CPU runtime for L1 (362 images) — feasible? Decide after pilot.
- [ ] Matcher choice (exhaustive vs vocabulary tree) — fixed after pilot, same for all levels.
- [ ] Code license for the repository (separate from the CC BY-NC-SA data license).

## Closed

- [x] CHSD folder structure, naming, resolution, background → see [[03-Dataset-CHSD]] (2026-10-29).
- [x] ±90° cameras are pole views (in-plane spins, no new viewpoint) → `pole_rings = [-90, 90]` (2026-10-29).
- [x] Hypothesis "depth is 8-bit" → **false**: 16-bit PNG with ~11-bit effective resolution (2026-10-29). The paper's RMSE 37.35 scale is still unexplained.

- [x] Authors' GitLab repo https://gitlab.com/VasilisAramp/chsd-dataset → 404 for the team on 2026-10-25 (private or removed). Not a usable source.

- [x] Kshiti's git author identity → `Kshiti Bhavsar <kshitibhavsar@gmail.com>`, GitHub Kshitii05 (2026-10-25).

## Risks

- Synthetic renders may have textureless/uniform backgrounds → SfM may match background or fail; masks may be needed.
- 16 GB RAM may limit OpenMVS densify at full resolution → may need reduced resolution (recorded).
- Depth scale may not be recoverable in metres (no intrinsics/near-far in the files) → metric 3D reference impossible → fall back to Option B.
- Half the artifacts are cut off by the image frame in some views → fewer usable artifacts for the main set.
