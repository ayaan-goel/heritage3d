"""Checks on the extracted CHSD files: naming, completeness, image format, depth values.

CHSD layout (verified 2026-10-29): <root>/<artifact>/RGB/<frame>_<elevation>_.png for
colour and <root>/<artifact>/Z/<frame>_<elevation>_.png for depth, with frame 0001-0360
(one per 1 deg of turntable rotation) and elevation in {-90, -45, 0, 45, 90}.
"""

import re

import numpy as np
from PIL import Image

NAME_RE = re.compile(r"^(\d{4})_(-?\d+)_\.png$")


def parse_name(name):
    """'0091_-45_.png' -> (91, -45); None if the name does not follow the CHSD scheme."""
    m = NAME_RE.match(name)
    return (int(m.group(1)), int(m.group(2))) if m else None


def scan_folder(folder, rings, frames):
    """Compare the files in one RGB or Z folder with the expected frame x ring grid."""
    expected = {(f, e) for f in frames for e in rings}
    found, unexpected = set(), []
    for p in folder.iterdir():
        key = parse_name(p.name)
        if key in expected:
            found.add(key)
        else:
            unexpected.append(p.name)
    return {
        "files": len(found) + len(unexpected),
        "missing": sorted(expected - found),
        "unexpected": sorted(unexpected),
    }


def image_header(path):
    with Image.open(path) as im:
        return {"mode": im.mode, "size": list(im.size)}


def load(path):
    with Image.open(path) as im:
        return np.asarray(im)


def foreground_rgb(rgb, threshold=8):
    """Object pixels in a CHSD colour render (background is black, values <= ~1)."""
    return rgb.max(axis=2) > threshold


def touches_border(mask):
    """True if the object is cut off by the image frame."""
    return bool(mask[0].any() or mask[-1].any() or mask[:, 0].any() or mask[:, -1].any())


def depth_stats(depth):
    """Value range and quantization of one depth map; 0 is background."""
    fg = depth[depth > 0]
    out = {"dtype": str(depth.dtype), "background_fraction": round(float(np.mean(depth == 0)), 4)}
    if fg.size == 0:
        return out
    levels = np.unique(fg)
    gaps = np.diff(levels.astype(np.int64))
    out.update(
        min=int(levels[0]),
        max=int(levels[-1]),
        distinct_values=int(levels.size),
        # Smallest and typical spacing between distinct values: the effective resolution.
        min_gap=int(gaps.min()) if gaps.size else None,
        median_gap=float(np.median(gaps)) if gaps.size else None,
    )
    return out


def iou(a, b):
    union = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / union) if union else 1.0


def spun(mask, degrees):
    """Mask rotated in the image plane about the image centre (counter-clockwise)."""
    im = Image.fromarray(mask.astype(np.uint8) * 255).rotate(degrees, resample=Image.BILINEAR)
    return np.asarray(im) > 127


def in_plane_rotation_iou(reference, other, degrees):
    """How well `other` is `reference` spun by +/-degrees. Near 1 => no new viewpoint."""
    return max(iou(spun(reference, s * degrees), other) for s in (1, -1))
