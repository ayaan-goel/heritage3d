import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.ply import read_vertices, xyz


def test_binary_with_lists_like_openmvs(tmp_path):
    header = (
        "ply\nformat binary_little_endian 1.0\nelement vertex 2\n"
        "property float32 x\nproperty float32 y\nproperty float32 z\n"
        "property uint8 red\nproperty uint8 green\nproperty uint8 blue\n"
        "property list uint8 uint32 view_indices\nproperty list uint8 float32 view_weights\nend_header\n"
    )
    body = struct.pack("<fffBBB", 1, 2, 3, 10, 20, 30) + struct.pack("<BII", 2, 7, 9) + struct.pack("<Bff", 2, .5, .5)
    body += struct.pack("<fffBBB", 4, 5, 6, 40, 50, 60) + struct.pack("<BI", 1, 3) + struct.pack("<Bf", 1, 1.0)
    path = tmp_path / "cloud.ply"
    path.write_bytes(header.encode() + body)
    v = read_vertices(path)
    assert np.allclose(xyz(v), [[1, 2, 3], [4, 5, 6]])
    assert list(v["red"]) == [10, 40] and list(v["blue"]) == [30, 60]


def test_binary_fixed_with_faces_after(tmp_path):
    header = ("ply\nformat binary_little_endian 1.0\nelement vertex 3\nproperty float x\nproperty float y\n"
              "property float z\nelement face 1\nproperty list uchar int vertex_indices\nend_header\n")
    body = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0) + struct.pack("<B3i", 3, 0, 1, 2)
    path = tmp_path / "mesh.ply"
    path.write_bytes(header.encode() + body)
    assert np.allclose(xyz(read_vertices(path))[1], [1, 0, 0])


def test_ascii(tmp_path):
    path = tmp_path / "a.ply"
    path.write_text("ply\nformat ascii 1.0\nelement vertex 2\nproperty float x\nproperty float y\n"
                    "property float z\nend_header\n0 0 0\n1.5 2 3\n")
    assert np.allclose(xyz(read_vertices(path)), [[0, 0, 0], [1.5, 2, 3]])
