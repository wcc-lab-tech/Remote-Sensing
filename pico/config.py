"""
config.py -- TEAM SETTINGS. Your team edits this file.
"""

# Copy the ProductUID from your team's Notehub project (Settings page).
PRODUCT_UID = "edu.whatcom.JVanHyning:test"

# ---------------------------------------------------------------------------
# How often things happen
# ---------------------------------------------------------------------------

# Seconds between samples. Any value from 1 up works, so you can sample quickly
# while testing the Notecard. For a deployed node use 300 (5 minutes) or more:
# LoRa airtime limits make faster sampling a bad idea, and every extra sample
# uses up more of your Datacake daily data allowance. The node prints a reminder
# at start-up whenever this is under 300.
SAMPLE_SECONDS = 30

# Minutes between uploads. Each sample is queued on the Notecard, and the
# Notecard sends everything that is waiting at this interval. Use a whole
# number, 1 or more. (Uploads can't be faster than once a minute, so with very
# fast sampling several readings travel together in each upload.)
#   * Smaller = fresher dashboard, but more radio use and more battery drain.
#   * Larger  = several samples travel together in one upload.
# Uploading more often than you sample gains you nothing.
OUTBOUND_MINUTES = 1

# Should the Pico sleep between samples?
#   False = stay awake and just wait. USB and the Thonny REPL keep working, so
#           you can read printed messages, see errors, and press Stop.
#           Use this while you are building and testing.
#   True  = low-power sleep (machine.lightsleep). The Pico uses much less
#           energy, which matters on battery or solar power. The cost: USB
#           shuts off during every sleep, so Thonny disconnects and you cannot
#           see output or stop the program. To work on the code again, unplug
#           the Pico, then hold BOOTSEL while plugging it back in and re-save
#           your files, or ask your instructor.
# Switch to True only when the code is finished and the node is deployed on
# battery or solar power. Wall-powered nodes have no battery to protect, so
# they can leave this False.
SLEEP_BETWEEN_SAMPLES = False

# ---------------------------------------------------------------------------
# What the node does
# ---------------------------------------------------------------------------

# True until your real sensor is wired up. The fake sensor lets you test the
# whole data path, including the dashboard, before your parts arrive.
USE_FAKE_SENSOR = True

# True if your team is sending GPS location. Fill in location.py and
# telemetry.LOCATION_FIELDS first.
USE_GPS = False

# ---------------------------------------------------------------------------
# Pico pins. Match these to your kit's wiring.
# ---------------------------------------------------------------------------

I2C_ID = 0              # I2C bus to the Notecard LoRa
I2C_SDA = 4             # I2C signal data  (GP4)
I2C_SCL = 5             # I2C signal clock (GP5)

SENSOR_ADC0_PIN = 26    # analog input (GP26 = ADC0)
SENSOR_ADC1_PIN = 27    # analog input (GP27 = ADC1)
SENSOR_ADC2_PIN = 28    # analog input (GP28 = ADC2)

SENSOR_POWER_PIN = 15   # drives the MOSFET that switches sensor power