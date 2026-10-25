# heritage3d — rules for coding agents

Cost-effective image-based 3D digitization of individual cultural heritage artifacts for a web-based virtual museum.
Team: Ayaan Goel, Kshiti Bhavsar. Mentor: Ms. Komal Singh.

## 1. The vault is mandatory

`vault/` is the project's memory (an Obsidian vault). It is the source of truth for decisions, dataset facts and status.

- **Start of every session:** read `vault/00-Home.md`, then the notes relevant to the task.
- **End of every session (and before every commit that changes code, data handling or decisions):** update the vault. This is required, not optional. A session is not finished until it is done.
  - Append an entry to `vault/10-Session-Log.md`: date, who directed the session, what changed, files touched, commands run **with their real outcomes**, next action.
  - Update `vault/00-Home.md` → "Current status" and "Next action".
  - Record any decision in `vault/08-Decisions.md` (decision, reason, date).
  - Record new unknowns in `vault/09-Open-Questions.md`; close answered ones.
  - Update dataset facts in `vault/03-Dataset-CHSD.md`, results in `vault/07-Results.md`.
- Never write an unverified claim as fact. Tag it **(to verify)** or **(hypothesis)**.

## 2. Honesty rules

- Never invent dataset statistics, citations, metrics, results, or claim a command ran when it did not.
- Distinguish: verified fact / assumption / plan / measured result.
- Results come only from real runs on real data, with the config and log committed.

## 3. Scope (frozen — see `vault/01-Project-Definition.md`)

- Core experiment: same artifact → controlled image subsets (L1–L5) → same SfM + MVS pipeline → compare quality vs cost.
- Input to reconstruction is **RGB only**. CHSD depth maps are used **only for evaluation**.
- The web-based virtual museum is a **compulsory** deliverable.
- Out of scope unless explicitly agreed: new reconstruction algorithms, NeRF/3DGS studies, YOLO/neural network training, segmentation, condition monitoring, urban asset management, VR/HCI user studies.

## 4. Hardware reality

The team laptop is an HP Envy x360 16" with **Intel Iris Xe (no NVIDIA GPU, no CUDA)**, 16 GB RAM, Windows.
- COLMAP dense MVS needs CUDA → not available. Use COLMAP (no-CUDA build, CPU) for SfM and **OpenMVS (CPU)** for densify / mesh / texture.
- Pilot on one artifact before scaling. Record runtime and peak RAM.
- Commands given to the team must work on Windows (PowerShell).

## 5. Data and Git

- Never commit raw data, extracted images, point clouds, meshes or textures. Data lives outside the repo (see `vault/06-Environment-Setup.md`); paths come from `configs/`.
- Commit small artifacts only: configs, scripts, metrics (CSV/JSON), logs, plots, the final optimized GLB(s) for the museum if small.

## 6. Commits

- Author commits as the team member directing the session (`Ayaan Goel` or `Kshiti Bhavsar`). No AI attribution trailers.
- Small, focused commits with clear imperative messages (e.g. `Add subset generator for azimuth-step levels`).
- Prefer small, testable milestones over generating the whole system at once.
