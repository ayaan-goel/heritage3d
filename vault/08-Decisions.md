# Decisions

| Date | Decision | Reason |
|---|---|---|
| 2026-10-25 | Project definition, RQ1–3, H1–3 and scope frozen as in the literature workbook | Agreed before mid-term |
| 2026-10-25 | CHSD is the only core dataset | Controlled multi-view RGB + reference depth |
| 2026-10-25 | Web-based virtual museum is a **compulsory** deliverable | Team decision |
| 2026-10-25 | Subset levels by azimuth step: 3°, 6°, 12°, 24°, 45° (L1–L5) | Integer counts, uniform coverage, ~halving; replaces 100/50/25/12.5/6.25% |
| 2026-10-25 | Depth maps used for evaluation only, never as reconstruction input | Using the reference as input makes evaluation circular and turns the study into RGB-D fusion, against the camera-only cost-effective goal |
| 2026-10-25 | COLMAP (CPU) for SfM + OpenMVS (CPU) for dense/mesh/texture | Laptop has Intel Iris Xe, no CUDA |
| 2026-10-25 | Experiments run on the team laptop; cloud agent writes code/docs/museum | Cloud session: no GPU, limited disk, ephemeral, Zenodo blocked |
| 2026-10-25 | Data stored on D: outside the repo | More free space; keeps repo small |
| 2026-10-25 | Vault updates are mandatory every session | Context must survive agent/session switches |
| 2026-10-25 | Commit authorship split between Ayaan and Kshiti, switching after an irregular number of commits; no AI attribution | Both work together on one machine and direct every session (replaces the earlier per-director rule) |
| 2026-10-25 | Presentation rules dropped for now | Focus is the working project; presentation discussed later |
