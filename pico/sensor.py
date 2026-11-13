"""
sensor.py -- SENSOR DRIVER MODULE
OWNER: ______________________

YOUR CONTRIBUTION
    read(sensor_data)   [function]

        *   Takes an empty Data object (sensor_data) and stores raw sensor
            values inside it, exactly as the sensor reports them (ADC counts,
            echo time in microseconds, register values, etc...). Converting
            to real units will be handled by the calibration module.

            Example: sensor_data.counts = 23110.

      * If the read fails, sets sensor_data.ok = False and leaves the value unset.

      * Never let an exception escape! The rest of the system copes with a
        failed read; it cannot cope with a crash. I2C or Serial devices have
        the potential to cause errors if they become disconnected unexpectedly.

POWER MANAGEMENT
    Switching the sensor off between reads (see SENSOR_POWER_PIN in config.py)
    saves energy when your node runs on a battery: a sensor that stays powered
    can use more energy than the rest of the node combined. Some sensors (many
    gas sensors, for example) need warm-up time after power-on. If yours does,
    say so in your proposal.

YOUR JOB
    1. Replace _read_sensor1() ... _read_sensor5() with code for your team's
       sensor. If your sensor has a MicroPython library, you will create its
       object and call its methods, the same way you use machine.Pin and
       machine.ADC.
    2. Handle the ways your sensor can fail (no response, timeout, a reading
       outside what the sensor can physically report).
    3. Keep _read_fake() working and make it resemble YOUR sensor's raw output,
       because your teammates use it to test their modules without hardware.
       It runs while USE_FAKE_SENSOR is True in config.py.
"""

import config


def read(sensor_data):
    try:
        if config.USE_FAKE_SENSOR:
            _read_fake(sensor_data)
        else:
            _read_sensor1(sensor_data)
            _read_sensor2(sensor_data)
            _read_sensor3(sensor_data)
            _read_sensor4(sensor_data)
            _read_sensor5(sensor_data)
    except Exception:               # Ctrl+C still stops the program
        sensor_data.ok = False


def _read_sensor1(sensor_data):
    #sensor_data.data1 = ?
    return

def _read_sensor2(sensor_data):
    #sensor_data.data2 = ?
    return

def _read_sensor3(sensor_data):
    #sensor_data.data3 = ?
    return

def _read_sensor4(sensor_data):
    #sensor_data.data4 = ?
    return

def _read_sensor5(sensor_data):
    #sensor_data.data5 = ?
    return


def _read_fake(sensor_data):
    sensor_data.counts = 30000          # raw ADC counts, used by the example in calibration.py
    sensor_data.data1 = 32767
    sensor_data.data2 = 2147483647
    sensor_data.data3 = 21474.83647
    sensor_data.data4 = 32.767
    sensor_data.data5 = True
