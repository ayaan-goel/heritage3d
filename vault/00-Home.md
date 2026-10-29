# heritage3d — Home

**Project:** Cost-Effective Image-Based 3D Digitization of Cultural Heritage Artifacts for Virtual Museum Applications
**Team:** Ayaan Goel, Kshiti Bhavsar · **Mentor:** Ms. Komal Singh · **Mid-term evaluator:** Dr. Kalgi Gandhi

> Updating this vault at the end of every session is **mandatory** (see `CLAUDE.md`).

## Current status (updated 2026-10-29)

- Phase: **setup → pilot**. Subset generator, environment check and dataset inspection written and tested on real data; no reconstruction, no results yet.
- Repository created and scaffolded (README, CLAUDE.md, vault, literature workbook).
- CHSD Zenodo records identified; file names, sizes and license confirmed from the record pages.
- Dataset **downloaded, MD5-verified, extracted and inspected** (2026-10-29): 81 artifacts, complete 360 × 5 grid, RGB 800×600 on black, 16-bit depth; ±90° are pole views; 41/81 artifacts cut off by the frame in some views. See [[03-Dataset-CHSD]].
- Config filled in with the real file pattern and `pole_rings = [-90, 90]` → levels L1–L5 = 362/182/92/47/26 images. 19/19 tests pass.
- Laptop toolchain verified: COLMAP 4.2.1 (CPU), OpenMVS 2.4.0, Python 3.13.15; repo at `D:\heritage3d`; 12/12 tests pass and `check_env.py` reports everything (2026-10-25).
- **Agent moved from the cloud to a local Claude Code session on the laptop (2026-10-29).** Read [[sources/handoff-2026-10-29]] first.
- Hardware confirmed: Intel Iris Xe, no CUDA → CPU pipeline (COLMAP SfM + OpenMVS).

## Next action

1. Team: confirm the pilot artifact (proposed `Ark_HM_272_HI`). The zips in `Downloads` can be kept as backup or deleted.
2. Agent: pilot reconstruction on that artifact at L3 (92 images): COLMAP SfM (CPU) → OpenMVS; record runtime and peak RAM; check registered-image count before going dense.
3. Team: try to get the companion paper PDF (doi 10.1007/978-3-032-06389-2_15) via the university library.

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
