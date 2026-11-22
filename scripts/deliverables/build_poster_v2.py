"""A1 poster, version 2 (department template colours kept: lavender bars, Times New Roman headings; acquisition-cost table with the combined-score formula, score breakdown chart)
on the department's template -> Deliverables/Poster/heritage3d_Poster_v2.pptx. Version 1 (build_poster.py) is kept."""
import csv

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from common import FIG, GUIDE, OUT, ROOT, TEAM, TEAM_ID, TITLE, references

NUMS, REFS = references()
BROWN, TERRA, GOLD, OLIVE = RGBColor(0x4B, 0x25, 0x77), RGBColor(0x9B, 0x59, 0xD0), RGBColor(0xCC, 0x99, 0xFF), RGBColor(0x5E, 0x8C, 0x6A)
INK, CREAM, PARCH, PARCH2, HILITE = (RGBColor(0x2E, 0x22, 0x38), RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0xFF, 0xFF, 0xFF),
                                     RGBColor(0xF4, 0xEB, 0xFF), RGBColor(0xE6, 0xCC, 0xFF))
SERIF, SANS = "Georgia", "Calibri"
prs = Presentation(OUT / "Poster Template.pptx")
s = prs.slides[0]
W, H = prs.slide_width, prs.slide_height
group = next(sh for sh in s.shapes if sh.shape_type == 6)
for sh in list(group.shapes):  # drop the sample SmartArt and "Insert ..." placeholders
    if sh.shape_type is None or (sh.has_text_frame and sh.text_frame.text.strip().startswith("Insert")):
        sh._element.getparent().remove(sh._element)

def set_words(shape, lines, sub_size=26):
    """Change the words but keep the template's own formatting of the first run."""
    tf = shape.text_frame
    for p in list(tf.paragraphs)[1:]:
        p._p.getparent().remove(p._p)
    runs = tf.paragraphs[0].runs
    runs[0].text = lines[0]
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    for line in lines[1:]:
        p = tf.add_paragraph(); p.alignment = tf.paragraphs[0].alignment
        r = p.add_run(); r.text = line; r.font.size = Pt(sub_size); r.font.bold = False; r.font.name = "Times New Roman"


for sh in group.shapes:
    t = sh.text_frame.text.strip() if sh.has_text_frame else ""
    if t.startswith("TITLE OF THE"):
        set_words(sh, [TITLE, f"Team {TEAM_ID}   ·   " + "   ·   ".join(f"{n} ({r})" for n, r in TEAM) + f"   ·   Guide: {GUIDE}"])
        tf = sh.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(2.75)
        tf.paragraphs[0].runs[0].font.size = Pt(40)
    elif t == "Expected Results":
        set_words(sh, ["Results"])
    elif t.startswith("Budget"):
        set_words(sh, ["Budget and References"])
for sh in s.shapes:
    if sh.has_text_frame and "Logo" in sh.text_frame.text:
        set_words(sh, ["School of", "Technology"], 24)


def text(x, y, w, h, lines, size=24, color=INK, align=PP_ALIGN.LEFT, font=SANS, spacing=8):
    tf = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.1)
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.space_after, p.line_spacing = align, Pt(spacing), 1.08
        bullet = line.startswith("• ")
        if bullet:
            r = p.add_run(); r.text = "◆  "
            r.font.size, r.font.name, r.font.color.rgb = Pt(size - 6), font, TERRA
            line = line[2:]
        for j, chunk in enumerate(line.split("**")):
            if chunk:
                r = p.add_run(); r.text = chunk
                r.font.size, r.font.name, r.font.color.rgb, r.font.bold = Pt(size), font, (BROWN if j % 2 else color), j % 2 == 1
    return tf


def pic(path, x, y, w=None, h=None, frame=True):
    p = s.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    if frame:
        p.line.color.rgb = BROWN; p.line.width = Pt(2.5)
    return p


def panel(x, y, w, h, fill=CREAM):
    b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    b.adjustments[0] = 0.04
    b.fill.solid(); b.fill.fore_color.rgb = fill
    b.line.color.rgb = GOLD; b.line.width = Pt(1.5)
    b.shadow.inherit = False
    return b


# Brief motivation / Objective ------------------------------------------------------------------------
text(0.55, 3.0, 10.9, 4.2, [
    "• Museums can digitize artifacts with a camera and free software, but **every photo costs** capture time, storage and processing.",
    "• Too few photos leave parts missing. **How many are enough?** Studies rarely vary the image count for single objects and relate it to both cost and quality.",
    "• We answer it on a **student laptop without a GPU** and deliver the result as a web museum."], 25)
text(12.25, 3.0, 10.75, 4.2, [
    "**Aim:** measure how acquisition effort affects 3D quality and cost, and present suitable models in a virtual museum.",
    "• **RQ1:** how does effort change shape and look?",
    "• **RQ2:** what is the trade-off between effort, cost and quality?",
    "• **RQ3:** can optimised web models stay faithful at lower cost?",
    "• 40 CHSD artifacts × 5 image levels = **200 reconstructions**, RGB images only"], 24)

