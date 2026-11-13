"""
simulator/fake_kit.py -- LAPTOP STAND-IN FOR pico/kit.py. PLEASE DO NOT EDIT.

The simulator runs your team's real modules from the pico folder on your
laptop. Those modules say "import kit", and the Pico's kit.py needs the Pico's
hardware (machine, notecard). So simulate.py loads THIS file and registers it
under the name "kit". Your modules get it without knowing the difference. This
file is called fake_kit.py so it can never be mistaken for the real one.

This Node has the same methods as the real one, but:
  * its "Notecard" writes each reading to a file instead of a radio
  * its clock is simulated, so sleep() jumps ahead instead of waiting
  * like the real Notecard, it rejects a reading that does not match the
    template, and drops 0 and false values from what it stores
  * it shows each warning and error once, not once per sample, so a problem
    in 192 simulated samples does not bury you in 192 copies of the same message
  * it ignores OUTBOUND_MINUTES and SLEEP_BETWEEN_SAMPLES in config.py: those
    only matter to real hardware

Nothing in this folder is copied onto the Pico.
"""

import json
import os
import traceback

import config
from kit_data import *          # Data, RollingAverage, RateOfChange, Trigger, pack, ...

DATA_NOTEFILE = "data.qo"
LOCATION_NOTEFILE = "location.qo"
MIN_DEPLOYED_SAMPLE_SECONDS = 300   # same reminder threshold as the real kit.py
START_TIME = 1791788400         # 2026-10-12 07:00 UTC: when simulated time begins


class Node:
    """A pretend sensor node for laptop testing."""

    def __init__(self, events_path=None, start_time=START_TIME, verbose=False):
        self.events_path = events_path or os.devnull
        self.clock = start_time
        self.verbose = verbose          # True prints every reading
        self.data_fields = {}
        self.location_fields = {}
        self.state = {}
        self._shown = set()             # messages already printed once

    # -- connecting and setting up ------------------------------------------------
    def connect(self, verbose=True):
        if verbose:
            print("Simulated Notecard connected.")
        return True

    def request(self, req, quiet=False):
        """The real node sends a request to the Notecard. Here there is no Notecard."""
        return {}

    def setup(self, data_fields, location_fields=None):
        self.data_fields = data_fields
        self.location_fields = location_fields or {}
        if config.SAMPLE_SECONDS < MIN_DEPLOYED_SAMPLE_SECONDS:
            print("note: SAMPLE_SECONDS is under", MIN_DEPLOYED_SAMPLE_SECONDS,
                  "seconds. Fine for testing, but set it back before you deploy.")
        print("Sampling every", self.sample_seconds(), "seconds (simulated)")

    # -- each sample ----------------------------------------------------------------
    def time(self):
        return self.clock

    def new_data(self):
        return Data(self.time())

    def add_data(self, data):
        return self._add(data, DATA_NOTEFILE, self.data_fields)

    def add_location(self, data):
        if not self.location_fields:
            return None
        return self._add(data, LOCATION_NOTEFILE, self.location_fields)

    def _add(self, data, notefile, fields):
        if data.ok:
            for name in unset_fields(data, fields):
                self._show_once("warning: no module set data." + name + "; check the spelling")
        if self.verbose:
            print(data)
        body = pack(data, fields)
        err = check_template(body, fields)
        if err:
            self._show_once("Notecard error on note.add -> " + err)
            return {"err": err}
        stored = {k: v for k, v in body.items() if v not in (0, False, "")}
        with open(self.events_path, "a") as f:
            f.write(json.dumps({"file": notefile, "when": self.clock, "body": stored}) + "\n")
        return {}

    def sync(self):
        return {}

    def check_connection(self, wait_seconds=None):
        print("Simulated LoRa connection OK.")
        return True

    # -- between samples ------------------------------------------------------------
    def sample_seconds(self):
        return max(1, config.SAMPLE_SECONDS)

    def outbound_minutes(self):
        return max(1, int(config.OUTBOUND_MINUTES))

    def sleep(self, seconds=None):
        # Save memory the way the Pico would, so anything that cannot be saved
        # as JSON fails here on the laptop instead of later in the field.
        save_memory(self.state)
        json.dumps(self.state)
        self.clock += seconds if seconds is not None else self.sample_seconds()

    def error(self, err):
        """Like the real node: count the error and keep going. The first one is
        printed in full so you can see what went wrong."""
        self.state["errors"] = self.state.get("errors", 0) + 1
        if self.state["errors"] == 1:
            print("cycle failed (shown once; later failures are only counted):")
            traceback.print_exception(type(err), err, err.__traceback__)

    def _show_once(self, message):
        if message not in self._shown:
            self._shown.add(message)
            print(message)


def check_template(body, fields):
    """The same type checks the real Notecard makes against its template."""
    for key, value in body.items():
        if key not in fields:
            return "error adding note: field not in template: " + key
        hint = fields[key]
        if hint is True:
            if not isinstance(value, bool):
                return "error adding note: boolean expected because of template (" + key + ")"
        elif isinstance(hint, float):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return "error adding note: float expected because of template (" + key + ")"
        elif isinstance(value, bool) or not isinstance(value, int):
            return "error adding note: integer expected because of template (" + key + ")"
    return None