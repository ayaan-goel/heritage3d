"""Write one image-list file per level for an artifact.

Each list holds image paths relative to the CHSD RGB folder, one per line, ready
for `colmap feature_extractor --image_path <chsd_rgb> --image_list_path <list>`.

Usage (PowerShell):
    python scripts/create_subsets.py --artifact <name> --out D:\\heritage3d-data\\runs\\<name>
    python scripts/create_subsets.py --artifact <name> --out ... --check   # verify files exist
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.config import DEFAULT_CONFIG, load_config  # noqa: E402
from heritage3d.subsets import build_levels, view_path  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--artifact", required=True)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--check", action="store_true", help="fail if any listed image is missing")
    args = p.parse_args(argv)

    config = load_config(args.config)
    pattern = config["dataset"]["rgb_pattern"]
    rgb_root = Path(config["paths"]["chsd_rgb"])
    args.out.mkdir(parents=True, exist_ok=True)

    summary = {}
    for name, views in build_levels(config).items():
        paths = [view_path(v, args.artifact, pattern) for v in views]
        if args.check:
            missing = [x for x in paths if not (rgb_root / x).is_file()]
            if missing:
                print(f"{name}: {len(missing)} of {len(paths)} images missing, e.g. {missing[0]}", file=sys.stderr)
                return 1
        (args.out / f"{name}_images.txt").write_text("\n".join(paths) + "\n", encoding="utf-8")
        summary[name] = len(paths)
        print(f"{name}: {len(paths)} images")

    (args.out / "subsets.json").write_text(
        json.dumps({"artifact": args.artifact, "config": str(args.config), "counts": summary}, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
