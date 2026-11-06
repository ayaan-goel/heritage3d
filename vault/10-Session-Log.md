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

- 2026-10-30: team confirmed pilot artifact `Ark_HM_272_HI`.
- Wrote `src/heritage3d/pipeline.py` (COLMAP/OpenMVS stage commands; `run_stage` logs output and records wall time + peak memory of the process tree via a Windows job object, started suspended so child processes are counted) + `tests/test_pipeline.py`, and `scripts/run_pipeline.py` (`--stages sparse|dense`, metrics + logs copied to `experiments/`). Added `[pipeline]` settings to the config (`SIMPLE_PINHOLE`, single camera, `exhaustive_matcher`, densify resolution level 1).
  - `pytest tests -q` → 23 passed.
- `run_pipeline.py --artifact Ark_HM_272_HI --level L3 --stages sparse` → exit 0: feature extraction 11.7 s, exhaustive matching 283.4 s, mapper 51.9 s; peak 2.0 GB; **92/92 images registered**, 35,995 points, reprojection error 0.19 px. See [[07-Results]].

- Team approved the dense stage. `run_pipeline.py ... --stages dense` → exit 0, 742 s total (densify 547 s, mesh 84 s, texture 111 s), peak 1.2 GB; 1,194,573 dense points from 91/92 depth maps (none for the single top view `0001_90_`), mesh 240,838 v / 481,612 f. See [[07-Results]].
  - Checked: 92 undistorted images present; OpenMVS's own memory report matches the job-object figure (650 vs 649 MB).
- Added `src/heritage3d/ply.py` (PLY vertex reader, handles OpenMVS per-vertex lists) + `tests/test_ply.py`, and `scripts/preview_cloud.py` (three-view splat picture). Preview → `experiments/plots/Ark_HM_272_HI_L3_dense.jpg`: pot clearly reconstructed. `pytest tests -q` → 26 passed.
- `run_pipeline.py` now also copies OpenMVS's own `*.log` files into `experiments/logs/`.
- Team went to sleep and asked the agent to keep working overnight with clean commits balanced between Ayaan and Kshiti (history before tonight: Ayaan 9, Kshiti 4).

- Commits (as Kshiti, to rebalance authorship): `71ac740` pipeline runner + L3 pilot, `d86dc81` PLY reader + preview. Pushed.
- Started L5 → L4 → L2 → L1 runs on `Ark_HM_272_HI` in the background (scratch PowerShell loop calling `run_pipeline.py` sparse then dense, then `preview_cloud.py`).
- Meanwhile, decoded the CHSD depth geometry (scratch analyses, then code):
  - CHSD value vs COLMAP z on 277,449 L3 observations: linear (R² 0.998, median residual 20 ≈ one depth step); per-image slopes nearly identical → one global mapping.
  - COLMAP camera centres = ideal turntable (elevations ±45.0 ± 0.02°, steps 12.000 ± 0.011°, equal radius).
  - Depth-only consistency (no COLMAP) on 5 artifacts → best f = 1000 px, near 0.5 R, far 1.5 R, rotation sign +1; poles' roll found (2 artifacts). See [[03-Dataset-CHSD]].
- Wrote `src/heritage3d/reference.py`, `src/heritage3d/evaluate.py`, `scripts/evaluate_run.py`, `tests/test_reference.py`; `[evaluation]` config; `pip install scipy` → 1.18.1. `pytest tests -q` → 34 passed.
- `evaluate_run.py --artifact Ark_HM_272_HI --level L3` → exit 0 (376 s incl. reference build): camera RMS 0.00025 R, Chamfer 0.00075 R, F@0.002 R 0.974. See [[07-Results]].

- Level chain finished (scratch loop): L2 sparse 1,346 s + dense 1,363 s; L1 sparse 5,273 s (matching 4,826 s) + dense 2,841 s, peak 4.7 GB; all images registered at every level. Commit `4793548` (Kshiti).
- Re-ran L5 and L4 with `--overwrite` on an idle machine: L5 205 s, L4 475 s (first runs 5–15 % slower because of concurrent work).
- First evaluation attempt did nothing (`/usr/bin/time` missing in Git Bash) — re-ran without it: `evaluate_run.py` L5/L4/L2/L1 → exit 0, 4–15 s each (reference cached).
- Added `src/heritage3d/compare.py`, `scripts/compare_levels.py`, `tests/test_compare.py`; `pip install matplotlib` → 3.11.2. `pytest tests -q` → 36 passed.
- `compare_levels.py --artifact Ark_HM_272_HI` → CSV + plot. Best dense-cloud quality at L4 (F@0.002 R 0.991); precision falls with more images; mesh F flat 0.988–0.994 for L4–L1; L5 loses completeness (recall 0.926). See [[07-Results]].

