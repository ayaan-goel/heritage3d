import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_batch", ROOT / "scripts" / "run_batch.py")
run_batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_batch)


class Cond:
    def __init__(self, unplugged_s):
        self.unplugged_s = unplugged_s


@pytest.fixture
def scripts(tmp_path, monkeypatch):
    (tmp_path / "quick.py").write_text("print('ok')\n")
    (tmp_path / "slow.py").write_text("import time\ntime.sleep(30)\n")
    monkeypatch.setattr(run_batch, "SCRIPTS", tmp_path)
    return tmp_path


def test_step_keeps_running_while_unplugged_within_grace(scripts):
    lines = []
    assert run_batch.run_step(lines.append, "quick.py", [], Cond(unplugged_s=600), grace_s=900, poll=0.1)
    assert "exit 0" in lines[-1]


def test_step_stopped_once_unplugged_for_the_grace_period(scripts):
    lines = []
    with pytest.raises(run_batch.Unplugged):
        run_batch.run_step(lines.append, "slow.py", [], Cond(unplugged_s=900), grace_s=900, poll=0.1)
    assert "charger out for 15 min" in lines[-1]


def test_conditions_recorded_in_metrics(tmp_path, monkeypatch):
    monkeypatch.setattr(run_batch, "RESULTS", tmp_path)
    (tmp_path / "A_L3.json").write_text('{"input_images": 92}')
    cond = type("C", (), {"slept_s": 0.4, "battery_s": 120.0, "longest_unplugged_s": 85.0})()
    run_batch.record_conditions("A", "L3", cond)
    m = json.loads((tmp_path / "A_L3.json").read_text())
    assert m["input_images"] == 92 and m["conditions"] == {"slept_s": 0, "battery_s": 120, "longest_unplugged_s": 85}
