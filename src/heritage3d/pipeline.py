"""SfM + MVS pipeline: COLMAP (CPU) for sparse, OpenMVS (CPU) for dense/mesh/texture.

Each stage is one external command. `run_stage` records wall time and the peak memory
of the whole process tree (on Windows via a job object, so helper processes such as
the COLMAP.bat -> colmap.exe chain are included).
"""

import re
import subprocess
import sys
import time
from pathlib import Path

from heritage3d.environment import COLMAP_CANDIDATES, find_tool


def sparse_commands(colmap, ws, image_root, image_list, settings):
    """COLMAP feature extraction, matching and mapping into ws/sparse."""
    db = ws / "database.db"
    return [
        ("feature_extractor", [
            colmap, "feature_extractor", "--database_path", db, "--image_path", image_root,
            "--image_list_path", image_list,
            "--ImageReader.camera_model", settings["camera_model"],
            "--ImageReader.single_camera", int(settings["single_camera"]),
            "--FeatureExtraction.use_gpu", 0,
        ]),
        (settings["matcher"], [colmap, settings["matcher"], "--database_path", db, "--FeatureMatching.use_gpu", 0]),
        ("mapper", [colmap, "mapper", "--database_path", db, "--image_path", image_root,
                    "--output_path", ws / "sparse"]),
    ]


def dense_commands(colmap, ws, image_root, model, settings):
    """Undistort with COLMAP, then OpenMVS densify -> mesh -> texture in ws/mvs."""
    dense, mvs = ws / "dense", ws / "mvs"
    return [
        ("image_undistorter", [colmap, "image_undistorter", "--image_path", image_root, "--input_path", model,
                               "--output_path", dense, "--output_type", "COLMAP"]),
        ("InterfaceCOLMAP", ["InterfaceCOLMAP", "-i", dense, "-o", mvs / "scene.mvs",
                             "--image-folder", dense / "images"]),
        ("DensifyPointCloud", ["DensifyPointCloud", "-i", mvs / "scene.mvs", "-o", mvs / "scene_dense.mvs",
                               "--resolution-level", settings["densify_resolution_level"]]),
        ("ReconstructMesh", ["ReconstructMesh", "-i", mvs / "scene_dense.mvs",
                             "-o", mvs / "scene_dense_mesh.ply"]),
        ("TextureMesh", ["TextureMesh", "-i", mvs / "scene_dense.mvs", "-m", mvs / "scene_dense_mesh.ply",
                         "-o", mvs / "scene_dense_texture.ply"]),
    ]


def colmap_path():
    path = find_tool(COLMAP_CANDIDATES)
    if not path:
        raise FileNotFoundError("COLMAP not found on PATH")
    return path


def parse_model_analyzer(text):
    """Pull the key numbers out of `colmap model_analyzer` output."""
    fields = {
        "cameras": r"Cameras:\s*(\d+)",
        "images": r"\] Images:\s*(\d+)",
        "registered_images": r"Registered images:\s*(\d+)",
        "points": r"Points:\s*(\d+)",
        "observations": r"Observations:\s*(\d+)",
        "mean_track_length": r"Mean track length:\s*([\d.]+)",
        "mean_observations_per_image": r"Mean observations per image:\s*([\d.]+)",
        "mean_reprojection_error_px": r"Mean reprojection error:\s*([\d.]+)",
    }
    out = {}
    for key, pattern in fields.items():
        m = re.search(pattern, text)
        if m:
            out[key] = float(m.group(1)) if "." in m.group(1) else int(m.group(1))
    return out


if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    class _IoCounters(ctypes.Structure):
        _fields_ = [(n, ctypes.c_ulonglong) for n in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class _BasicLimits(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD),
        ]

    class _ExtendedLimits(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _BasicLimits), ("IoInfo", _IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    _JOB_EXTENDED_LIMIT_INFORMATION = 9
    _CREATE_SUSPENDED = 0x4


def run_stage(name, cmd, log_path, cwd=None):
    """Run one command, log its output, and return time / peak memory / exit code.

    peak_memory_mb is the peak committed (private) memory of the process tree on
    Windows; None elsewhere.
    """
    cmd = [str(c) for c in cmd]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    job = None
    if sys.platform == "win32":
        # Start suspended, put it in a job object, then resume: children are counted from the first instruction.
        flags |= _CREATE_SUSPENDED
        job = _kernel32.CreateJobObjectW(None, None)
    start = time.perf_counter()
    with open(log_path, "w", encoding="utf-8", errors="replace") as log:
        log.write("$ " + subprocess.list2cmdline(cmd) + "\n")
        log.flush()
        proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=cwd, creationflags=flags)
        if job:
            _kernel32.AssignProcessToJobObject(job, wintypes.HANDLE(int(proc._handle)))
            ctypes.WinDLL("ntdll").NtResumeProcess(wintypes.HANDLE(int(proc._handle)))
        returncode = proc.wait()
    seconds = time.perf_counter() - start
    peak = None
    if job:
        info = _ExtendedLimits()
        if _kernel32.QueryInformationJobObject(job, _JOB_EXTENDED_LIMIT_INFORMATION, ctypes.byref(info),
                                               ctypes.sizeof(info), None):
            peak = round(info.PeakJobMemoryUsed / 1024**2, 1)
        _kernel32.CloseHandle(job)
    return {"stage": name, "seconds": round(seconds, 1), "peak_memory_mb": peak, "returncode": returncode,
            "log": str(log_path)}


def folder_bytes(path):
    path = Path(path)
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.exists() else 0


# Intermediates that can be regenerated and are not needed for evaluation or the museum:
# per-view depth maps, the COLMAP feature database and the undistorted image copies.
# Undistorted images sit in subfolders named after the input paths (dense/images/<artifact>/RGB/...).
INTERMEDIATES = ("mvs/depth*.dmap", "database.db", "dense/images/**/*")


def clean_workspace(ws):
    """Delete regenerable intermediates from a finished workspace; returns bytes freed."""
    freed = 0
    for pattern in INTERMEDIATES:
        for f in Path(ws).glob(pattern):
            if f.is_file():
                freed += f.stat().st_size
                f.unlink()
    return freed