- Team: frozen settings approved; asked to work efficiently.
- Added `src/heritage3d/selection.py` + `scripts/select_artifacts.py` → `configs/artifact_order.json` (40 candidates, farthest-point order in size × texture from the pilot; rank 1 `Ark_HM_1260B_HI` smallest, rank 2 `Ark_HM_470_HI` most textured, 2.8× the pilot). `tests/test_selection.py` (first texture test failed: a period-2 stripe cancels in Sobel; fixed the test pattern).
- Added `clean_workspace` (pipeline.py) and `scripts/run_batch.py` (fixed order, resume by existing eval files, failures logged, optional cleanup). `--count 3 --dry-run` → 10 pending (pilot skipped).
- Test run `run_batch.py --count 2 --levels L5 --clean` → `Ark_HM_1260B_HI` L5: **only 7/26 images registered**, densify 0 depth maps / 0 points (each image paired with 0 views), mesh from 273 sparse points; reference 63,126 points (54 s).
- Made failures first-class: `evaluate_run.py` records F = 0 / recall 0 for missing output (and needs ≥ 3 cameras to align); `run_pipeline.py --stages dense` with no sparse model records it and exits 0; `compare.py` tolerates missing parts. Re-evaluated 1260B L5: dense F = 0, mesh F@0.005 0.144 (P 0.934, R 0.078). `pytest tests -q` → 41 passed.

- Team approved round 1. `check_env.py` → exit 0; D: 299 GB free. `run_batch.py` now asks Windows not to idle-sleep while it runs (`SetThreadExecutionState`; lid close still sleeps).
- Launched detached (`Start-Process`, PID 18148, 10:59:53): `run_batch.py --count 13 --clean` → 59 level runs pending (pilot + ranks 1–12). Progress: `D:\heritage3d-data\runs\batch.log`, output `D:\heritage3d-data\runs\round1.out` / `.err`.

- Round 1 stopped by itself at ~11:47 during `Ark_HM_470_HI` L3 DensifyPointCloud — no error logged, no processes left. System log shows a Claude-app package event at 11:47:27 → the detached batch was most likely killed with the app's process tree (hypothesis). Done before that: `Ark_HM_1260B_HI` L1–L5 (all in 24 min), `Ark_HM_470_HI` L5, L4. Power source changed 6× at 11:37 (charger), during 470 L4 dense → its timing is suspect; re-run it.
- Team leaving for college (lid will be closed): batch not restarted. Lid-close sleep would add sleep time to wall-clock timings and battery throttles the CPU.

- Team asked to run the batch inside this session so its state is visible. Added `src/heritage3d/conditions.py` (AC status via `GetSystemPowerStatus`; time asleep = wall time − `QueryUnbiasedInterruptTime`) + `tests/test_conditions.py`. `run_batch.py`: waits for the charger before each level; stops a running level (whole process tree) when the charger is removed and redoes it; sets aside (`*.suspect`) and re-queues a level that slept or ran on battery (`--attempts`, default 3). `pytest tests -q` → 45 passed; simulated unplug stopped a two-process script and its child in 3 s.
- Set aside 470 L4 (charger changes during its run). Started the batch as a session background task at 13:26:48.
- 13:27 laptop entered standby (lid closed); woke 14:16 on battery → the guard stopped 470 L4 ("stopped after 2991 s: charger removed") and waited. 15:48 laptop put to sleep/hibernate from the Start menu → the background task ended (exit 4, nothing logged). No results affected.
- 19:05 team back, on charger: batch resumed in this session (54 level runs pending).

**Next action** — when round 1 finishes: check `batch.log` for failures/suspects, run `compare_levels.py` per artifact, write cross-artifact results, commit.

## 2026-10-30 19:05 → 2026-10-31 — round 1 finished (directed by Ayaan and Kshiti)

