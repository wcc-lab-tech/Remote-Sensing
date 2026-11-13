"""
kit_data.py -- SUPPLIED CODE. PLEASE DO NOT EDIT.

The objects your modules use, shared by the Pico and the laptop simulator:

  * Data: carries one sample through your four modules
  * RollingAverage, RateOfChange, Trigger: objects that remember earlier
    readings, for the processing module

You reach these through kit (kit.Data, kit.RollingAverage, and so on), so
you never need to import this file yourself. You use them the same way you use
machine.Pin: create an object, then call its methods. If you are curious how
an object remembers things between calls, read the classes below; each one is
short.
"""

MISSING = -9999.0               # stands in for "no valid reading"; templates cannot hold None


# ---------------------------------------------------------------------------
# Data: one sample on its way through the four modules
# ---------------------------------------------------------------------------
class Data:
    """One sample. main.py gets a new Data object from the node each cycle and
    passes it to each module in turn; each module fills in its part:

        data = node.new_data()          data.time, and data.ok = True
        sensor.read(data)               sets raw values (or data.ok = False)
        calibration.calibrate(data)     sets values in real units
        processing.process(data)        smooths, sets derived values and flags
        telemetry.check(data)           marks it bad if it is not believable
        node.add_data(data)             queues the values named in DATA_FIELDS

    Set a value with   data.level_mm = 123.4
    Read it with       data.level_mm
    A value nobody has set reads as None, so a module never crashes because an
    earlier module failed to fill something in.
    """

    def __init__(self, time):
        self.time = time        # UNIX seconds
        self.ok = True          # any module sets this to False when something goes wrong

    def __getattr__(self, name):
        # Python calls this only for a name that was never set.
        if name.startswith("__"):
            raise AttributeError(name)
        return None
    
    def values(self):
        """Everything set on this reading, as a dictionary."""
        return dict(self.__dict__)

    def __repr__(self):
        values = self.values()
        names = ["time", "ok"] + sorted(n for n in values if n not in ("time", "ok"))
        parts = []
        for name in names:
            value = values[name]
            if isinstance(value, float):
                value = round(value, 2)
            parts.append(name + "=" + str(value))
        return "Data(" + ", ".join(parts) + ")"


# ---------------------------------------------------------------------------
# Objects that remember: for the processing module
#
# Create these at the top of processing.py, outside any function, so the same
# object is used every cycle. Each one remembers what it needs between samples,
# and the node saves and restores them so they also survive a reboot.
# ---------------------------------------------------------------------------
_memory = []                    # every memory object, in the order created


class _Memory:
    """Shared plumbing for the memory objects below (not used directly)."""

    def __init__(self):
        _memory.append(self)
        self.reset()

    def reset(self):
        pass

    def _save(self):
        return None

    def _load(self, data):
        pass


class RollingAverage(_Memory):
    """The average of the last `size` values added.

        smoother = kit.RollingAverage(4)
        smooth = smoother.add(level)     # adds level, returns the new average
    """

    def __init__(self, size):
        self.size = size
        _Memory.__init__(self)

    def reset(self):
        self.recent = []

    def add(self, value):
        self.recent.append(value)
        if len(self.recent) > self.size:
            self.recent.pop(0)
        return self.average()

    def average(self):
        if not self.recent:
            return None
        return sum(self.recent) / len(self.recent)

    def _save(self):
        return self.recent

    def _load(self, data):
        self.recent = list(data)[-self.size:]


class RateOfChange(_Memory):
    """How fast a value is changing, in units per hour.

        rate = kit.RateOfChange()
        per_hour = rate.update(level, data.time)

    Returns None for the first value, because one value has no rate yet.
    """

    def reset(self):
        self.last_value = None
        self.last_time = None

    def update(self, value, time):
        rate = None
        if self.last_value is not None and time > self.last_time:
            hours = (time - self.last_time) / 3600
            rate = (value - self.last_value) / hours
        self.last_value = value
        self.last_time = time
        return rate

    def _save(self):
        return [self.last_value, self.last_time]

    def _load(self, data):
        self.last_value, self.last_time = data


class Trigger(_Memory):
    """An on/off event flag with two thresholds (hysteresis).

        rising = kit.Trigger(on=40.0, off=10.0)
        is_rising = rising.update(rate)

    Turns on when the value goes above `on`, and turns off only when it drops
    below `off`. The gap between the thresholds keeps a noisy value near one
    threshold from flipping the flag on and off. A value of None leaves the
    flag as it was. For an event that starts when a value FALLS (a temperature
    dropping below freezing), pass the value with its sign flipped: -temp_c.
    """

    def __init__(self, on, off):
        self.on = on
        self.off = off
        _Memory.__init__(self)

    def reset(self):
        self.active = False

    def update(self, value):
        if value is not None:
            if not self.active and value > self.on:
                self.active = True
            elif self.active and value < self.off:
                self.active = False
        return self.active

    def _save(self):
        return self.active

    def _load(self, data):
        self.active = bool(data)


def reset_memory():
    """Make every memory object forget, as if the Pico had just been flashed.
    The simulator and the tests use this to start fresh."""
    for m in _memory:
        m.reset()


def save_memory(state):
    state["memory"] = [[type(m).__name__, m._save()] for m in _memory]


def restore_memory(state):
    """After a reboot, put back what the memory objects remembered. If the code
    has changed since then (different objects), start fresh instead."""
    saved = state.get("memory")
    if not saved or len(saved) != len(_memory):
        return
    if [name for name, _ in saved] != [type(m).__name__ for m in _memory]:
        return
    for m, (_, data) in zip(_memory, saved):
        try:
            m._load(data)
        except Exception:
            m.reset()


# ---------------------------------------------------------------------------
# Packing a Data object into the radio message (used by Node.add_data)
# ---------------------------------------------------------------------------
def pack(reading, fields):
    """Turn a Data object into the radio message described by fields: exactly those
    names, each with the type its template hint asks for. A number that is None,
    or any number on a reading marked bad (ok is False), becomes MISSING, because
    a template cannot hold None and a bad number should never reach a chart."""
    payload = {}
    for name, hint in fields.items():
        value = getattr(reading, name)
        if not reading.ok and hint is not True:
            value = None
        if hint is True:
            payload[name] = bool(value)
        elif isinstance(hint, float):
            payload[name] = MISSING if value is None else float(value)
        else:
            payload[name] = int(MISSING) if value is None else int(round(value))
    return payload


def unset_fields(reading, fields):
    """Names in fields that no module ever set on this reading. On a good reading
    this usually means a misspelled name somewhere."""
    have = reading.values()
    return [name for name in fields if name not in have]
