# Open Questions and Risks

## Open

- [ ] Team: confirm evaluation Option A as implemented (see [[04-Methodology]]) and the thresholds τ = 0.002/0.005/0.01 R.
- [ ] Companion paper: Arampatzakis, Arnaoutoglou, Koutsoudis & Pavlidis, "Deep Learning-Based Monocular Depth Estimation in Cultural Heritage", CAA-GR 2024 proceedings (Springer), doi 10.1007/978-3-032-06389-2_15 (to verify: does it describe camera setup and depth encoding?). Team to check access via university library.
- [ ] Are the original Virtual Hampson Museum models obtainable, and under what license?
- [ ] Why does dense-cloud precision fall as images increase (L4 0.985 → L1 0.829)? Hypothesis: fixed OpenMVS fusion settings. Round 1: the same pattern on all six artifacts that reconstruct as one model.
- [ ] Main artifact set: how many artifacts beyond round 1 (13 done; L1 takes 18–150 min per artifact)?
- [ ] SfM splits into two models (one elevation ring + pole cut off) in 7/13 artifacts at some level; the pipeline densifies only the largest model. Keep as a finding under frozen settings, or change the pipeline (e.g. densify/merge all models) and re-run everything? Team decision.
- [ ] Tolerance for small objects: τ is relative to R, harsh for `Ark_HM_1260B_HI` (F@0.002 0.06 but F@0.01 0.91 at L1). Also report a tolerance relative to object size?
- [ ] Matcher choice (exhaustive vs vocabulary tree) — fixed after pilot, same for all levels.
- [ ] Code license for the repository (separate from the CC BY-NC-SA data license).

## Closed

- [x] CPU runtime for L1 (362 images) → feasible: 135 min, peak 4.7 GB on the pilot (2026-10-30).
- [x] Black background → SfM registered every image at every level with 0.16–0.24 px error; no masks needed on the pilot (2026-10-30).
- [x] Depth encoding and intrinsics → decoded from the depth maps: z = R(1.5 − v/65535), f = 1000 px, ideal turntable rig (2026-10-30, [[03-Dataset-CHSD]]). Option A feasible.
- [x] Pilot artifact → `Ark_HM_272_HI`, confirmed by the team 2026-10-30.

- [x] CHSD folder structure, naming, resolution, background → see [[03-Dataset-CHSD]] (2026-10-29).
- [x] ±90° cameras are pole views (in-plane spins, no new viewpoint) → `pole_rings = [-90, 90]` (2026-10-29).
- [x] Hypothesis "depth is 8-bit" → **false**: 16-bit PNG with ~11-bit effective resolution (2026-10-29). The paper's RMSE 37.35 scale is still unexplained.

- [x] Authors' GitLab repo https://gitlab.com/VasilisAramp/chsd-dataset → 404 for the team on 2026-10-25 (private or removed). Not a usable source.

- [x] Kshiti's git author identity → `Kshiti Bhavsar <kshitibhavsar@gmail.com>`, GitHub Kshitii05 (2026-10-25).

## Risks

- Synthetic renders may have textureless/uniform backgrounds → SfM may match background or fail; masks may be needed.
- 16 GB RAM may limit OpenMVS densify at full resolution → may need reduced resolution (recorded).
- At L3 the pilot is already near the measurement floor (reference voxel 0.002 R) → differences between dense levels may be small; the low levels (L4/L5) and cost may carry most of the story.
- Half the artifacts are cut off by the image frame in some views → fewer usable artifacts for the main set.
