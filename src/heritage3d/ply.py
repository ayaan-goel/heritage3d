"""Read the vertex table of a PLY file (ASCII or binary little-endian).

OpenMVS dense clouds store per-vertex lists (view_indices, view_weights) after the
fixed properties; those lists are skipped, only the fixed properties are returned.
"""

import numpy as np

_TYPES = {
    "char": "i1", "int8": "i1", "uchar": "u1", "uint8": "u1",
    "short": "<i2", "int16": "<i2", "ushort": "<u2", "uint16": "<u2",
    "int": "<i4", "int32": "<i4", "uint": "<u4", "uint32": "<u4",
    "float": "<f4", "float32": "<f4", "double": "<f8", "float64": "<f8",
}


def _header(f):
    lines = []
    while True:
        line = f.readline()
        if not line:
            raise ValueError("PLY header has no end_header")
        line = line.decode("ascii", "replace").strip()
        lines.append(line)
        if line == "end_header":
            return lines


def read_vertices(path):
    """Structured numpy array of the vertex element's fixed properties (x, y, z, red, ...)."""
    with open(path, "rb") as f:
        header = _header(f)
        if header[0] != "ply":
            raise ValueError(f"{path} is not a PLY file")
        fmt = header[1].split()[1]
        fields, lists, count, in_vertex = [], [], 0, False
        for line in header:
            parts = line.split()
            if parts[0] == "element":
                if in_vertex:
                    break  # vertex element is first in every file we read
                in_vertex = parts[1] == "vertex"
                count = int(parts[2]) if in_vertex else count
            elif parts[0] == "property" and in_vertex:
                if parts[1] == "list":
                    lists.append((np.dtype(_TYPES[parts[2]]), np.dtype(_TYPES[parts[3]])))
                else:
                    fields.append((parts[2], _TYPES[parts[1]]))
        dtype = np.dtype(fields)
        if fmt == "ascii":
            rows = [f.readline().split() for _ in range(count)]
            return np.array([tuple(r[: len(fields)]) for r in rows], dtype=dtype)
        if fmt != "binary_little_endian":
            raise ValueError(f"unsupported PLY format {fmt}")
        raw = f.read()
    if not lists:
        return np.frombuffer(raw, dtype=dtype, count=count).copy()
    # Variable-length records: find each record's start, then gather the fixed part.
    starts = np.empty(count, np.int64)
    pos = 0
    for i in range(count):
        starts[i] = pos
        pos += dtype.itemsize
        for count_type, item_type in lists:
            n = int(np.frombuffer(raw, count_type, 1, pos)[0])
            pos += count_type.itemsize + n * item_type.itemsize
    buf = np.frombuffer(raw, np.uint8)
    return buf[starts[:, None] + np.arange(dtype.itemsize)].copy().view(dtype).reshape(count)


def xyz(vertices):
    return np.stack([vertices["x"], vertices["y"], vertices["z"]], axis=1).astype(np.float64)
