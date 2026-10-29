"""Controlled image subsets defined by a uniform azimuth step on every camera ring.

A view is identified by (elevation, azimuth) in degrees. Subsets always start at
azimuth 0 so they are reproducible, and a step that divides a larger step yields
nested subsets (e.g. 12 deg is contained in 6 deg).
"""

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class View:
    elevation: int
    azimuth: int


def azimuths(step, source_step=1):
    """Azimuths 0..359 sampled every `step` degrees from views rendered every `source_step`."""
    if step <= 0 or source_step <= 0:
        raise ValueError("steps must be positive")
    if step % source_step:
        raise ValueError(f"step {step} is not a multiple of the source step {source_step}")
    return list(range(0, 360, step))


def select_views(step, rings, pole_rings=(), source_step=1):
    """All views for one level. Pole rings contribute only their azimuth-0 view."""
    unknown = set(pole_rings) - set(rings)
    if unknown:
        raise ValueError(f"pole rings {sorted(unknown)} are not in rings {list(rings)}")
    views = []
    for elevation in rings:
        if elevation in pole_rings:
            views.append(View(elevation, 0))
        else:
            views.extend(View(elevation, a) for a in azimuths(step, source_step))
    return views


def build_levels(config):
    """Map level name -> list of views, from a loaded experiment config."""
    ds = config["dataset"]
    return {
        name: select_views(step, ds["rings"], ds.get("pole_rings", []), ds["azimuth_step"])
        for name, step in config["levels"].items()
    }


def view_path(view, artifact, pattern, source_step=1):
    """Fill a file pattern. CHSD numbers files from 1, so azimuth 0 is frame 1."""
    frame = view.azimuth // source_step + 1
    return pattern.format(artifact=artifact, elevation=view.elevation, azimuth=view.azimuth, frame=frame)
