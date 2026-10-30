import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.conditions import ConditionMonitor, awake_seconds, on_ac


class FakeClock:
    def __init__(self):
        self.wall = self.awake = 0.0


def test_sleep_detected_from_wall_vs_awake_time():
    c = FakeClock()
    with ConditionMonitor(poll=0.01, power=lambda: True, awake=lambda: c.awake, clock=lambda: c.wall) as m:
        c.wall, c.awake = 100.0, 40.0  # 60 s of the 100 s were spent asleep
    assert m.slept_s == 60.0 and not m.clean()


def test_battery_detected():
    with ConditionMonitor(poll=0.01, power=lambda: False) as m:
        pass
    assert m.battery_s > 0 and not m.clean()


def test_clean_run():
    with ConditionMonitor(poll=0.01, power=lambda: True) as m:
        pass
    assert m.clean()


def test_real_readings_work():
    assert isinstance(on_ac(), bool)
    a = awake_seconds()
    assert a > 0 and awake_seconds() >= a