- Batch ran in this session (background task) from 19:05 to 2026-10-31 15:01. Charger removed twice (19:17, 19:27): the guard stopped 470 L3 and redid it; no level slept or was set aside. `batch.log` end: `batch done: 51 ok, 3 failed ['RL_907_HI L5', 'Ark_HM_31_HI L5', 'Ark_HM_797_hi L5']`.
- The 3 failures: 5–9/26 images registered, DensifyPointCloud 0 points, then TextureMesh exit 1 → `run_pipeline.py --stages dense` exit 1 and the batch skipped evaluation. Ran `evaluate_run.py --level L5` for the three → exit 0, F = 0 (no points); cleaned their workspaces. `run_batch.py` now evaluates a level whenever sparse succeeded, logging "dense stage failed: evaluated as a failed reconstruction".
- `run_batch.py --count 13 --dry-run` → 0 pending.
- Added `level_summary` (compare.py) + test, `scripts/summarize_round.py`; `compare_levels.py` prints registered images and handles failed runs (it crashed on a missing Chamfer). `pytest -q` → 46 passed.
- `compare_levels.py` for all 13 artifacts and `summarize_round.py --count 13 --name round1` → CSVs + plots. See [[07-Results]].
- Checked the split-model hypothesis with `colmap model_converter` (TXT into scratch): at L1, 341 / 31 / 797 lose exactly one ring + pole (120 + 1 images) into a second model; 1260B L1 one model, camera RMS 0.018 R; F@0.01 0.912.
- Corrected during the session: the agent first said 809 was the last artifact; `--count 13` = pilot + ranks 1–12, so 797 (rank 12) was last.

**Next action** — team: decide on the split-model question and the main-set size ([[09-Open-Questions]]); then either round 2 (next ranks) or museum preparation (decimate + GLB for the best artifacts).
- Team decision: split SfM models stay a reported finding (no pipeline change, no re-run). Recorded in [[08-Decisions]]; vault edits go into the next work commit.

## 2026-10-31 afternoon — museum preparation (directed by Ayaan and Kshiti)

- Team chose museum prep before round 2; asked whether artifacts can be added later → yes, same cost (batch resumes; museum reads a manifest).
- `museum/` static site (index.html, style.css, app.js; `<model-viewer>` 3.5.0 from jsDelivr) reading `museum/artifacts.json`. Preview via `.claude/launch.json` (`python -m http.server 8765`).
- `src/heritage3d/glb.py` (GLB read/write with embedded texture, z-up → y-up, surface sampling) + `tests/test_glb.py`; `scripts/export_glb.py`; `[museum]` config.
- Debugging the black texture: first a wrong guess (V flip) and a sampler change; then OpenMVS's own GLB also rendered black; UV-over-texture plots showed faces mapped onto black blobs → `TextureMesh --global-seam-leveling 0 --local-seam-leveling 0`: black face centres 100 % → 0.2 % (either flag alone 91 % / 100 %). Flip reverted; sampler kept linear/no-mipmap/clamped like OpenMVS.
- `export_glb.py --count 13` → exit 0: 8 exhibits, 5 skipped by the F ≥ 0.95 rule; 2.8–3.8 MB each; F unchanged (see [[07-Results]]). Checked 470, 809, RL_907 in the browser: textured and upright; phone width (375 px) layout stacks.
- Fixed `clean_workspace`: `dense/images/*` missed the nested undistorted images (~170 MB per L1 workspace kept); now `dense/images/**/*`. Existing workspaces still hold them. `pytest -q` → 49 passed.

## 2026-10-31 16:54 → 2026-11-01 — round 2 (directed by Ayaan and Kshiti)

- Team: "start round 2 now". `check_env.py` → exit 0; on AC; `run_batch.py --count 20 --dry-run` → 35 pending; D: 288 GB free. Started in-session (background task) 16:54:32: `run_batch.py --count 20 --clean` (ranks 13–19: 1304, 1303, 314, 299, 38, 747, 11).
- Charger removed at 19:50 (1303 L1), 23:56 and 00:32 (299 L2): each level stopped and redone. `batch.log` end 2026-11-01 07:37:09: `batch done: 35 ok, 0 failed []`. `Ark_HM_38_HI` L4/L5: dense stage exit 1 (2 / 4 images registered) → evaluated as failed reconstructions.
- Looked at `Ark_HM_38_HI` input images: smooth plain round vessel, colour std ≈ 8/255 inside the object → low-texture failure at every level (hypothesis), not a pipeline error.
- `compare_levels.py` for the 7 artifacts; `summarize_round.py --count 20 --name round2` → median cloud F L1 0.881, L2 0.920, L3 0.963, **L4 0.980**, L5 0.679 (see [[07-Results]]).
- `export_glb.py --artifacts <the 7>` → exit 0: 6 new exhibits (2.9–3.1 MB), 38 skipped; manifest 14 artifacts, 43 MB.
- Museum: opening a `#<artifact>` link on an already-open page did nothing → `app.js` now listens for `hashchange`; checked in the browser (hash switch, button click, no console errors).
- Opened questions: low-texture objects; main-set size updated to 20 / 40.

