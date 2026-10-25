# Project Definition (frozen)

Source: `docs/literature/Literature_Review_Cultural_Heritage_Artifacts_FINAL.xlsx` → sheet "Final Project Definition". Changes need an explicit team decision logged in [[08-Decisions]].

## Problem

How much image acquisition effort is necessary to obtain a reconstruction that is sufficiently accurate and visually suitable for digital preservation and virtual-museum presentation?

## Research gap (from the team's reviewed literature)

Existing studies demonstrate low-cost photogrammetric digitization and quantitative reconstruction evaluation, but there is comparatively limited systematic analysis of the relationship between image acquisition effort, computational cost and reconstruction quality for individual cultural heritage artifacts under a controlled, reproducible setup.

## Research questions

- **RQ1 — Quality:** How does variation in image acquisition effort affect the geometric and visual quality of 3D reconstructions of individual cultural heritage artifacts?
- **RQ2 — Efficiency:** What trade-off exists between image acquisition effort, reconstruction processing cost and resulting 3D model quality?
- **RQ3 — Application:** Can an optimized reconstruction retain sufficient geometric and visual fidelity for interactive virtual-museum presentation while reducing storage and rendering requirements?

## Hypotheses

- **H1:** Reducing input images reduces computational requirements, but excessive reduction decreases reconstruction quality and completeness.
- **H2:** There is a practical image-acquisition range in which substantially fewer images give quality comparable to a much larger image set.
- **H3:** Model optimization can reduce storage/rendering requirements while retaining sufficient visual quality for interactive virtual-museum presentation.

## Contribution

A controlled, reproducible acquisition-to-quality evaluation framework linking image acquisition effort and computational requirements with geometric/visual reconstruction quality, followed by web-based visualization. The novelty is the controlled framework and its integration — not a new reconstruction algorithm.

## Deliverables

1. Reproducible reconstruction + evaluation pipeline (scripts, configs).
2. Quality-vs-cost results across subset levels (tables, plots).
3. Optimized web-ready GLB model(s).
4. **Web-based virtual museum — compulsory** (decided 2026-10-25).

## Out of scope

New SfM/MVS algorithms; NeRF/3DGS comparison study; segmentation/classification; condition monitoring; extensive software comparison; VR/HCI user study; proprietary scanning hardware; YOLO / neural network training; urban asset management.

## Known limitation

CHSD is synthetic. Results are controlled benchmark findings, not universal claims about real museum photography. Real-world validation is optional future work.
