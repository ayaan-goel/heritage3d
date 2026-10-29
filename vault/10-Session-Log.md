# Session Log

Newest first. Every session must add an entry (see `CLAUDE.md`).

---

## 2026-10-29 — Handoff (directed by Ayaan Goel and Kshiti Bhavsar)

- Team switched from the cloud session to a local Claude Code session on the laptop.
- Wrote `vault/sources/handoff-2026-10-29.md` (context that existed only in the chat), updated `CLAUDE.md` for local work (agent runs tools itself; commit command that sets author and committer in PowerShell).
- Dataset download still in progress.


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
- Laptop: `git pull`, `pytest tests` → 12 passed; `check_env.py` → OpenMVS 2.4.0 and hardware (i7-1255U, 12 CPUs, 15.72 GB) now reported. Windows fix verified.

**Next action** — see [[00-Home]].

---

## 2026-10-29 — Session 2, first local session (directed by Ayaan Goel and Kshiti Bhavsar)

**What happened**
- Read [[00-Home]] and [[sources/handoff-2026-10-29]]; ran the first local checks.
- Found the dataset is **not extracted yet**: `D:\heritage3d-data` does not exist; no 7-Zip process running.
- Both zips are in `C:\Users\goel3\Downloads\` (finished 2026-10-26). Sizes match Zenodo byte for byte; expected MD5 recorded in [[03-Dataset-CHSD]]. Local MD5 not computed yet.
- Stray `DensifyPointCloud-2610260128130002ED.log` (2026-10-26) in the repo root, untracked — left over from an OpenMVS run before the `check_env` temp-folder fix; today's `check_env.py` did not create a new one.

**Commands run (laptop) and outcomes**
- `git pull` → already up to date.
- `python -m pytest tests -q` → 12 passed in 1.81 s.
- `python scripts/check_env.py` → exit 0; COLMAP 4.2.1 (no GPU), OpenMVS 2.4.0, all 5 tools found, i7-1255U / 12 CPUs / 15.72 GB.
- Zenodo API (`/api/records/11492154`, `/11484461`) → sizes and MD5 (see [[03-Dataset-CHSD]]).
- Free space: C: 167.9 GB, D: 359 GB. 7-Zip installed at `C:\Program Files\7-Zip\7z.exe`.

- Team approved MD5 check + extraction. Ran a scratch PowerShell script (not in repo): `Get-FileHash -Algorithm MD5`, then `7z x <zip> -o<out> -aos`.
  - depth MD5 match (28 s); RGB MD5 match (160 s).
  - depth → `D:\heritage3d-data\chsd\depth`, exit 0 (180 s); RGB → `D:\heritage3d-data\chsd\rgb`, exit 0 (246 s).
  - File count: depth 145,800 files (7.4 GiB), RGB 145,800 files (43.1 GiB); single top folders `CHSDD_depth\`, `CHSDD_RGB\`.

- Team approved dataset inspection. Explored by hand (scratch probes + contact sheets, not in repo), then wrote:
  - `src/heritage3d/dataset.py` (name parsing, folder scan, depth stats, framing, in-plane spin test) + `tests/test_dataset.py`.
  - `scripts/inspect_dataset.py` → `experiments/results/dataset_inspection.json`.
  - Config: real paths (`...\CHSDD_RGB`, `...\CHSDD_depth`), `rgb_pattern` / `depth_pattern` with `{frame:04d}`, `pole_rings = [-90, 90]`; `subsets.view_path` maps azimuth → 1-based frame. Level totals now 362/182/92/47/26.
  - `requirements.txt`: + numpy, pillow. README, [[05-Experiment-Plan]], [[06-Environment-Setup]] updated.
- `pip install pillow numpy` → numpy 2.5.4, pillow 13.0.0.
- `pytest tests -q` → 19 passed (one new test first failed because its "different shape" was a near-spin of the bar; fixed the test shape).
- `inspect_dataset.py` (all 81) → exit 0, ~40 s: complete 360×5 grid everywhere; RGB 800×600 8-bit on black; depth 16-bit, 0 = background, ~2,048 levels, larger = nearer; ±90° spin IoU ≥ 0.991 on well-framed artifacts; 41/81 artifacts cut off by the frame in some sample views. Details in [[03-Dataset-CHSD]].
- `create_subsets.py --artifact Ark_HM_272_HI --out D:\heritage3d-data\runs\Ark_HM_272_HI --check` → exit 0, L1 362, L2 182, L3 92, L4 47, L5 26.

**Next action** — team confirms pilot artifact (proposed `Ark_HM_272_HI`); then pilot L3 (92 images) COLMAP SfM (CPU) → OpenMVS, recording time and peak RAM.
