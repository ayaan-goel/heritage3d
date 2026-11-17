"""Evaluation presentation (department's 20-point guideline, ~15 content slides + backups)
-> Deliverables/Presentation/heritage3d_Presentation.pptx"""
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

from common import DEPARTMENT, DESIGNATION, EVAL_DATE, FIG, GUIDE, LEVELS, OUT, PLOTS, PROGRAMME, RQ3, TEAM, TEAM_ID, TITLE, cite, references

NUMS, REFS = references()
C = lambda *k: cite(NUMS, *k)
NAVY, CLAY, SAGE, INK, MUTED, LIGHT, WHITE = (RGBColor(0x1D, 0x35, 0x57), RGBColor(0xB5, 0x56, 0x2F), RGBColor(0x4F, 0x7A, 0x5A),
                                             RGBColor(0x22, 0x22, 0x22), RGBColor(0x5A, 0x5A, 0x5A), RGBColor(0xF3, 0xEF, 0xE8), RGBColor(255, 255, 255))
FONT = "Calibri"
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
W, H = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]
count = {"n": 0}


def box(slide, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(1.25)
    s.shadow.inherit = False
    return s


def text(slide, x, y, w, h, paras, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, para in enumerate(paras if isinstance(paras, list) else [paras]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        bullet = isinstance(para, str) and para.startswith("• ")
        content = para[2:] if bullet else para
        if bullet:
            p.level = 0
        p.space_after = Pt(6)
        if bullet:
            r = p.add_run(); r.text = "•  "; r.font.size, r.font.name = Pt(size), FONT; r.font.color.rgb = color
        for j, chunk in enumerate(content.split("**")):
            if not chunk:
                continue
            r = p.add_run(); r.text = chunk
            r.font.size, r.font.name = Pt(size), FONT
            r.font.bold = bold or j % 2 == 1
            r.font.color.rgb = color
    return tb


def slide(title, kicker=None):
    s = prs.slides.add_slide(BLANK)
    count["n"] += 1
    box(s, 0, 0, Inches(0.18), H, NAVY)
    text(s, Inches(0.55), Inches(0.3), Inches(11.5), Inches(0.8), title, 30, NAVY, True)
    if kicker:
        text(s, Inches(0.57), Inches(0.98), Inches(12), Inches(0.5), kicker, 15, CLAY)
    box(s, Inches(0.57), Inches(1.42), Inches(1.2), Inches(0.05), CLAY)
    text(s, Inches(0.55), Inches(7.0), Inches(9), Inches(0.35), f"heritage3d · Team {TEAM_ID} · Ayaan Goel & Kshiti Bhavsar", 10, MUTED)
    text(s, Inches(12.2), Inches(7.0), Inches(0.8), Inches(0.35), str(count["n"]), 10, MUTED, align=PP_ALIGN.RIGHT)
    return s


def card(s, x, y, w, h, title, lines, color=NAVY, size=15):
    box(s, x, y, w, h, WHITE, RGBColor(0xDD, 0xD6, 0xCB), MSO_SHAPE.ROUNDED_RECTANGLE).adjustments[0] = 0.05
    box(s, x, y, w, Inches(0.08), color)
    text(s, x + Inches(0.15), y + Inches(0.15), w - Inches(0.3), Inches(0.5), title, size + 2, color, True)
    text(s, x + Inches(0.15), y + Inches(0.65), w - Inches(0.3), h - Inches(0.75), lines, size)


def grid(s, x, y, w, header, rows, size=13, col_w=None, hi=None):
    t = s.shapes.add_table(len(rows) + 1, len(header), x, y, w, Inches(0.38) * (len(rows) + 1)).table
    for i, hd in enumerate(header):
        c = t.cell(0, i); c.text = hd
        c.fill.solid(); c.fill.fore_color.rgb = NAVY
    for r, row in enumerate(rows, 1):
        for i, v in enumerate(row):
            c = t.cell(r, i); c.text = str(v)
            c.fill.solid(); c.fill.fore_color.rgb = RGBColor(0xE3, 0xEF, 0xE5) if hi == r else (LIGHT if r % 2 else WHITE)
    for r in range(len(rows) + 1):
        for i in range(len(header)):
            c = t.cell(r, i); c.margin_left = c.margin_right = Inches(0.06); c.margin_top = c.margin_bottom = Inches(0.03)
            for p in c.text_frame.paragraphs:
                for run in p.runs:
                    run.font.size, run.font.name = Pt(size), FONT
                    run.font.bold = r == 0 or hi == r
                    run.font.color.rgb = WHITE if r == 0 else INK
    if col_w:
        for i, cw in enumerate(col_w):
            t.columns[i].width = Inches(cw)
    return t


def pic(s, path, x, y, w=None, h=None):
    return s.shapes.add_picture(str(path), x, y, w, h)


# 1 title -------------------------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK); count["n"] += 1
box(s, 0, 0, W, H, NAVY)
pic(s, FIG / "museum_rotunda.jpg", Inches(7.4), 0, h=H).crop_left = 0.18
box(s, Inches(7.4), 0, Inches(0.12), H, CLAY)
text(s, Inches(0.6), Inches(0.6), Inches(6.5), Inches(0.4), "MINOR PROJECT · END-SEMESTER EVALUATION", 13, RGBColor(0xF0, 0xC9, 0xB5), True)
text(s, Inches(0.6), Inches(1.15), Inches(6.6), Inches(2.6), TITLE, 32, WHITE, True)
text(s, Inches(0.6), Inches(3.95), Inches(6.5), Inches(1.0), [f"{n}  ·  {r}" for n, r in TEAM], 18, WHITE)
text(s, Inches(0.6), Inches(4.95), Inches(6.5), Inches(1.6), [
    f"Mentor: {GUIDE}, {DESIGNATION}", PROGRAMME, f"{DEPARTMENT}, School of Technology", "Pandit Deendayal Energy University, Gandhinagar",
    f"Team {TEAM_ID} · {EVAL_DATE}"], 13, RGBColor(0xDD, 0xE3, 0xEC))

# 2 introduction and problem ---------------------------------------------------------------------------
s = slide("Introduction and problem statement", "Photographs in, 3D model out, but how many photographs?")
text(s, Inches(0.6), Inches(1.75), Inches(6.2), Inches(5), [
    "• Museums hold far more artifacts than they can show; many are fragile or far from the people who study them.",
    "• **Image-based 3D reconstruction** (photogrammetry) builds a 3D model from ordinary photos: **SfM** finds camera positions, **MVS** builds a dense surface " + C("colmap", "openmvs") + ".",
    "• It needs only a camera and free software, so it suits small museums and colleges " + C("Medina JJ, Maley JM, Sannapareddy S, Medina NN, Gilman CM, McCormack JE") + ".",
    "• **But every photo costs** capture time, storage and processing time; too few photos leave parts missing."], 17)
card(s, Inches(7.2), Inches(1.8), Inches(5.6), Inches(4.6), "Problem statement", [
    "How much image acquisition effort is necessary to obtain a reconstruction that is sufficiently accurate and visually suitable for digital preservation and virtual-museum presentation?",
    "", "Who is affected: museums, archives and colleges digitizing collections with modest hardware."], CLAY, 17)

# 3 motivation, aim and objectives ---------------------------------------------------------------------
s = slide("Motivation, aim and objectives")
card(s, Inches(0.6), Inches(1.75), Inches(4.0), Inches(4.9), "Why it matters", [
    "• Capture and computing budgets can be planned on a normal laptop",
    "• A controlled, reproducible framework instead of separate reports of quality or cost",
    "• Visitors get light, faithful models that load fast",
    "• Open-source, CPU-only tools match the hardware small institutions have"], SAGE, 15)
card(s, Inches(4.85), Inches(1.75), Inches(7.9), Inches(4.9), "Aim and objectives", [
    "**Aim:** quantify how image acquisition effort affects the quality and cost of 3D reconstruction of single heritage artifacts, and deliver suitable models in a web virtual museum.",
    "• **Design** a controlled experiment: same artifact, 5 image subsets, one frozen pipeline",
    "• **Implement** a reproducible CPU-only reconstruction and evaluation pipeline",
    "• **Evaluate** shape, appearance and cost for 40 artifacts",
    "• **Compare** levels with paired tests and a combined cost-effectiveness score",
    "• **Optimise** models for the web and measure download and drawing cost",
    "• **Develop** a walkable web-based virtual museum"], NAVY, 15)

# 4 RQs, scope -----------------------------------------------------------------------------------------
s = slide("Research questions, scope and assumptions")
grid(s, Inches(0.6), Inches(1.75), Inches(7.4), ["", "Research question"], [
    ("RQ1", "How does acquisition effort affect geometric and visual quality?"),
    ("RQ2", "What trade-off exists between effort, processing cost and quality?"),
    ("RQ3", "Can an optimised model keep its fidelity while cutting storage and rendering cost?"),
    ("H1", "Fewer images cut cost; too few cut quality and completeness"),
    ("H2", "A practical range of far fewer images matches a large set"),
    ("H3", "Optimisation cuts storage/rendering cost with sufficient quality")], 14, [0.7, 6.7])
card(s, Inches(8.3), Inches(1.75), Inches(4.5), Inches(4.9), "Scope", [
    "**In:** single artifacts, one public dataset (CHSD), RGB-only input, COLMAP + OpenMVS on CPU, shape + look + cost evaluation, web museum",
    "**Out:** new algorithms, NeRF / Gaussian Splatting study, neural training, user studies",
    "**Assumes:** synthetic renders stand in for a controlled capture; dataset depth maps are accurate reference geometry"], CLAY, 14)

# 5 literature ----------------------------------------------------------------------------------------
s = slide("Review of existing work", "29 papers (2011–2026) in four themes: artifact digitization, reconstruction, low-cost capture, virtual museums")
grid(s, Inches(0.6), Inches(1.75), Inches(12.2), ["Work", "Approach", "Measures", "Limitation for our question"], [
    ("Guidi et al. 2015 " + C("Guidi, Micoli & Gonizzi Barsanti"), "Image-based capture vs laser reference", "Uncertainty, deviation", "Few objects; no computing cost"),
    ("Medina et al. 2020 " + C("Medina JJ, Maley JM, Sannapareddy S, Medina NN, Gilman CM, McCormack JE"), "Cost-effective museum photogrammetry", "Capture time, quality, cost", "Image count not varied"),
    ("Croce et al. 2024 " + C("Tzanetakis et al."), "NeRF vs photogrammetry", "Completeness, fidelity, efficiency", "Compares methods, not effort"),
    ("Maté-González et al. 2025 " + C("Maté-González et al."), "SfM vs NeRF vs Gaussian Splatting", "RMS, Chamfer", "Very small objects; one image set"),
    ("Rattanarungrot et al. 2025 " + C("Rattanarungrot et al."), "Optimised web 3D delivery", "Fidelity, web access", "Capture effort not studied"),
    ("Balado et al. 2025 " + C("Balado et al."), "Review of low-cost 3D mapping", "Cost, accuracy", "No controlled experiment")],
    13, [3.1, 3.3, 2.6, 3.2])
text(s, Inches(0.6), Inches(5.25), Inches(12.2), Inches(1.4), [
    "• Established: photogrammetry of artifacts, SfM-MVS, low-cost capture and web museums all work " + C("Pepe, Alfio & Costantino", "Raykovska et al.", "Virtual museums: Captured reality and 3D modeling") + ".",
    "• Most studies add hardware, compare methods or devices, or focus on sites and user experience."], 15)

# 6 gap -------------------------------------------------------------------------------------------------
s = slide("Research gap and contribution")
card(s, Inches(0.6), Inches(1.75), Inches(6.0), Inches(4.8), "What is missing", [
    "• Image count is rarely **varied systematically** for single artifacts",
    "• Acquisition effort, **computing cost** and **quality** are seldom measured together on the same objects",
    "• Results are rarely carried through to **web delivery** with measured costs",
    "Gap Matrix of our review: acquisition and compute costs are often not treated together with model quality."], CLAY, 16)
card(s, Inches(6.9), Inches(1.75), Inches(5.9), Inches(4.8), "Our contribution", [
    "A **controlled, reproducible framework** that links image acquisition effort and computing cost to geometric and visual quality, per artifact, and carries the result to a working virtual museum.",
    "", "Not a new reconstruction algorithm: the novelty is the controlled joint analysis and its integration."], SAGE, 16)

# 7 architecture ---------------------------------------------------------------------------------------
s = slide("Proposed approach: pipeline", "Same artifact → 5 image subsets → same pipeline → compare quality against cost → deliver to the web")
pic(s, FIG / "pipeline.png", Inches(0.7), Inches(1.65), w=Inches(11.9))

# 8 methodology -----------------------------------------------------------------------------------------
s = slide("Methodology: levels and measures")
grid(s, Inches(0.6), Inches(1.75), Inches(4.6), ["Level", "Step", "Images"], [(l, st, n) for l, n, st, *_ in LEVELS], 15, [1.3, 1.4, 1.9])
text(s, Inches(0.6), Inches(4.25), Inches(4.6), Inches(2.4), [
    "Every n-th azimuth on all 5 camera rings; both pole views always kept, so coverage stays even.",
    "Only the number of images changes."], 14, MUTED)
card(s, Inches(5.5), Inches(1.75), Inches(3.6), Inches(4.9), "Shape", [
    "**F-score at 0.002 R** against reference geometry fused from all 1,800 depth maps " + C("tanks"),
    "F = 2·P·Rc / (P + Rc)", "Also Chamfer, Hausdorff95; checks at 0.005 R and 0.01 R"], NAVY, 14)
card(s, Inches(9.25), Inches(1.75), Inches(3.55), Inches(4.9), "Look and cost", [
    "**PSNR, SSIM** " + C("ssim") + ", silhouette IoU from 12 held-out views",
    "**Cost:** time, peak RAM, storage per run",
    "**Statistics:** paired Wilcoxon " + C("wilcoxon") + ", Holm " + C("holm") + ", bootstrap 95% CI",
    "**Score** = w·Quality + (1−w)·Saving, w = 0.5, checked for w = 0…1"], CLAY, 14)

# 9 setup -----------------------------------------------------------------------------------------------
s = slide("Experimental setup and requirements")
grid(s, Inches(0.6), Inches(1.75), Inches(7.6), ["Item", "Details"], [
    ("Laptop", "HP Envy x360, i7-1255U, 16 GB RAM, Intel Iris Xe (no CUDA)"),
    ("Reconstruction", "COLMAP 4.2.1 (CPU), OpenMVS 2.4.0 (CPU)"),
    ("Analysis", "Python 3.13, NumPy, SciPy, Matplotlib; 81 tests"),
    ("Web museum", "three.js r170 (WebGL), static site, GLB models"),
    ("Dataset", "CHSD: 81 artifacts × 360 azimuths × 5 rings, 800×600, depth maps " + C("chsd_rgb", "chsd_depth")),
    ("Main set", "40 artifacts never cut off by the frame; 19 cut-off artifacts at L3 apart")], 13, [1.7, 5.9])
card(s, Inches(8.5), Inches(1.75), Inches(4.3), Inches(4.9), "Conditions and ethics", [
    "• One frozen configuration for all 200 runs",
    "• Runs repeated if the laptop slept or ran on battery",
    "• Depth maps for evaluation only, never input",
    "• Data licence CC BY-NC-SA 4.0: non-commercial, attribution shown in the museum",
    "• No personal data involved"], SAGE, 14)

# 10 progress -----------------------------------------------------------------------------------------
s = slide("Work completed", "All objectives complete; every result comes from real runs with logs")
grid(s, Inches(0.6), Inches(1.75), Inches(7.3), ["Objective / phase", "Status"], [
    ("Dataset verified (MD5), 81 artifacts inspected", "Completed"),
    ("Pilot on one artifact, settings frozen", "Completed"),
    ("200 main-set + 19 cut-off reconstructions", "Completed"),
    ("Geometric + visual evaluation (263 models)", "Completed"),
    ("Trade-off analysis, statistics, combined score", "Completed"),
    ("Web optimisation + browser cost (44 models)", "Completed"),
    ("Virtual museum: gate, hall, 2 floors, 44 exhibits", "Completed"),
    ("Hosting the museum online", "Pending")], 13, [5.6, 1.7])
pic(s, FIG / "museum_gate.jpg", Inches(8.2), Inches(1.75), w=Inches(4.6))
pic(s, FIG / "museum_upper.jpg", Inches(8.2), Inches(4.45), w=Inches(4.6))

# 11 RQ1 ------------------------------------------------------------------------------------------------
s = slide("Results · RQ1: quality against effort", "Quality is a threshold, not a slope: 47 images match 362; 26 break down")
grid(s, Inches(0.6), Inches(1.75), Inches(6.3), ["Level", "Images", "Mesh F", "PSNR", "SSIM", "F ≥ 0.95"],
     [(l, n, f"{mf:.3f}", f"{ps:.1f}", f"{ss:.3f}", f"{ok}/40") for l, n, _, _, _, _, mf, _, ps, ss, ok, _ in LEVELS], 14, hi=4)
text(s, Inches(0.6), Inches(4.25), Inches(6.3), Inches(2.6), [
    "• L1–L4 within 0.003 mesh F and 0.5 dB PSNR (medians, 40 artifacts)",
    "• L5: mesh F 0.58; 14 of 40 runs give no dense cloud",
    "• More images lowered cloud precision (0.98 → 0.80) at the tight tolerance",
    "• 9 of 40 never pass at any level (split SfM models, plain objects)"], 14)
pic(s, PLOTS / "tradeoff_quality_vs_time.png", Inches(7.1), Inches(1.8), w=Inches(5.9))

# 12 RQ2 ------------------------------------------------------------------------------------------------
s = slide("Results · RQ2: trade-off and combined score", "Time grows as images^1.34; quality plateaus at 47 images")
grid(s, Inches(0.6), Inches(1.75), Inches(6.1), ["Level", "Time", "Share of L1", "Pass", "Score"],
     [(l, f"{t} min", sh, f"{ok}/40", f"{sc:.2f}") for l, _, _, t, sh, _, _, _, _, _, ok, sc in LEVELS], 14, hi=4)
text(s, Inches(0.6), Inches(4.25), Inches(6.1), Inches(2.6), [
    "• All 40 artifacts: L4 2.7 h (28 pass) · L3 6.3 h (30) · L1 40.1 h (31)",
    "• **L4 most cost-effective (0.82), L3 the safer choice (0.79)**",
    "• L4 best for quality weights 0.15–0.80, L3 for 0.85–0.95: the ranking does not hang on the weights"], 14)
pic(s, PLOTS / "tradeoff_score.png", Inches(6.95), Inches(1.85), w=Inches(6.0))

# 13 RQ3 ------------------------------------------------------------------------------------------------
s = slide("Results · RQ3: optimised models in the museum", "100k-triangle models keep their accuracy and lose only 0.2 dB PSNR")
grid(s, Inches(0.6), Inches(1.75), Inches(6.4), ["Measure (median, 44)", "Museum", "Full", "Share"], RQ3, 13, [2.9, 1.2, 1.2, 1.1])
text(s, Inches(0.6), Inches(4.65), Inches(6.4), Inches(2.2), [
    "• Shape change ≤ 0.0003 F; look −0.20 dB PSNR, −0.005 SSIM",
    "• Whole collection: 129.6 MB vs 669 MB; 68 s vs 281 s at 20 Mbit/s",
    "• Museum holds **60 fps** on integrated graphics with 44 exhibits"], 14)
pic(s, PLOTS / "rq3_costs.png", Inches(7.2), Inches(1.85), w=Inches(5.8))
pic(s, FIG / "museum_lobby.jpg", Inches(7.2), Inches(4.45), w=Inches(2.85))
pic(s, FIG / "museum_rotunda.jpg", Inches(10.15), Inches(4.45), w=Inches(2.85))

# 14 testing, challenges ------------------------------------------------------------------------------
s = slide("Evaluation approach, challenges and mitigation")
card(s, Inches(0.6), Inches(1.75), Inches(4.3), Inches(4.9), "How it was evaluated", [
    "• Paired comparison on the same 40 artifacts",
    "• Wilcoxon tests, Holm correction, bootstrap intervals",
    "• Threshold (F ≥ 0.95) fixed before analysis",
    "• 81 unit tests; preview image for every run",
    "• Museum: frame rate, triangles, draw calls per view"], NAVY, 14)
grid(s, Inches(5.15), Inches(1.75), Inches(7.65), ["Challenge", "Mitigation"], [
    ("No NVIDIA GPU / CUDA", "COLMAP CPU + OpenMVS CPU; pilot first"),
    ("200 long runs (65 h)", "Resumable overnight batches; sleep/battery guard"),
    ("SfM splits some models", "Reported as a finding; largest model densified"),
    ("Default texturing blackened faces", "Re-textured with seam levelling off"),
    ("Arbitrary score weights", "Weight check over w = 0…1"),
    ("Browser timing tied to 60 Hz", "Offscreen batches of 30 frames")], 13, [3.2, 4.45])

# 15 timeline and deliverables -------------------------------------------------------------------------
s = slide("Timeline and deliverables")
grid(s, Inches(0.6), Inches(1.75), Inches(6.3), ["Dates (2026)", "Milestone"], [
    ("25–29 Oct", "Setup, dataset download and verification"), ("30 Oct", "Pilot; settings frozen"),
    ("31 Oct – 4 Nov", "7 batches: 200 reconstructions"), ("1–5 Nov", "Museum hall, gate, upper floor"),
    ("5 Nov", "Cut-off set; trade-off analysis"), ("6 Nov", "Visual fidelity; browser costs; results"),
    ("16–17 Nov", "Mentor review; report, slides, poster")], 13, [1.8, 4.5])
grid(s, Inches(7.2), Inches(1.75), Inches(5.6), ["Deliverable", "Objective"], [
    ("Reproducible pipeline + tests", "Design, implement"), ("Quality-vs-cost results, plots", "Evaluate, compare"),
    ("44 optimised GLB models", "Optimise"), ("Web virtual museum", "Develop"),
    ("Report, slides, poster", "Document")], 13, [3.2, 2.4])

# 16 conclusion ---------------------------------------------------------------------------------------
s = slide("Conclusion and next steps")
card(s, Inches(0.6), Inches(1.75), Inches(7.4), Inches(4.9), "Conclusion", [
    "• **47–92 photos** give the same shape and look as 362, at **6–17%** of the time; 26 are too few",
    "• **L4 most cost-effective**, L3 the safer choice, for almost any weighting",
    "• Web models keep accuracy at **a fifth of the size**, and draw in under half the time",
    "• A walkable museum shows 44 artifacts at 60 fps on a laptop",
    "• H1, H2 and H3 supported, for this controlled synthetic setting"], NAVY, 15)
card(s, Inches(8.25), Inches(1.75), Inches(4.55), Inches(4.9), "Next steps", [
    "• Validate with real photographs",
    "• Densify split SfM models; faster matcher",
    "• Host the museum online; real download times",
    "• Compare neural methods on the same subsets"], CLAY, 15)

# 17 references -----------------------------------------------------------------------------------------
s = slide("References", "IEEE style; numbering follows the report's alphabetical list (selected)")
used = sorted({NUMS[k] for k in ("colmap", "openmvs", "chsd_rgb", "chsd_depth", "tanks", "ssim", "wilcoxon", "holm", "Guidi, Micoli & Gonizzi Barsanti",
                                  "Medina JJ, Maley JM, Sannapareddy S, Medina NN, Gilman CM, McCormack JE", "Tzanetakis et al.", "Maté-González et al.",
                                  "Rattanarungrot et al.", "Balado et al.", "Pepe, Alfio & Costantino", "Raykovska et al.", "Virtual museums: Captured reality and 3D modeling")})
half = (len(used) + 1) // 2
for col, part in enumerate((used[:half], used[half:])):
    text(s, Inches(0.6 + col * 6.2), Inches(1.7), Inches(6.0), Inches(5.2), [f"[{n}] {REFS[n - 1]}" for n in part], 9.5)

# 18 Q&A ------------------------------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK); count["n"] += 1
box(s, 0, 0, W, H, NAVY)
pic(s, FIG / "museum_gate.jpg", Inches(6.9), Inches(1.4), w=Inches(6.1))
text(s, Inches(0.7), Inches(2.3), Inches(6), Inches(1.2), "Thank you", 48, WHITE, True)
text(s, Inches(0.7), Inches(3.4), Inches(6), Inches(1.6), ["Questions and live demo of the virtual museum", "", "Ayaan Goel · Kshiti Bhavsar", f"Mentor: {GUIDE}"], 18, RGBColor(0xDD, 0xE3, 0xEC))

# backups -------------------------------------------------------------------------------------------------
s = slide("Backup · Hypotheses and paired tests")
grid(s, Inches(0.6), Inches(1.75), Inches(12.2), ["Compare (40 artifacts)", "Mesh F (median, 95% CI)", "p (Holm)", "PSNR dB (median, 95% CI)", "p (Holm)"], [
    ("L2 − L1", "0.000 (−0.002, 0.001)", "0.75", "−0.34 (−0.58, −0.16)", "<0.001"), ("L3 − L1", "+0.003 (0.001, 0.004)", "0.039", "−0.41 (−0.75, 0.04)", "0.065"),
    ("L4 − L1", "+0.001 (−0.006, 0.004)", "0.75", "−0.47 (−1.57, 0.07)", "0.065"), ("L5 − L1", "−0.32 (−0.44, −0.20)", "<0.001", "−12.72 (−16.27, −8.72)", "<0.001"),
    ("Museum − full L3 (44)", "≤ 0.0003 change", "—", "−0.20 (−0.24, −0.16)", "<0.001")], 13)
text(s, Inches(0.6), Inches(4.6), Inches(12.2), Inches(2), [
    "• **H1 supported:** time 6.3% of L1 at L4, 1.7% at L5; quality and completeness collapse at L5 (recall 0.41). Memory stops falling below L3 (~2 GB).",
    "• **H2 supported:** L3/L4 within 0.003 mesh F and 0.5 dB of L1 at 17% / 6.3% of the time (no formal equivalence margin was set).",
    "• **H3 supported:** 19% of file size, 23% of download, 43% of drawing time for 0.2 dB PSNR."], 14)

s = slide("Backup · Limitations")
text(s, Inches(0.6), Inches(1.75), Inches(12.2), Inches(5), [
    "• **Synthetic data:** ideal cameras and lighting; benchmark findings, not universal claims for real museum photos.",
    "• **One pipeline, one laptop:** one frozen COLMAP + OpenMVS setting; each level timed once.",
    "• **Split SfM models:** only the largest model is densified, lowering some scores.",
    "• **Cut-off set at L3 only;** its reference shares the image framing.",
    "• **Combined score weights are our choice;** the weight check shows the L3/L4 ranking is stable.",
    "• **Browser costs:** one laptop, simulated 20 Mbit/s, no latency; museum not yet hosted."], 17)

out = OUT / "Presentation"
out.mkdir(parents=True, exist_ok=True)
prs.save(out / "heritage3d_Presentation.pptx")
print("saved", count["n"], "slides")
