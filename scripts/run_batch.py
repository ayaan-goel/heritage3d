"""Run the main experiment over the fixed artifact order, resuming where it stopped.

For each of the first --count artifacts in configs/artifact_order.json and each level
(cheapest first): skip if its evaluation already exists in experiments/results/runs/;
otherwise run sparse, dense, evaluation and preview with the frozen config. A failed level is
logged and the batch moves on. Each level starts only on mains power and is stopped if the
charger is removed (then redone once it is back). A level during which the laptop slept (lid
closed) or ran on battery has distorted timings: its results are set aside (*.suspect) and it is
queued again (up to --attempts times). With --clean, regenerable intermediates (depth maps,
feature database, undistorted images) are deleted after a level is evaluated (~80 % of the space).
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

from heritage3d.conditions import ConditionMonitor, on_ac  # noqa: E402
from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402
from heritage3d.pipeline import clean_workspace  # noqa: E402

SCRIPTS = REPO_ROOT / "scripts"
RESULTS = REPO_ROOT / "experiments" / "results" / "runs"


def pending(artifacts, levels):
    """(artifact, level) pairs without an evaluation file, in run order."""
    return [(a, lv) for a in artifacts for lv in levels if not (RESULTS / f"{a}_{lv}_eval.json").exists()]


def wait_for_ac(log, poll=30):
    if not on_ac():
        log("  on battery: waiting for the charger before starting the next level")
        while not on_ac():
            time.sleep(poll)
        log("  charger connected: continuing")


def set_aside(artifact, level):
    """Rename the level's committed result files so the level counts as pending again."""
    for f in (RESULTS / f"{artifact}_{level}_eval.json", RESULTS / f"{artifact}_{level}.json"):
        if f.exists():
            f.replace(f.with_name(f.name + ".suspect"))


class Unplugged(Exception):
    """The charger was removed while a level was running."""


def step(log, name, args, poll=5):
    """Run one script; stop it (and its child tools) if the laptop switches to battery."""
    start = time.perf_counter()
    proc = subprocess.Popen([sys.executable, str(SCRIPTS / name), *args])
    while proc.poll() is None:
        try:
            proc.wait(poll)
        except subprocess.TimeoutExpired:
            if not on_ac():
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
                proc.wait()
                log(f"  {name} stopped after {time.perf_counter() - start:.0f} s: charger removed")
                raise Unplugged
    log(f"  {name} {' '.join(args)} -> exit {proc.returncode}, {time.perf_counter() - start:.0f} s")
    return proc.returncode == 0


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
    p.add_argument("--attempts", type=int, default=3, help="tries per level when conditions were not clean")
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
    if sys.platform == "win32":  # no idle sleep while the batch runs (ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    failed, tries = [], {}
    queue = list(todo)
    while queue:
        artifact, level = queue.pop(0)
        tries[artifact, level] = tries.get((artifact, level), 0) + 1
        wait_for_ac(log)
        log(f"{artifact} {level}" + (f" (attempt {tries[artifact, level]})" if tries[artifact, level] > 1 else ""))
        try:
            with ConditionMonitor() as cond:
                ok = run_level(log, artifact, level, runs / artifact / level, args.clean)
        except Unplugged:  # not the level's fault: redo it next, without using up an attempt
            set_aside(artifact, level)
            tries[artifact, level] -= 1
            queue.insert(0, (artifact, level))
            continue
        if not cond.clean():
            log(f"  conditions not clean (asleep {cond.slept_s:.0f} s, on battery {cond.battery_s:.0f} s): timings invalid")
            set_aside(artifact, level)
            if tries[artifact, level] < args.attempts:
                queue.append((artifact, level))
                continue
            failed.append(f"{artifact} {level} (conditions)")
        elif not ok:
            failed.append(f"{artifact} {level}")
            log(f"  FAILED {artifact} {level}")
    log(f"batch done: {len(todo) - len(failed)} ok, {len(failed)} failed {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
