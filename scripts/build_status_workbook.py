"""Write the Excel status of all CHSD artifacts: experiments/results/artifact_status.xlsx.

Reads only what the runs left behind (experiments/results/runs, museum/artifacts.json,
configs/artifact_order.json, experiments/results/dataset_inspection.json), so it can be rerun at any
time, also during a batch. Rerun after every round; close the file in Excel first.

Usage (PowerShell):
    python scripts/build_status_workbook.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from openpyxl import Workbook  # noqa: E402
from openpyxl.formatting.rule import ColorScaleRule  # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill  # noqa: E402

from heritage3d.compare import collect  # noqa: E402
from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402
from heritage3d.status import LEVELS, artifact_status  # noqa: E402

OUT = REPO_ROOT / "experiments" / "results" / "artifact_status.xlsx"
FONT = "Arial"
HEADER_FILL = PatternFill("solid", fgColor="3B3228")
MUSEUM_FILL = {"Yes": "D5E8D4", "No": "F4D6D2", "Pending": "FFF2CC"}
COLUMNS = [  # key, header, width
    ("rank", "Rank", 6), ("artifact", "Artifact", 21), ("set", "Set", 8), ("status", "Status", 11),
    *[(level, level, 7) for level in LEVELS],
    ("best", "Best level", 7), ("registered", "L3 photos used (of 92)", 10), ("mesh_f", "L3 mesh F", 8),
    ("museum", "In museum", 9), ("museum_level", "Museum level", 8), ("museum_f", "Museum model F", 8),
    ("reason", "Reason if not in museum", 78),
]
LETTER = {key: chr(ord("A") + i) for i, (key, _, _) in enumerate(COLUMNS)}


def read_json(*parts):
    return json.loads(REPO_ROOT.joinpath(*parts).read_text(encoding="utf-8"))


def load_rows():
    museum = load_config(DEFAULT_CONFIG)["museum"]
    ranks = {a["name"]: a["rank"] for a in read_json("configs", "artifact_order.json")["artifacts"]}
    inspection = read_json("experiments", "results", "dataset_inspection.json")["artifacts"]
    exhibits = {e["id"]: e for e in read_json("museum", "artifacts.json")["artifacts"]}
    runs = REPO_ROOT / "experiments" / "results" / "runs"
    rows = [
        artifact_status(name, ranks.get(name), collect(runs, name, LEVELS), inspection[name]["cut_off_fraction"],
                        exhibits.get(name), museum["min_mesh_f"], museum["level"])
        for name in inspection
    ]
    return sorted(rows, key=lambda r: (r["rank"] is None, r["rank"] or 0, r["artifact"])), museum


def artifacts_sheet(sheet, rows):
    sheet.append([header for _, header, _ in COLUMNS])
    for i, (key, _, width) in enumerate(COLUMNS, start=1):
        sheet.column_dimensions[LETTER[key]].width = width
        cell = sheet.cell(1, i)
        cell.font = Font(name=FONT, bold=True, color="FFFFFF")
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    sheet.row_dimensions[1].height = 48
    first, last = LETTER[LEVELS[0]], LETTER[LEVELS[-1]]
    for n, row in enumerate(rows, start=2):
        scores = f"{first}{n}:{last}{n}"
        best = f'=IF(COUNT({scores})=0,"",INDEX(${first}$1:${last}$1,MATCH(MAX({scores}),{scores},0)))'
        sheet.append([best if key == "best" else row[key] for key, _, _ in COLUMNS])
        for key, _, _ in COLUMNS:
            cell = sheet[f"{LETTER[key]}{n}"]
            cell.font = Font(name=FONT)
            if key in (*LEVELS, "mesh_f", "museum_f"):
                cell.number_format = "0.000"
            if key not in ("artifact", "reason"):
                cell.alignment = Alignment(horizontal="center")
        sheet[f"{LETTER['museum']}{n}"].fill = PatternFill("solid", fgColor=MUSEUM_FILL[row["museum"]])
    end = len(rows) + 1
    sheet.conditional_formatting.add(f"{first}2:{last}{end}", ColorScaleRule(
        start_type="num", start_value=0, start_color="F08A7E",
        mid_type="num", mid_value=0.75, mid_color="FFE699",
        end_type="num", end_value=1, end_color="7FC97F"))
    sheet.freeze_panes = "C2"
    sheet.auto_filter.ref = f"A1:{LETTER['reason']}{end}"


def summary_sheet(sheet, rows, museum):
    end = len(rows) + 1
    col = lambda key: f"'All artifacts'!${LETTER[key]}$2:${LETTER[key]}${end}"
    bold, plain = Font(name=FONT, bold=True), Font(name=FONT)
    lines = [
        ("heritage3d: status of all CHSD artifacts", None),
        (f"Updated {datetime.now():%Y-%m-%d %H:%M} by scripts/build_status_workbook.py", None),
        (None, None),
        ("Artifacts", None),
        ("In CHSD", f"=COUNTA({col('artifact')})"),
        ("Main set (never cut off in the sample views)", f'=COUNTIF({col("set")},"Main")'),
        ("Cut off by the frame", f'=COUNTIF({col("set")},"Cut off")'),
        ("Cut off, run at some levels (separate from the main set)", f'=COUNTIF({col("status")},"Partly run")'),
        ("Done at all five levels", f'=COUNTIF({col("status")},"Done")'),
        ("In progress", f'=COUNTIF({col("status")},"In progress")'),
        ("Queued", f'=COUNTIF({col("status")},"Queued")'),
        ("In the museum", f'=COUNTIF({col("museum")},"Yes")'),
        ("Museum decision pending", f'=COUNTIF({col("museum")},"Pending")'),
        ("Finished but not exhibited", f'=COUNTIFS({col("museum")},"No",{col("set")},"Main")'),
    ]
    for label, value in lines:
        sheet.append([label, value])
    sheet["A1"].font = Font(name=FONT, bold=True, size=14)
    sheet["A2"].font = Font(name=FONT, italic=True, color="666666")
    for r in range(3, sheet.max_row + 1):
        sheet[f"A{r}"].font = bold if r == 4 else plain
        sheet[f"B{r}"].font = plain

    sheet.append([])
    sheet.append(["Per level, main set", "Runs", "Median F", "Lowest F", "F below 0.5"])
    head = sheet.max_row
    for c in "ABCDE":
        sheet[f"{c}{head}"].font = Font(name=FONT, bold=True, color="FFFFFF")
        sheet[f"{c}{head}"].fill = HEADER_FILL
    main_end = sum(r["set"] == "Main" for r in rows) + 1  # rows are sorted with the main set first
    for level in LEVELS:
        c = f"'All artifacts'!${LETTER[level]}$2:${LETTER[level]}${main_end}"
        sheet.append([level, f"=COUNT({c})", f"=MEDIAN({c})", f"=MIN({c})", f'=COUNTIF({c},"<0.5")'])
        r = sheet.max_row
        for letter in "ABCDE":
            sheet[f"{letter}{r}"].font = plain
        sheet[f"C{r}"].number_format = sheet[f"D{r}"].number_format = "0.000"

    notes = [
        "How to read this",
        "L1 to L5 hold F@0.002 R of the dense point cloud against the CHSD reference (1.0 is perfect; 0.000 means no usable cloud; blank means no result yet).",
        "Photos per level: L1 362, L2 182, L3 92, L4 47, L5 26.",
        f"Exhibit rule: {museum['level']} mesh F (vertices, from the evaluation) at least {museum['min_mesh_f']}. Every exhibit shows {museum['level']}.",
        "Museum model F is measured on the final museum model's surface, so it differs a little from the other columns.",
        "L3 photos used counts the photos in the sparse model that was densified.",
        "Cut off: the object touches or leaves the image edge in some of the 20 sample views (dataset_inspection.json). Those cut off in at most 30% were run at L3 as a separate set; the others were not reconstructed.",
        "Every value comes from the run files in experiments/results. Do not edit by hand: the file is rewritten by the script.",
    ]
    sheet.append([])
    for i, text in enumerate(notes):
        sheet.append([text])
        sheet[f"A{sheet.max_row}"].font = bold if i == 0 else plain
    sheet.column_dimensions["A"].width = 46
    for c in "BCDE":
        sheet.column_dimensions[c].width = 12


def main():
    rows, museum = load_rows()
    book = Workbook()
    book.active.title = "Summary"
    summary_sheet(book.active, rows, museum)
    artifacts_sheet(book.create_sheet("All artifacts"), rows)
    try:
        book.save(OUT)
    except PermissionError:
        sys.exit(f"Could not write {OUT}: close it in Excel and run this again.")
    count = lambda key, value: sum(r[key] == value for r in rows)
    print(f"{len(rows)} artifacts: {count('status', 'Done')} done, {count('status', 'In progress')} in progress, "
          f"{count('status', 'Queued')} queued, {count('status', 'Not run')} not run; "
          f"museum {count('museum', 'Yes')} yes, {count('museum', 'Pending')} pending")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
