# Results: RQ1–RQ3 and H1–H3 (draft)

> **Draft for the project report.** Every number below comes from a committed result file (listed in Section 7) and from real runs on this project's laptop. Two team decisions to show the mentor: the geometric evaluation compares the RGB reconstructions with reference geometry from the CHSD depth maps (Option A, planned when the dataset was chosen), and cost-effectiveness is reported side by side with a combined score on top (Section 3.1).

## 1. What was measured

**Data.** The Cultural Heritage Synthetic Dataset (CHSD) gives 81 artifacts, each rendered from 360 azimuths × 5 elevations at 800 × 600 px on a black background, with a depth map per view. The **main set** is 40 artifacts that are never cut off by the frame in the sample views, processed in a fixed order (`configs/artifact_order.json`). A separate **cut-off set** of 19 artifacts, cut off in at most 30% of sample views, was run at L3 only and is reported apart.

**Acquisition effort.** Five image subsets of the same artifact, made by widening the azimuth step on every elevation ring (the two pole views are always kept):

| Level | Azimuth step | Images |
|---|---|---|
| L1 | 3° | 362 |
| L2 | 6° | 182 |
| L3 | 12° | 92 |
| L4 | 24° | 47 |
| L5 | 45° | 26 |

**Pipeline.** One frozen configuration for every run, RGB images only: COLMAP 4.2.1 (CPU build) for structure from motion, then OpenMVS 2.4.0 (CPU) for the dense point cloud, mesh and texture. Hardware: HP Envy x360, Intel i7-1255U, 16 GB RAM, Intel Iris Xe graphics, no CUDA. 200 main-set runs (40 artifacts × 5 levels), each timed with its peak memory.

**Geometric quality.** The reconstruction is aligned to the CHSD frame through its cameras and compared with a reference point set built from all 1,800 depth maps of the artifact. Distances are in units of R, the camera-to-object-centre distance. The main measure is the **F-score at 0.002 R**: the harmonic mean of precision (share of reconstructed points within 0.002 R of the reference) and recall (share of the reference within 0.002 R of the reconstruction). It is reported for the dense cloud and for the mesh vertices. Depth maps are used for evaluation only, never as reconstruction input.

**Visual quality.** Each textured model is rendered with the ideal CHSD camera from 12 **held-out views** that no level uses (azimuths 7°, 97°, 187°, 277° × elevations −45°, 0°, 45°) and compared with the CHSD image of that view: PSNR, SSIM and silhouette IoU, over the union of both silhouettes, so missing parts count against the model.

**Optimized models (museum).** Every artifact whose L3 mesh reaches F ≥ 0.95 is exported for the web museum as a GLB: decimated to about 100,000 triangles, texture at most 2048 px JPEG. 30 main-set and 14 cut-off artifacts pass, 44 in all. For RQ3 each is compared with a "full" GLB of the same L3 mesh, undecimated, with a lossless texture.

**Statistics.** Differences between levels are paired on the same 40 artifacts: median difference, bootstrap 95% interval of the median (10,000 resamples), Wilcoxon signed-rank test with Holm's correction within each table.

## 2. RQ1 — How does acquisition effort affect geometric and visual quality?

**Table 1.** Quality by level, medians over the 40 main-set artifacts.

| Level | Images | Mesh F | Cloud F | Cloud precision | Cloud recall | PSNR (dB) | SSIM | Silhouette IoU | Mesh F ≥ 0.95 | No dense cloud |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 362 | 0.984 | 0.883 | 0.795 | 0.996 | 29.55 | 0.918 | 0.995 | 31 / 40 | 0 |
| L2 | 182 | 0.982 | 0.925 | 0.868 | 0.994 | 29.03 | 0.919 | 0.995 | 31 / 40 | 0 |
| L3 | 92 | 0.989 | 0.965 | 0.938 | 0.994 | 29.25 | 0.924 | 0.995 | 30 / 40 | 0 |
| L4 | 47 | 0.988 | 0.984 | 0.981 | 0.988 | 29.20 | 0.922 | 0.995 | 28 / 40 | 1 |
| L5 | 26 | 0.580 | 0.583 | 0.996 | 0.413 | 14.39 | 0.595 | 0.791 | 5 / 40 | 14 |

F-scores at 0.002 R. Precision and recall cover only runs that produced a dense cloud.

**Table 2.** Paired differences against L1 (median, 95% interval, Holm-corrected p).

