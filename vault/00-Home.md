# heritage3d — Home

**Project:** Cost-Effective Image-Based 3D Digitization of Cultural Heritage Artifacts for Virtual Museum Applications
**Team:** Ayaan Goel, Kshiti Bhavsar · **Mentor:** Ms. Komal Singh · **Mid-term evaluator:** Dr. Kalgi Gandhi

> Updating this vault at the end of every session is **mandatory** (see `CLAUDE.md`).

## Current status (updated 2026-10-25)

- Phase: **setup**. No code, no reconstruction, no results yet.
- Repository created and scaffolded (README, CLAUDE.md, vault, literature workbook).
- CHSD Zenodo records identified; file names, sizes and license confirmed from the record pages.
- Dataset **not yet downloaded**. COLMAP / OpenMVS **not yet installed**.
- Hardware confirmed: Intel Iris Xe, no CUDA → CPU pipeline (COLMAP SfM + OpenMVS).

## Next action

1. Team: download both CHSD zips to `D:\heritage3d-data\raw\`, check MD5, extract with 7-Zip (see [[06-Environment-Setup]]).
2. Team: install COLMAP (no-CUDA) and OpenMVS; send `--help` outputs.
3. Team: send the folder tree + a few file names of one artifact, and the README of the authors' GitLab repo.
4. Agent: write `scripts/inspect_dataset.py` once the real layout is known.

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
