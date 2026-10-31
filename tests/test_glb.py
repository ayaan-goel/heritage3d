import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.glb import read_glb, read_mesh, sample_surface, write_mesh, z_up_to_y_up


def square():
    positions = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], float)
    texcoords = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], np.float32)
    return positions, texcoords, np.array([[0, 1, 2], [0, 2, 3]])


def test_write_then_read_round_trip(tmp_path):
    positions, texcoords, triangles = square()
    image = b"\xff\xd8fake-jpeg\xff\xd9"
    size = write_mesh(tmp_path / "m.glb", positions, texcoords, triangles, image)
    assert size == (tmp_path / "m.glb").stat().st_size and size % 4 == 0
    p, t, tri, uri = read_mesh(tmp_path / "m.glb")
    assert np.allclose(p, positions) and np.allclose(t, texcoords) and (tri == triangles).all() and uri is None
    gltf, binary = read_glb(tmp_path / "m.glb")
    view = gltf["bufferViews"][gltf["images"][0]["bufferView"]]
    assert binary[view["byteOffset"]:view["byteOffset"] + view["byteLength"]] == image
    assert gltf["accessors"][0]["max"] == [1, 1, 0]


def test_z_up_to_y_up_keeps_handedness():
    x, y, z = np.eye(3)
    a, b, c = z_up_to_y_up(np.array([x, y, z]))
    assert np.allclose(c, [0, 1, 0]) and np.allclose(np.cross(a, b), c)


def test_sample_surface_stays_on_the_mesh():
    positions, _, triangles = square()
    pts = sample_surface(positions, triangles, 2000)
    assert pts.shape == (2000, 3) and np.allclose(pts[:, 2], 0)
    assert pts[:, :2].min() >= 0 and pts[:, :2].max() <= 1
    assert abs(pts[:, 0].mean() - 0.5) < 0.05  # uniform over the square
