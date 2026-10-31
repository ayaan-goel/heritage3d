"""Read and write single textured-mesh GLB files (glTF 2.0 binary) for the museum.

OpenMVS TextureMesh exports a GLB whose texture is a separate PNG next to it. The museum needs
one self-contained file, so the mesh is read back and rewritten with the texture embedded.
"""

import json
import struct

import numpy as np

_MAGIC, _JSON, _BIN = 0x46546C67, 0x4E4F534A, 0x004E4942
_COMPONENTS = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
_WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def read_glb(path):
    """(gltf dict, binary chunk bytes)."""
    data = open(path, "rb").read()
    magic, version, _ = struct.unpack_from("<III", data, 0)
    if magic != _MAGIC or version != 2:
        raise ValueError(f"{path} is not a glTF 2.0 binary")
    pos, gltf, binary = 12, None, b""
    while pos < len(data):
        length, kind = struct.unpack_from("<II", data, pos)
        chunk = data[pos + 8:pos + 8 + length]
        if kind == _JSON:
            gltf = json.loads(chunk)
        elif kind == _BIN:
            binary = chunk
        pos += 8 + length
    return gltf, binary


def accessor(gltf, binary, index):
    """Accessor `index` as a numpy array (rows = elements)."""
    acc = gltf["accessors"][index]
    view = gltf["bufferViews"][acc["bufferView"]]
    dtype, width = _COMPONENTS[acc["componentType"]], _WIDTH[acc["type"]]
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    arr = np.frombuffer(binary, dtype, acc["count"] * width, start)
    return arr.reshape(acc["count"], width) if width > 1 else arr.copy()


def read_mesh(path):
    """(positions N×3, texcoords N×2, triangles M×3, external texture uri or None) of the first primitive."""
    gltf, binary = read_glb(path)
    prim = gltf["meshes"][0]["primitives"][0]
    positions = accessor(gltf, binary, prim["attributes"]["POSITION"]).astype(np.float64)
    texcoords = accessor(gltf, binary, prim["attributes"]["TEXCOORD_0"]).astype(np.float32)
    triangles = accessor(gltf, binary, prim["indices"]).reshape(-1, 3)
    uri = gltf.get("images", [{}])[0].get("uri")
    return positions, texcoords, triangles, uri


def _pad(b, fill=b"\0"):
    return b + fill * (-len(b) % 4)


def write_mesh(path, positions, texcoords, triangles, image, mime="image/jpeg"):
    """Write one unlit, double-sided textured mesh with the image embedded. Returns the file size."""
    parts = [np.asarray(positions, np.float32).tobytes(), np.asarray(texcoords, np.float32).tobytes(),
             np.asarray(triangles, np.uint32).tobytes(), image]
    views, binary = [], b""
    for i, part in enumerate(parts):
        view = {"buffer": 0, "byteOffset": len(binary), "byteLength": len(part)}
        if i < 2:
            view["target"] = 34962  # ARRAY_BUFFER
        elif i == 2:
            view["target"] = 34963  # ELEMENT_ARRAY_BUFFER
        views.append(view)
        binary += _pad(part)
    pos = np.asarray(positions, np.float32)
    gltf = {
        "asset": {"version": "2.0", "generator": "heritage3d"},
        "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "TEXCOORD_0": 1}, "indices": 2,
                                    "material": 0, "mode": 4}]}],
        "materials": [{"doubleSided": True, "extensions": {"KHR_materials_unlit": {}},
                       "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicFactor": 0.0}}],
        "extensionsUsed": ["KHR_materials_unlit"],
        "textures": [{"sampler": 0, "source": 0}],
        # Linear, no mipmaps, clamped (as OpenMVS writes it): the texture atlas has black padding around
        # each patch, which mipmaps would blend into the colours and darken the model from a distance.
        "samplers": [{"magFilter": 9729, "minFilter": 9729, "wrapS": 33071, "wrapT": 33071}],
        "images": [{"bufferView": 3, "mimeType": mime}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(pos), "type": "VEC3",
             "min": pos.min(0).tolist(), "max": pos.max(0).tolist()},
            {"bufferView": 1, "componentType": 5126, "count": len(pos), "type": "VEC2"},
            {"bufferView": 2, "componentType": 5125, "count": int(np.size(triangles)), "type": "SCALAR"},
        ],
        "bufferViews": views,
        "buffers": [{"byteLength": len(binary)}],
    }
    js = _pad(json.dumps(gltf, separators=(",", ":")).encode(), b" ")
    total = 12 + 8 + len(js) + 8 + len(binary)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", _MAGIC, 2, total))
        f.write(struct.pack("<II", len(js), _JSON) + js)
        f.write(struct.pack("<II", len(binary), _BIN) + binary)
    return total


def z_up_to_y_up(points):
    """CHSD reference frame (turntable axis z) to glTF (y up): (x, y, z) -> (x, z, -y)."""
    p = np.asarray(points)
    return np.stack([p[:, 0], p[:, 2], -p[:, 1]], axis=1)


def sample_surface(positions, triangles, n, seed=0):
    """n points spread uniformly over the triangle surface (area-weighted)."""
    rng = np.random.default_rng(seed)
    a, b, c = (positions[triangles[:, i]] for i in range(3))
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    pick = rng.choice(len(triangles), n, p=area / area.sum())
    u, v = rng.random((2, n))
    flip = u + v > 1
    u[flip], v[flip] = 1 - u[flip], 1 - v[flip]
    return a[pick] + u[:, None] * (b[pick] - a[pick]) + v[:, None] * (c[pick] - a[pick])
