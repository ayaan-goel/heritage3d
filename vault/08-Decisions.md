# Decisions

| Date | Decision | Reason |
|---|---|---|
| 2026-10-25 | Project definition, RQ1–3, H1–3 and scope frozen as in the literature workbook | Agreed before mid-term |
| 2026-10-25 | CHSD is the only core dataset | Controlled multi-view RGB + reference depth |
| 2026-10-25 | Web-based virtual museum is a **compulsory** deliverable | Team decision |
| 2026-10-25 | Subset levels by azimuth step: 3°, 6°, 12°, 24°, 45° (L1–L5) | Integer counts, uniform coverage, ~halving; replaces 100/50/25/12.5/6.25% |
| 2026-10-25 | Depth maps used for evaluation only, never as reconstruction input | Using the reference as input makes evaluation circular and turns the study into RGB-D fusion, against the camera-only cost-effective goal |
| 2026-10-25 | COLMAP (CPU) for SfM + OpenMVS (CPU) for dense/mesh/texture | Laptop has Intel Iris Xe, no CUDA |
| 2026-10-25 | Experiments run on the team laptop; cloud agent writes code/docs/museum (superseded 2026-10-29: agent now local) | Cloud session: no GPU, limited disk, ephemeral, Zenodo blocked |
| 2026-10-25 | Data stored on D: outside the repo | More free space; keeps repo small |
| 2026-10-25 | Vault updates are mandatory every session | Context must survive agent/session switches |
| 2026-10-25 | Commit authorship split between Ayaan and Kshiti, switching after an irregular number of commits; no AI attribution | Both work together on one machine and direct every session (replaces the earlier per-director rule) |
| 2026-10-25 | Keep Python 3.13 on the laptop (no downgrade) | Open3D 0.20.0 has 3.13 wheels; avoids reinstalling |
| 2026-10-25 | Tools in `C:\tools\colmap` and `C:\tools\openmvs`, both on user PATH | Scripts call `colmap` / OpenMVS tools by name |
| 2026-10-29 | Agent moves from cloud session to local Claude Code on the laptop | Team prefers working offline; agent can now run tools and experiments directly |
| 2026-10-25 | Presentation rules dropped for now | Focus is the working project; presentation discussed later |
| 2026-10-29 | `pole_rings = [-90, 90]`: one image (frame 0001) from each pole ring per level → L1–L5 = 362/182/92/47/26 images | Verified ±90° views are in-plane spins of one picture (IoU ≥ 0.991 on 40 well-framed artifacts); applies the 2026-10-25 rule |
| 2026-10-29 | Pick pilot/main artifacts from those not cut off by the image frame | 41/81 artifacts leave the frame in some views; partial views would confound the image-count comparison |
