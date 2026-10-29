import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.config import load_config
from heritage3d.subsets import View, azimuths, build_levels, select_views, view_path

RINGS = [-90, -45, 0, 45, 90]


def test_planned_level_totals():
    levels = build_levels(load_config())
    # 3 turning rings x 360/step views + one view for each of the 2 pole rings.
    assert {k: len(v) for k, v in levels.items()} == {"L1": 362, "L2": 182, "L3": 92, "L4": 47, "L5": 26}


def test_levels_l1_to_l4_are_nested():
    levels = build_levels(load_config())
    order = ["L1", "L2", "L3", "L4"]
    for big, small in zip(order, order[1:]):
        assert set(levels[small]) <= set(levels[big])


def test_azimuths_start_at_zero_and_are_uniform():
    assert azimuths(45) == [0, 45, 90, 135, 180, 225, 270, 315]


def test_pole_rings_contribute_one_view_each():
    views = select_views(24, RINGS, pole_rings=[-90, 90])
    assert len(views) == 3 * 15 + 2
    assert View(90, 0) in views and View(90, 24) not in views


def test_step_must_match_source_sampling():
    with pytest.raises(ValueError):
        azimuths(3, source_step=2)


def test_unknown_pole_ring_rejected():
    with pytest.raises(ValueError):
        select_views(12, RINGS, pole_rings=[30])


def test_view_path_uses_pattern():
    assert view_path(View(-45, 90), "pot01", "{artifact}/{elevation}/{azimuth}.png") == "pot01/-45/90.png"


def test_view_path_chsd_frames_start_at_one():
    pattern = load_config()["dataset"]["rgb_pattern"]
    assert view_path(View(0, 0), "a", pattern) == "a/RGB/0001_0_.png"
    assert view_path(View(-45, 359), "a", pattern) == "a/RGB/0360_-45_.png"