**Next action** — team: decide whether to run round 3 (ranks 20–26) and where to host the museum.

## 2026-11-01 morning — round 3 start, power-guard change (directed by Ayaan and Kshiti)

- Team: museum needs at least 30 exhibits; round 3 only 3 artifacts (laptop may be shut). `check_env.py` → exit 0; on AC; D: 283 GB free; `run_batch.py --count 23 --clean` started in-session 08:48:49 (15 level runs: `Ark_HM_746_HI`, `Ark_HM_522_HI`, `BEY_1415_HI`). Runs with the old (strict) power guard — the process loaded the code before the change below.
- Team asked: don't stop on a brief charger removal; stop only after 15 min unplugged. `conditions.py`: `ConditionMonitor` tracks the current and longest unbroken battery stretch; `clean(max_unplugged_s=...)`. `run_batch.py`: `--unplug-grace` (min, default 15), stops a level only when the stretch reaches it, logs kept battery time, writes `conditions` into the run's metrics JSON. Tests: 2 new in `tests/test_conditions.py`, new `tests/test_run_batch.py` (3: keeps running within grace, stops at grace, conditions recorded). `pytest -q` → 54 passed.
- Flagged to the team: at the current pass rate the 40-artifact set gives ≈ 28 exhibits, below 30 (open question).

**Next action** — when round 3 finishes: batch.log check, compare/summarize, export, results into the vault, commit.

## 2026-11-01 afternoon — round 3 finished (directed by Ayaan and Kshiti)

- Team first cut round 3 to 2 artifacts (agent armed an auto-stop for when `BEY_1415_HI` would start), then back to 3 (laptop stays home); auto-stop cancelled before it fired, batch untouched.
- `batch.log`: `2026-11-01 14:49:55 batch done: 15 ok, 0 failed []`, no charger removal or sleep.
- `compare_levels.py` for 746, 522, BEY_1415; `summarize_round.py --count 23 --name round3`. BEY_1415 L3: 44 + 31 / 92 images in two models, F 0.627.
- `export_glb.py --artifacts Ark_HM_746_HI Ark_HM_522_HI BEY_1415_HI` → exit 0: 746 and 522 added (2.9 MB each), BEY skipped (0.593); manifest 16. Checked both in the browser.

**Next action** — team: round 4 size/timing; how to reach 30 exhibits ([[09-Open-Questions]]).

## 2026-11-01 evening — walkable 3D museum hall (directed by Ayaan and Kshiti)

- Team asked for a museum palace with a dome: first-person walking (WASD), artifacts on pedestals with details below, 360° view when near. Agent asked first; team chose: dome + galleries, E for close-up, placards with research facts only, laptop/desktop only.
- New `museum/index.html` + `museum/hall/` (`main.js`, `layout.js`, `building.js`, `textures.js`, `labels.js`, `hall.css`); three.js 0.170.0 via import map from jsDelivr; all textures procedural (canvas), no new image files. Old page renamed `list.html` / `list.js`, linked both ways by `#<artifact>`; `style.css` link style.
- Checks: `node --check` on all modules → ok; floor-plan walking tests in Node (n = 3…48: spots/zones right, slides around the centre stand and along walls, stops at gallery walls). Browser pane: hall, rotunda, gallery, placard, close-up, deep link from the list, E in/out, walking with keys, no new console errors. Pointer lock is refused in the app's pane → added the drag-to-look fallback (after the first failure, or a second one). Stress test `?repeat=3` → numbers in [[07-Results]]. `pytest -q` → 54 passed.

**Next action** — team: try the hall in a normal browser at full screen (pointer lock, feel); then round 4.

## 2026-11-01 night — round 4 started, entrance boards (directed by Ayaan and Kshiti)

