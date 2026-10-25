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

**Next action** — see [[00-Home]].
