"""Evaluation presentation, version 2: one consistent design system (department lavender/purple palette,
Georgia headings, Calibri body, fixed title/content/footer grid) -> Deliverables/Presentation/heritage3d_Presentation_v2.pptx
Version 1 (build_slides.py) is kept unchanged."""
import csv

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from common import DEPARTMENT, DESIGNATION, EVAL_DATE, FIG, GUIDE, LEVELS, OUT, PROGRAMME, ROOT, TEAM, TEAM_ID, TITLE, cite, references

NUMS, REFS = references()
C = lambda *k: cite(NUMS, *k)
rgb = lambda h: RGBColor.from_string(h)
PURPLE, ACCENT, LAV, LAVL, LAVM, INK, MUTED, LINE, WHITE, SAGE = (rgb("4B2577"), rgb("9B59D0"), rgb("CC99FF"), rgb("F6F0FC"),
                                                                rgb("E6CCFF"), rgb("2E2238"), rgb("6E5F7E"), rgb("E2D6F0"), rgb("FFFFFF"), rgb("5E8C6A"))
HEAD, BODY = "Georgia", "Calibri"
IN = Inches
prs = Presentation()
prs.slide_width, prs.slide_height = IN(13.333), IN(7.5)
W, H = prs.slide_width, prs.slide_height
L, R, TOP, BOT = 0.6, 12.73, 1.55, 6.8  # content box (inches)
CW = R - L
n = {"slide": 0}


