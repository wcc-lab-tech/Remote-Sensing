"""Tests for calibration.py. Owner: add tests for YOUR conversion.
Run all tests with run_tests.py (press F5 in Thonny)."""

import calibration
import kit


def test_known_point_converts_correctly():
    # 1.0 V should give SLOPE * 1.0 + INTERCEPT.
    reading = kit.Reading(0)
    reading.counts = 1.0 / calibration.V_REF * calibration.ADC_FULL_SCALE
    calibration.calibrate(reading)
    expected = calibration.SLOPE + calibration.INTERCEPT
    assert reading.ok
    assert abs(reading.level_mm - expected) < 0.01


def test_failed_read_passes_through():
    reading = kit.Reading(0)
    reading.ok = False                  # the sensor driver could not read
    calibration.calibrate(reading)
    assert reading.ok is False
    assert reading.level_mm is None

# TODO: a test that a reading at each end of your expected range gives a
# sensible value, using a reference point you measured yourself.
