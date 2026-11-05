# Open Questions and Risks

## Open

- [ ] Team: confirm evaluation Option A as implemented (see [[04-Methodology]]) and the thresholds τ = 0.002/0.005/0.01 R.
- [ ] Companion paper: Arampatzakis, Arnaoutoglou, Koutsoudis & Pavlidis, "Deep Learning-Based Monocular Depth Estimation in Cultural Heritage", CAA-GR 2024 proceedings (Springer), doi 10.1007/978-3-032-06389-2_15 (to verify: does it describe camera setup and depth encoding?). Team to check access via university library.
- [ ] Are the original Virtual Hampson Museum models obtainable, and under what license?
- [ ] Why does dense-cloud precision fall as images increase (L4 0.985 → L1 0.829)? Hypothesis: fixed OpenMVS fusion settings. Round 1: the same pattern on all six artifacts that reconstruct as one model; round 2: on six more (12 / 20).
- [ ] Main artifact set: how many artifacts beyond round 2 (20 of 40 done; a round of 7 took ~15 h overnight)?
- [ ] Tolerance for small objects: τ is relative to R, harsh for `Ark_HM_1260B_HI` (F@0.002 0.06 but F@0.01 0.91 at L1). Also report a tolerance relative to object size?
- [ ] Matcher choice (exhaustive vs vocabulary tree) — fixed after pilot, same for all levels.
- [ ] Code license for the repository (separate from the CC BY-NC-SA data license).

- [x] Avatars → no photos for now: stylized figures stay (team, 2026-11-03). A scan needs each person's agreement and a rigging tool if revisited.
- [ ] Team: check with Prof. Singh that showing the PDEU gate and logo is fine, especially if the museum goes public.
- [x] Do the 14 artifacts from the cut-off set that pass the exhibit rule go in the museum? **Yes, on an upper floor (team, 2026-11-05)**; 44 exhibits measured at 60 fps in the app's pane. See [[07-Results]].
- [ ] How much of an object each cut-off view loses is not measured, so the upper-floor models may lack parts the F-score does not penalise (hypothesis). See [[07-Results]].
- [ ] Visual and texture fidelity (RQ1, RQ3): method built and piloted on 2 artifacts; the full run is still to do. See [[07-Results]].
- [ ] RQ3 rendering cost: full against optimized models in the browser is not compared yet.
- [ ] Should the mentor be asked to accept the joint trade-off reporting, with no single cost-effectiveness score? See [[08-Decisions]].
- [ ] Does the 44-exhibit hall hold its frame rate full screen, and how long does the 129.6 MB collection take to download once hosted? Only measured in the app's pane from localhost.
- [x] Museum needs **≥ 30 exhibits** (team minimum, 2026-11-01). Closed 2026-11-04: all four last artifacts passed the unchanged rule (L3, mesh F ≥ 0.95), giving exactly 30 of the 40. No fallback level, extra artifacts or lower bar needed.
- [ ] Where to host the museum (GitHub Pages from this repo, university server, or local demo only)? Team decision; GLBs are ~4 MB each.
- [ ] Why does OpenMVS seam leveling blacken faces on CHSD renders? (hypothesis: pure-black background pixels at silhouettes pull the colour correction to black). Not needed for the experiment; museum export avoids it.
- [ ] Low-texture objects (`Ark_HM_1260B_HI`, `Ark_HM_38_HI`) fail at every level: report as a limitation only, or also measure texture per artifact and relate it to F? (hypothesis: too few SIFT matches)

## Closed

- [x] Split SfM models (one ring + pole cut off, 7/13 artifacts at some level) → kept as a reported finding under frozen settings, no pipeline change (team, 2026-10-31).
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
