"""
processing.py -- SIGNAL PROCESSING MODULE
OWNER: ______________________

YOUR CONTRIBUTION
    process(sensor_data)    [function]

      * Starts from the calibrated values stored in sensor_data and adds the
        values your team reports: cleaned-up sensor_data, derived metrics, and
        event flags.
        
      * Every value your team sends must also appear in telemetry.FIELDS, with
        exactly the same name.

REMEMBERING EARLIER sensor_data
    Smoothing, rates, and events all depend on earlier sensor_datas. The objects
    created below the settings remember what they need from one cycle to the
    next (and through a reboot), so your function never has to. Create them
    once, at the top of the file, the same way you would create a machine.Pin,
    then call their methods inside process(). See kit_data.py for what each offers.

THE EXAMPLE
    1. Range check: discard physically impossible sensor_datas.
    2. Smoothing: a moving average of the last WINDOW good sensor_datas.
    3. Rate of change, in mm per hour.
    4. Event detection with hysteresis: a "rising" event turns on when the level
       climbs faster than RISE_ON and turns off only when the rate drops below
       RISE_OFF. Two thresholds keep noise near one threshold from making the
       flag flicker on and off.

YOUR JOB
    Adapt this to your team's question. What does a meaningful event look like
    in your data? What number would help someone make a decision? Tune the
    settings against real or simulated data, and be ready to justify them.
"""

import kit

# Settings: tune these, and be ready to explain your choices.
WINDOW = 4                      # sensor_datas in the moving average
LOW_MM = 0.0                    # anything outside LOW_MM to HIGH_MM is a bad read
HIGH_MM = 2000.0
RISE_ON_MM_HR = 40.0            # event starts above this rate
RISE_OFF_MM_HR = 10.0           # event ends below this rate

# Objects that remember earlier sensor_datas.
smoother = kit.RollingAverage(WINDOW)
rate = kit.RateOfChange()
rising = kit.Trigger(on=RISE_ON_MM_HR, off=RISE_OFF_MM_HR)


def process(sensor_data):
    level = sensor_data.level_mm

    if not sensor_data.ok or level is None or level < LOW_MM or level > HIGH_MM:
        sensor_data.ok = False                  # its numbers are sent as "missing"
        sensor_data.rising = rising.active      # an event in progress stays on
        return

    sensor_data.level_mm = smoother.add(level)
    sensor_data.rate_mm_hr = rate.update(sensor_data.level_mm, sensor_data.time)
    sensor_data.rising = rising.update(sensor_data.rate_mm_hr)
