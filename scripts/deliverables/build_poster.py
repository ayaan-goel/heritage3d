"""A1 poster on the department's template -> Deliverables/Poster/heritage3d_Poster.pptx"""
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from common import FIG, GUIDE, LEVELS, OUT, PLOTS, TEAM, TEAM_ID, TITLE, cite, references

NUMS, REFS = references()
NAVY, INK, WHITE, LIGHT = RGBColor(0x1D, 0x35, 0x57), RGBColor(0x22, 0x22, 0x22), RGBColor(255, 255, 255), RGBColor(0xF3, 0xEF, 0xE8)
prs = Presentation(OUT / "Poster Template.pptx")
s = prs.slides[0]
group = next(sh for sh in s.shapes if sh.shape_type == 6)

for sh in list(group.shapes):  # drop the sample SmartArt and "Insert ..." placeholders
    if sh.shape_type is None or (sh.has_text_frame and sh.text_frame.text.strip().startswith("Insert")):
        sh._element.getparent().remove(sh._element)


def set_text(shape, lines):
    tf = shape.text_frame
    r0 = tf.paragraphs[0].runs[0]
    size, bold, color = r0.font.size, r0.font.bold, None
    for p in list(tf.paragraphs)[1:]:
        p._p.getparent().remove(p._p)
    tf.paragraphs[0].runs[0].text = lines[0]
    for r in tf.paragraphs[0].runs[1:]:
        r._r.getparent().remove(r._r)
    for line in lines[1:]:
        p = tf.add_paragraph(); p.alignment = tf.paragraphs[0].alignment
        r = p.add_run(); r.text = line; r.font.size = Pt(28); r.font.bold = False


for sh in group.shapes:
    if sh.has_text_frame and sh.text_frame.text.startswith("TITLE OF THE"):
        set_text(sh, [TITLE, f"Team {TEAM_ID}  ·  " + "  ·  ".join(f"{n} ({r})" for n, r in TEAM) + f"  ·  Guide: {GUIDE}"])
        tf = sh.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(2.7)
        tf.paragraphs[0].runs[0].font.size = Pt(40)
        tf.paragraphs[1].runs[0].font.size = Pt(26)
    elif sh.has_text_frame and sh.text_frame.text.strip() == "Expected Results":
        sh.text_frame.paragraphs[0].runs[0].text = "Results"
        for r in sh.text_frame.paragraphs[0].runs[1:]:
            r.text = ""
    elif sh.has_text_frame and sh.text_frame.text.strip().startswith("Budget"):
        sh.text_frame.paragraphs[0].runs[0].text = "Budget and References"
        for r in sh.text_frame.paragraphs[0].runs[1:]:
            r.text = ""
for sh in s.shapes:
    if sh.has_text_frame and "Logo" in sh.text_frame.text:
        set_text(sh, ["School of", "Technology"])


def text(x, y, w, h, lines, size=26, color=INK):
    tf = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(10); p.alignment = PP_ALIGN.LEFT
        for j, chunk in enumerate(line.split("**")):
            if chunk:
                r = p.add_run(); r.text = chunk
                r.font.size, r.font.name, r.font.color.rgb, r.font.bold = Pt(size), "Calibri", color, j % 2 == 1


def pic(path, x, y, w=None, h=None):
    s.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)


def table(x, y, w, header, rows, size=22):
    t = s.shapes.add_table(len(rows) + 1, len(header), Inches(x), Inches(y), Inches(w), Inches(0.62) * (len(rows) + 1)).table
    for r, row in enumerate([header] + rows):
        for i, v in enumerate(row):
            c = t.cell(r, i); c.text = str(v)
            c.fill.solid(); c.fill.fore_color.rgb = NAVY if r == 0 else (RGBColor(0xE3, 0xEF, 0xE5) if row[0] == "L4" else (LIGHT if r % 2 else WHITE))
            for run in c.text_frame.paragraphs[0].runs:
                run.font.size, run.font.name, run.font.bold = Pt(size), "Calibri", r == 0 or row[0] == "L4"
                run.font.color.rgb = WHITE if r == 0 else INK


# Brief motivation / Objective
text(0.5, 2.95, 11.0, 4.3, [
    "• Museums can digitize artifacts with just a camera and free software, but **every photo costs** capture time, storage and processing.",
    "• Too few photos leave parts missing. **How many are enough?** Existing studies rarely vary the image count for single objects and relate it to both cost and quality.",
    "• Answer it on a **student laptop without a GPU**, and deliver the result as a web museum."], 25)
text(12.3, 2.95, 10.7, 4.3, [
    "**Aim:** measure how acquisition effort affects 3D quality and cost, and present suitable models in a virtual museum.",
    "• **RQ1** effort → shape and look   • **RQ2** effort ↔ cost ↔ quality trade-off",
    "• **RQ3** can optimised models stay faithful while cheaper to store and draw?",
    "• 40 CHSD artifacts × 5 image levels = **200 reconstructions**, RGB only"], 25)

# Methodology
pic(FIG / "pipeline.png", 1.0, 8.05, w=21.4)
text(1.0, 17.15, 21.4, 1.2, ["Levels: L1 362 · L2 182 · L3 92 · L4 47 · L5 26 images (azimuth step 3°→45°).  Shape: F-score at 0.002 R vs depth-map reference.  "
                             "Look: PSNR, SSIM from 12 held-out views.  Cost: time, peak RAM, storage.  Paired Wilcoxon tests + combined score."], 22)

# Results
table(0.6, 19.4, 11.2, ["Level", "Images", "Time", "Mesh F", "PSNR", "Pass", "Score"],
      [[l, n, f"{t} min", f"{mf:.3f}", f"{ps:.1f}", f"{ok}/40", f"{sc:.2f}"] for l, n, _, t, _, _, mf, _, ps, _, ok, sc in LEVELS])
text(0.6, 23.4, 11.2, 4.0, [
    "• **47–92 photos match 362** in shape and look at **6–17% of the time**; 26 photos break down.",
    "• Time grows as images^1.34. **L4 most cost-effective** (score 0.82), L3 the safer choice.",
    "• Museum models: **19% of the size, 23% of download, 43% of drawing time**, only −0.2 dB PSNR."], 23)
pic(PLOTS / "tradeoff_score.png", 12.2, 19.35, w=10.6)

# Outcomes
pic(FIG / "museum_gate.jpg", 0.6, 28.15, w=5.9)
pic(FIG / "museum_rotunda.jpg", 6.7, 28.15, w=5.9)
text(0.6, 31.45, 12.0, 1.6, ["Walkable web museum: **44 exhibits**, two floors, gate scene, 60 fps on a laptop. Reproducible pipeline, 81 tests, all results logged."], 21)

# Budget and references
text(13.2, 28.1, 9.8, 1.2, ["**Budget: ₹0.** Free open-source software, open CC BY-NC-SA dataset, own laptop."], 22)
keys = ["colmap", "openmvs", "chsd_rgb", "tanks", "Medina JJ, Maley JM, Sannapareddy S, Medina NN, Gilman CM, McCormack JE"]
text(13.2, 29.2, 9.8, 3.8, [f"[{NUMS[k]}] {REFS[NUMS[k] - 1]}" for k in keys] + ["Full list: project report."], 14)

out = OUT / "Poster"
out.mkdir(parents=True, exist_ok=True)
prs.save(out / "heritage3d_Poster.pptx")
print("saved poster")
