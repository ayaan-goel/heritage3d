import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.evaluate import align_to_reference, apply, distance_metrics, umeyama
from heritage3d.reference import FOCAL, HEIGHT, WIDTH, backproject, camera, depth_to_z, voxel_downsample


def test_cameras_sit_on_unit_sphere_and_look_at_centre():
    for frame, elev in [(1, 0), (91, 45), (200, -45), (1, 90), (37, -90)]:
        rotation, centre = camera(frame, elev)
        assert np.isclose(np.linalg.norm(centre), 1)
        assert np.allclose(rotation @ rotation.T, np.eye(3))
        assert np.allclose(rotation @ (np.zeros(3) - centre), [0, 0, 1])  # centre straight ahead


def test_pole_camera_is_limit_of_ring_camera():
    near_pole = camera(31, 89.999)[0]
    assert np.allclose(near_pole, camera(31, 90)[0], atol=1e-4)


def test_depth_encoding_range():
    assert np.allclose(depth_to_z([0, 65535]), [1.5, 0.5])


def test_backproject_lands_on_the_right_pixel():
    depth = np.zeros((HEIGHT, WIDTH), np.uint16)
    depth[100, 600] = 30000
    point = backproject(depth, 46, 45)[0]
    rotation, centre = camera(46, 45)
    cam = rotation @ (point - centre)
    assert np.isclose(cam[2], depth_to_z(30000))
    assert np.allclose([cam[0] / cam[2] * FOCAL + WIDTH / 2, cam[1] / cam[2] * FOCAL + HEIGHT / 2], [600.5, 100.5])


def test_voxel_downsample_merges_close_points():
    pts = np.array([[0.0001, 0, 0], [0.0002, 0, 0], [0.5, 0, 0]])
    assert len(voxel_downsample(pts, 0.01)) == 2


def _similarity(seed=0):
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1
    return 3.7, q, np.array([0.3, -2.0, 5.0])


def test_umeyama_recovers_similarity():
    src = np.random.default_rng(1).normal(size=(20, 3))
    s, r, t = _similarity()
    s2, r2, t2 = umeyama(src, s * src @ r.T + t)
    assert np.isclose(s2, s) and np.allclose(r2, r) and np.allclose(t2, t)


def test_alignment_maps_colmap_frame_to_reference():
    names = [f"a/RGB/{f:04d}_{e}_.png" for e in (-45, 0, 45) for f in range(1, 361, 30)]
    ideal = {n: camera(int(n[6:10]), int(n.split("_")[1]))[1] for n in names}
    s, r, t = _similarity(2)
    inv = (1 / s, r.T, -r.T @ t / s)  # COLMAP coordinates = inverse similarity of ideal
    colmap = {n: apply(inv, c[None])[0] for n, c in ideal.items()}
    transform, info = align_to_reference(colmap)
    assert info["cameras"] == len(names) and info["camera_error_rms"] < 1e-9
    assert np.allclose(apply(transform, colmap[names[0]][None])[0], ideal[names[0]])


def test_distance_metrics_identical_and_shifted():
    ref = np.random.default_rng(3).uniform(size=(500, 3))
    same = distance_metrics(ref, ref, [0.01])
    assert same["chamfer"] == 0 and same["fscore"]["0.01"]["f"] == 1
    shifted = distance_metrics(ref + [0, 0, 5], ref, [0.01])
    assert shifted["fscore"]["0.01"]["f"] == 0 and shifted["accuracy_median"] > 4
