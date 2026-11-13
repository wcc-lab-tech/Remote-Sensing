"""
main.py -- runs automatically when the Pico powers up.

Each cycle gets a new Data object from the node and passes it through the team
modules, in order. Each module fills in its part of the data.

Your team should rarely need to change this file. If you do, agree on it together.
"""

import config
import kit
import sensor
import calibration
import processing
import telemetry
import location


def setup(node):
    while not node.connect():
        node.sleep(30)                 # try again until the Notecard answers

    # Set up the Notecard: Notehub project, upload interval, and note templates.
    node.setup(telemetry.DATA_FIELDS)


def run(node):
    sensor_data = node.new_data()

    sensor.read(sensor_data)               # raw numbers from the sensor
    calibration.calibrate(sensor_data)     # engineering units
    processing.process(sensor_data)        # cleaned values, derived metrics, flags
    telemetry.check(sensor_data)           # marks it bad if it is not believable

    node.add_data(sensor_data)             # queued on the Notecard for upload

    return sensor_data


def main():
    node = kit.Node()

    setup(node)

    while True:
        try:
            run(node)
        except Exception as err:           # Ctrl+C still stops the program
            node.error(err)
        node.sleep()                       # wait until the next sample


if __name__ == "__main__":
    main()
