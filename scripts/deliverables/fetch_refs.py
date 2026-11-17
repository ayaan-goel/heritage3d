"""Fetch reference metadata (Crossref) for the literature workbook papers -> docs/report/references.json."""
import json, re, urllib.request, urllib.parse
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[2]
EXTRA = {  # links without a DOI in the workbook -> DOI found by lookup (2026-11-16/17)
    "mdpi.com/2076-3417/12/24/12886": "10.3390/app122412886",
    "mdpi.com/2072-4292/16/2/301": "10.3390/rs16020301",
    "portalcientifico.upm.es": "10.3390/rs17142535",
    "S1296207424001055": "10.1016/j.culher.2024.05.008",
    "s40494-025-01944-z": "10.1038/s40494-025-01944-z",
    "s40494-024-01241-1": "10.1038/s40494-024-01241-1",
    "s40494-024-01365-4": "10.1038/s40494-024-01365-4",
}
QUERY = {  # no DOI: bibliographic search
    "re.public.polimi.it": "Image-based 3D capture of cultural heritage artifacts an experimental study about 3D data quality Guidi 2015",
    "PMC7425849": "A rapid and cost-effective pipeline for digitization of museum specimens with 3D photogrammetry Medina 2020",
    "XLVIII-2-W4-2024/317": "Poux 2024 multi-view stereo NeRF close-range heritage documentation ISPRS",
    "gi.6.24": "Kirchhofer Chandler Wackrow cultural heritage recording utilising low-cost close-range photogrammetry",
    "XLVIII-2-W8-2024/425": "Cuca 2024 Tombs of the Kings 360 camera photogrammetry ISPRS",
    "XLVIII-1-2024/487": "Maschio 2024 iPhone 15 Pro RTK heritage documentation ISPRS",
    "XLVIII-M-9-2025/1167": "Pavelka Vana 2025 low-cost technologies heritage documentation ISPRS",
    "pone.0308": "Li Lv 2024 online VR museum exhibition Liangzhu PLOS ONE",
    "S1296207420303551": "Virtual museums captured reality and 3D modeling Journal of Cultural Heritage 2020",
    "S2212054823000048": "Antikythera Mechanism virtual museum CT photorealistic Digital Applications in Archaeology and Cultural Heritage 2023",
}

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "heritage3d-references/1.0 (student project)"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def doi_of(link):
    m = re.search(r"10\.\d{4,9}/[^\s?#]+", link)
    if m: return m.group(0).rstrip("/")
    for k, v in EXTRA.items():
        if k in link: return v
    return None

rows = list(openpyxl.load_workbook(ROOT / "docs/literature/Literature_Review_Cultural_Heritage_Artifacts_FINAL.xlsx", read_only=True)["All Papers"].iter_rows(values_only=True))[1:]
seen, out = set(), []
for r in rows:
    link = r[9]
    if link in seen: continue
    seen.add(link)
    doi = doi_of(link)
    try:
        if doi:
            m = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
        else:
            q = next(v for k, v in QUERY.items() if k in link)
            m = get("https://api.crossref.org/works?rows=1&query.bibliographic=" + urllib.parse.quote(q))["message"]["items"][0]
        out.append({"workbook_author": r[1], "year": r[2], "link": link, "title": m.get("title", [""])[0],
                    "authors": [f"{a.get('given','')} {a.get('family','')}".strip() for a in m.get("author", [])],
                    "venue": (m.get("container-title") or [""])[0], "volume": m.get("volume"), "issue": m.get("issue"),
                    "page": m.get("page") or m.get("article-number"), "doi": m.get("DOI"), "type": m.get("type"),
                    "issued": (m.get("issued", {}).get("date-parts") or [[None]])[0][0], "matched_by": "doi" if doi else "search"})
    except Exception as e:
        out.append({"workbook_author": r[1], "year": r[2], "link": link, "error": str(e)})
(ROOT / "docs/report").mkdir(parents=True, exist_ok=True)
(ROOT / "docs/report/references.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
for o in out:
    print(o.get("matched_by", "ERR"), "|", o["workbook_author"], o["year"], "|", o.get("issued"), "|", (o.get("title") or o.get("error", ""))[:85], "|", (o.get("venue") or "")[:40])
