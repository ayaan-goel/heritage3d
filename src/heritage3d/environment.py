"""Record the software and hardware environment of a run (tool versions, CPU, RAM, OS)."""

import os
import platform
import re
import shutil
import subprocess
import sys

COLMAP_CANDIDATES = ["colmap", "COLMAP.bat"]
OPENMVS_TOOLS = ["InterfaceCOLMAP", "DensifyPointCloud", "ReconstructMesh", "RefineMesh", "TextureMesh"]


def find_tool(names):
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def _run(cmd):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return out.stdout + out.stderr
    except (OSError, subprocess.TimeoutExpired):
        return ""


def parse_colmap_version(text):
    m = re.search(r"COLMAP (\S+) \(Commit (\w+).*?(with|without) GPU support", text)
    if not m:
        return None
    return {"version": m.group(1), "commit": m.group(2), "gpu": m.group(3) == "with"}


def parse_openmvs_version(text):
    m = re.search(r"OpenMVS \S+ v(\S+)", text)
    return {"version": m.group(1)} if m else None


def parse_openmvs_hardware(text):
    """OpenMVS prints CPU, RAM and OS in its banner; reuse it to avoid extra dependencies."""
    info = {}
    for key, pattern in (("cpu", r"CPU: (.+)"), ("ram", r"RAM: (\S+) Physical"), ("os", r"OS: (.+)")):
        m = re.search(pattern, text)
        if m:
            info[key] = m.group(1).strip()
    return info


def collect():
    report = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "colmap": None,
        "openmvs": None,
        "openmvs_tools": {},
        "hardware": {},
    }
    colmap = find_tool(COLMAP_CANDIDATES)
    if colmap:
        report["colmap"] = parse_colmap_version(_run([colmap, "-h"])) or {"version": "unknown"}
        report["colmap"]["path"] = colmap
    for tool in OPENMVS_TOOLS:
        report["openmvs_tools"][tool] = find_tool([tool])
    densify = report["openmvs_tools"]["DensifyPointCloud"]
    if densify:
        text = _run([densify, "--help"])
        report["openmvs"] = parse_openmvs_version(text) or {"version": "unknown"}
        report["hardware"] = parse_openmvs_hardware(text)
    return report


def problems(report):
    """Human-readable list of what is missing; empty when the pipeline can run."""
    issues = []
    if not report["colmap"]:
        issues.append("COLMAP not found on PATH")
    missing = [t for t, p in report["openmvs_tools"].items() if not p]
    if missing:
        issues.append("OpenMVS tools not found on PATH: " + ", ".join(missing))
    return issues
