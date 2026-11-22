# Final evaluation deliverables: Team T212

**Cost-Effective Image-Based 3D Digitization of Cultural Heritage Artifacts for Virtual Museum Applications**
Ayaan Goel (23BCP264) · Kshiti Bhavsar (23BCP275) · Guide: Prof. Komal Singh

| Deliverable | Files | Notes |
|---|---|---|
| Project report | `Report/heritage3d_Report.docx`, `.pdf` | Department format: A4, Times New Roman 12, 1.5 spacing, margins 1.5" left / 1" others; 35 pages |
| Presentation | `Presentation/heritage3d_Presentation.pptx`, `.pdf` | 18 main slides + 2 backup, following the 20-point PPT guideline |
| Presentation, version 2 | `Presentation/heritage3d_Presentation_v2.pptx`, `.pdf` | Same content, one consistent design (department lavender/purple, Georgia headings, fixed grid), new purple charts and a museum slide; 19 main + 2 backup. Version 1 kept |
| Poster | `Poster/heritage3d_Poster_v2.pptx` | Hand-edited by the team (SoT logo) plus 5 labelled figures (Fig. 1–5: pipeline, reconstruction strip, score chart, two museum views) and three result tiles; do not rebuild with `build_poster_v2.py`, it would overwrite those edits. Department template colours kept (lavender bars, Times New Roman headings) with matching purple accents; adds the acquisition-cost table, the combined-score formula and a score-breakdown chart. |
| Live demo | `Demo/Run_Museum.bat`, `Demo/Demo_Checklist.md` | Double-click to start the museum at http://localhost:8000 |
| Figures | `figures/` | Pipeline diagram and museum screenshots used in all three documents |
| Department guidelines | `Projet Report Format.pdf`, `Minor_Project_PPT_Preparation_Guidelines.pdf`, `Poster Template.pptx`, panel list | As received; kept on this laptop only (git-ignored), except the poster template the poster script builds on |

The software itself (pipeline, analysis, museum) is in the repository; every number in these documents comes from
`experiments/results/` (sources listed in `docs/report/results.md`, Section 7).

## Fill in before submitting

- [x] **Department name** and **Prof. Komal Singh's designation**: Department of Computer Science and Engineering; Assistant Professor (filled 2026-11-22).
- [x] **Evaluation date** on slide 1: 23-11-2026.
- [ ] **Examiner's name and designation** on the report certificate (`[Name of Examiner]`, `[Designation]`).
- [ ] **AI-use declaration** (report page 4): it states truthfully that an AI coding assistant was used, including for drafting text. Confirm this wording with Prof. Singh, then delete the red note.
- [ ] Read and edit the report text, then right-click the contents page → Update Field if page numbers move.
- [ ] Add the school logo to the poster's top-right box if required.
- [ ] Printing: cover page in colour on card stock, rest black and white, soft-bound with a blue cover.

## Rebuilding

```
python scripts/deliverables/diagram.py
python scripts/deliverables/build_report.py
python scripts/deliverables/build_slides.py
python scripts/deliverables/build_poster.py
python scripts/deliverables/diagram.py --heritage
python scripts/deliverables/score_chart.py
python scripts/deliverables/build_poster_v2.py
python scripts/deliverables/slide_charts.py
python scripts/deliverables/build_slides_v2.py
powershell -File scripts/deliverables/to_pdf.ps1
```

Rebuilding overwrites manual edits to the .docx/.pptx files, so edit the generated files only once the content is final.
