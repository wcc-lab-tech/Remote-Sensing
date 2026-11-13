"""Tests for processing.py. Owner: add tests for YOUR processing."""

import json

import kit
import processing


def run(levels, dt=900):
    """Feed a list of levels through process(), starting with fresh memory.
    Returns the list of Readings. None stands for a failed sensor read."""
    kit.reset_memory()
    readings = []
    for i, level in enumerate(levels):
        reading = kit.Reading(1_000_000 + i * dt)
        if level is None:
            reading.ok = False
        else:
            reading.level_mm = level
        processing.process(reading)
        readings.append(reading)
    return readings


def test_smoothing_reduces_noise():
    noisy = [100 + (5 if i % 2 else -5) for i in range(20)]
    readings = run(noisy)
    assert all(abs(r.level_mm - 100) < 5 for r in readings[processing.WINDOW:])


def test_rising_event_turns_on_and_off():
    levels = [100] * 10 + [100 + 50 * i for i in range(1, 9)] + [500] * 20
    flags = [r.rising for r in run(levels)]
    assert any(flags), "a fast rise should start an event"
    assert not flags[-1], "the event should end once the level stops rising"


def test_bad_reading_does_not_crash():
    readings = run([100, None, 100, 99999])
    assert readings[1].ok is False
    assert readings[3].ok is False      # out of range


def test_memory_survives_a_reboot():
    # The Pico saves the memory objects as JSON in state.json. After a reboot,
    # restore_memory() should put them back exactly.
    run([100, 110, 120, 130])
    state = {}
    kit.save_memory(state)
    saved = json.loads(json.dumps(state))     # what state.json would hold
    before = processing.smoother.average()
    kit.reset_memory()
    kit.restore_memory(saved)
    assert processing.smoother.average() == before
    assert processing.rate.last_value is not None
