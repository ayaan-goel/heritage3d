"""Watch run conditions that would distort timings: sleep and running on battery (Windows).

Wall time includes time spent asleep (lid closed), and on battery the CPU may be throttled. Sleep
always invalidates a level's timings; a short time on battery (the charger pin knocked loose) is
tolerated up to a grace period and recorded with the run.
"""

import ctypes
import sys
import threading
import time


class _PowerStatus(ctypes.Structure):
    _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte),
                ("BatteryLifePercent", ctypes.c_ubyte), ("SystemStatusFlag", ctypes.c_ubyte),
                ("BatteryLifeTime", ctypes.c_ulong), ("BatteryFullLifeTime", ctypes.c_ulong)]


def on_ac():
    """True when on mains power (or not Windows / unknown)."""
    if sys.platform != "win32":
        return True
    status = _PowerStatus()
    ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status))
    return status.ACLineStatus != 0  # 0 = battery, 1 = AC, 255 = unknown


def awake_seconds():
    """Seconds since boot excluding sleep/hibernate (QueryUnbiasedInterruptTime, 100 ns units)."""
    if sys.platform != "win32":
        return time.monotonic()
    t = ctypes.c_ulonglong()
    ctypes.windll.kernel32.QueryUnbiasedInterruptTime(ctypes.byref(t))
    return t.value / 1e7


class ConditionMonitor:
    """Context manager: measures seconds asleep and seconds on battery while it is open.

    `unplugged_s` is the current unbroken stretch on battery (0 while on mains power);
    `longest_unplugged_s` the longest such stretch so far.
    """

    def __init__(self, poll=5.0, power=on_ac, awake=awake_seconds, clock=time.time):
        self.poll, self._power, self._awake, self._clock = poll, power, awake, clock
        self.slept_s = self.battery_s = self.unplugged_s = self.longest_unplugged_s = 0.0
        self._stop = threading.Event()

    def _sample(self):
        if self._power():
            self.unplugged_s = 0.0
        else:
            self.battery_s += self.poll
            self.unplugged_s += self.poll
            self.longest_unplugged_s = max(self.longest_unplugged_s, self.unplugged_s)

    def _watch(self):
        while not self._stop.wait(self.poll):
            self._sample()

    def __enter__(self):
        self._wall0, self._awake0 = self._clock(), self._awake()
        self._sample()
        self._thread = threading.Thread(target=self._watch, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join()
        self.slept_s = max(0.0, (self._clock() - self._wall0) - (self._awake() - self._awake0))
        return False

    def clean(self, tolerance=5.0, max_unplugged_s=0.0):
        """True when the timed work ran awake and no stretch on battery reached max_unplugged_s
        (with the default 0: none at all)."""
        if self.slept_s > tolerance:
            return False
        return self.battery_s == 0 if max_unplugged_s <= 0 else self.longest_unplugged_s < max_unplugged_s
