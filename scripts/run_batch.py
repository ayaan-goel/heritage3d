"""Run the main experiment over the fixed artifact order, resuming where it stopped.

For each of the first --count artifacts in configs/artifact_order.json and each level
(cheapest first): skip if its evaluation already exists in experiments/results/runs/;
otherwise run sparse, dense, evaluation and preview with the frozen config. A failed level is
logged and the batch moves on. With --clean, regenerable intermediates (depth maps, feature
database, undistorted images) are deleted after a level is evaluated (~80 % of the space).
Progress is appended to <runs>/batch.log.

Usage (PowerShell):
    python scripts/run_batch.py --count 12 --clean
    python scripts/run_batch.py --count 12 --levels L2 L3 L4 L5 --clean
    python scripts/run_batch.py --count 12 --dry-run      # list what would run
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402
from heritage3d.pipeline import clean_workspace  # noqa: E402

SCRIPTS = REPO_ROOT / "scripts"
RESULTS = REPO_ROOT / "experiments" / "results" / "runs"


def pending(artifacts, levels):
    """(artifact, level) pairs without an evaluation file, in run order."""
    return [(a, lv) for a in artifacts for lv in levels if not (RESULTS / f"{a}_{lv}_eval.json").exists()]


def step(log, name, args):
    start = time.perf_counter()
    code = subprocess.run([sys.executable, str(SCRIPTS / name), *args]).returncode
    log(f"  {name} {' '.join(args)} -> exit {code}, {time.perf_counter() - start:.0f} s")
    return code == 0


def run_level(log, artifact, level, ws, clean):
    common = ["--artifact", artifact, "--level", level]
    ok = (step(log, "run_pipeline.py", [*common, "--stages", "sparse", "--overwrite"])
          and step(log, "run_pipeline.py", [*common, "--stages", "dense"])
          and step(log, "evaluate_run.py", common))
    if ok:
        step(log, "preview_cloud.py", [str(ws / "mvs" / "scene_dense.ply"), "--out",
                                       str(REPO_ROOT / "experiments" / "plots" / f"{artifact}_{level}_dense.jpg")])
        if clean:
            log(f"  cleaned {clean_workspace(ws) / 2**30:.2f} GB")
    return ok


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--count", type=int, required=True, help="use the first N artifacts of the fixed order")
    p.add_argument("--levels", nargs="+", help="default: all levels in the config, cheapest first")
    p.add_argument("--clean", action="store_true", help="delete regenerable intermediates after evaluation")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--order", type=Path, default=REPO_ROOT / "configs" / "artifact_order.json")
    args = p.parse_args(argv)

    config = load_config(args.config)
    levels = args.levels or list(reversed(list(config["levels"])))
    order = [a["name"] for a in json.loads(args.order.read_text(encoding="utf-8"))["artifacts"]]
    todo = pending(order[:args.count], levels)
    runs = Path(config["paths"]["runs"])

    def log(msg):
        line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
        print(line, flush=True)
        if not args.dry_run:
            with open(runs / "batch.log", "a", encoding="utf-8") as f:
                f.write(line + "\n")

    log(f"batch: {len(todo)} level runs pending for the first {args.count} artifacts, levels {' '.join(levels)}")
    if args.dry_run:
        for a, lv in todo:
            print(f"  {a} {lv}")
        return 0
    failed = []
    for artifact, level in todo:
        log(f"{artifact} {level}")
        if not run_level(log, artifact, level, runs / artifact / level, args.clean):
            failed.append(f"{artifact} {level}")
            log(f"  FAILED {artifact} {level}")
    log(f"batch done: {len(todo) - len(failed)} ok, {len(failed)} failed {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