# Methodology -----------------------------------------------------------------------------------------
pic(FIG / "pipeline_heritage.png", 1.0, 8.0, w=21.4, frame=False)
text(1.0, 17.1, 21.4, 1.3, ["Levels L1 362 · L2 182 · L3 92 · L4 47 · L5 26 images (azimuth step 3° → 45°)   ◆   Shape: F-score at 0.002 R vs depth-map reference   ◆   "
                            "Look: PSNR, SSIM from 12 held-out views   ◆   Cost: time, peak RAM, storage   ◆   Paired Wilcoxon tests"], 21, align=PP_ALIGN.CENTER, spacing=0)

# Results: acquisition-cost table + formula + findings (left), score chart (right) --------------------
rows = list(csv.DictReader(open(ROOT / "experiments/results/tradeoff_score.csv", encoding="utf-8")))
TIME = {"L1": "55.4", "L2": "22.4", "L3": "9.7", "L4": "3.9", "L5": "1.0"}  # median minutes, tradeoff_levels.csv
pct = lambda v: f"{float(v) * 100:.0f}%" if float(v) >= 0.1 else f"{float(v) * 100:.1f}%"
header = ["Level", "Images", "Time (min)", "Time", "RAM", "Storage", "Quality Q", "Saving S", "Score"]
data = [[r["level"], r["images"], TIME[r["level"]], pct(r["time_share"]), pct(r["peak_ram_share"]), pct(r["storage_share"]),
         f"{float(r['quality']):.2f}", f"{float(r['saving']):.2f}", f"{float(r['score']):.2f}"] for r in rows]
text(0.55, 19.25, 11.4, 0.6, ["**Acquisition cost and combined score** (medians, 40 artifacts; costs as share of L1)"], 21, spacing=0)
t = s.shapes.add_table(len(data) + 1, len(header), Inches(0.6), Inches(19.9), Inches(11.3), Inches(0.56) * (len(data) + 1)).table
widths = [0.95, 1.1, 1.35, 1.1, 1.05, 1.25, 1.5, 1.5, 1.5]
for i, wd in enumerate(widths):
    t.columns[i].width = Inches(wd)
for r, row in enumerate([header] + data):
    best = row[0] == "L4"
    for i, v in enumerate(row):
        c = t.cell(r, i); c.text = v
        c.fill.solid(); c.fill.fore_color.rgb = BROWN if r == 0 else (HILITE if best else (CREAM if r % 2 else PARCH2))
        c.margin_left = c.margin_right = Inches(0.05); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = c.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        for run in p.runs:
            run.font.size, run.font.name = Pt(17 if r == 0 else 19), SANS
            run.font.bold = r == 0 or best or i == len(row) - 1
            run.font.color.rgb = CREAM if r == 0 else (TERRA if best and i == len(row) - 1 else INK)
panel(0.6, 23.55, 11.3, 1.55, CREAM)
text(0.75, 23.62, 11.0, 1.45, [
    "**Score = w·Q + (1 − w)·S**,  w = 0.5",
    "Q = mean(mesh F, SSIM, share with F ≥ 0.95)   ·   S = 1 − mean(time, RAM, storage vs L1)"],
    19, align=PP_ALIGN.CENTER, font=SERIF, spacing=2)
text(0.55, 25.25, 11.4, 2.1, [
    "• **47–92 photos match 362** in shape and look at **6–17% of the time**; 26 photos break down.",
    "• **Museum models:** 19% of the size, 23% of download, 43% of drawing time, only −0.2 dB PSNR."], 21, spacing=4)
pic(FIG / "score_breakdown.png", 12.25, 19.3, w=10.7)
text(12.25, 25.75, 10.7, 1.5, ["**L4 is the most cost-effective level, L3 the safer choice.** L4 stays best for quality weights 0.15–0.80, "
                               "L3 for 0.85–0.95, so the result does not hinge on the weighting."], 20, align=PP_ALIGN.CENTER, spacing=0)

# Outcomes ---------------------------------------------------------------------------------------------
pic(FIG / "museum_gate.jpg", 0.65, 28.15, w=5.75)
pic(FIG / "museum_rotunda.jpg", 6.65, 28.15, w=5.75)
text(0.55, 31.45, 12.0, 1.5, ["Walkable web museum: **44 exhibits**, two floors, gate scene, 60 fps on a laptop.  Reproducible pipeline, 81 tests, all results logged."], 20, spacing=0)

# Budget and references -----------------------------------------------------------------------------------
panel(13.2, 28.1, 9.75, 1.15, CREAM)
text(13.3, 28.2, 9.55, 1.0, ["**Budget: ₹0**  ·  free open-source software, open CC BY-NC-SA dataset, own laptop"], 21, align=PP_ALIGN.CENTER, spacing=0)
keys = ["colmap", "openmvs", "chsd_rgb", "tanks", "Medina JJ, Maley JM, Sannapareddy S, Medina NN, Gilman CM, McCormack JE"]
text(13.2, 29.45, 9.75, 3.6, [f"[{NUMS[k]}] {REFS[NUMS[k] - 1]}" for k in keys] + ["Full reference list in the project report."], 14, spacing=3)

out = OUT / "Poster"
prs.save(out / "heritage3d_Poster_v2.pptx")
print("saved poster v2")
