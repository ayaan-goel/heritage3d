# Session Log

Newest first. Every session must add an entry (see `CLAUDE.md`).

---

## 2026-10-25 — Session 1 (directed by Ayaan Goel)

**What happened**
- Read the project handoff and the literature workbook.
- Identified both CHSD Zenodo records; team shared screenshots confirming file names, sizes, license (CC BY-NC-SA 4.0), authors and the GitLab link.
- Hardware corrected: Intel Iris Xe (no CUDA), not RTX 3050 → switched dense stage to OpenMVS (CPU).
- Decided subset levels L1–L5 by azimuth step; depth maps for evaluation only; museum compulsory.
- Scaffolded the repository: `README.md`, `CLAUDE.md`, `.gitignore`, `vault/`, `docs/literature/` workbook, handoff copy in `vault/sources/`.

**Commands run (cloud session) and outcomes**
- `nvidia-smi` → not found (no GPU in cloud container). `nproc` → 4; RAM 15 GB; ~30 GB free disk.
- `curl https://zenodo.org/api/records/...` → proxy 403 (host not allowed).
- `git clone https://gitlab.com/VasilisAramp/chsd-dataset` → auth prompt, failed. WebFetch → 403.
- `git clone https://github.com/ayaan-goel/heritage3d` → empty repository.

- Added both team members' git author identities to `CLAUDE.md`.
- Team started downloading CHSD to D:.
- Authors' GitLab repo returned 404. Found likely companion paper (doi 10.1007/978-3-032-06389-2_15) via web search; logged in open questions.

- Commit rule changed: authorship split between Ayaan and Kshiti at irregular intervals (both work together).

- Added clean-commit rule to `CLAUDE.md` (one commit per meaningful working unit).
- Built the subset generator: `configs/experiment.toml`, `src/heritage3d/{config,subsets}.py`, `scripts/create_subsets.py`, `tests/test_subsets.py`.
  - `pytest tests` → 7 passed (cloud session, Python 3.13).
  - `python scripts/create_subsets.py --artifact demo --out <scratch>` → L1 600, L2 300, L3 150, L4 75, L5 40 (file pattern is still a placeholder; not run on real data).
- Laptop setup (run by team, output pasted into chat):
  - COLMAP 4.2.1 no-CUDA extracted to `C:\tools\colmap`; `COLMAP.bat -h` → "COLMAP 4.2.1 (Commit bd1fcf6 on 2026-09-29 without GPU support)".
  - OpenMVS 2.4.0 extracted to `C:\tools\openmvs`; `InterfaceCOLMAP --help` and `DensifyPointCloud --help` → OK; banner: i7-1255U, 15.72 GB RAM, Windows 11.
  - Both added to user PATH; `colmap -h` and `DensifyPointCloud --help` work from any folder.
  - `git clone` to `D:\heritage3d`, venv with Python 3.13.15, `pytest tests` → 7 passed.
- Added `scripts/check_env.py` + `src/heritage3d/environment.py` (records tool versions and hardware; exits 1 if a tool is missing).
  - Cloud: `pytest tests` → 11 passed; `check_env.py` → exit 1 with "COLMAP not found" (expected: no tools in the cloud container). Not yet run on the laptop.
- Laptop: `git pull`, `pytest tests` → 11 passed; `check_env.py` → COLMAP 4.2.1 detected, all 5 OpenMVS tools found, but OpenMVS version "unknown" and hardware empty (OpenMVS writes its banner to the Windows console, not stdout).
- Fixed `environment.py`: hardware now read from Windows registry / `GlobalMemoryStatusEx` (or `/proc` on Linux); OpenMVS run in a temp folder without a console and its `*.log` read for the version.
  - Cloud: `pytest tests` → 12 passed; simulated OpenMVS that only writes a log file → version 2.4.0 parsed. Windows behaviour **to verify** on the laptop.

**Next action** — see [[00-Home]].
