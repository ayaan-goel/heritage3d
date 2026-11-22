"""Final project report (department format) -> Deliverables/Report/heritage3d_Report.docx

Format: A4, Times New Roman 12 pt, 1.5 line spacing, Word "Narrow" margins (0.5 inch, team choice), page border,
cover (colour) + title page + certificate + declaration + acknowledgement + abstract + contents + lists,
chapters 1-5, conclusion, future work, appendices, references in alphabetical order.
Tables of contents/figures/tables are Word fields, filled when the file is opened or exported (to_pdf.ps1).
"""
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

from common import (DEPARTMENT, DESIGNATION, FIG, GUIDE, LEVELS, MONTH, OUT, PLOTS, RQ3, TEAM, TITLE, cite, references)

NUMS, REFS = references()
C = lambda *k: cite(NUMS, *k)
BLUE = RGBColor(0x1D, 0x35, 0x57)

doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
sec.top_margin = sec.bottom_margin = sec.right_margin = sec.left_margin = Inches(0.5)  # Word "Narrow" (team, 2026-11-22)
st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.line_spacing = 1.5
st.paragraph_format.space_after = Pt(6)
for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 12), ("Title", 20), ("Caption", 11)):
    s = doc.styles[name]
    s.font.name, s.font.size, s.font.bold = "Times New Roman", Pt(size), name != "Caption"
    s.font.color.rgb = RGBColor(0, 0, 0)
    s.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    s.element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    s.element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    for theme in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):  # theme fonts override explicit ones
        s.element.rPr.rFonts.attrib.pop(qn(theme), None)
doc.styles["Heading 1"].paragraph_format.space_before = Pt(0)
doc.styles["Heading 1"].paragraph_format.space_after = Pt(18)
doc.styles["Caption"].font.italic = False
doc.styles["Caption"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER


def field(par, code, placeholder="Right-click and choose Update Field."):
    run = par.add_run()
    for tag, text in (("begin", None), (None, code), ("separate", None), (None, None), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), tag)
            if tag == "begin":
                el.set(qn("w:dirty"), "true")
            run._r.append(el)
        elif text:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = text; run._r.append(it)
        else:
            t = OxmlElement("w:t"); t.text = placeholder; run._r.append(t)
    return par


def p(text="", bold=False, align=None, size=None, italic=False, after=None, color=None, keep=False):
    par = doc.add_paragraph()
    if align == "c":
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "j" or align is None:
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if after is not None:
        par.paragraph_format.space_after = Pt(after)
    if keep:
        par.paragraph_format.keep_with_next = True
    for i, chunk in enumerate(text.split("**")):
        if chunk:
            r = par.add_run(chunk)
            r.bold = bold or i % 2 == 1
            r.italic = italic
            if size:
                r.font.size = Pt(size)
            if color:
                r.font.color.rgb = color
    return par


def bullets(items):
    for it in items:
        par = p(it)
        par.style = doc.styles["List Bullet"]


def border(section):
    """Single-line page border on every page of the section."""
    pr = section._sectPr
    for old in pr.findall(qn("w:pgBorders")):
        pr.remove(old)
    b = OxmlElement("w:pgBorders"); b.set(qn("w:offsetFrom"), "page")
    for side in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{side}")
        for k, v in (("val", "single"), ("sz", "12"), ("space", "24"), ("color", "000000")):
            e.set(qn(f"w:{k}"), v)
        b.append(e)
    # pgBorders must come after pgMar in sectPr
    pr.insert(list(pr).index(pr.find(qn("w:pgMar"))) + 1, b)


def new_section(fmt=None, start=1, number=True):
    """Start a new page in a new section; fmt 'lowerRoman' or 'decimal'; number=False leaves the footer empty."""
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    s.footer.is_linked_to_previous = False
    for par in s.footer.paragraphs:
        for r in list(par.runs):
            r._r.getparent().remove(r._r)
    pr = s._sectPr
    for old in pr.findall(qn("w:pgNumType")):
        pr.remove(old)
    if fmt:
        pg = OxmlElement("w:pgNumType"); pg.set(qn("w:fmt"), fmt); pg.set(qn("w:start"), str(start)); pr.append(pg)
    if number:
        f = s.footer.paragraphs[0]; f.alignment = WD_ALIGN_PARAGRAPH.CENTER
        field(f, " PAGE ", "1")
        for r in f.runs:
            r.font.name, r.font.size = "Times New Roman", Pt(11)
    border(s)
    return s


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def caption(kind, text):
    par = doc.add_paragraph(style="Caption")
    par.add_run(f"{kind} ")
    field(par, f" SEQ {kind} \\* ARABIC ", "1")
    par.add_run(f": {text}")
    return par


def figure(path, text, width=6.0):
    par = doc.add_paragraph(); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.keep_with_next = True
    par.add_run().add_picture(str(path), width=Inches(width))
    caption("Figure", text)


