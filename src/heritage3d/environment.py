"""Record the software and hardware environment of a run (tool versions, CPU, RAM, OS)."""

import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

COLMAP_CANDIDATES = ["colmap", "COLMAP.bat"]
OPENMVS_TOOLS = ["InterfaceCOLMAP", "DensifyPointCloud", "ReconstructMesh", "RefineMesh", "TextureMesh"]


def find_tool(names):
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def _run(cmd, cwd=None):
    """Run a tool and return its captured output.

    On Windows, OpenMVS writes its banner straight to the console, not to stdout,
    so it is run without a console window (output is dropped instead of cluttering
    the terminal) and its log file in `cwd` is read instead.
    """
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=cwd, creationflags=flags)
        return out.stdout + out.stderr
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _run_with_logs(cmd):
    """Run in a temporary folder and append any *.log files the tool wrote there."""
    with tempfile.TemporaryDirectory() as tmp:
        text = _run(cmd, cwd=tmp)
        for log in sorted(Path(tmp).glob("*.log")):
            text += "\n" + log.read_text(encoding="utf-8", errors="replace")
    return text


def parse_colmap_version(text):
    m = re.search(r"COLMAP (\S+) \(Commit (\w+).*?(with|without) GPU support", text)
    if not m:
        return None
    return {"version": m.group(1), "commit": m.group(2), "gpu": m.group(3) == "with"}


def parse_openmvs_version(text):
    m = re.search(r"OpenMVS \S+ v(\S+)", text)
    return {"version": m.group(1)} if m else None


def cpu_name():
    if sys.platform == "win32":
        try:
            import winreg

            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            return winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        except OSError:
            pass
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or None


def ram_gb():
    if sys.platform == "win32":
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + [
                (n, ctypes.c_ulonglong)
                for n in ("total", "avail", "totalPage", "availPage", "totalVirtual", "availVirtual", "availExtended")
            ]

        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return round(status.total / 1024**3, 2)
        return None
    try:
        return round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024**3, 2)
    except (ValueError, OSError, AttributeError):
        return None


def collect():
    report = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "colmap": None,
        "openmvs": None,
        "openmvs_tools": {},
        "hardware": {"cpu": cpu_name(), "logical_cpus": os.cpu_count(), "ram_gb": ram_gb()},
    }
    colmap = find_tool(COLMAP_CANDIDATES)
    if colmap:
        report["colmap"] = parse_colmap_version(_run([colmap, "-h"])) or {"version": "unknown"}
        report["colmap"]["path"] = colmap
    for tool in OPENMVS_TOOLS:
        report["openmvs_tools"][tool] = find_tool([tool])
    densify = report["openmvs_tools"]["DensifyPointCloud"]
    if densify:
        report["openmvs"] = parse_openmvs_version(_run_with_logs([densify, "--help"])) or {"version": "unknown"}
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