| Compare | Mesh F | p | Cloud F | p | PSNR (dB) | p | SSIM | p |
|---|---|---|---|---|---|---|---|---|
| L2 − L1 | 0.0000 (−0.0020, 0.0011) | 0.75 | +0.034 (0.030, 0.037) | < 0.001 | −0.34 (−0.58, −0.16) | < 0.001 | −0.0006 (−0.0036, 0.0010) | 0.92 |
| L3 − L1 | +0.0028 (0.0007, 0.0042) | 0.039 | +0.069 (0.060, 0.075) | < 0.001 | −0.41 (−0.75, 0.04) | 0.065 | +0.0035 (−0.0001, 0.0059) | 0.49 |
| L4 − L1 | +0.0011 (−0.0061, 0.0043) | 0.75 | +0.081 (0.065, 0.089) | 0.028 | −0.47 (−1.57, 0.07) | 0.065 | +0.0048 (−0.0066, 0.0087) | 1.0 |
| L5 − L1 | −0.32 (−0.44, −0.20) | < 0.001 | −0.23 (−0.36, −0.12) | < 0.001 | −12.72 (−16.27, −8.72) | < 0.001 | −0.28 (−0.44, −0.19) | < 0.001 |
| L4 − L3 | −0.0002 (−0.0045, 0.0006) | 0.50 | +0.013 (0.007, 0.019) | 0.087 | +0.06 (−0.32, 0.40) | 0.69 | +0.0019 (−0.0036, 0.0042) | 1.0 |

**Findings.**

1. **From 362 down to 47 images, quality hardly changes.** Median mesh F stays between 0.982 and 0.989 from L1 to L4. No level is meaningfully better than L1 on the mesh: the largest median difference is 0.003. Appearance follows: L2 to L4 are within half a decibel of L1 in PSNR, with no significant SSIM difference and the same silhouettes (IoU 0.995).
2. **At 26 images (45° steps) quality collapses.** Median mesh F falls to 0.58 and PSNR to 14.4 dB; 14 of 40 runs produce no dense cloud at all, and recall falls to 0.41, meaning most of the object surface is missing. The collapse is a loss of coverage, not of accuracy: what L5 does reconstruct is precise (precision 0.996).
3. **More images did not give a better dense cloud.** Cloud F *rises* as images are removed, from 0.883 at L1 to 0.984 at L4, because precision falls with more images (0.981 at L4 against 0.795 at L1) while recall stays level. This is an effect at the tight tolerance only: at 0.01 R every level from L1 to L4 scores 0.998 or more, and meshing removes it. Why it happens is not established (hypothesis: extra, closely spaced views add slightly misplaced points that the fixed OpenMVS settings do not filter).
4. **L1 has a small PSNR lead** (0.34–0.47 dB in median, significant only against L2 after correction) that SSIM does not show. Its cause is not established; texture atlas size, which OpenMVS chooses per model, may play a part (hypothesis, not tested).
5. **Geometry and appearance agree.** Over the 200 main-set models, visual scores rank models much as geometry does (Spearman ρ against mesh F: 0.80 for PSNR, 0.87 for SSIM).
6. **Some objects fail whatever the effort.** 9 of 40 artifacts never reach mesh F 0.95 at any level, L1 included. The causes seen are structure from motion splitting the images into separate models (only the largest is densified) and small, plain, low-texture objects with few feature matches (the second cause is a hypothesis, not tested).

**Answer to RQ1.** Over this range, acquisition effort affects quality as a threshold, not a slope: once the azimuth step is 24° or finer (47 images or more), geometric and visual quality are at the same level as with 362 images; at 45° (26 images) coverage breaks down and both collapse. Above the threshold, more images bring no measurable gain on the mesh or in appearance, and a small loss of precision in the dense cloud.

## 3. RQ2 — What trade-off exists between effort, processing cost and quality?

**Table 3.** Cost by level, medians over the 40 artifacts, with the median share of the same artifact's L1 cost.