def table(text, header, rows, widths=None, size=10):
    if text:
        caption("Table", text).paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        cell = t.rows[0].cells[i]; cell.text = ""
        r = cell.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(size)
        sh = OxmlElement("w:shd"); sh.set(qn("w:fill"), "D9E2F3"); cell._tc.get_or_add_tcPr().append(sh)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(size)
    for row in t.rows:
        for i, cell in enumerate(row.cells):
            for par in cell.paragraphs:
                par.paragraph_format.line_spacing = 1.0
                par.paragraph_format.space_after = Pt(2)
                par.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if widths:
                cell.width = Inches(widths[i])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def h1(text):
    doc.add_heading(text, level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER


def h2(text):
    doc.add_heading(text, level=2)


def equation(text):
    par = p(text, align="c", italic=True)
    return par


# ---------------------------------------------------------------- cover (colour) and title page (black and white)
LOGO = OUT.parent / "museum" / "hall" / "pdeu-logo.png"


def front_page(color, last=False):
    col = BLUE if color else None
    par = doc.add_paragraph(); par.alignment = WD_ALIGN_PARAGRAPH.CENTER; par.paragraph_format.space_after = Pt(14)
    par.add_run().add_picture(str(LOGO), width=Inches(1.6))
    p("A Minor Project Report", align="c", size=16, after=4, color=col)
    p("on", align="c", size=13, after=10)
    p(TITLE, bold=True, align="c", size=20, after=24, color=col)
    p("by", align="c", after=4)
    for name, roll in TEAM:
        p(f"{name}  ({roll})", bold=True, align="c", size=14, after=2)
    p("", after=18)
    p("Under the Guidance of", align="c", after=4)
    p(GUIDE, bold=True, align="c", size=14, after=2)
    p(DESIGNATION, align="c", after=24)
    p("Submitted to", align="c", after=4)
    p(DEPARTMENT, bold=True, align="c", after=2)
    p("School of Technology", align="c", after=2)
    p("Pandit Deendayal Energy University, Gandhinagar", align="c", after=24)
    p(MONTH, bold=True, align="c", size=14, color=col)
    if not last:
        page_break()


border(doc.sections[0])
front_page(True)
front_page(False, last=True)
new_section("lowerRoman", 1)  # certificate to abbreviations: i, ii, iii ...

# ---------------------------------------------------------------- certificate (Appendix 2 format)
p("CERTIFICATE", bold=True, align="c", size=16, after=24)
p(f"This is to certify that the project report entitled “{TITLE},” submitted by Ayaan Goel (23BCP264) and "
  f"Kshiti Bhavsar (23BCP275), has been conducted under the supervision of {GUIDE}, {DESIGNATION}, and is hereby "
  f"approved for the partial fulfilment of the requirements for the award of the degree of Bachelor of Technology in the "
  f"{DEPARTMENT} at Pandit Deendayal Energy University, Gandhinagar. This work is original and has not been submitted to "
  "any other institution for the award of any degree.")
p("", after=40)
sig = doc.add_table(rows=1, cols=2)
for cell, (who, desig) in zip(sig.rows[0].cells, ((GUIDE, DESIGNATION), ("[Name of Examiner]", "[Designation]"))):
    cell.text = ""
    for line in ("Sign: ____________________", who, desig, DEPARTMENT, "School of Technology", "Pandit Deendayal Energy University"):
        par = cell.add_paragraph(line); par.paragraph_format.line_spacing = 1.15; par.paragraph_format.space_after = Pt(0)
page_break()

# ---------------------------------------------------------------- declaration (department Appendix 3 layout, stated truthfully)
p("DECLARATION", bold=True, align="c", size=16, after=18)
p(f"We hereby declare that the project report entitled “{TITLE}” is the result of work carried out by us under the "
  f"guidance of {GUIDE}, {DESIGNATION}, {DEPARTMENT}. All experiments were run by us, and every result in this report comes "
  "from those runs; the configurations, logs and result files are kept in the project repository.")
p("In accordance with the department's guidelines on the use of artificial-intelligence tools, we disclose that an AI coding "
  "assistant was used during this project, as listed below, including for drafting the text of this report from our measured "
  "results. We have read, checked and edited the report, and the project decisions, the choice of dataset and method, and the "
  "interpretation of the results are our own.")
p("This declaration affirms that the work presented in this report was genuinely carried out by us and, to the best of our "
  "knowledge, is original.")
p("", after=10)
dec = doc.add_table(rows=1, cols=2)
for cell, (name, roll) in zip(dec.rows[0].cells, TEAM):
    cell.text = ""
    for i, line in enumerate(("Sign: ____________________", name, roll, DEPARTMENT, "School of Technology",
                              "Pandit Deendayal Energy University", "Gandhinagar")):
        par = cell.add_paragraph(line); par.paragraph_format.line_spacing = 1.15; par.paragraph_format.space_after = Pt(0)
        if i == 1:
            par.runs[0].bold = True
p("", after=6)
p("Date: 23-11-2026", align="l", after=0)
p("Place: Gandhinagar", align="l", after=14)
p("List of Tools Used for the Report with Purpose:", bold=True, align="l", keep=True)
bullets([
    "Claude Code (Anthropic): writing and testing the pipeline, evaluation and analysis code; building the web museum; "
    "producing plots and tables; drafting the text of this report, the presentation and the poster, which we reviewed and edited.",
    "COLMAP, OpenMVS, Python (NumPy, SciPy, Matplotlib) and three.js: reconstruction, evaluation and visualisation software (not AI tools).",
])
page_break()

# ---------------------------------------------------------------- acknowledgement
p("ACKNOWLEDGEMENT", bold=True, align="c", size=16, after=18)
p(f"We are grateful to our guide, {GUIDE}, for her guidance throughout this project, for helping us frame the research "
  "questions and for her feedback on the evaluation method and the reporting of results. We thank the evaluation panel "
  "for their time and comments, and the School of Technology, Pandit Deendayal Energy University, for the opportunity to "
  "carry out this work.")
p("We also thank the creators of the Cultural Heritage Synthetic Depth Dataset (CHSD) and the Virtual Hampson Museum, "
  "whose openly licensed data made a controlled study possible, and the developers of COLMAP, OpenMVS and three.js.")
p("", after=30)
for name, roll in TEAM:
    p(f"{name} ({roll})", align="j", after=0)
page_break()

# ---------------------------------------------------------------- abstract
p("ABSTRACT", bold=True, align="c", size=16, after=18)
p("Image-based 3D digitization lets museums preserve artifacts and show them online, but how many photographs are "
  "actually needed, and what each extra photograph costs in computing, is rarely measured for single objects under "
  "controlled conditions. This project measures that relationship and carries the result through to a working "
  "web-based virtual museum.")
p("Forty artifacts from the Cultural Heritage Synthetic Depth Dataset (CHSD) were each reconstructed from five image "
  "subsets of decreasing size, from 362 to 26 images, with one frozen, CPU-only pipeline (COLMAP for structure from "
  "motion and OpenMVS for dense reconstruction) on a student laptop without a dedicated GPU: 200 reconstructions in all. "
  "Shape accuracy was measured with the F-score at 0.002 R against reference geometry built from the dataset's depth "
  "maps, appearance with PSNR and SSIM from 12 held-out views, and cost as processing time, peak memory and storage.")
p("Quality behaved as a threshold rather than a slope. From 362 down to 47 images, median mesh F-score stayed between "
  "0.982 and 0.989 and PSNR within 0.5 dB, while processing time fell to 6.3% of the 362-image level; at 26 images "
  "coverage broke down (median mesh F-score 0.58, 14 of 40 runs without a dense cloud). Processing time grew as about "
  "images^1.34. A combined cost-effectiveness score ranked 47 images (L4) first and 92 images (L3) second for almost any "
  "weighting. Web-optimised models of 100,000 triangles kept their geometric accuracy, lost 0.2 dB PSNR, and in the "
  "browser took 19% of the file size, 23% of the download time and 43% of the drawing time of the full models. The "
  "resulting virtual museum presents 44 artifacts in a walkable two-floor hall at 60 frames per second on integrated "
  "graphics. All three hypotheses were supported for this synthetic, controlled setting.")
p("Keywords: photogrammetry, structure from motion, multi-view stereo, cultural heritage, cost-effectiveness, virtual museum, WebGL.", italic=True)
page_break()

# ---------------------------------------------------------------- contents and lists
for heading, code in (("TABLE OF CONTENTS", ' TOC \\o "1-2" \\h \\z \\u '), ("LIST OF TABLES", ' TOC \\h \\z \\c "Table" '),
                      ("LIST OF FIGURES", ' TOC \\h \\z \\c "Figure" ')):
    p(heading, bold=True, align="c", size=16, after=18)
    field(doc.add_paragraph(), code)
    page_break()

p("LIST OF SYMBOLS, ABBREVIATIONS AND NOMENCLATURE", bold=True, align="c", size=16, after=18)
abbr = [("3DGS", "3D Gaussian Splatting"), ("CHSD", "Cultural Heritage Synthetic Depth Dataset"), ("CPU / GPU", "Central / Graphics Processing Unit"),
        ("CUDA", "NVIDIA's GPU computing platform"), ("F, F@τ", "F-score at distance tolerance τ (harmonic mean of precision and recall)"),
        ("GLB", "Binary glTF, a file format for 3D models on the web"), ("IoU", "Intersection over union of two silhouettes"),
        ("L1–L5", "Image levels: 362, 182, 92, 47 and 26 images"), ("MVS", "Multi-view stereo"), ("NeRF", "Neural Radiance Fields"),
        ("P, Rc", "Precision and recall of a reconstruction against the reference"), ("PSNR", "Peak signal-to-noise ratio (dB)"),
        ("R", "Camera-to-object-centre distance; unit of all distances"), ("RAM", "Random-access memory"),
        ("RQ, H", "Research question, hypothesis"), ("SfM", "Structure from motion"), ("SSIM", "Structural similarity index"),
        ("τ", "Distance tolerance of the F-score (0.002 R unless stated)"), ("w", "Weight on quality in the combined score")]
table(None, ["Symbol", "Meaning"], abbr, widths=[1.6, 5.6], size=11)
new_section("decimal", 1)  # chapters onward: 1, 2, 3 ...

# ---------------------------------------------------------------- chapter 1
h1("Chapter 1: Introduction")
h2("1.1 Background")
p("Museums hold far more artifacts than they can display, and many objects are fragile, rarely shown or held far from "
  "the people who study them. Digital 3D models address all three: they preserve an object's shape and surface, they "
  "can be examined from any side, and they can be published online. Image-based reconstruction, or photogrammetry, "
  "builds such models from ordinary photographs: structure from motion (SfM) finds the camera positions and a sparse set "
  "of 3D points, multi-view stereo (MVS) turns the posed images into a dense point cloud, and the cloud is meshed and "
  "textured " + C("colmap", "openmvs", "Pepe, Alfio & Costantino") + ". Because it needs only a camera and free software, "
  "it is the most affordable route to digitization for small institutions " + C("Medina JJ, Maley JM, Sannapareddy S, Medina NN, Gilman CM, McCormack JE", "Balado et al.") + ".")
h2("1.2 Problem statement")
p("Every photograph adds capture time, storage and, above all, processing time; too few photographs leave parts of the "
  "object missing or wrongly shaped. Existing studies show that low-cost digitization works and measure quality or "
  "runtime, but they rarely vary the number of images systematically for individual artifacts and relate it to both "
  "computing cost and model quality under the same conditions. A practitioner therefore has little evidence for how "
  "many photographs are enough. The problem this project addresses is: **how much image acquisition effort is necessary "
  "to obtain a reconstruction that is sufficiently accurate and visually suitable for digital preservation and "
  "virtual-museum presentation?**")
h2("1.3 Motivation and significance")
p("A measured answer helps three groups. Small museums and colleges can plan capture sessions and computing budgets on a "
  "normal laptop. Researchers get a controlled, reproducible framework that links acquisition effort, computation and "
  "quality instead of reporting them separately. Visitors benefit from a virtual museum whose models are small enough to "
  "load quickly but still faithful. Open-source, CPU-only tools were chosen deliberately: they match the hardware such "
  "institutions actually have.")
h2("1.4 Aim and objectives")
p("**Aim:** to quantify how image acquisition effort affects the quality and cost of image-based 3D reconstruction of "
  "individual heritage artifacts, and to deliver the suitable models in a web-based virtual museum.")
bullets(["Design a controlled experiment in which the same artifact is reconstructed from five image subsets with one frozen pipeline.",
         "Implement a reproducible, resumable reconstruction and evaluation pipeline on a CPU-only laptop.",
         "Evaluate geometric quality (F-score, Chamfer distance), visual quality (PSNR, SSIM, silhouette IoU) and cost (time, memory, storage) for 40 artifacts.",
         "Compare levels with paired statistical tests and a combined cost-effectiveness score.",
         "Optimise the suitable models for the web and measure their download, decoding and drawing cost against the full models.",
         "Develop a walkable web-based virtual museum that presents the optimised models with their measured facts."])
h2("1.5 Research questions and hypotheses")
table("Research questions and hypotheses", ["ID", "Statement"], [
    ("RQ1", "How does variation in image acquisition effort affect the geometric and visual quality of 3D reconstructions of individual cultural heritage artifacts?"),
    ("RQ2", "What trade-off exists between image acquisition effort, reconstruction processing cost and resulting 3D model quality?"),
    ("RQ3", "Can an optimised reconstruction retain sufficient geometric and visual fidelity for interactive virtual-museum presentation while reducing storage and rendering requirements?"),
    ("H1", "Reducing input images reduces computational requirements, but excessive reduction decreases reconstruction quality and completeness."),
    ("H2", "There is a practical image-acquisition range in which substantially fewer images give quality comparable to a much larger image set."),
    ("H3", "Model optimisation can reduce storage and rendering requirements while retaining sufficient visual quality for interactive virtual-museum presentation."),
], widths=[0.6, 5.3])
h2("1.6 Scope and assumptions")
p("**Included:** individual artifacts from one public dataset; RGB images as the only reconstruction input; one open-source "
  "SfM + MVS pipeline on a CPU; geometric, visual and cost evaluation; web optimisation; a web-based virtual museum. "
  "**Excluded:** new reconstruction algorithms, NeRF or Gaussian Splatting studies, neural network training, segmentation, "
  "condition monitoring and user studies. **Assumptions:** the synthetic renders of CHSD stand in for a controlled capture "
  "(ideal cameras and lighting), and the dataset's depth maps are accurate enough to serve as reference geometry.")
h2("1.7 Organisation of the report")
p("Chapter 2 reviews related work and identifies the gap. Chapter 3 describes the dataset, the experimental design and "
  "the evaluation measures. Chapter 4 describes the setup and implementation. Chapter 5 presents and discusses the "
  "results for each research question. The report closes with conclusions and future work.")
page_break()

# ---------------------------------------------------------------- chapter 2
h1("Chapter 2: Literature Survey")
p("The review covered 29 papers from 2011 to 2026 in four themes: heritage artifact digitization, image-based "
  "reconstruction, low-cost digitization and virtual museums. This chapter summarises what each theme establishes and "
  "what it leaves open.")
h2("2.1 Heritage artifact digitization")
p("Photogrammetry is an established way to document archaeological objects. Raykovska et al. combined photogrammetry and "
  "structured-light scanning to build an online exhibition of vessels " + C("Raykovska et al.") + "; Croci et al. compared "
  "low-cost photogrammetry with a 3D scanner on museum objects and reported its dimensional accuracy " + C("Croci et al.") +
  "; Valente et al. used photogrammetric models for immersive storytelling " + C("Valente et al.") + ". Other work extends "
  "capture with reflectance transformation imaging for featureless objects " + C("Morita et al.") + ", multiband imaging "
  "for pigments " + C("Ferdani et al.") + " or neural pipelines for poor lighting " + C("He & Jia") + ", and reviews "
  "document the state of the art for fragile materials " + C("Iakovaki, Makris & Malea") + ". These studies show that "
  "digitization works, but most add hardware or complexity and do not ask how little capture is enough.")
h2("2.2 Image-based reconstruction")
p("SfM-MVS is mature and inexpensive, and acquisition strategy and image overlap are known to matter " +
  C("Pepe, Alfio & Costantino", "Guidi, Micoli & Gonizzi Barsanti") + ". Guidi et al. compared shooting configurations and "
  "image redundancy against laser-scanned references " + C("Guidi, Micoli & Gonizzi Barsanti") + ". Recent comparisons "
  "set conventional MVS against learning-based methods and NeRF " + C("Poux et al.", "Tzanetakis et al.", "Croce et al.") +
  " and against Gaussian Splatting for very small artifacts " + C("Maté-González et al.") + "; they find no universal best "
  "method and note that neural methods cost more computation and can be noisier. Benchmarks commonly report the F-score "
  "at a distance tolerance as the summary of accuracy and completeness " + C("tanks") + ".")
h2("2.3 Low-cost digitization")
p("Low-cost recording has been demonstrated with consumer cameras and phones for many years " +
  C("Kirchhöfer, Chandler & Wackrow", "Cuca et al.", "Dharmatanna & Agustianti") + ", and with mobile LiDAR and affordable "
  "sensors for buildings and monuments " + C("Kim et al.", "Maschio et al.", "Pavelka & Váňa") + ". Medina et al. built an "
  "efficient, explicitly costed photogrammetry workflow for museum specimens " +
  C("Medina JJ, Maley JM, Sannapareddy S, Medina NN, Gilman CM, McCormack JE") + ", Balado et al. reviewed the trade-offs of "
  "low-cost 3D mapping " + C("Balado et al.") + ", and Lu combined COLMAP with Gaussian Splatting for a low-cost system " +
  C("Lu") + ". Most of this work concerns sites and buildings or compares devices, rather than the image count for a single object.")
h2("2.4 Virtual museums")
p("Virtual museums built from captured models are well documented, from open-source photogrammetric workflows " +
  C("Virtual museums: Captured reality and 3D modeling") + " and web frameworks with optimised models " +
  C("Rattanarungrot et al.") + " to complete photogrammetry-to-museum workflows " + C("Bamuni Hill study") + " and immersive "
  "exhibitions evaluated with users " + C("Antikythera Mechanism virtual museum", "Xu et al.", "Zheng et al.", "Li & Lv") +
  ". Their focus is delivery and user experience, not the acquisition effort behind the models.")
h2("2.5 Comparison and research gap")
table("Comparison of closely related work", ["Work", "Approach", "Measures", "Limitation for our question"], [
    ("Guidi et al. " + C("Guidi, Micoli & Gonizzi Barsanti"), "Image-based capture vs laser reference", "Uncertainty, deviation", "Older; few objects; no computing cost"),
    ("Medina et al. " + C("Medina JJ, Maley JM, Sannapareddy S, Medina NN, Gilman CM, McCormack JE"), "Cost-effective museum photogrammetry", "Capture time, quality, cost", "Natural-history specimens; image count not varied"),
    ("Croce et al. " + C("Tzanetakis et al."), "NeRF vs photogrammetry", "Completeness, fidelity, efficiency", "Method comparison, not acquisition effort"),
    ("Maté-González et al. " + C("Maté-González et al."), "SfM vs NeRF vs Gaussian Splatting", "RMS, Chamfer", "Very small objects; one image set"),
    ("Rattanarungrot et al. " + C("Rattanarungrot et al."), "Optimised web 3D delivery", "Fidelity, web access", "Delivery focus; capture effort not studied"),
    ("Balado et al. " + C("Balado et al."), "Review of low-cost 3D mapping", "Cost, accuracy (reviewed)", "Broad review; no controlled experiment"),
], widths=[1.4, 1.6, 1.3, 1.9], size=9.5)
p("The reviewed work establishes that low-cost artifact digitization, quantitative evaluation and virtual-museum delivery "
  "are each feasible. What is comparatively less studied is a **controlled, reproducible, per-artifact analysis that "
  "links image acquisition effort and computational cost to reconstruction quality**, and carries the result through to "
  "web delivery. This project addresses that gap. Its novelty is the framework and its integration, not a new "
  "reconstruction algorithm.")
page_break()

# ---------------------------------------------------------------- chapter 3
h1("Chapter 3: Methodology")
h2("3.1 Overview")
p("The same artifact is reconstructed from controlled image subsets with the same pipeline, and the results are compared "
  "for quality against cost (Figure 1). Depth maps from the dataset build the reference geometry and are never used as "
  "reconstruction input.")
figure(FIG / "pipeline.png", "Pipeline of the study: reconstruction, evaluation, analysis and web delivery", 6.0)
h2("3.2 Dataset")
p("The Cultural Heritage Synthetic Depth Dataset (CHSD) " + C("chsd_rgb", "chsd_depth") + " contains 81 artifacts from the "
  "Virtual Hampson Museum, each rendered from 360 azimuths on five camera elevations at 800 × 600 pixels, with a 16-bit "
  "depth map for every view; elevations ±90° are single pole views. Both records are licensed CC BY-NC-SA 4.0, so the "
  "derived models are shared non-commercially with attribution. 41 of the 81 artifacts are cut off by the image frame "
  "in some views; the **main set** is the 40 that are never cut off, processed in a fixed order. The 19 least cut-off "
  "artifacts (at most 30% of sample views) form a separate **cut-off set**, run at one level only.")
h2("3.3 Experimental design: image levels")
p("Five subsets are made by widening the azimuth step on every elevation ring while always keeping the two pole views, so "
  "coverage stays even around the object (Table 3). Only the number of images changes between levels.")
table("Image levels", ["Level", "Azimuth step", "Images", "Share of L1"], [
    ("L1", "3°", 362, "100%"), ("L2", "6°", 182, "50%"), ("L3", "12°", 92, "25%"), ("L4", "24°", 47, "13%"), ("L5", "45°", 26, "7%")],
    widths=[1.0, 1.4, 1.0, 1.2])
h2("3.4 Reconstruction pipeline")
p("COLMAP " + C("colmap") + " extracts SIFT features, matches every image pair (exhaustive matching) and runs incremental "
  "mapping with one shared pinhole camera. OpenMVS " + C("openmvs") + " then computes depth maps and a fused dense cloud "
  "(DensifyPointCloud), reconstructs a mesh (ReconstructMesh) and textures it (TextureMesh). The settings were frozen "
  "after a pilot on one artifact and applied unchanged to every run. When SfM produces more than one model, the model "
  "with the most registered images is densified.")
h2("3.5 Geometric evaluation")
p("The reconstruction is aligned to the dataset frame through its camera positions, and compared with a reference point "
  "set fused from all 1,800 depth maps of the artifact. Distances are expressed in R, the camera-to-object-centre "
  "distance. Precision P is the share of reconstructed points within τ of the reference, recall Rc the share of the "
  "reference within τ of the reconstruction, and")
equation("F@τ = 2 · P · Rc / (P + Rc)")
p("with τ = 0.002 R as the main tolerance and 0.005 R and 0.01 R as checks " + C("tanks") + ". Clouds are thinned on a "
  "0.002 R voxel grid before comparison. Chamfer distance and the 95th-percentile Hausdorff distance are also reported. "
  "The F-score is computed for the dense cloud and for the mesh vertices; the mesh F-score is the main quality measure "
  "because the mesh is what the museum shows.")
h2("3.6 Visual evaluation")
p("Each textured model is rendered with the ideal dataset camera from 12 held-out views that no level uses (azimuths 7°, "
  "97°, 187° and 277° at elevations −45°, 0° and 45°) and compared with the dataset image of the same view over the union "
  "of both silhouettes, so missing parts count against the model. The measures are PSNR, SSIM " + C("ssim") + " and the "
  "silhouette IoU:")
equation("PSNR = 10 · log10(MAX² / MSE)")
h2("3.7 Cost measures and statistics")
p("For every run the pipeline records wall-clock time per stage, peak memory of the whole process tree and the size of "
  "the inputs and outputs. Levels are compared on the same 40 artifacts with the Wilcoxon signed-rank test " +
  C("wilcoxon") + ", Holm's correction for several comparisons " + C("holm") + " and a bootstrap 95% interval of the median "
  "difference (10,000 resamples). A level is **sufficient** for an artifact when its mesh F@0.002 R reaches 0.95, a "
  "threshold fixed before the analysis.")
h2("3.8 Combined cost-effectiveness score")
p("The costs are reported side by side; in addition each level receives one score between 0 and 1:")
equation("Score = w · Quality + (1 − w) · Saving")
p("where Quality is the mean of the median mesh F-score, the median SSIM and the share of artifacts that are sufficient, "
  "and Saving is one minus the mean of the time, peak-memory and storage shares of the same artifact's L1 run. The main "
  "setting is w = 0.5; the ranking of the levels is recomputed for every w from 0 to 1 in steps of 0.05 to check that "
  "the conclusion does not depend on the weighting.")
h2("3.9 Web optimisation and the virtual museum")
p("An artifact is exhibited when its L3 mesh reaches F ≥ 0.95. Its mesh is decimated to about 100,000 triangles, "
  "re-textured with a JPEG atlas of at most 2048 pixels and packed as a binary glTF (GLB) file " + C("gltf") + ". For RQ3, "
  "each museum model is compared with a full GLB of the same undecimated L3 mesh in geometry, appearance, file size, "
  "download, decoding, GPU upload and drawing time. The museum is a static website built with three.js " + C("threejs") + ".")
page_break()

# ---------------------------------------------------------------- chapter 4
h1("Chapter 4: Experimental Setup and Implementation")
h2("4.1 Hardware and software")
table("Experimental setup", ["Item", "Details"], [
    ("Laptop", "HP Envy x360 16, Intel Core i7-1255U (12 logical CPUs), 16 GB RAM, Intel Iris Xe integrated graphics (no NVIDIA GPU, no CUDA), Windows 11"),
    ("Reconstruction", "COLMAP 4.2.1 (CPU build), OpenMVS 2.4.0 (CPU)"),
    ("Analysis", "Python 3.13 with NumPy, SciPy, Matplotlib, OpenPyXL; 81 automated tests (pytest)"),
    ("Web museum", "three.js r170 (WebGL), static HTML/JavaScript, GLB models; tested in Chrome"),
    ("Data", "CHSD RGB (46.2 GB) and depth (7.9 GB) records from Zenodo, MD5-verified; stored outside the code repository"),
    ("Version control", "Git and GitHub; configurations, logs, metrics and plots committed; raw data and meshes not committed"),
], widths=[1.4, 4.5], size=10)
p("Because COLMAP's own dense stage requires CUDA, OpenMVS performs the dense steps on the CPU. A pilot on one artifact "
  "checked feasibility first: at L3 the full pipeline took 18 minutes and 2.0 GB of memory.")
h2("4.2 Implementation")
p("The software is organised as small, tested modules: a dataset inspector; a subset generator that writes the image "
  "lists for each level; a pipeline runner that calls COLMAP and OpenMVS and records time and peak memory for each stage; "
  "a resumable batch runner; the geometric evaluation (camera alignment, reference fusion, voxel thinning, F-score and "
  "distances); a CPU rasteriser for the held-out-view comparison; the statistical analysis; the GLB exporter; and a "
  "status workbook for the team. A configuration file fixes every setting, and each result is written as a JSON file "
  "next to its log.")
h2("4.3 Running the experiment")
p("The 200 main-set reconstructions ran in seven overnight batches between 30 October and 4 November 2026, about 65 "
  "hours of processing in total. The batch runner stopped and repeated any level during which the laptop slept or ran "
  "on battery, so timings come from comparable conditions. The cut-off set (19 runs at L3) ran on 4–5 November. The "
  "visual evaluation of 263 models (200 main-set, 19 cut-off and 44 museum models) took 8.8 hours.")
h2("4.4 Virtual museum")
p("The museum is a walkable 3D building in the browser (Figure 2). A visit starts at a model of the university's main "
  "gate, from which the museum building is visible at the end of the drive. Inside, a domed rotunda and four galleries "
  "hold the 30 exhibited main-set artifacts, and a staircase leads to an upper gallery with the 14 exhibited cut-off "
  "artifacts. Each pedestal carries a placard with that artifact's measured facts; pressing E opens a 360° close-up with "
  "an information panel. The layout grows automatically from the exhibit list, and the nearest models load first.")
for f, cap in (("museum_gate.jpg", "Virtual museum: the visit starts at the university gate, with the museum at the end of the drive"),
               ("museum_lobby.jpg", "Virtual museum: entrance lobby with the project signboards"),
               ("museum_rotunda.jpg", "Virtual museum: domed rotunda with exhibits on pedestals"),
               ("museum_upper.jpg", "Virtual museum: upper gallery holding the cut-off set")):
    figure(FIG / f, cap, 5.6)
h2("4.5 Testing")
p("Functional correctness was checked with 81 unit tests covering subset generation, configuration, the evaluation "
  "metrics, the statistics, the combined score and the visual renderer. Each reconstruction was checked by a preview "
  "image, and the museum was checked by walking every floor in the browser and by recording frame rate, triangles and "
  "draw calls in several views.")
page_break()

# ---------------------------------------------------------------- chapter 5
h1("Chapter 5: Result Analysis and Discussion")
h2("5.1 RQ1: quality against acquisition effort")
table("Quality and cost by level, medians over the 40 main-set artifacts",
      ["Level", "Images", "Time (min)", "Time share", "Peak RAM (GB)", "Mesh F", "Cloud F", "PSNR (dB)", "SSIM", "F ≥ 0.95"],
      [(l, n, t, s, r, f"{mf:.3f}", f"{cf:.3f}", f"{ps:.2f}", f"{ss:.3f}", f"{ok}/40") for l, n, _, t, s, r, mf, cf, ps, ss, ok, _ in LEVELS],
      size=9.5)
p("From 362 down to 47 images, quality hardly changes: median mesh F stays between 0.982 and 0.989, and L2 to L4 are "
  "within half a decibel of L1 in PSNR with no significant SSIM difference (Table 6). At 26 images coverage breaks down: "
  "median mesh F falls to 0.58, PSNR to 14.4 dB, recall to 0.41, and 14 of 40 runs produce no dense cloud. The loss is "
  "one of coverage, not accuracy: what L5 does reconstruct is precise (precision 0.996).")
table("Paired differences against L1 (median, bootstrap 95% interval, Holm-corrected p)",
      ["Compare", "Mesh F", "p", "PSNR (dB)", "p", "SSIM", "p"], [
    ("L2 − L1", "0.000 (−0.002, 0.001)", "0.75", "−0.34 (−0.58, −0.16)", "<0.001", "−0.001 (−0.004, 0.001)", "0.92"),
    ("L3 − L1", "+0.003 (0.001, 0.004)", "0.039", "−0.41 (−0.75, 0.04)", "0.065", "+0.004 (0.000, 0.006)", "0.49"),
    ("L4 − L1", "+0.001 (−0.006, 0.004)", "0.75", "−0.47 (−1.57, 0.07)", "0.065", "+0.005 (−0.007, 0.009)", "1.0"),
    ("L5 − L1", "−0.32 (−0.44, −0.20)", "<0.001", "−12.72 (−16.27, −8.72)", "<0.001", "−0.28 (−0.44, −0.19)", "<0.001"),
], size=9)
figure(PLOTS / "tradeoff_quality_vs_time.png", "Quality against processing time for all 200 runs; large marks are medians", 6.0)
figure(PLOTS / "visual_by_level.png", "Visual quality (PSNR, SSIM, silhouette IoU) by level", 6.0)
p("Two further observations matter. First, more images did not give a better dense cloud: cloud F rises as images are "
  "removed, from 0.883 at L1 to 0.984 at L4, because precision falls with more images (0.795 at L1, 0.981 at L4) while "
  "recall stays level. This is an effect at the tight tolerance only (at 0.01 R every level from L1 to L4 scores at "
  "least 0.998) and meshing removes it; its cause is not established (a hypothesis is that many closely spaced views add "
  "slightly misplaced points that the fixed fusion settings do not filter). Second, 9 of 40 artifacts never reach mesh F "
  "0.95 at any level, because SfM split the images into separate models or because the object is small and plain, with "
  "few features to match. Visual and geometric scores agree: across the 200 models, Spearman's ρ between mesh F and "
  "PSNR is 0.80 and with SSIM 0.87.")
p("**Answer to RQ1:** within this range, acquisition effort affects quality as a threshold rather than a slope. With an "
  "azimuth step of 24° or finer (47 images or more), shape and appearance match those from 362 images; at 45° (26 "
  "images) coverage breaks down and both collapse.")
h2("5.2 RQ2: trade-off between effort, cost and quality")
table("Applying one level to every artifact", ["Policy", "Artifacts with mesh F ≥ 0.95", "Total processing time"], [
    ("Every artifact at L1", "31", "40.1 h"), ("Every artifact at L2", "31", "15.5 h"), ("Every artifact at L3", "30", "6.3 h"),
    ("Every artifact at L4", "28", "2.7 h"), ("Every artifact at L5", "5", "0.8 h"),
    ("Cheapest sufficient level per artifact (hindsight only)", "31", "2.6 h")], widths=[3.0, 1.6, 1.4])
p("Processing time grows faster than the number of images, as about images^1.34 (median over artifacts), because "
  "exhaustive matching compares every pair of images; peak memory stops falling below L3 at about 2 GB. Where the cost "
  "curve is steep, the quality curve is flat: L3 uses 17% and L4 6.3% of L1's time with median mesh F within 0.003 of "
  "L1. The real trade-off is reliability against time (Table 7): moving from L4 to L3 more than doubles the time and "
  "recovers two artifacts; L2 and L1 cost 15.5 h and 40.1 h and recover one more.")
table("Combined cost-effectiveness score (w = 0.5)", ["Level", "Quality", "Saving", "Score"], [
    ("L1", "0.893", "0.000", "0.446"), ("L2", "0.892", "0.510", "0.701"), ("L3", "0.887", "0.689", "0.788"),
    ("L4", "0.870", "0.772", "0.821"), ("L5", "0.433", "0.825", "0.629")], widths=[1.0, 1.2, 1.2, 1.2])
figure(PLOTS / "tradeoff_score.png", "Combined score of each level as the weight on quality changes", 5.4)
p("With equal weights L4 scores best (0.821) and L3 second (0.788). The weight check shows that L4 is best for every "
  "quality weight from 0.15 to 0.80 and L3 from 0.85 to 0.95; L1 wins only when cost is ignored entirely and L5 only "
  "when quality counts for 10% or less (Figure 8).")
p("**Answer to RQ2:** cost and quality are not traded smoothly. Cost rises steeply with image count while quality "
  "reaches its plateau at about 47 images. The practical choice is between 47 images (lowest cost, 28 of 40 sufficient) "
  "and 92 images (2.3 times the time, 30 of 40 sufficient); 182 or 362 images add cost without adding quality.")
h2("5.3 RQ3: optimised models in the virtual museum")
table("Museum model against full L3 model, medians over 44 exhibits", ["Measure", "Museum model", "Full model", "Museum as share of full"],
      RQ3, widths=[2.4, 1.2, 1.2, 1.3])
p("Decimation to 100,000 triangles changed the surface F-score by at most 0.0003 and the Chamfer distance by at most "
  "0.3% on any exhibit. Appearance dropped by 0.20 dB PSNR (95% interval −0.24 to −0.16) and 0.005 SSIM, consistently "
  "on 43 and 44 of 44 exhibits; this is smaller than the PSNR gap between L1 and L3. In the browser (Chrome on the same "
  "laptop, 20 Mbit/s simulated bandwidth for downloads), the museum models took 19% of the file size, 23% of the "
  "download time, 31% of the decoding time and 43% of the drawing time of the full models (Table 9). The whole "
  "collection is 129.6 MB against 669 MB and downloaded in 68 s against 281 s. GPU upload saves least (85%) because "
  "both versions carry the same texture, which also dominates graphics memory.")
figure(PLOTS / "rq3_costs.png", "Browser cost of the museum and full models for the 44 exhibits", 6.0)
figure(FIG / "visual_compare.jpg", "One exhibit from three held-out views: dataset photo (top), museum model render (middle), difference ×3 (bottom)", 3.6)
p("**Answer to RQ3:** yes, on this hardware. The optimised models keep their geometric accuracy, lose only 0.2 dB of "
  "PSNR, and reduce file size and download time to about a fifth to a quarter. The complete museum with 44 exhibits "
  "held 60 frames per second in every measured view on integrated graphics.")
h2("5.4 Hypotheses")
table("Outcome of the hypotheses", ["Hypothesis", "Result", "Evidence"], [
    ("H1", "Supported (memory stops falling below L3)", "Time falls to 6.3% of L1 at L4 and 1.7% at L5; quality and completeness collapse at L5 (recall 0.41, mesh F 0.58)."),
    ("H2", "Supported", "L3 and L4 keep median mesh F within 0.003 of L1 and PSNR within 0.5 dB at 17% and 6.3% of the time."),
    ("H3", "Supported", "19% of the file size, 23% of download and 43% of drawing time for 0.20 dB PSNR and no measurable geometric change."),
], widths=[0.6, 1.8, 3.5], size=10)
h2("5.5 Limitations")
bullets(["CHSD images are synthetic renders with ideal cameras and lighting; the results are controlled benchmark findings, not universal claims about real museum photography.",
         "One frozen COLMAP + OpenMVS configuration on one laptop; each level was timed once.",
         "SfM sometimes split the images into separate models and only the largest was densified, which lowered scores for some artifacts.",
         "The cut-off set was run at L3 only, and its reference shares the framing of the images.",
         "The combined score's parts and weights are the team's choice; the weight check shows the ranking of L3 and L4 is stable.",
         "Browser costs were measured on one laptop with simulated bandwidth and no network latency; the museum is not yet hosted online."])
page_break()

# ---------------------------------------------------------------- conclusion, future work
h1("Conclusion")
p("This project measured, under controlled conditions, how many photographs are needed to digitize an individual "
  "heritage artifact and what each extra photograph costs. Across 200 reconstructions of 40 artifacts on a CPU-only "
  "laptop, quality reached its plateau at about 47 images: 47 to 92 images gave the same shape and appearance as 362 at "
  "6–17% of the processing time, while 26 images were too few. A combined cost-effectiveness score confirmed 47 images "
  "(L4) as the most economical choice and 92 images (L3) as the safer one, for almost any weighting. Web-optimised "
  "models kept their accuracy at a fraction of the size and rendering cost, and a walkable virtual museum now presents "
  "44 of the artifacts. All three hypotheses were supported. The contribution is a reproducible framework that links "
  "acquisition effort, computing cost and quality for single artifacts and carries the result through to web delivery.")
h1("Scope for Future Work")
bullets(["Validate the findings with real photographs of a small set of objects.",
         "Densify all models when SfM splits the images, and test a faster feature matcher to cut the cost of large image sets.",
         "Study the precision loss with many images by tuning the dense-fusion settings.",
         "Host the museum online, measure real download times, and add a small user study of the visitor experience.",
         "Extend the comparison to neural methods (NeRF, Gaussian Splatting) on the same controlled subsets."])
page_break()

# ---------------------------------------------------------------- appendices
h1("Appendices")
h2("Appendix A: Reproducing the results")
for line in ("python scripts/check_env.py", "python scripts/run_batch.py --count 40 --clean",
             "python scripts/analyze_tradeoff.py", "python scripts/evaluate_visual.py   then   python scripts/analyze_visual.py",
             "python scripts/export_glb.py   and   python scripts/analyze_rq3.py",
             "python -m http.server 8000 --directory museum   (open http://localhost:8000)"):
    par = p(line, align="l"); par.runs[0].font.name = "Consolas"; par.runs[0].font.size = Pt(10)
p("Data paths come from configs/experiment.toml; raw data, clouds and meshes are kept outside the repository.")
h2("Appendix B: Repository structure")
table("Main folders of the project repository", ["Folder", "Contents"], [
    ("configs/", "Frozen pipeline settings and artifact order"), ("src/heritage3d/", "Shared Python modules"),
    ("scripts/", "Command-line tools for every step"), ("tests/", "81 automated tests"),
    ("experiments/results/", "Per-run JSON files, summary CSV files, team Excel workbook"),
    ("experiments/plots/", "Charts and preview images"), ("experiments/logs/", "Logs of every run"),
    ("museum/", "Virtual museum website and the 44 GLB models"), ("vault/", "Project notes, decisions and session log")],
    widths=[1.8, 4.1], size=10)
page_break()

# ---------------------------------------------------------------- references
h1("References")
for i, ref in enumerate(REFS, 1):
    par = doc.add_paragraph()
    par.paragraph_format.line_spacing = 1.0
    par.paragraph_format.left_indent = Inches(0.45)
    par.paragraph_format.first_line_indent = Inches(-0.45)
    par.paragraph_format.space_after = Pt(4)
    par.add_run(f"[{i}]\t{ref}").font.size = Pt(11)


out = OUT / "Report"
out.mkdir(parents=True, exist_ok=True)
doc.save(out / "heritage3d_Report.docx")
print("saved", out / "heritage3d_Report.docx")
