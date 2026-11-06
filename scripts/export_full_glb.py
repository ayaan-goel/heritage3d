"""Export each exhibit's full, unoptimized L3 model as one GLB, for comparing it with the museum model (RQ3).

The same steps as export_glb.py's "full" model (TextureMesh without decimation, texture up to 8192 px as PNG, turned
upright), but written outside the repo, since full models are data (CLAUDE.md), and without touching the museum.

Usage (PowerShell):
    python scripts/export_full_glb.py                  # every exhibit in museum/artifacts.json
    python scripts/export_full_glb.py --artifacts Ark_HM_272_HI
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from export_glb import MUSEUM, ensure_images, pack, texture_mesh  # noqa: E402
from heritage3d.config import DEFAULT_CONFIG, load_config  # noqa: E402
from heritage3d.evaluate import align_to_reference, read_colmap_centres  # noqa: E402

OUT = Path(r"D:\heritage3d-data\full_glb")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--artifacts", nargs="+")
    p.add_argument("--out", type=Path, default=OUT)
    args = p.parse_args(argv)
    config = load_config(DEFAULT_CONFIG)
    level = config["museum"]["level"]
    exhibits = [e["id"] for e in json.loads((MUSEUM / "artifacts.json").read_text(encoding="utf-8"))["artifacts"]]
    args.out.mkdir(parents=True, exist_ok=True)
    for i, artifact in enumerate(args.artifacts or exhibits, 1):
        out = args.out / f"{artifact}.glb"
        if out.exists():
            continue
        ws = Path(config["paths"]["runs"]) / artifact / level
        metrics = json.loads((ws / "metrics.json").read_text(encoding="utf-8"))
        transform, _ = align_to_reference(read_colmap_centres(ws / "sparse_txt" / "images.txt"))
        ensure_images(ws, Path(config["paths"]["chsd_rgb"]), str(metrics["dense_from_model"]), config["pipeline"])
        with tempfile.TemporaryDirectory() as tmp:
            seconds = texture_mesh(ws, Path(tmp) / "full.glb", 1.0, 8192)
            _, triangles, size = pack(Path(tmp) / "full.glb", transform, out)
        print(f"[{i}] {artifact}: {len(triangles)} faces, {size / 2**20:.1f} MB, texture {seconds:.0f} s", flush=True)
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
