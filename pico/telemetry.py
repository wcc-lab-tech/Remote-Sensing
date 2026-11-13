"""
telemetry.py -- TELEMETRY MODULE
OWNER: ______________________

YOUR CONTRIBUTION
    DATA_FIELDS       [variable] 

        *   defines the sensor data framework, shared by the Notecard and the
            dashboard
    
    check(reading)    [function] 
        
        *   marks the reading bad (reading.ok = False) if anything 
            about it is not believable at your site

WHY A FRAMEWORK

    The Notecard LoRa sends readings using a template: every field has a fixed
    name and type, packed into a very small radio message. 
    
    node.add_data(sensor_data) takes the values saved in sensor_data, converts them 
    to the types specified by DATA_FIELDS, and then passes the data to the Blues Notecard
    to be transmitted. 

    Every value your team sends must also appear in DATA_FIELDS, with
    exactly the same name.
    
    If sensor_data contains values that are not also defined in DATA_FIELDS,
    those values will be ignored and not transmitted.
    
    If DATA_FIELDS contains values that are not also defined in sensor_data, 
    it sends the values as kit.MISSING (-9999).

TEMPLATE TYPE HINTS (from the Blues documentation)
    14.1  4-byte float              12.1  2-byte float (about 3 significant digits)
    14    4-byte signed integer     12    2-byte signed integer
    True  boolean

YOUR JOB
    * Keep DATA_FIELDS in agreement with processing.py and with your dashboard's field
      mapping (datacake/decoder.js). You own that agreement: if a name changes
      here, it changes there.
    * Write check() rules for your data: values that are physically possible but
      not believable at your site, or combinations that should never happen.
    * Keep the payload small. A few numbers per sample is the right size.
"""

# All of the values that you want to transmit to the Datacake  
DATA_FIELDS = {
    "data1":12,
    "data2":14,
    "data3":12.1,
    "data4":14.1,
    "data5":True,
    
}


# Define variables that might be useful for checking the data's validity
MAX_RATE = 5000.0     # faster than this is a sensor glitch
MIN_RATE = 10.0       # slower than this is a missed reading

def check(sensor_data):
    if not sensor_data.ok:
        return                              # already marked bad upstream
    return
    