| Level | Images | Processing time | Peak RAM | Input images | Dense cloud | Textured mesh | Time for all 40 |
|---|---|---|---|---|---|---|---|
| L1 | 362 | 55.4 min | 4.4 GB | 103.7 MB | 260.2 MB | 23.9 MB | 40.1 h |
| L2 | 182 | 22.4 min (40%) | 2.3 GB (51%) | 52.2 MB (50%) | 147.2 MB (56%) | 22.9 MB (95%) | 15.5 h |
| L3 | 92 | 9.7 min (17%) | 2.0 GB (46%) | 26.4 MB (26%) | 73.5 MB (28%) | 21.4 MB (88%) | 6.3 h |
| L4 | 47 | 3.9 min (6.3%) | 2.0 GB (46%) | 13.6 MB (13%) | 28.2 MB (12%) | 18.1 MB (76%) | 2.7 h |
| L5 | 26 | 1.0 min (1.7%) | 2.0 GB (45%) | 7.5 MB (7.2%) | 5.8 MB (2.5%) | 5.4 MB (27%) | 0.8 h |

L5's costs are partly low because 14 of its runs produced no dense cloud and skipped the later stages.

**Table 4.** Applying one level to every artifact: how many reach mesh F ≥ 0.95, and at what total time.

| Policy | Artifacts reaching mesh F ≥ 0.95 | Total processing time |
|---|---|---|
| Every artifact at L1 | 31 | 40.1 h |
| Every artifact at L2 | 31 | 15.5 h |
| Every artifact at L3 | 30 | 6.3 h |
| Every artifact at L4 | 28 | 2.7 h |
| Every artifact at L5 | 5 | 0.8 h |
| Cheapest sufficient level per artifact (needs reference geometry, so hindsight only) | 31 | 2.6 h |

**Findings.**

1. **Processing cost grows faster than the number of images.** Across L1–L4, time grows as about images^1.34 (median per artifact), so doubling the images takes about 2.5 times as long. Exhaustive feature matching, which compares every pair of images, grows about with the square of the image count and took 60% of the L1 time in the pilot artifact. Peak RAM stops falling below L3 (about 2 GB, set by feature extraction), and the textured mesh shrinks little until L5.
2. **The quality curve is flat where the cost curve is steep.** L3 uses 25% of L1's images and 17% of its time, L4 13% and 6.3%, and both keep median mesh F within 0.003 of L1 (interval limits within 0.0061) and PSNR within 0.5 dB.
3. **The real trade-off is reliability against time, not quality against time.** Going from L4 to L3 more than doubles the time (2.7 h → 6.3 h for all 40) and recovers two more artifacts above the threshold; going further to L2 or L1 costs 15.5 h or 40.1 h and recovers one more. L4 is the most economical level and L3 the safer one; nothing finer than L2 gained anything here.
4. **The threshold choice changes little.** With a sufficiency threshold of mesh F 0.90, L4 is the cheapest sufficient level for 22 artifacts; at 0.98, for 20.

### 3.1 Combined cost-effectiveness score

The reviewed literature reports quality and the costs of acquisition and computation separately. To summarise them together, each level also gets one combined score between 0 and 1:

- **Quality** = mean of three parts, each between 0 and 1: median mesh F (shape), median SSIM (appearance), and the share of artifacts reaching mesh F ≥ 0.95 (reliability, so a cheap level that often fails scores low).
- **Saving** = 1 − mean of three cost shares against the same artifact's L1 run: processing time, peak RAM, and storage (input images + dense cloud + textured mesh). L1 has saving 0.
- **Score** = w × quality + (1 − w) × saving, with equal weights (w = 0.5) as the main setting.

The score summarises the side-by-side tables; it does not replace them. The weights are a choice, so the ranking is also checked for every quality weight from 0 to 1 in steps of 0.05.

**Table 5.** Combined score by level, equal weights.

| Level | Images | Mesh F | SSIM | Share sufficient | Time share | RAM share | Storage share | Quality | Saving | **Score** |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 362 | 0.985 | 0.918 | 0.775 | 1.000 | 1.000 | 1.000 | 0.893 | 0.000 | 0.446 |
| L2 | 182 | 0.982 | 0.919 | 0.775 | 0.396 | 0.507 | 0.568 | 0.892 | 0.510 | 0.701 |
| L3 | 92 | 0.989 | 0.924 | 0.750 | 0.167 | 0.456 | 0.309 | 0.887 | 0.689 | 0.788 |
| **L4** | 47 | 0.988 | 0.922 | 0.700 | 0.063 | 0.456 | 0.164 | 0.870 | 0.772 | **0.821** |
| L5 | 26 | 0.580 | 0.595 | 0.125 | 0.017 | 0.454 | 0.053 | 0.433 | 0.825 | 0.629 |