# ------------------------------------------------------------------ primitives
def shape(s, x, y, w, h, fill=None, line=None, kind=MSO_SHAPE.RECTANGLE, lw=1.0, radius=None):
    sh = s.shapes.add_shape(kind, IN(x), IN(y), IN(w), IN(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line; sh.line.width = Pt(lw)
    if radius is not None:
        sh.adjustments[0] = radius
    sh.shadow.inherit = False
    return sh


def text(s, x, y, w, h, paras, size=17, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, gap=7, lsp=1.05):
    tf = s.shapes.add_textbox(IN(x), IN(y), IN(w), IN(h)).text_frame
    tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = IN(0.04); tf.margin_top = tf.margin_bottom = IN(0.02)
    for i, para in enumerate(paras if isinstance(paras, list) else [paras]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.space_after, p.line_spacing = align, Pt(gap), lsp
        bullet = para.startswith("• ")
        if bullet:
            r = p.add_run(); r.text = "▪  "
            r.font.size, r.font.name, r.font.color.rgb = Pt(size), font, ACCENT
            para = para[2:]
        for j, chunk in enumerate(para.split("**")):
            if chunk:
                r = p.add_run(); r.text = chunk
                r.font.size, r.font.name = Pt(size), font
                r.font.bold = bold or j % 2 == 1
                r.font.color.rgb = PURPLE if (j % 2 == 1 and color == INK) else color
    return tf


def slide(title, section):
    s = prs.slides.add_slide(prs.slide_layouts[6]); n["slide"] += 1
    text(s, L, 0.28, CW, 0.3, section.upper(), 11.5, ACCENT, BODY, True)
    text(s, L, 0.52, CW, 0.65, title, 29, PURPLE, HEAD, True)
    shape(s, L, 1.22, CW, 0.035, LAV)
    shape(s, L, 7.02, CW, 0.012, LINE)
    text(s, L, 7.07, 9, 0.3, f"heritage3d  ·  Team {TEAM_ID}  ·  Ayaan Goel & Kshiti Bhavsar  ·  Mentor: {GUIDE}", 10, MUTED)
    pill = shape(s, R - 0.55, 7.07, 0.55, 0.27, LAVL, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    text(s, R - 0.55, 7.075, 0.55, 0.27, str(n["slide"]), 10.5, PURPLE, BODY, True, PP_ALIGN.CENTER)
    return s


def card(s, x, y, w, h, title, items, size=15.5, accent=ACCENT, fill=WHITE):
    shape(s, x, y, w, h, fill, LINE, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.035)
    shape(s, x, y + 0.12, 0.07, h - 0.24, accent)
    text(s, x + 0.25, y + 0.14, w - 0.4, 0.45, title, 17.5, PURPLE, HEAD, True)
    text(s, x + 0.25, y + 0.62, w - 0.4, h - 0.7, items, size)


def stat(s, x, y, w, big, label):
    shape(s, x, y, w, 1.12, LAVL, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
    text(s, x + 0.15, y + 0.08, w - 0.3, 0.6, big, 30, PURPLE, HEAD, True)
    text(s, x + 0.15, y + 0.66, w - 0.3, 0.42, label, 12.5, MUTED)


def table(s, x, y, w, header, rows, size=14, widths=None, hi=None, row_h=0.4):
    t = s.shapes.add_table(len(rows) + 1, len(header), IN(x), IN(y), IN(w), IN(row_h * (len(rows) + 1))).table
    for r, row in enumerate([header] + rows):
        for i, v in enumerate(row):
            c = t.cell(r, i); c.text = str(v)
            c.fill.solid()
            c.fill.fore_color.rgb = PURPLE if r == 0 else (LAVM if hi is not None and r == hi else (WHITE if r % 2 else LAVL))
            c.margin_left = c.margin_right = IN(0.08); c.margin_top = c.margin_bottom = IN(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            for run in c.text_frame.paragraphs[0].runs:
                run.font.size, run.font.name = Pt(size), BODY
                run.font.bold = r == 0 or (hi is not None and r == hi)
                run.font.color.rgb = WHITE if r == 0 else INK
    if widths:
        for i, cw in enumerate(widths):
            t.columns[i].width = IN(cw)
    for r in range(len(rows) + 1):
        t.rows[r].height = IN(row_h)
    return t


def pic(s, path, x, y, w=None, h=None, border=True):
    p = s.shapes.add_picture(str(path), IN(x), IN(y), IN(w) if w else None, IN(h) if h else None)
    if border:
        p.line.color.rgb = LINE; p.line.width = Pt(1)
    return p


def chip(s, x, y, label, fill, color=WHITE, w=1.25):
    shape(s, x, y, w, 0.3, fill, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    text(s, x, y + 0.01, w, 0.28, label, 11.5, color, BODY, True, PP_ALIGN.CENTER)


# ------------------------------------------------------------------ 1 title
s = prs.slides.add_slide(prs.slide_layouts[6]); n["slide"] += 1
shape(s, 0, 0, 13.333, 7.5, PURPLE)
pic(s, FIG / "museum_rotunda.jpg", 7.55, 0, h=7.5, border=False).crop_left = 0.2
shape(s, 7.55, 0, 0.09, 7.5, LAV)
text(s, 0.75, 0.75, 6.5, 0.35, "MINOR PROJECT  ·  END-SEMESTER EVALUATION", 12.5, LAV, BODY, True)
text(s, 0.75, 1.25, 6.6, 2.7, TITLE, 31, WHITE, HEAD, True, lsp=1.08)
shape(s, 0.78, 4.12, 1.3, 0.05, LAV)
text(s, 0.75, 4.35, 6.4, 0.9, [f"{nm}   ·   {roll}" for nm, roll in TEAM], 18, WHITE, BODY, gap=4)
text(s, 0.75, 5.35, 6.4, 1.6, [f"Mentor: {GUIDE}, {DESIGNATION}", PROGRAMME, f"{DEPARTMENT}, School of Technology",
                                "Pandit Deendayal Energy University, Gandhinagar", f"Team {TEAM_ID}  ·  {EVAL_DATE}"], 13, rgb("E6DDF2"), gap=2)

# ------------------------------------------------------------------ 2 introduction
s = slide("Introduction and problem statement", "Context")
text(s, L, TOP + 0.05, 6.6, 4.8, [
    "• Museums hold far more artifacts than they can show; many are fragile or far from the people who study them.",
    "• **Image-based 3D reconstruction** builds a model from ordinary photos: **SfM** finds the camera positions, **MVS** builds the dense surface " + C("colmap", "openmvs") + ".",
    "• It needs only a camera and free software, so it suits small museums and colleges " + C("Medina JJ, Maley JM, Sannapareddy S, Medina NN, Gilman CM, McCormack JE") + ".",
    "• But **every photo costs** capture time, storage and processing; too few photos leave parts missing."], 17.5, gap=12)
shape(s, 7.55, TOP + 0.05, 5.18, 4.9, LAVL, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.04)
text(s, 7.85, TOP + 0.3, 4.6, 0.4, "PROBLEM STATEMENT", 12, ACCENT, BODY, True)
text(s, 7.85, TOP + 0.75, 4.6, 2.8, "How much image acquisition effort is necessary to obtain a reconstruction that is accurate and visually suitable "
     "for digital preservation and virtual-museum presentation?", 21, PURPLE, HEAD, lsp=1.12)
text(s, 7.85, TOP + 3.75, 4.6, 1.0, "Affects museums, archives and colleges digitizing collections with modest hardware.", 14.5, MUTED)

# ------------------------------------------------------------------ 3 motivation, aim, objectives
s = slide("Motivation, aim and objectives", "Context")
card(s, L, TOP, 4.0, 5.2, "Why it matters", [
    "• Capture and computing budgets can be planned on a normal laptop",
    "• A controlled framework instead of separate reports of quality or cost",
    "• Visitors get light, faithful models that load fast",
    "• Free CPU tools match the hardware small institutions have"])
shape(s, 4.85, TOP, 7.88, 1.25, LAVL, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
text(s, 5.1, TOP + 0.15, 7.4, 1.0, "**Aim:** quantify how image acquisition effort affects the quality and cost of 3D reconstruction of single "
     "heritage artifacts, and deliver suitable models in a web virtual museum.", 16.5, anchor=MSO_ANCHOR.MIDDLE)
objs = [("Design", "a controlled experiment: same artifact, 5 image subsets, one frozen pipeline"),
        ("Implement", "a reproducible, CPU-only reconstruction and evaluation pipeline"),
        ("Evaluate", "shape, appearance and cost for 40 artifacts"),
        ("Compare", "levels with paired tests and a combined cost-effectiveness score"),
        ("Optimise", "models for the web; measure download and drawing cost"),
        ("Develop", "a walkable web-based virtual museum")]
for i, (verb, rest) in enumerate(objs):
    y = TOP + 1.45 + i * 0.62
    chip(s, 4.85, y + 0.07, verb, PURPLE, w=1.35)
    text(s, 6.35, y + 0.04, 6.4, 0.45, rest, 15.5)

# ------------------------------------------------------------------ 4 RQs and scope
s = slide("Research questions, hypotheses and scope", "Context")
table(s, L, TOP, 7.5, ["", "Research question / hypothesis"], [
    ("RQ1", "How does acquisition effort affect geometric and visual quality?"),
    ("RQ2", "What trade-off exists between effort, processing cost and quality?"),
    ("RQ3", "Can an optimised model keep fidelity while cutting storage and rendering cost?"),
    ("H1", "Fewer images cut cost; too few cut quality and completeness"),
    ("H2", "A range of far fewer images matches a large set"),
    ("H3", "Optimisation cuts storage/rendering cost with sufficient quality")], 14.5, [0.75, 6.75], row_h=0.55)
card(s, 8.4, TOP, 4.33, 5.2, "Scope", [
    "**In:** single artifacts, one public dataset (CHSD), RGB-only input, COLMAP + OpenMVS on CPU, shape + look + cost, web museum",
    "**Out:** new algorithms, NeRF / Gaussian Splatting, neural training, user studies",
    "**Assumes:** synthetic renders stand in for a controlled capture; depth maps are accurate reference geometry"], 14.5)

# ------------------------------------------------------------------ 5 literature
s = slide("Review of existing work", "Prior work and gap")
text(s, L, TOP - 0.05, CW, 0.4, "29 papers (2011–2026) in four themes: artifact digitization · image-based reconstruction · low-cost capture · virtual museums", 14.5, MUTED)
table(s, L, TOP + 0.45, CW, ["Work", "Approach", "Measures", "Limitation for our question"], [
    ("Guidi et al., 2015 " + C("Guidi, Micoli & Gonizzi Barsanti"), "Image-based capture vs laser reference", "Uncertainty, deviation", "Few objects; no computing cost"),
    ("Medina et al., 2020 " + C("Medina JJ, Maley JM, Sannapareddy S, Medina NN, Gilman CM, McCormack JE"), "Cost-effective museum photogrammetry", "Capture time, quality, cost", "Image count not varied"),
    ("Croce et al., 2024 " + C("Tzanetakis et al."), "NeRF vs photogrammetry", "Completeness, fidelity, efficiency", "Compares methods, not effort"),
    ("Maté-González et al., 2025 " + C("Maté-González et al."), "SfM vs NeRF vs Gaussian Splatting", "RMS, Chamfer", "Very small objects; one image set"),
    ("Rattanarungrot et al., 2025 " + C("Rattanarungrot et al."), "Optimised web 3D delivery", "Fidelity, web access", "Capture effort not studied"),
    ("Balado et al., 2025 " + C("Balado et al."), "Review of low-cost 3D mapping", "Cost, accuracy", "No controlled experiment")],
    13.5, [3.25, 3.3, 2.55, 3.03], row_h=0.48)
text(s, L, TOP + 4.0, CW, 0.9, [
    "• Established: photogrammetry of artifacts, SfM-MVS, low-cost capture and web museums all work " + C("Pepe, Alfio & Costantino", "Raykovska et al.", "Virtual museums: Captured reality and 3D modeling") + ".",
    "• Most studies add hardware, compare methods or devices, or focus on sites and user experience."], 15.5, gap=5)

# ------------------------------------------------------------------ 6 gap
s = slide("Research gap and contribution", "Prior work and gap")
card(s, L, TOP, 6.0, 5.2, "What is missing", [
    "• Image count is rarely **varied systematically** for single artifacts",
    "• Acquisition effort, **computing cost** and **quality** are seldom measured together on the same objects",
    "• Results are rarely carried through to **web delivery** with measured costs",
    "Our review's gap matrix: acquisition and compute costs are often not treated together with model quality."], 16)
shape(s, 6.85, TOP, 5.88, 5.2, PURPLE, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.035)
text(s, 7.15, TOP + 0.25, 5.3, 0.4, "OUR CONTRIBUTION", 12, LAV, BODY, True)
text(s, 7.15, TOP + 0.75, 5.3, 2.8, "A controlled, reproducible framework that links image acquisition effort and computing cost to geometric and "
     "visual quality, per artifact, and carries the result to a working virtual museum.", 19.5, WHITE, HEAD, lsp=1.12)
text(s, 7.15, TOP + 3.9, 5.3, 1.1, "Not a new reconstruction algorithm: the novelty is the controlled joint analysis and its integration.", 14.5, rgb("E6DDF2"))

# ------------------------------------------------------------------ 7 pipeline
s = slide("Proposed approach: pipeline", "Proposed approach")
text(s, L, TOP - 0.05, CW, 0.4, "Same artifact → 5 image subsets → same pipeline → compare quality against cost → deliver to the web", 15, MUTED)
pic(s, FIG / "pipeline_heritage.png", 0.95, TOP + 0.4, w=11.45, border=False)

# ------------------------------------------------------------------ 8 methodology
s = slide("Methodology: image levels and measures", "Proposed approach")
table(s, L, TOP, 4.0, ["Level", "Azimuth step", "Images"], [(l, st, im) for l, im, st, *_ in LEVELS], 15, [1.1, 1.6, 1.3], row_h=0.5)
text(s, L, TOP + 3.2, 4.0, 1.9, ["Every n-th azimuth on all 5 camera rings; both pole views always kept, so coverage stays even.",
                                "Only the number of images changes."], 14, MUTED, gap=6)
card(s, 4.95, TOP, 3.75, 5.2, "Shape and look", [
    "• **F-score at 0.002 R** against geometry fused from all 1,800 depth maps " + C("tanks"),
    "• F = 2·P·Rc / (P + Rc)",
    "• **PSNR, SSIM** " + C("ssim") + " and silhouette IoU from 12 held-out views"], 15)
card(s, 8.95, TOP, 3.78, 5.2, "Cost and comparison", [
    "• **Cost:** time, peak RAM, storage per run",
    "• Paired Wilcoxon " + C("wilcoxon") + ", Holm " + C("holm") + ", bootstrap 95% CI",
    "• **Score = w·Q + (1 − w)·S**, w = 0.5",
    "Q: mesh F, SSIM, share passing.  S: 1 − cost share of L1"], 15)

# ------------------------------------------------------------------ 9 setup
s = slide("Experimental setup and requirements", "Proposed approach")
table(s, L, TOP, 7.6, ["Item", "Details"], [
    ("Laptop", "HP Envy x360, i7-1255U, 16 GB RAM, Intel Iris Xe (no CUDA)"),
    ("Reconstruction", "COLMAP 4.2.1 (CPU), OpenMVS 2.4.0 (CPU)"),
    ("Analysis", "Python 3.13, NumPy, SciPy, Matplotlib; 81 tests"),
    ("Web museum", "three.js r170 (WebGL), static site, GLB models"),
    ("Dataset", "CHSD: 81 artifacts, 360 azimuths × 5 rings, 800 × 600, depth maps " + C("chsd_rgb", "chsd_depth")),
    ("Main set", "40 artifacts never cut off; 19 cut-off artifacts run apart at L3")], 14, [1.75, 5.85], row_h=0.62)
card(s, 8.45, TOP, 4.28, 5.2, "Conditions and ethics", [
    "• One frozen configuration for all 200 runs",
    "• Runs repeated if the laptop slept or ran on battery",
    "• Depth maps for evaluation only, never input",
    "• CC BY-NC-SA 4.0 data: non-commercial, credit shown in the museum",
    "• No personal data"], 15, SAGE)

# ------------------------------------------------------------------ 10 progress
s = slide("Work completed", "Progress and evidence")
phases = [("Dataset verified (MD5); 81 artifacts inspected", True), ("Pilot on one artifact; settings frozen", True),
          ("200 main-set + 19 cut-off reconstructions", True), ("Geometric + visual evaluation of 263 models", True),
          ("Trade-off analysis, statistics, combined score", True), ("Web optimisation + browser cost of 44 models", True),
          ("Virtual museum: gate, hall, two floors, 44 exhibits", True), ("Hosting the museum online", False)]
for i, (ph, done) in enumerate(phases):
    y = TOP + i * 0.64
    shape(s, L, y, 7.0, 0.54, WHITE if i % 2 else LAVL, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.15)
    text(s, L + 0.2, y + 0.1, 5.4, 0.36, ph, 15)
    chip(s, L + 5.6, y + 0.12, "Completed" if done else "Pending", SAGE if done else LAV, WHITE if done else PURPLE)
pic(s, FIG / "museum_gate.jpg", 7.95, TOP, w=4.78)
pic(s, FIG / "museum_upper.jpg", 7.95, TOP + 2.82, w=4.78)

# ------------------------------------------------------------------ 11 RQ1
s = slide("RQ1: quality against acquisition effort", "Results")
stat(s, L, TOP, 2.45, "47 = 362", "photos give the same median mesh F and PSNR")
stat(s, L + 2.6, TOP, 2.45, "0.58", "median mesh F at 26 photos: breakdown")
table(s, L, TOP + 1.35, 5.05, ["Level", "Images", "Mesh F", "PSNR", "F ≥ 0.95"],
      [(l, im, f"{mf:.3f}", f"{ps:.1f}", f"{ok}/40") for l, im, _, _, _, _, mf, _, ps, _, ok, _ in LEVELS], 14, [0.85, 0.95, 1.05, 1.0, 1.2], hi=4, row_h=0.42)
text(s, L, TOP + 4.0, 5.05, 1.2, ["• More images lowered cloud precision (0.98 → 0.80) at the tight tolerance.",
                                 "• 9 of 40 never pass at any level (split SfM models, plain objects)."], 13.5, gap=4)
pic(s, FIG / "rq1_quality_time.png", 5.95, TOP - 0.05, w=6.8, border=False)

# ------------------------------------------------------------------ 12 RQ2
s = slide("RQ2: acquisition cost and combined score", "Results")
rows = list(csv.DictReader(open(ROOT / "experiments/results/tradeoff_score.csv", encoding="utf-8")))
TIME = {"L1": "55.4", "L2": "22.4", "L3": "9.7", "L4": "3.9", "L5": "1.0"}
pct = lambda v: f"{float(v) * 100:.0f}%" if float(v) >= 0.1 else f"{float(v) * 100:.1f}%"
table(s, L, TOP, 6.05, ["Level", "Time", "Time %", "RAM %", "Storage %", "Q", "S", "Score"],
      [[r["level"], f"{TIME[r['level']]} min", pct(r["time_share"]), pct(r["peak_ram_share"]), pct(r["storage_share"]),
        f"{float(r['quality']):.2f}", f"{float(r['saving']):.2f}", f"{float(r['score']):.2f}"] for r in rows],
      13.5, [0.7, 0.95, 0.75, 0.75, 0.95, 0.6, 0.6, 0.75], hi=4, row_h=0.42)
shape(s, L, TOP + 2.75, 6.05, 0.95, LAVL, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
text(s, L + 0.15, TOP + 2.8, 5.75, 0.85, ["**Score = w·Q + (1 − w)·S**,  w = 0.5", "Q = mean(mesh F, SSIM, share with F ≥ 0.95)  ·  S = 1 − mean(cost shares of L1)"],
     13.5, align=PP_ALIGN.CENTER, gap=2, anchor=MSO_ANCHOR.MIDDLE)
text(s, L, TOP + 3.9, 6.05, 1.3, ["• Time grows as images^1.34; quality plateaus at 47 images.",
                                 "• All 40: L4 2.7 h (28 pass) · L3 6.3 h (30) · L1 40.1 h (31).",
                                 "• L4 best for weights 0.15–0.80, L3 for 0.85–0.95."], 13.5, gap=3)
pic(s, FIG / "score_breakdown.png", 6.95, TOP, w=5.78, border=False)

# ------------------------------------------------------------------ 13 RQ3
s = slide("RQ3: optimised models in the browser", "Results")
stat(s, L, TOP, 2.95, "−0.20 dB", "PSNR change vs full model; shape change ≤ 0.0003 F")
stat(s, L + 3.1, TOP, 2.95, "68 s", "all 44 exhibits at 20 Mbit/s (full models: 281 s)")
pic(s, FIG / "rq3_shares.png", L - 0.1, TOP + 1.3, w=6.3, border=False)
pic(s, FIG / "museum_lobby.jpg", 7.0, TOP, w=5.73)
text(s, 7.0, TOP + 3.35, 5.73, 1.8, ["• 100k-triangle GLB, JPEG texture ≤ 2048 px",
                                    "• 44-exhibit museum held **60 fps** on integrated graphics",
                                    "• Texture dominates GPU memory: next saving lies there"], 14.5, gap=4)

# ------------------------------------------------------------------ 14 museum
s = slide("The virtual museum", "Progress and evidence")
for (f, cap), (x, y) in zip([("museum_gate.jpg", "Start at the PDEU gate; museum at the end of the drive"),
                             ("museum_lobby.jpg", "Lobby with project signboards"),
                             ("museum_rotunda.jpg", "Domed rotunda, exhibits with measured facts"),
                             ("museum_upper.jpg", "Upper gallery: the 14 cut-off-set exhibits")],
                            [(L, TOP), (6.75, TOP), (L, TOP + 2.65), (6.75, TOP + 2.65)]):
    pic(s, FIG / f, x, y, w=4.1)
    text(s, x + 4.2, y + 0.6, 1.75, 1.6, cap, 12.5, MUTED)

# ------------------------------------------------------------------ 15 evaluation and challenges
s = slide("Evaluation approach, challenges and mitigation", "Planning and closure")
card(s, L, TOP, 4.3, 5.2, "How it was evaluated", [
    "• Paired comparison on the same 40 artifacts",
    "• Wilcoxon, Holm, bootstrap intervals",
    "• Threshold F ≥ 0.95 fixed before analysis",
    "• 81 unit tests; a preview for every run",
    "• Museum: fps, triangles, draw calls"], 15)
table(s, 5.15, TOP, 7.58, ["Challenge", "Mitigation"], [
    ("No NVIDIA GPU / CUDA", "COLMAP CPU + OpenMVS CPU; pilot first"),
    ("200 long runs (65 h)", "Resumable overnight batches; sleep/battery guard"),
    ("SfM splits some models", "Reported as a finding; largest model densified"),
    ("Default texturing blackened faces", "Re-textured with seam levelling off"),
    ("Arbitrary score weights", "Weight check over w = 0 … 1"),
    ("Browser timing tied to 60 Hz", "Offscreen batches of 30 frames")], 14, [3.2, 4.38], row_h=0.62)

# ------------------------------------------------------------------ 16 timeline and deliverables
s = slide("Timeline and deliverables", "Planning and closure")
steps = [("25–29 Oct", "Setup, dataset download and checks"), ("30 Oct", "Pilot; settings frozen"), ("31 Oct – 4 Nov", "7 batches: 200 reconstructions"),
         ("1–5 Nov", "Museum hall, gate, upper floor"), ("5 Nov", "Cut-off set; trade-off analysis"), ("6 Nov", "Visual fidelity; browser costs"),
         ("16–22 Nov", "Mentor review; report, slides, poster")]
shape(s, L + 0.12, TOP + 0.2, 0.03, 4.75, LAV)
for i, (d, m) in enumerate(steps):
    y = TOP + 0.08 + i * 0.7
    shape(s, L + 0.02, y + 0.05, 0.24, 0.24, PURPLE, WHITE, MSO_SHAPE.OVAL, 2)
    text(s, L + 0.45, y, 1.75, 0.35, d, 14, ACCENT, BODY, True)
    text(s, L + 2.2, y, 4.2, 0.4, m, 14.5)
table(s, 7.3, TOP, 5.43, ["Deliverable", "Objective"], [
    ("Reproducible pipeline + tests", "Design, implement"), ("Quality-vs-cost results", "Evaluate, compare"),
    ("44 optimised GLB models", "Optimise"), ("Web virtual museum", "Develop"), ("Report, slides, poster", "Document")],
    14, [3.2, 2.23], row_h=0.6)

# ------------------------------------------------------------------ 17 conclusion
s = slide("Conclusion and next steps", "Planning and closure")
for i, (big, lab) in enumerate([("47–92", "photos match 362 in shape and look"), ("6–17%", "of the processing time"),
                                ("19%", "file size of the web models"), ("60 fps", "44-exhibit museum on a laptop")]):
    stat(s, L + i * 3.07, TOP, 2.92, big, lab)
card(s, L, TOP + 1.35, 7.5, 3.85, "Conclusion", [
    "• Quality is a **threshold, not a slope**: 26 photos are too few",
    "• **L4 most cost-effective**, L3 the safer choice, for almost any weighting",
    "• Web models keep accuracy at a fifth of the size",
    "• H1, H2 and H3 supported for this controlled, synthetic setting"], 18)
card(s, 8.35, TOP + 1.35, 4.38, 3.85, "Next steps", [
    "• Validate with real photographs", "• Densify split SfM models", "• Host the museum online", "• Compare neural methods"], 18, SAGE)

# ------------------------------------------------------------------ 18 references
s = slide("References", "Planning and closure")
used = sorted({NUMS[k] for k in ("colmap", "openmvs", "chsd_rgb", "chsd_depth", "tanks", "ssim", "wilcoxon", "holm", "Guidi, Micoli & Gonizzi Barsanti",
                                  "Medina JJ, Maley JM, Sannapareddy S, Medina NN, Gilman CM, McCormack JE", "Tzanetakis et al.", "Maté-González et al.",
                                  "Rattanarungrot et al.", "Balado et al.", "Pepe, Alfio & Costantino", "Raykovska et al.", "Virtual museums: Captured reality and 3D modeling")})
half = (len(used) + 1) // 2
for col, part in enumerate((used[:half], used[half:])):
    text(s, L + col * 6.15, TOP - 0.05, 5.95, 5.3, [f"[{k}] {REFS[k - 1]}" for k in part], 10.5, gap=5, lsp=1.0)

# ------------------------------------------------------------------ 19 thank you
s = prs.slides.add_slide(prs.slide_layouts[6]); n["slide"] += 1
shape(s, 0, 0, 13.333, 7.5, PURPLE)
pic(s, FIG / "museum_gate.jpg", 6.95, 1.55, w=5.8, border=False)
shape(s, 6.95, 1.55 + 3.26, 5.8, 0.06, LAV)
text(s, 0.75, 2.2, 6, 1.0, "Thank you", 50, WHITE, HEAD, True)
shape(s, 0.78, 3.3, 1.3, 0.05, LAV)
text(s, 0.75, 3.55, 6, 1.8, ["Questions, and a live demo of the virtual museum", "", "Ayaan Goel  ·  Kshiti Bhavsar", f"Mentor: {GUIDE}"], 18, rgb("E6DDF2"), gap=3)

# ------------------------------------------------------------------ backups
s = slide("Backup: paired tests and hypotheses", "Backup")
table(s, L, TOP, CW, ["Compare (40 artifacts)", "Mesh F, median (95% CI)", "p (Holm)", "PSNR dB, median (95% CI)", "p (Holm)"], [
    ("L2 − L1", "0.000 (−0.002, 0.001)", "0.75", "−0.34 (−0.58, −0.16)", "< 0.001"), ("L3 − L1", "+0.003 (0.001, 0.004)", "0.039", "−0.41 (−0.75, 0.04)", "0.065"),
    ("L4 − L1", "+0.001 (−0.006, 0.004)", "0.75", "−0.47 (−1.57, 0.07)", "0.065"), ("L5 − L1", "−0.32 (−0.44, −0.20)", "< 0.001", "−12.72 (−16.27, −8.72)", "< 0.001"),
    ("Museum − full L3 (44)", "≤ 0.0003 change", "—", "−0.20 (−0.24, −0.16)", "< 0.001")], 14, [2.9, 2.75, 1.4, 3.18, 1.9], row_h=0.48)
text(s, L, TOP + 3.15, CW, 2.0, [
    "• **H1 supported:** time 6.3% of L1 at L4, 1.7% at L5; quality and completeness collapse at L5 (recall 0.41). Memory stops falling below L3 (~2 GB).",
    "• **H2 supported:** L3/L4 within 0.003 mesh F and 0.5 dB of L1 at 17% / 6.3% of the time (no formal equivalence margin set).",
    "• **H3 supported:** 19% of file size, 23% of download, 43% of drawing time for 0.2 dB PSNR."], 15, gap=6)

s = slide("Backup: limitations", "Backup")
card(s, L, TOP, CW, 5.2, "What these results do and do not show", [
    "• **Synthetic data:** ideal cameras and lighting; benchmark findings, not universal claims for real museum photos.",
    "• **One pipeline, one laptop:** one frozen COLMAP + OpenMVS setting; each level timed once.",
    "• **Split SfM models:** only the largest model is densified, lowering some scores.",
    "• **Cut-off set at L3 only;** its reference shares the image framing.",
    "• **Combined score weights are our choice;** the weight check shows the L3/L4 ranking is stable.",
    "• **Browser costs:** one laptop, simulated 20 Mbit/s, no latency; museum not yet hosted."], 19.5)

out = OUT / "Presentation"
prs.save(out / "heritage3d_Presentation_v2.pptx")
print("saved", n["slide"], "slides")