- Team: the hall worked "perfect" in a normal browser (port 8765). Asked for round 4 to end around 06:30 and for entrance boards.
- `check_env.py` → ok. 20:27 → 10 h left at ~2.1 h/artifact (rounds 2–3) → **4 artifacts** (ranks 23–26, ETA ~05:00–05:30; 5 would run to ~07:00). `run_batch.py --count 27 --clean` started in-session 20:28 (20 level runs: `Ark_HM_192_HI`, `Ark_HM_711_HI`, `Ark_HM_1286_HI`, `Ark_HM_1299_Hi`); first time under the 15-min unplug grace. `Ark_HM_192_HI` L5 dense finished in 2 s (few images registered, to check).
- Museum: two signboards in the entrance lobby (lobby 3 → 5 m, spawn 1.4 m from the entrance): title board with the PDEU logo and name, team board. Checked in the browser pane (both readable, in view from the start); walking checks still pass; `pytest -q` → 54 passed.

**Next action** — when round 4 finishes: compare, summarize, export, results into the vault, commit.

## 2026-11-02 early morning — round 4 finished, round 5 started (directed by Ayaan and Kshiti)

- `batch.log`: `2026-11-02 04:02:33 batch done: 20 ok, 0 failed []`; no charger removal or sleep. `Ark_HM_192_HI` L5: 6 / 26 images registered → empty dense cloud, evaluated as failed (F 0); its preview step exit 1 (no points).
- Team rule (given during the run): if round 4 ends before 04:30, start one more artifact as round 5. Ended 04:02 → `check_env.py` → ok; `run_batch.py --count 28 --clean` started in-session 04:03 (`Ark_HM_1260C_HI`, 5 level runs).
- `compare_levels.py` for 192, 711, 1286, 1299; `summarize_round.py --count 27 --name round4` → see [[07-Results]].
- `export_glb.py --artifacts Ark_HM_192_HI Ark_HM_711_HI Ark_HM_1286_HI Ark_HM_1299_Hi` → exit 0 (ran ~11 min alongside round 5): all four added, 2.8–2.9 MB; manifest 20. 1299 surface F 0.924 (lowest exhibit; passes the mesh-vertex rule).
- Browser pane: hall plans 20 exhibits (South 1–3, Rotunda 4–11, East 12–14, North 15–17, West 18–20); close-ups of all four new exhibits by deep link (full reload; a hash change during a close-up is ignored by design). The pane renders black while hidden — show it before screenshots.

- Round 4 committed as Ayaan (`e5b8393`) and pushed.
- Round 5: `batch.log` `2026-11-02 04:23:50 batch done: 5 ok, 0 failed []` (21 min). `compare_levels.py --artifact Ark_HM_1260C_HI` → 153 / 56 / 26 / 12 / 6 registered, F 0.070 / 0.082 / 0.050 / 0.632 / 0.000; `summarize_round.py --count 28 --name round5`; `export_glb.py --artifacts Ark_HM_1260C_HI` → not exhibited (L3 mesh F 0.045), manifest still 20. `pytest -q` → 54 passed.

**Next action** — team: round 6 size/timing (12 artifacts left); the 30-exhibit question is now likely short ([[09-Open-Questions]]).

## 2026-11-02 night — next round started, 7 artifacts (directed by Ayaan and Kshiti)

- Team stopped after the 1-artifact round at 04:23, then asked for 7 more artifacts (they called it "round 5"; files use `round6` because `round5_*` already holds the `Ark_HM_1260C_HI` round).
- `check_env.py` → exit 0; on AC; D: 277 GB free. `run_batch.py --count 35 --clean` started in-session 23:07 (35 level runs: `Ark_HM_557_HI`, `Ark_HM_792_hi`, `Ark_HM_703_HI`, `Ark_HM_498_HI`, `Ark_HM_596_Hi`, `Ark_HM_259_HI`, `Ark_HM_611_HI`). Estimate ≈ 15 h at ~2.1 h/artifact, less if some fail early.

- Finished 2026-11-03 07:29: `batch done: 35 ok, 0 failed []`, 8.4 h, no charger removal or sleep. `preview_cloud.py` exit 1 on 6 L5 runs (no points).
- `compare_levels.py` for the 7; `summarize_round.py --count 35 --name round6` → see [[07-Results]]. Checked `git status` on configs/src/scripts: no changes, so the L5 drop is not from settings.
- `export_glb.py --artifacts <the 7>` → exit 0: 5 added (2.8–2.9 MB), 792 and 703 skipped; manifest 25. Browser pane: close-ups of all five, zones right, no console errors. `pytest -q` → 54 passed.

