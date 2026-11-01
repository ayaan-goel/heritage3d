# heritage3d — Home

**Project:** Cost-Effective Image-Based 3D Digitization of Cultural Heritage Artifacts for Virtual Museum Applications
**Team:** Ayaan Goel, Kshiti Bhavsar · **Mentor:** Ms. Komal Singh · **Mid-term evaluator:** Dr. Kalgi Gandhi

> Updating this vault at the end of every session is **mandatory** (see `CLAUDE.md`).

## Current status (updated 2026-11-01)

- **Museum is now a walkable 3D hall** (`museum/index.html`): domed rotunda + four galleries, WASD + mouse, pedestals with research-fact placards, E for a 360° close-up. Layout grows from `artifacts.json`. Measured in the app's browser pane on this laptop: 16 exhibits 60 fps, 48 (stress test) 59–60 fps. The old page is the List view (`list.html`). See [[07-Results]].
- **Round 3 complete: 23 of 40 artifacts × 5 levels** (2026-11-01 14:49, 15 / 15 runs, no failures). 746 and 522 clean (best L4); `BEY_1415_HI` breaks from L3 down (partial registration, two models). Per-level medians barely changed (L4 0.984, L3 0.964). **Museum: 16 exhibits, 49 MB.** See [[07-Results]].
- **Round 2 complete: 20 of 40 artifacts × 5 levels** (2026-11-01, 35 / 35 runs, no failures). Median cloud F@0.002 R across 20: L1 0.881, L2 0.920, L3 0.963, **L4 0.980**, L5 0.679; L4 is best when it works but breaks on 4 / 20 (L3: 2 / 20, both low-texture objects that fail at every level). 12 / 20 artifacts reconstruct cleanly. New failure: `Ark_HM_38_HI` (smooth plain vessel). See [[07-Results]].
- **Museum: 14 exhibits** (6 added from round 2), 2.8–3.8 MB each, 43 MB in all.
- **Virtual museum started** (`museum/`): 8 round-1 artifacts exhibited from L3 as ~100k-triangle GLBs (median 16.3 MB → 3.0 MB, accuracy unchanged). Static site, grows by running `export_glb.py`. See [[07-Results]].
- **Round 1 complete: 13 artifacts × 5 levels, all 65 runs evaluated** (2026-10-31). Median cloud F@0.002 R by level: L1 0.878, L2 0.915, **L3 0.961**, L4 0.820, L5 0.651; median time L1 52 min → L3 10 min → L5 1.4 min. Six artifacts behave like the pilot (best at L3/L4, mesh ≥ 0.97); in 7 SfM splits off one ring into a second model that is not densified (kept as a reported finding, team 2026-10-31); L5 fails outright on 4. See [[07-Results]].
- Settings frozen; main set = 40 well-framed artifacts in a fixed order (`configs/artifact_order.json`); resumable batch runner ready (`scripts/run_batch.py`). First batch test: small plain `Ark_HM_1260B_HI` **fails at L5** (7/26 images registered, no dense cloud) — L5 is not enough for every object.
- **Pilot complete on `Ark_HM_272_HI`: all five levels reconstructed and evaluated.** L4 (47 images, 7.9 min) gave the best dense-cloud quality (F@0.002 R 0.991); L1 (362 images) took 135 min / 4.7 GB and scored lower (0.905, precision drops as images increase). Mesh quality flat 0.988–0.994 from L4 to L1. One artifact only — see [[07-Results]].
- Phase: **pilot**. Subset generator, environment check, dataset inspection and pipeline runner written and tested; first measured result: full pilot reconstruction of `Ark_HM_272_HI` at L3 (2026-10-30).
- Repository created and scaffolded (README, CLAUDE.md, vault, literature workbook).
- CHSD Zenodo records identified; file names, sizes and license confirmed from the record pages.
- Dataset **downloaded, MD5-verified, extracted and inspected** (2026-10-29): 81 artifacts, complete 360 × 5 grid, RGB 800×600 on black, 16-bit depth; ±90° are pole views; 41/81 artifacts cut off by the frame in some views. See [[03-Dataset-CHSD]].
- Config filled in with the real file pattern and `pole_rings = [-90, 90]` → levels L1–L5 = 362/182/92/47/26 images. 19/19 tests pass.
- Laptop toolchain verified: COLMAP 4.2.1 (CPU), OpenMVS 2.4.0, Python 3.13.15; repo at `D:\heritage3d`; 12/12 tests pass and `check_env.py` reports everything (2026-10-25).
- **Agent moved from the cloud to a local Claude Code session on the laptop (2026-10-29).** Read [[sources/handoff-2026-10-29]] first.
- Hardware confirmed: Intel Iris Xe, no CUDA → CPU pipeline (COLMAP SfM + OpenMVS).

## Next action

1. Round 4 when the team is ready: `run_batch.py --count N --clean` (next ranks from 23; the guard now tolerates unplugs up to 15 min). Then compare, summarize, `export_glb.py`, commit.
2. Team: how to reach the **30-exhibit minimum** ([[09-Open-Questions]]).
3. Team: walk the new hall in a normal browser (`python -m http.server 8000 --directory museum`), check the feel (speed, mouse sensitivity, placards) and decide where to host it ([[09-Open-Questions]]); later: load-time measurement for RQ3.
4. Team: confirm the evaluation method (Option A, decoded CHSD depth — [[04-Methodology]]).
5. The zips in `Downloads` can be kept as backup or deleted (team's choice).
6. Team: try to get the companion paper PDF (doi 10.1007/978-3-032-06389-2_15) via the university library.

## Notes

- [[01-Project-Definition]] — problem, RQs, hypotheses, scope
- [[02-Literature-Review]] — summary of the reviewed literature
- [[03-Dataset-CHSD]] — verified facts vs to-verify
- [[04-Methodology]] — pipeline and tools
- [[05-Experiment-Plan]] — subset levels L1–L5, metrics
- [[06-Environment-Setup]] — laptop, installs, data paths
- [[07-Results]] — measured results only
- [[08-Decisions]] — decision log
- [[09-Open-Questions]] — unknowns and risks
- [[10-Session-Log]] — what happened each session
