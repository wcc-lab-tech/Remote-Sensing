"""Tests for telemetry.py. Owner: add tests for YOUR check() rules."""

import kit          # the simulator's stand-in kit
import telemetry


def good_reading():
    reading = kit.Reading(1_000_000)
    reading.level_mm = 123.4
    reading.rate_mm_hr = 5
    reading.rising = False
    return reading


def test_payload_matches_schema():
    payload = kit.pack(good_reading(), telemetry.FIELDS)
    assert set(payload) == set(telemetry.FIELDS)
    assert isinstance(payload["rate_mm_hr"], float)     # converted to the template's type


def test_bad_reading_sends_missing_numbers():
    reading = good_reading()
    reading.ok = False
    payload = kit.pack(reading, telemetry.FIELDS)
    assert payload["level_mm"] == kit.MISSING
    assert payload["ok"] is False


def test_every_field_is_set_on_a_good_reading():
    # Catches a misspelled name in FIELDS or in processing.py.
    assert kit.unset_fields(good_reading(), telemetry.FIELDS) == []


def test_check_marks_unbelievable_rate_bad():
    reading = good_reading()
    reading.rate_mm_hr = 1e6
    telemetry.check(reading)
    assert reading.ok is False
    reading = good_reading()
    telemetry.check(reading)
    assert reading.ok is True


def test_notecard_accepts_reading():
    node = kit.Node()
    node.setup(telemetry.FIELDS)
    assert "err" not in node.send(good_reading())
