// This section does need to be edited to match telemetry.DATA_FIELDS. Use "number" or "boolean".
var DATA_FIELDS = {
    "data1": "number",
    "data2": "number",
    "data3": "number",
    "data4": "number",
    "data5": "True"
};


// This section does not need to be edited by your group and should be able to handle most cases. 
// If you run into errors, ask your instructor or lab tech
var DATA_NOTEFILE = "data.qo";
var LOCATION_NOTEFILE = "location.qo"
var MISSING = -9999;

function Decoder(request) {    

    var event = JSON.parse(request.body);
    console.log("Message received");
    
    var body = event.body || {};
    var device = event.device;          // Notecard ID, e.g. "dev:864475040123456"
    var time = event.when || event.received;
    var results = [];
        
    if (event.file === DATA_NOTEFILE) {
        
        for (var name in DATA_FIELDS) {
            var value = body[name];
            if (value === undefined || value === null) {
                value = (FIELDS[name] === "boolean") ? false : 0;
            }
            if (DATA_FIELDS[name] === "number" && value <= MISSING) {
                continue;
            }
            var item = { device: device, field: name.toUpperCase(), value: value };
            if (time) {
                item.timestamp = Math.floor(time);
            }
            results.push(item);
        }
    }
    
    if (event.file === LOCATION_NOTEFILE){
        
        var lat = event.body && event.body.lat;
        var long = event.body && event.body.long;
        console.log(typeof lat)
        console.log(typeof long)

        if (typeof lat === "number" && typeof long === "number") {
            console.log("test2")
            results.push({
              device: device,
              field: "LOCATION",
              value: "(" + lat + "," + long + ")"
            });
        } 
    }
    return results;
}
