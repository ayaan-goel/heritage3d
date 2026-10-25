"""Load the experiment configuration from configs/experiment.toml."""

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "experiment.toml"


def load_config(path=DEFAULT_CONFIG):
    with open(path, "rb") as f:
        return tomllib.load(f)
