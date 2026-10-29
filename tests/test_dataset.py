import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.dataset import depth_stats, in_plane_rotation_iou, parse_name, scan_folder, touches_border


def test_touches_border():
    mask = np.zeros((10, 10), bool)
    mask[3:6, 3:6] = True
    assert not touches_border(mask)
    mask[3:6, 9] = True
    assert touches_border(mask)


def test_parse_name():
    assert parse_name("0091_-45_.png") == (91, -45)
    assert parse_name("0360_90_.png") == (360, 90)
    assert parse_name("0001_0.png") is None
    assert parse_name("Thumbs.db") is None


def test_scan_folder_reports_missing_and_unexpected(tmp_path):
    for f in (1, 2):
        for e in (0, 45):
            (tmp_path / f"{f:04d}_{e}_.png").touch()
    (tmp_path / "0002_45_.png").unlink()
    (tmp_path / "notes.txt").touch()
    result = scan_folder(tmp_path, rings=[0, 45], frames=[1, 2])
    assert result == {"files": 4, "missing": [(2, 45)], "unexpected": ["notes.txt"]}


def test_depth_stats_quantization():
    depth = np.zeros((4, 4), np.uint16)
    depth[0, :3] = [1000, 1032, 1096]
    s = depth_stats(depth)
    assert s["background_fraction"] == 0.8125
    assert (s["min"], s["max"], s["distinct_values"]) == (1000, 1096, 3)
    assert (s["min_gap"], s["median_gap"]) == (32, 48.0)


def test_depth_stats_empty_map():
    assert depth_stats(np.zeros((2, 2), np.uint16)) == {"dtype": "uint16", "background_fraction": 1.0}


def test_spun_view_detected_and_new_view_not():
    mask = np.zeros((60, 80), bool)
    mask[25:35, 10:60] = True  # off-centre bar
    spun = np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).rotate(90)) > 127
    assert in_plane_rotation_iou(mask, spun, 90) > 0.95
    other = np.zeros_like(mask)
    other[20:40, 30:50] = True  # square blob: not a spin of the bar
    assert in_plane_rotation_iou(mask, other, 90) < 0.5