**Next action** — team: last round (5 artifacts, `--count 40`); 30 exhibits needs all five to pass ([[09-Open-Questions]]).

## 2026-11-03 morning — last round started, 5 artifacts (directed by Ayaan and Kshiti)

- `check_env.py` → exit 0; on AC; D: 273 GB free. `run_batch.py --count 40 --clean` started in-session 08:43 (25 level runs: `Ark_HM_658_HI`, `Ark_HM_393_HI`, `Ark_HM_1292_HI`, `Ark_HM_1288_HI`, `Ark_HM_209_HI`). Estimate 6–10 h (1.2–2.1 h/artifact in recent rounds).

**Next action** — when it finishes: `batch.log` check, compare, `summarize_round.py --count 40 --name round7`, export, vault, commit.

## 2026-11-03 morning — main gate and Excel summary (directed by Ayaan and Kshiti)

- Team asked for a main-gate entrance with a rotating yellow arrow that leads into the museum, and supplied 6 photos of the gate; also a summary of all 81 artifacts, then an Excel version kept up to date.
- `museum/hall/gate.js` (new): separate three.js scene (canopy, piers, closed gates, centre block with logo, guard room, forecourt, road, drive, trees, sky), arrow, ring, walk bounds. `main.js`: starts outside, `enterHall` fade, deep links and `teleport` go straight to the hall, map hidden at the gate; shadow map drawn once. `index.html`, `hall.css`: fade layer, menu text and button.
- Checks: `node --check` ok. Browser pane: gate view from three positions; holding W walked into the arrow → hall lobby, map back; deep link `#Ark_HM_498_HI` → close-up in the hall; no console errors. Pointer lock not testable in the pane (drag-look used), so full-screen mouse feel is not checked.
- `src/heritage3d/status.py`, `tests/test_status.py` (5 tests), `scripts/build_status_workbook.py`, `openpyxl` added (3.1.5). Run → `81 artifacts: 35 done, 1 in progress, 4 queued, 41 not run; museum 25 yes, 5 pending`; level medians computed from its cells match `round6_summary.csv` where the data is the same (L1 0.883, L4 0.984). **Formulas not recalculated here: LibreOffice is not installed and the file has not been opened in Excel by the agent** (Excel calculates them on opening). `pytest -q` → 59 passed.

- Team then supplied 9 Street View captures: `gate.js` rebuilt with the street (see [[08-Decisions]]), hazy sky, fog, 4096 px shadow map drawn once, clumped trees. Browser pane: views from the start point, the plaza's west side, the service road and the fence; Shift+W from the start → hall in 6.6 s; bounds checked with `hall.gate.move` (bikes, gate line, fence, street end); no console errors. If the pane is hidden when the page loads the canvas stays 0 × 0 until a reload (pane only, not seen in a normal tab; **to verify** in a normal browser).

- Team: SBI name on the booth, no plants in front of the gate, gates stay shut, a way back to the gate, third-person toggle, character switch. Done (see [[08-Decisions]]). Browser pane: `V`, `C`, walking in third person into the arrow, third-person camera at a rotunda pedestal, `E` close-up in and out, `G` and the pause-menu button shown; no console errors. Standing at the hall's spawn point the camera has only 1 m of room, so the figure is hidden until the visitor steps forward.

- Team: go back to the gate by a circle inside the museum, not a key. `museum/hall/portal.js` (new, shared arrow and circle), lobby 5 → 7.5 m, circle beside the entrance doors, `G` removed, pause-menu button kept. A first placement on the centre line blocked the third-person view on arrival, so it moved 2.4 m to the side. Browser pane: gate → hall → circle → gate round trip, both views, map marker, hint text; no console errors. `pytest -q` → 59 passed.

- Team asked to stop the batch when 393 finished (watcher armed), then at 12:38 to stop now and restart L1 later. Watcher stopped; `taskkill` on the batch's process tree at 12:38:24 → no pipeline tools left. 393 L1 had no evaluation file, so `pending()` still lists it; about 1 h of its work is lost (sparse 2077 s + 28 min of dense). `experiments/results/runs/Ark_HM_393_HI_L1.json` is a partial run file, overwritten on the redo; not to be committed before then. Team chose stylized characters, no photos, for now.

