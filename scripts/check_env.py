"""Check that COLMAP and OpenMVS are reachable and print/save the environment report.

Usage (PowerShell):
    python scripts/check_env.py
    python scripts/check_env.py --out D:\\heritage3d-data\\runs\\environment.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.environment import collect, problems  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, help="write the report as JSON")
    args = p.parse_args(argv)

    report = collect()
    text = json.dumps(report, indent=2)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")

    issues = problems(report)
    for issue in issues:
        print("PROBLEM:", issue, file=sys.stderr)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
