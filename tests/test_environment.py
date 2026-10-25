import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.environment import (
    collect,
    parse_colmap_version,
    parse_openmvs_version,
    problems,
)

# Banners as printed on the team laptop (2026-10-25).
COLMAP_BANNER = "COLMAP 4.2.1 (Commit bd1fcf6 on 2026-09-29 without GPU support, boost hash maps)\nUsage:"
OPENMVS_BANNER = """01:23:22 [App     ] OpenMVS x64 v2.4.0
01:23:22 [App     ] CPU: 12th Gen Intel(R) Core(TM) i7-1255U (12 cores)
01:23:22 [App     ] RAM: 15.72GB Physical Memory 128.00TB Virtual Memory
01:23:22 [App     ] OS: Windows 11+ x64
"""


def test_parse_colmap_version():
    assert parse_colmap_version(COLMAP_BANNER) == {"version": "4.2.1", "commit": "bd1fcf6", "gpu": False}


def test_parse_colmap_version_unrecognised():
    assert parse_colmap_version("something else") is None


def test_parse_openmvs_version():
    assert parse_openmvs_version(OPENMVS_BANNER) == {"version": "2.4.0"}


def test_hardware_is_detected_without_tools():
    hw = collect()["hardware"]
    assert hw["logical_cpus"] and hw["logical_cpus"] > 0
    assert hw["ram_gb"] and hw["ram_gb"] > 0


def test_problems_lists_missing_tools():
    report = {"colmap": None, "openmvs_tools": {"DensifyPointCloud": None, "TextureMesh": "x"}}
    assert problems(report) == [
        "COLMAP not found on PATH",
        "OpenMVS tools not found on PATH: DensifyPointCloud",
    ]
