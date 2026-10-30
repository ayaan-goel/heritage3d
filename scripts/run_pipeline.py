"""Reconstruct one artifact at one image level and record cost per stage.

Workspace: <runs>/<artifact>/<level>/ (outside the repo). Per-stage logs go to
<workspace>/logs/, metrics to <workspace>/metrics.json; copies of both go to
experiments/results/runs/<artifact>_<level>.json and experiments/logs/<artifact>/<level>/ (committed).

Usage (PowerShell):
    python scripts/run_pipeline.py --artifact Ark_HM_272_HI --level L3 --stages sparse
    python scripts/run_pipeline.py --artifact Ark_HM_272_HI --level L3 --stages dense
    python scripts/run_pipeline.py ... --stages sparse --overwrite   # delete the workspace first
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.config import DEFAULT_CONFIG, REPO_ROOT, load_config  # noqa: E402
from heritage3d.environment import collect  # noqa: E402
from heritage3d.pipeline import (  # noqa: E402
    colmap_path,
    dense_commands,
    folder_bytes,
    parse_model_analyzer,
    run_stage,
    sparse_commands,
)
from heritage3d.subsets import build_levels, view_path  # noqa: E402


def analyze_models(colmap, ws):
    """model_analyzer on every sparse model COLMAP produced; returns {model_dir: stats}."""
    models = {}
    for model in sorted((ws / "sparse").glob("[0-9]*")):
        result = run_stage("model_analyzer", [colmap, "model_analyzer", "--path", model],
                           ws / "logs" / f"model_analyzer_{model.name}.log")
        models[model.name] = parse_model_analyzer(Path(result["log"]).read_text(encoding="utf-8", errors="replace"))
    return models


def run(stages, ws, metrics):
    for name, cmd, cwd in stages:
        result = run_stage(name, cmd, ws / "logs" / f"{name}.log", cwd=cwd)
        metrics["stages"][name] = result
        print(f"{name}: exit {result['returncode']}, {result['seconds']} s, peak {result['peak_memory_mb']} MB")
        if result["returncode"] != 0:
            print(f"stopped: {name} failed, see {result['log']}", file=sys.stderr)
            return False
    return True


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--artifact", required=True)
    p.add_argument("--level", required=True)
    p.add_argument("--stages", choices=["sparse", "dense"], required=True)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--overwrite", action="store_true", help="delete an existing workspace before the sparse stage")
    args = p.parse_args(argv)

    config = load_config(args.config)
    settings, ds = config["pipeline"], config["dataset"]
    rgb_root = Path(config["paths"]["chsd_rgb"])
    ws = Path(config["paths"]["runs"]) / args.artifact / args.level
    metrics_path = ws / "metrics.json"
    colmap = colmap_path()

    if args.stages == "sparse":
        if ws.exists():
            if not args.overwrite:
                print(f"{ws} exists; pass --overwrite to start again", file=sys.stderr)
                return 1
            shutil.rmtree(ws)
        ws.mkdir(parents=True)
        views = build_levels(config)[args.level]
        images = [view_path(v, args.artifact, ds["rgb_pattern"], ds["azimuth_step"]) for v in views]
        (ws / "images.txt").write_text("\n".join(images) + "\n", encoding="utf-8")
        (ws / "sparse").mkdir()
        metrics = {
            "artifact": args.artifact,
            "level": args.level,
            "started": datetime.now().isoformat(timespec="seconds"),
            "config": config,
            "environment": collect(),
            "input_images": len(images),
            "input_bytes": sum((rgb_root / x).stat().st_size for x in images),
            "stages": {},
        }
        cmds = sparse_commands(colmap, ws, rgb_root, ws / "images.txt", settings)
        ok = run([(n, c, ws) for n, c in cmds], ws, metrics)
        if ok:
            metrics["sparse_models"] = analyze_models(colmap, ws)
            for name, stats in metrics["sparse_models"].items():
                print(f"model {name}: {stats}")
    else:
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        if "sparse_models" not in metrics:
            print("no sparse run; run --stages sparse first", file=sys.stderr)
            return 1
        models = metrics["sparse_models"]
        if not models:
            print("SfM produced no model: nothing to densify", file=sys.stderr)
            metrics["dense_from_model"] = None
            metrics_path.write_text(json.dumps(metrics, indent=1, default=str), encoding="utf-8")
            return 0
        best = max(models, key=lambda k: models[k].get("registered_images", 0))
        metrics["dense_from_model"] = best
        (ws / "mvs").mkdir(exist_ok=True)
        cmds = dense_commands(colmap, ws, rgb_root, ws / "sparse" / best, settings)
        # OpenMVS writes its own *.log into the working folder: keep it inside the workspace.
        ok = run([(n, c, ws / "mvs") for n, c in cmds], ws, metrics)
        metrics["outputs_bytes"] = {
            "sparse": folder_bytes(ws / "sparse"),
            **{f.name: f.stat().st_size for f in (ws / "mvs").glob("scene_dense*") if f.is_file()},
        }

    metrics["finished"] = datetime.now().isoformat(timespec="seconds")
    metrics_path.write_text(json.dumps(metrics, indent=1, default=str), encoding="utf-8")
    copy = REPO_ROOT / "experiments" / "results" / "runs" / f"{args.artifact}_{args.level}.json"
    copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(metrics_path, copy)
    log_copy = REPO_ROOT / "experiments" / "logs" / args.artifact / args.level
    shutil.copytree(ws / "logs", log_copy, dirs_exist_ok=True)
    for log in (ws / "mvs").glob("*.log"):  # OpenMVS's own detailed logs
        shutil.copyfile(log, log_copy / log.name)
    print(f"metrics: {metrics_path}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
