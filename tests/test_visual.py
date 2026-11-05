import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.reference import HEIGHT, WIDTH
from heritage3d.visual import compare, holdout_views, render, sample_bilinear

# frame 1, elevation 0: the camera is at x = 1 looking towards -x, with +y to its right and +z up
QUAD = np.array([[0, -0.1, -0.1], [0, 0.1, -0.1], [0, 0.1, 0.1], [0, -0.1, 0.1]], float)
UV = np.array([[0, 1], [1, 1], [1, 0], [0, 0]], np.float32)  # v = 0 is the image's top row
TRIS = np.array([[0, 1, 2], [0, 2, 3]])
# the texture: left half red, right half blue
TEXTURE = np.zeros((4, 4, 3), np.float64)
TEXTURE[:, :2, 0] = 200
TEXTURE[:, 2:, 2] = 200


def test_holdout_views_are_in_no_level_and_refused_if_they_are():
    views = holdout_views((3, 6, 12, 24, 45))
    assert len(views) == 12 and (8, 0) in views
    with pytest.raises(ValueError):
        holdout_views((7,))


def test_quad_lands_at_the_right_pixels_with_the_right_way_up():
    rgb, coverage = render(QUAD, UV, TRIS, TEXTURE, 1, 0)
    assert coverage.shape == (HEIGHT, WIDTH)
    ys, xs = np.nonzero(coverage > 0.5)
    # 0.2 R wide at distance 1 with f = 1000 px is 200 px, centred on the principal point
    assert (xs.min(), xs.max(), ys.min(), ys.max()) == (300, 499, 200, 399)
    assert rgb[300, 320, 0] == pytest.approx(200) and rgb[300, 480, 2] == pytest.approx(200)
    assert coverage[100, 100] == 0


def test_nearer_surface_hides_the_farther_whatever_the_order():
    near = QUAD + [0.2, 0, 0]
    positions = np.vstack([near, QUAD])
    tris = np.vstack([TRIS, TRIS + 4])
    uv = np.vstack([np.zeros((4, 2)) + 0.1, UV]).astype(np.float32)  # the near quad samples only red
    for order in (tris, tris[::-1]):
        rgb, _ = render(positions, uv, order, TEXTURE, 1, 0)
        assert rgb[300, 400, 2] == 0 and rgb[300, 400, 0] == pytest.approx(200)


def test_textures_stay_correct_past_a_chunk_boundary(monkeypatch):
    monkeypatch.setattr("heritage3d.visual._CHUNK", 1)
    rgb, _ = render(QUAD, UV, TRIS, TEXTURE, 1, 0)
    assert rgb[300, 320, 0] == pytest.approx(200) and rgb[300, 480, 2] == pytest.approx(200)


def test_perspective_is_corrected_on_a_slanted_surface():
    slanted = np.array([[0.3, -0.1, -0.1], [-0.3, 0.1, -0.1], [-0.3, 0.1, 0.1], [0.3, -0.1, 0.1]], float)
    rgb, coverage = render(slanted, UV, TRIS, TEXTURE, 1, 0)
    centre_x = np.mean([x for x in range(WIDTH) if coverage[300, x] > 0.5])
    # the middle of the texture (red meets blue) is at y = 0, which projects to the image centre, off the quad's pixel middle
    assert rgb[300, 398, 0] > rgb[300, 398, 2] and rgb[300, 402, 2] > rgb[300, 402, 0]
    assert centre_x < 395


def test_empty_model_renders_nothing():
    rgb, coverage = render(np.zeros((0, 3)), np.zeros((0, 2)), np.zeros((0, 3), int), TEXTURE, 1, 0)
    assert rgb.sum() == 0 and coverage.sum() == 0


def test_sample_bilinear_blends_between_texels():
    assert sample_bilinear(np.array([[[0.0], [100.0]]]), np.array([[0.5, 0.5]]))[0, 0] == pytest.approx(50)


def photo():
    rng = np.random.default_rng(0)
    image = np.zeros((HEIGHT, WIDTH, 3))
    mask = np.zeros((HEIGHT, WIDTH), bool)
    mask[200:400, 300:500] = True
    image[mask] = rng.uniform(40, 220, (mask.sum(), 3))
    return image, mask


def test_identical_images_score_perfectly():
    image, mask = photo()
    m = compare(image, mask.astype(float), image, mask)
    assert m["psnr"] == 100 and m["ssim"] == pytest.approx(1) and m["iou"] == 1 and m["psnr_overlap"] == 100


def test_missing_half_counts_against_the_model_but_not_overlap_colour():
    image, mask = photo()
    half, coverage = image.copy(), mask.astype(float)
    half[:, 400:] = 0
    coverage[:, 400:] = 0
    m = compare(half, coverage, image, mask)
    assert m["iou"] == pytest.approx(0.5) and m["psnr"] < 15 and m["psnr_overlap"] == 100 and m["ssim"] < 0.6


def test_nothing_rendered_scores_low_and_has_no_overlap():
    image, mask = photo()
    m = compare(np.zeros_like(image), np.zeros(mask.shape), image, mask)
    assert m["iou"] == 0 and m["psnr_overlap"] is None and m["ssim"] < 0.1