**Weight check.** L4 has the best score for every quality weight from 0.15 to 0.80, and L3 from 0.85 to 0.95. L1 is best only when cost is ignored entirely (w = 1), and L5 only when quality counts for 10% or less. L1 is last for every quality weight up to 0.60.

**Answer to RQ2.** Cost and quality are not traded smoothly. Processing cost rises steeply with image count (about images^1.34), while quality reaches its plateau at about 47 images and does not improve beyond it. The practical trade-off is between 47 images (lowest cost, 28 of 40 sufficient) and 92 images (2.3× the time, 30 of 40 sufficient); 182 or 362 images add cost without adding quality. The combined score agrees: with equal weights L4 is the most cost-effective level (0.82), followed by L3 (0.79), and this holds over a wide range of weights, so the conclusion does not hang on the weighting chosen.

## 4. RQ3 — Can an optimized model keep its fidelity while reducing storage and rendering cost?

The museum model (about 100,000 triangles, ≤ 2048 px JPEG texture) is compared with the full model of the same L3 mesh on all 44 exhibits.

**Table 6.** Museum model against full model, medians over 44 exhibits.

| Measure | Museum model | Full model | Museum as share of full |
|---|---|---|---|
| Triangles | 100,000 | 424,073 | 24% |
| File size | 2.9 MB | 15.7 MB | 19% |
| Surface F@0.002 R, change against full | −0.00002 (largest change 0.0003) | — | — |
| PSNR, change against full | −0.20 dB (−0.24, −0.16) | — | — |
| SSIM, change against full | −0.005 (−0.005, −0.004) | — | — |
| Download at 20 Mbit/s, measured | 1.53 s | 6.62 s | 23% |
| Decoding in the browser | 19.8 ms | 66.8 ms | 31% |
| GPU upload and first frame | 29.9 ms | 34.7 ms | 85% |
| Drawing one frame (1280 × 720) | 0.56 ms | 1.19 ms | 43% |
| GPU memory, estimated (geometry + texture) | 2.5 + 21.3 MB | 10.9 + 21.3 MB | |

Browser costs were measured in Chrome on the team laptop with three.js, three runs per model (median). Downloads were sent at a fixed simulated 20 Mbit/s from a local server. Drawing was timed offscreen in batches of 30 frames per GPU read-back, because timing single frames was locked to the display's 60 Hz refresh.

**Whole collection (44 exhibits):** 129.6 MB against 669 MB; measured download at 20 Mbit/s 68 s against 281 s. Calculated from file size at 10 Mbit/s: about 109 s against 561 s. Measured times were a median 1.10× the size-over-bandwidth calculation, so the calculated figures are reliable for this setup. Estimated GPU memory for the whole hall: about 1.0 GB against 2.0 GB.

**Findings.**

1. **Decimation costs no measurable geometry.** Surface F changes by at most 0.0003 and Chamfer distance by at most 0.3% on any exhibit: reconstruction error, not tessellation, dominates the accuracy.
2. **The visual cost is small and consistent.** 0.20 dB PSNR and 0.005 SSIM, lower on 43 and 44 of 44 exhibits respectively. That is smaller than the gap between L1 and L3, and about one sixty-fifth of L5's loss (12.7 dB).
3. **Download is the largest saving and the largest cost.** Files are 19% of the full size and download in 23% of the time; decoding takes 31% and drawing 43%. GPU upload saves least (85%), because both versions carry the same texture.
4. **Texture dominates GPU memory.** Most models of both kinds carry a 2048 px texture (21.3 MB on the GPU with mipmaps), so decimation cuts geometry memory by 77% but total memory far less. The 10 full models with 4096 px textures had the slowest first frames (110–153 ms).
5. **The whole museum runs interactively on integrated graphics.** The walkable hall with all 44 museum models held 60 fps in every measured view on the Iris Xe (up to 4.25 M triangles and 108 draw calls on screen), in the app's browser pane at 746 × 630 px. A full-screen window has not been measured.

**Answer to RQ3.** Yes, on this hardware. The optimized model keeps its geometric accuracy unchanged and loses only 0.2 dB of PSNR, while cutting file size and download time to about a fifth to a quarter, decoding to a third and drawing to under half. Further GPU-memory savings would have to come from the texture, not the geometry.

## 5. Hypotheses

