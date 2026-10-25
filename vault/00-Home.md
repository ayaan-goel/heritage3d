# heritage3d — Home

**Project:** Cost-Effective Image-Based 3D Digitization of Cultural Heritage Artifacts for Virtual Museum Applications
**Team:** Ayaan Goel, Kshiti Bhavsar · **Mentor:** Ms. Komal Singh · **Mid-term evaluator:** Dr. Kalgi Gandhi

> Updating this vault at the end of every session is **mandatory** (see `CLAUDE.md`).

## Current status (updated 2026-10-25)

- Phase: **setup**. Subset generator and environment check written and unit-tested; no reconstruction, no results yet.
- Repository created and scaffolded (README, CLAUDE.md, vault, literature workbook).
- CHSD Zenodo records identified; file names, sizes and license confirmed from the record pages.
- Dataset **download in progress** (team laptop).
- Laptop toolchain verified: COLMAP 4.2.1 (CPU), OpenMVS 2.4.0, Python 3.13.15; repo cloned to `D:\heritage3d`, 7/7 tests passed there.
- Hardware confirmed: Intel Iris Xe, no CUDA → CPU pipeline (COLMAP SfM + OpenMVS).

## Next action

1. Team: download both CHSD zips to `D:\heritage3d-data\raw\`, check MD5, extract with 7-Zip (see [[06-Environment-Setup]]).
2. Team: `git pull`, then run `python scripts/check_env.py` on the laptop and send the output.
3. Team: send the folder tree + a few file names of one artifact; try to get the companion paper PDF (doi 10.1007/978-3-032-06389-2_15) via the university library.
4. Agent: set the real `rgb_pattern` / `pole_rings` in `configs/experiment.toml` and write `scripts/inspect_dataset.py` once the real layout is known.

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
