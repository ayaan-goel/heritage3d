import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.selection import farthest_point_order, texture_score


def test_farthest_point_order_covers_extremes_first():
    features = [(0.5, 0.5), (0.0, 0.0), (1.0, 1.0), (0.55, 0.5), (1.0, 0.0)]
    order = farthest_point_order(features, [0])
    assert sorted(order) == [1, 2, 3, 4]
    assert set(order[:2]) == {1, 2} and order[-1] == 3


def test_farthest_point_order_is_deterministic_on_ties():
    assert farthest_point_order([(0, 0), (1, 0), (-1, 0)], [0]) == [1, 2]


def test_texture_score_ignores_silhouette():
    mask = np.zeros((60, 60), bool)
    mask[10:50, 10:50] = True
    flat = np.where(mask[..., None], 120, 0).astype(np.uint8).repeat(3, axis=2)
    striped = flat.copy()
    striped[10:50, 10:50][np.arange(40) % 4 < 2] = 200  # 2-px bands: a period-2 pattern cancels in Sobel
    assert texture_score(flat, mask) == 0.0
    assert texture_score(striped, mask) > 50
