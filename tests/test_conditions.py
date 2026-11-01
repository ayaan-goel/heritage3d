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


class Power:
    """Scripted mains/battery readings: True = on AC; the last value repeats."""

    def __init__(self, *readings):
        self.readings = list(readings)

    def __call__(self):
        return self.readings.pop(0) if len(self.readings) > 1 else self.readings[0]


def test_short_unplug_within_grace_is_clean_and_recorded():
    m = ConditionMonitor(poll=1.0, power=Power(True, False, False, True, True))
    for _ in range(5):
        m._sample()
    assert m.battery_s == 2.0 and m.longest_unplugged_s == 2.0 and m.unplugged_s == 0.0
    assert not m.clean()  # strict default: any battery time invalidates
    assert m.clean(max_unplugged_s=900)


def test_unplug_stretches_are_not_added_together():
    m = ConditionMonitor(poll=1.0, power=Power(False, False, True, False, False, False, True))
    for _ in range(7):
        m._sample()
    assert m.battery_s == 5.0 and m.longest_unplugged_s == 3.0
    assert m.clean(max_unplugged_s=4) and not m.clean(max_unplugged_s=3)
