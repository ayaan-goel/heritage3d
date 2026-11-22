"""Shared facts, paths and references for the final-evaluation deliverables (report, slides, poster).

Every number here comes from the committed result files (see docs/report/results.md, Section 7)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Deliverables"
FIG = OUT / "figures"
PLOTS = ROOT / "experiments" / "plots"

TITLE = "Cost-Effective Image-Based 3D Digitization of Cultural Heritage Artifacts for Virtual Museum Applications"
TEAM = [("Ayaan Goel", "23BCP264"), ("Kshiti Bhavsar", "23BCP275")]
TEAM_ID = "T212"
GUIDE = "Prof. Komal Singh"
DESIGNATION = "Assistant Professor"
DEPARTMENT = "Department of Computer Science and Engineering"
PROGRAMME = "B.Tech Computer Engineering, Semester VII"
INSTITUTE = "School of Technology, Pandit Deendayal Energy University, Gandhinagar"
MONTH = "November 2026"
EVAL_DATE = "23-11-2026"

# Medians over the 40 main-set artifacts (tradeoff_levels.csv, visual_levels.csv, tradeoff_score.csv)
LEVELS = [  # level, images, step, time min, time share, RAM GB, mesh F, cloud F, PSNR, SSIM, pass, score
    ("L1", 362, "3°", 55.4, "100%", 4.4, 0.984, 0.883, 29.55, 0.918, 31, 0.446),
    ("L2", 182, "6°", 22.4, "40%", 2.3, 0.982, 0.925, 29.03, 0.919, 31, 0.701),
    ("L3", 92, "12°", 9.7, "17%", 2.0, 0.989, 0.965, 29.25, 0.924, 30, 0.788),
    ("L4", 47, "24°", 3.9, "6.3%", 2.0, 0.988, 0.984, 29.20, 0.922, 28, 0.821),
    ("L5", 26, "45°", 1.0, "1.7%", 2.0, 0.580, 0.583, 14.39, 0.595, 5, 0.629),
]
RQ3 = [  # measure, museum, full, share
    ("File size", "2.9 MB", "15.7 MB", "19%"),
    ("Triangles", "100,000", "424,073", "24%"),
    ("Download at 20 Mbit/s (measured)", "1.53 s", "6.62 s", "23%"),
    ("Decoding in the browser", "19.8 ms", "66.8 ms", "31%"),
    ("GPU upload and first frame", "29.9 ms", "34.7 ms", "85%"),
    ("Drawing one frame (1280 × 720)", "0.56 ms", "1.19 ms", "43%"),
]


def _ieee_authors(names):
    def short(n):
        parts = n.replace(".", ". ").split()
        if len(parts) == 1:
            return n
        initials = " ".join(p[0] + "." for p in parts[:-1] if p)
        return f"{initials} {parts[-1]}"
    names = [short(n) for n in names if n.strip()]
    if len(names) > 6:
        return names[0] + " et al."
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + ", and " + names[-1]


def _surname(names):
    return names[0].split()[-1] if names else ""


EXTRA_REFS = [  # tools, data and methods used (key, sort name, IEEE text)
    ("chsd_rgb", "CHSD", 'Cultural Heritage Synthetic Depth Dataset (CHSD): RGB images, Zenodo, 2024. doi: 10.5281/zenodo.11492154. Licence CC BY-NC-SA 4.0.'),
    ("chsd_depth", "CHSD", 'Cultural Heritage Synthetic Depth Dataset (CHSD): depth maps, Zenodo, 2024. doi: 10.5281/zenodo.11484461. Licence CC BY-NC-SA 4.0.'),
    ("colmap", "Schonberger", 'J. L. Schönberger and J.-M. Frahm, "Structure-from-Motion Revisited," in Proc. IEEE Conf. Computer Vision and Pattern Recognition (CVPR), 2016, pp. 4104–4113.'),
    ("openmvs", "Cernea", 'D. Cernea, "OpenMVS: Multi-View Stereo Reconstruction Library," 2020. [Online]. Available: https://cdcseacave.github.io/openMVS'),
    ("threejs", "three.js", 'three.js authors, "three.js – JavaScript 3D library," r170, 2024. [Online]. Available: https://threejs.org'),
    ("gltf", "Khronos", 'Khronos Group, "glTF 2.0 Specification," 2021. [Online]. Available: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html'),
    ("ssim", "Wang", 'Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli, "Image quality assessment: From error visibility to structural similarity," IEEE Trans. Image Processing, vol. 13, no. 4, pp. 600–612, 2004.'),
    ("tanks", "Knapitsch", 'A. Knapitsch, J. Park, Q.-Y. Zhou, and V. Koltun, "Tanks and Temples: Benchmarking large-scale scene reconstruction," ACM Trans. Graphics, vol. 36, no. 4, art. 78, 2017.'),
    ("wilcoxon", "Wilcoxon", 'F. Wilcoxon, "Individual comparisons by ranking methods," Biometrics Bulletin, vol. 1, no. 6, pp. 80–83, 1945.'),
    ("holm", "Holm", 'S. Holm, "A simple sequentially rejective multiple test procedure," Scandinavian J. Statistics, vol. 6, no. 2, pp. 65–70, 1979.'),
]


def references():
    """All references in alphabetical order -> ({key: number}, [text]). Keys for papers are the workbook author field."""
    papers = json.loads((ROOT / "docs/report/references.json").read_text(encoding="utf-8"))
    items, seen = [], set()
    for p in papers:
        p["authors"] = [a for a in p["authors"] if a.strip()]
        if p.get("doi") in seen:
            continue
        seen.add(p.get("doi"))
        text = f'{_ieee_authors(p["authors"])}, "{p["title"].strip().rstrip(".")}," {p["venue"]}'
        if p.get("volume"):
            text += f', vol. {p["volume"]}'
        if p.get("issue"):
            text += f', no. {p["issue"]}'
        if p.get("page"):
            text += f', {"pp." if "-" in str(p["page"]) or "–" in str(p["page"]) else "art."} {p["page"]}'
        text += f', {p.get("issued") or p["year"]}.'
        if p.get("doi"):
            text += f' doi: {p["doi"]}.'
        items.append((p["workbook_author"], _surname(p["authors"]).lower(), text))
    items += [(k, s.lower(), t) for k, s, t in EXTRA_REFS]
    items.sort(key=lambda x: (x[1].replace("ö", "o").replace("á", "a"), x[2]))
    return {k: i + 1 for i, (k, _, _) in enumerate(items)}, [t for _, _, t in items]


def cite(nums, *keys):
    return "[" + ", ".join(str(n) for n in sorted({nums[k] for k in keys})) + "]"