- Team asked to process 658 now. `compare_levels.py --artifact Ark_HM_658_HI`; `summarize_round.py --count 36 --name round7`; `export_glb.py --artifacts Ark_HM_658_HI` → exit 0, manifest 26; close-up checked in the browser pane; `pytest -q` → 59 passed. See [[07-Results]].

## 2026-11-04 — Resume the last round (Ayaan, Kshiti)

- Team asked how to shoot photos of themselves for a scanned character: guidance given (about 120 photos each); no photos received, nothing built, the no-photos decision stands.
- Team asked to push everything so far, then run the last 4 artifacts. `git rev-list` → no unpushed commits. Committed 393's finished L2–L5 run files, logs and plots and the Excel. Left out 393's partial L1 run file and L1 logs, which the redo overwrites. `build_status_workbook.py` → 36 done, 1 in progress, 3 queued, 41 not run; museum 26 yes, 4 pending. `pytest -q` → 59 passed. `check_env.py` → OK.

- Batch finished 06:14: 16 ok, 0 failed. `compare_levels.py` on the four artifacts; `summarize_round.py --count 40 --name round7`; `export_glb.py --artifacts Ark_HM_393_HI Ark_HM_1292_HI Ark_HM_1288_HI Ark_HM_209_HI` → exit 0, manifest 30. Browser pane: 30 / 30 loaded, no console errors, close-ups of Nos. 27–30 checked. An odd top-down view of No. 27 came from my test teleporting onto the plinth, not from the model. `build_status_workbook.py` → 40 done, 41 not run; museum 30. `pytest -q` → 59 passed. See [[07-Results]].

- Team asked to try artifacts with at least 70% of sample views uncut: 19 qualify (`dataset_inspection.json`). Trial with a one-artifact order file in the scratchpad: `run_batch.py --count 1 --levels L3 --clean --order ...` on `Ark_HM_640_HI` → 1 ok, 0 failed, 22:37–22:48. `check_env.py` → OK. Results not exported or committed yet. See [[07-Results]].

- Team chose to run the other 18 at L3: `run_batch.py --count 19 --levels L3 --clean --order configs/artifact_order_cutoff.json`.

- Batch finished 01:52: 18 ok, 0 failed. 14 of 19 pass the exhibit rule. Previews checked by eye, and doubtful ones compared with source photos. `summarize_round.py --count 19 --name cutoff_l3 --order configs/artifact_order_cutoff.json`. `status.py` and `build_status_workbook.py`: cut-off artifacts that were run now show as "Partly run", and the per-level Summary table covers the main set only. Rebuild → 40 done, 19 partly run, 22 not run; museum 30 yes, 14 pending. `pytest -q` → 60 passed.

- Team asked for a second floor with stairs, holding the 14 passing artifacts. `export_glb.py` for the 19 → 14 exported, 5 skipped by the rule, 44 in `museum/artifacts.json`, which now records each exhibit's `set` and, for the cut-off set, `cut_off_fraction`. `museum/hall/`: `layout.js` (stairs, upper gallery, floor height), `building.js` (stair hall, two flights, rails, signs, generalized `gallery()`), `main.js` (heights for camera, target and figure), `labels.js` (wall board, placard line), `character.js`; `list.js` shows the frame share too.
- First load failed: `mergeGeometries` needs indexed geometry and `ExtrudeGeometry` is not; fixed with `mergeVertices`. The pane kept serving the old `building.js` until a hard reload. Pane hidden read about 20 fps everywhere (a limit, not a measurement); visible: 60 fps in all five views. Rebuild → 40 done, 19 partly run, 22 not run; museum 44 yes, 0 pending. `pytest -q` → 60 passed.

- Team asked to see the museum from outside through the main gate. New `museum/hall/exterior.js` builds it from `plan.rooms`; `gate.js` shortens the drive, adds the paved court and drive sign, clears trees from the view from the start spot and adds trees behind the building; `main.js` passes the plan. First position (entrance at z = -62) left the arrow over most of the dome; moved to z = -48, then lowered the portico and raised the drum because the gable hid the dome. Checked in the pane: 60 fps at three gate positions, hall still 60 fps at the busiest view, no console errors. `pytest -q` → 60 passed. A first 37 fps reading was my script's error (its timer included a teleport and a wait) and is not a result.