| Hypothesis | Verdict | Evidence |
|---|---|---|
| **H1:** Reducing input images reduces computational requirements, but excessive reduction decreases reconstruction quality and completeness. | **Supported**, with a limit on memory | Time falls to 6.3% of L1 at L4 and 1.7% at L5; input and cloud size fall with images. Peak RAM stops falling below L3 (about 2 GB). Quality and completeness collapse at L5: recall 0.41, mesh F 0.58, PSNR 14.4 dB, 14 runs with no cloud. |
| **H2:** There is a practical range in which substantially fewer images give quality comparable to a much larger set. | **Supported** | L3 (92 images) and L4 (47 images) keep median mesh F within 0.003 of L1 (362 images) and PSNR within 0.5 dB, at 17% and 6.3% of the time; they have the best combined score for every quality weight from 0.15 to 0.95. No equivalence margin was fixed in advance, so this is stated as measured differences with intervals, not as a formal equivalence test. |
| **H3:** Model optimization can reduce storage and rendering requirements while keeping sufficient visual quality for an interactive virtual museum. | **Supported** | File size 19%, download 23%, decoding 31%, drawing 43% of the full model, for 0.20 dB PSNR, 0.005 SSIM and no measurable geometric change; the 44-exhibit hall runs at 60 fps on integrated graphics. |

## 6. Limitations

- **Synthetic data.** CHSD images are renders with ideal cameras, uniform lighting and a black background. These are controlled benchmark results, not universal claims about real museum photography; real-world validation is future work.
- **One pipeline, one machine.** One frozen COLMAP + OpenMVS configuration on one laptop CPU; times and memory are single runs per level, not repeated. Other software or settings may move the thresholds (for example, the precision loss at L1 may depend on OpenMVS's fusion settings).
- **Selection of artifacts.** The 40-artifact main set excludes artifacts cut off by the frame; the cut-off set was run at L3 only, so it gives no level comparison. Its reference shares the framing, so its F-scores may not fully penalise parts outside the frame (hypothesis).
- **Evaluation choices.** The geometric reference (Option A) and the 0.002 R tolerance were fixed before the comparison; the mentor has not yet reviewed them.
- **Combined score.** Its parts and equal weights are the team's choice, not a standard from the literature. The weight check shows the ranking of L3 and L4 holds over most weightings, but a different set of parts could move it.
- **Visual measures.** PSNR and SSIM against the dataset's own renders, unlit; no perceptual or user study (out of scope).
- **Browser costs.** One laptop and one browser; bandwidth simulated on a local server with no latency; the site is not hosted yet. GPU memory is calculated from decoded sizes, not read from the driver.
- **No sufficiency rule without reference geometry.** The cheapest sufficient level per artifact can only be found in hindsight; a real capture would choose one level in advance.

## 7. Figures and source files

| Figure | File |
|---|---|
| Quality against processing time, all 200 runs | `experiments/plots/tradeoff_quality_vs_time.png` |
| Cost by level | `experiments/plots/tradeoff_cost_by_level.png` |
| Cheapest sufficient level per artifact | `experiments/plots/tradeoff_sufficient.png` |
| Combined score against the quality weight | `experiments/plots/tradeoff_score.png` |
| Visual quality by level | `experiments/plots/visual_by_level.png` |
| Museum model against full model, visual | `experiments/plots/visual_museum.png` |
| Museum model against full model, browser costs | `experiments/plots/rq3_costs.png` |

| Numbers in | Source file | Made by |
|---|---|---|
| Tables 1–4 (geometry and cost) | `experiments/results/tradeoff_levels.csv`, `tradeoff_paired.csv`, `tradeoff_policies.csv`, `tradeoff_sufficient.csv` | `scripts/analyze_tradeoff.py` |
| Table 5 and weight check | `experiments/results/tradeoff_score.csv`, `tradeoff_weights.csv` | `scripts/analyze_tradeoff.py` |
| Tables 1–2 (visual) | `experiments/results/visual_levels.csv`, `visual_paired.csv`, `visual_all.csv` | `scripts/analyze_visual.py` |
| Table 6 (geometry) | `experiments/results/museum/<artifact>_glb.json` | `scripts/export_glb.py` |
| Table 6 (browser) | `experiments/results/rq3_summary.csv`, `rq3_models.csv`, `rq3/bench_*.json` | `bench/`, `scripts/analyze_rq3.py` |
| Hall frame rates | `vault/07-Results.md`, "Museum upper floor" | measured in the browser pane |
| Per-run data | `experiments/results/runs/<artifact>_<level>{,_eval}.json` | `scripts/run_batch.py` |
