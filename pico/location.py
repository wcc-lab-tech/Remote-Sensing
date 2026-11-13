# Used only when USE_GPS = True in config.py.
# Edit read() to fill in the values listed in telemetry.LOCATION_FIELDS.
# Used only when USE_GPS = True in config.py. Each name must match a value that
# location.read() sets. Every GPS value you transmit has to be listed here.
LOCATION_FIELDS = {
    "lat": 14.1,
    "long": 14.1,
}
def read(location_data):
    location_data.lat = 0
    location_data.long = 0