- Team asked to make the drive walkable. `gate.js`: gates swung open, new walkable areas (gateway, drive, court, portico) with `free()`-based `move()`, ground `height()` for the steps, arrow moved to the doors; `exterior.js` exports the portico's measures; `main.js` uses the gate's height, shows a hint to walk up the drive and adds `hall.position()` as a test aid; `index.html` text updated. Checked: `hall.gate.move` route from the street round the centre block to the doors (never stuck; floor rises to 0.9 m), six wall tests blocked, W key enters the museum from the portico. Not checked: a full walk at normal speed or the frame rate, because the pane stayed hidden (about 5 fps, and it left the canvas at 0 × 0 until a resize event was sent). `pytest -q` → 60 passed.

- Team asked to leave by the doors: the lobby circle now places the visitor on the portico facing the gate (`gate.doorstep`, `placeOnDoorstep()` in `main.js`); the pause menu's button still goes to the main gate. Team also confirmed the lawns stay out of bounds.

- Team asked whether the RQs were answered and whether the combined cost-effectiveness inputs were stored. All six sheets of the literature workbook read: it lists the cost metrics with no combining formula. Built the trade-off analysis it calls for: `src/heritage3d/tradeoff.py`, `tests/test_tradeoff.py`, `scripts/analyze_tradeoff.py`; `compare.py` also passes on RMSE and F at 0.005 and 0.01 R. Ran `python scripts/analyze_tradeoff.py`: results in [[07-Results]], and the 30 artifacts sufficient at L3 or below match the 30 exhibits. `pytest -q` → 68 passed. Plots checked by eye; one set of colliding labels fixed.

- Team asked to measure visual fidelity, then to stop at the pilot as they were leaving. Added `src/heritage3d/visual.py`, `tests/test_visual.py`, `scripts/evaluate_visual.py`. Ran `evaluate_visual.py --artifacts Ark_HM_658_HI --levels L5 L4 L1 --museum --previews` and `--artifacts Ark_HM_1260B_HI --levels L5 --previews`: both finished, results in [[07-Results]]; comparison images for L4 and the museum GLB checked by eye. `pytest -q` → 78 passed. Full run not started.

**Next action** — team: walk from the gate up the drive into the museum and to the upper floor in a normal browser. Then run the full visual fidelity measurement overnight, measure RQ3's remaining costs, and write up RQ1–RQ3.

## 2026-11-05 to 06 — visual fidelity, full run (directed by Ayaan Goel and Kshiti Bhavsar)

- Team said "START" on return; the full measurement ran in the background from 21:41 to 06:15 (`evaluate_visual.py` for 40 × 5 levels, the 19 cut-off artifacts at L3, then `--museum`): 263 results, exit 0, no errors in `experiments/logs/visual_full.log`. 8.8 h against my estimate of about 17 h: L1 took a median 412 s per model, not the pilot's 814 s.
- New `scripts/analyze_visual.py`; ran it: tables and plots listed in [[07-Results]]. Plots checked by eye; median labels moved under the axis to stop them overlapping the dots. `pytest -q` → 78 passed.

- Team asked to measure RQ3's rendering and download cost. Added `scripts/export_full_glb.py` (ran: 44 full models, 670 MB, outside the repo), `scripts/bench_server.py`, `bench/index.html`, `bench/bench.js`, `scripts/analyze_rq3.py`. First timing method was tied to the display refresh (every model 16.6 ms); switched to offscreen batches of 30 draws. Ran the benchmark locally and at 20 Mbit/s, then `analyze_rq3.py`: results in [[07-Results]]. Plot checked by eye; subtitle fixed. Also corrected in [[07-Results]] an unsupported claim that L1 textures were larger. `pytest -q` → 78 passed.

- Team asked for the results write-up ("Yes, draft it"). Wrote `docs/report/results.md`: setup, RQ1–RQ3 with tables and answers, H1–H3 verdicts, limitations, figure and source-file list. Every number checked against `tradeoff_*.csv`, `visual_*.csv`, `rq3_summary.csv`; museum-against-full geometry over all 44 exhibits computed from `experiments/results/museum/*_glb.json` (largest surface-F change 0.0003, Chamfer 0.3%) and added to [[07-Results]]. Corrected "a fiftieth" to "a sixty-fifth" of L5's PSNR loss in [[07-Results]]. Nothing re-run.

**Next action** — team reads the draft and sends it to Prof. Singh with the two open points (Option A, joint trade-off reporting).

