"""Fix the run order of the main artifact set.

Candidates: artifacts not cut off by the frame in the dataset inspection. For each, object size
and texture are measured on four equator views (azimuth 0/90/180/270). The order starts from the
pilot artifact (already run) and adds the candidate farthest in (size, texture) from those
already picked. Writes configs/artifact_order.json; scripts/run_batch.py runs in this order.

Usage (PowerShell):
    python scripts/select_artifacts.py
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402
from heritage3d.dataset import foreground_rgb, load  # noqa: E402
from heritage3d.selection import farthest_point_order, texture_score  # noqa: E402
from heritage3d.subsets import View, view_path  # noqa: E402

PILOT = "Ark_HM_272_HI"
AZIMUTHS = (0, 90, 180, 270)


def measure(rgb_root, artifact, ds):
    sizes, textures = [], []
    for az in AZIMUTHS:
        rgb = load(rgb_root / view_path(View(0, az), artifact, ds["rgb_pattern"], ds["azimuth_step"]))
        mask = foreground_rgb(rgb)
        sizes.append(mask.mean())
        textures.append(texture_score(rgb, mask))
    return float(sum(sizes) / len(sizes)), float(sum(textures) / len(textures))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--inspection", type=Path,
                   default=REPO_ROOT / "experiments" / "results" / "dataset_inspection.json")
    p.add_argument("--out", type=Path, default=REPO_ROOT / "configs" / "artifact_order.json")
    args = p.parse_args(argv)

    config = load_config(args.config)
    ds, rgb_root = config["dataset"], Path(config["paths"]["chsd_rgb"])
    inspection = json.loads(args.inspection.read_text(encoding="utf-8"))
    names = sorted(n for n, a in inspection["artifacts"].items() if a["cut_off_fraction"] == 0)
    measured = {n: measure(rgb_root, n, ds) for n in names}
    order = farthest_point_order([measured[n] for n in names], [names.index(PILOT)])
    ranked = [PILOT] + [names[i] for i in order]

    args.out.write_text(json.dumps({
        "created": date.today().isoformat(),
        "rule": "not cut off by the frame; farthest-point order in (size, texture) starting from the pilot",
        "artifacts": [{"rank": i, "name": n, "foreground_fraction": round(measured[n][0], 4),
                       "texture": round(measured[n][1], 2)} for i, n in enumerate(ranked)],
    }, indent=1) + "\n", encoding="utf-8")
    for i, n in enumerate(ranked):
        print(f"{i:2d} {n:22s} size {measured[n][0]:.3f}  texture {measured[n][1]:6.2f}")
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
