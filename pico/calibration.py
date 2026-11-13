"""
calibration.py -- CALIBRATION MODULE
OWNER: ______________________

YOUR CONTRIBUTION
    calibrate(reading) [function]

        *   Takes the raw values stored in sensor_data and converts them into
            engineering units, stored on the same reading. Put the units in the name
            (sensor_data.level_mm, sensor_data.temp_c, sensor_data.co2_ppm) so nobody has to guess.

        *   If the reading already failed (reading.ok is False), leaves it alone.

WHERE THE NUMBERS COME FROM
    1. Take reference measurements: set up known conditions (a ruler in a bucket,
       a trusted thermometer) and record the raw reading at each one. Aim for at
       least five points spread across the range you expect in the field.
    2. Save them as a CSV like laptop/sample_data/calibration_points.csv.
    3. Run laptop/fit_calibration.py on your points and paste the coefficients
       it prints into SLOPE and INTERCEPT below.

YOUR JOB
    Replace the example with the conversion your sensor needs. A straight line is
    a starting point, not a requirement: if your residuals show a curve, fit one.
    Be ready to explain how you know your calibration is good.
"""

# PICO ADC VALUES. Replace / add additional values as needed by your sensor.
ADC_FULL_SCALE = 65535
V_REF = 3.3

# EXAMPLE VALUES. Replace with the output of laptop/fit_calibration.py.
SLOPE = 250.0          # mm per volt
INTERCEPT = -50.0      # mm


def __counts_to_volts(counts):
    return counts * V_REF / ADC_FULL_SCALE


def calibrate(reading):
    if not reading.ok:
        return
    volts = __counts_to_volts(reading.counts)
    reading.level_mm = SLOPE * volts + INTERCEPT
