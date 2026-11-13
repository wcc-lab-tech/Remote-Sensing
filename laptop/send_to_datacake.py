"""
send_to_datacake.py -- fill your Datacake dashboard with simulated data.

Wraps each reading from simulator/simulate.py in the same envelope Notehub uses and posts
it to your Datacake webhook URL, so you can build and test your dashboard
before your hardware is ready. Times are shifted so the last reading is "now".

How to run it in Thonny (interpreter: Local Python 3):
    1. Run simulator/simulate.py first (F5) so there is simulated data to send.
    2. Paste your Datacake webhook URL and device serial into WEBHOOK_URL and
       DEVICE below, then press F5 on this file.
From a terminal you can instead pass --url and --device.

DEVICE must match the serial number of your device in Datacake. Use your
Notecard's device ID from Notehub (it starts with "dev:") so the same Datacake
device keeps working once real data arrives.
"""

import argparse
import json
import os
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

WEBHOOK_URL = "https://api.datacake.co/integrations/api/c3960044-a28e-4bb0-9e01-09f93b43e4cc/"   # from Datacake: Configuration > HTTP Payload Decoder
DEVICE = "dev:0080e1150045224b"        # your device's serial number in Datacake, e.g. "dev:864475040123456"


def notehub_envelope(event, device, shift=0):
    """Build the JSON that a Notehub route would send for one reading."""
    when = int(event["when"] + shift)
    return {
        "event": f"simulated-{when}",
        "device": device,
        "file": event.get("file", "data.qo"),
        "req": "note.add",
        "when": when,
        "received": when,
        "body": event["body"],
    }


def post(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as rsp:
        return rsp.status


def main():
    parser = argparse.ArgumentParser(description="Replay simulated readings into Datacake.")
    parser.add_argument("--url", default=WEBHOOK_URL, help="webhook URL from Datacake's HTTP Payload Decoder section")
    parser.add_argument("--device", default=DEVICE, help="the device's serial number in Datacake")
    parser.add_argument("--events", default=os.path.normpath(os.path.join(HERE, "..", "simulator", "output", "sim_events.jsonl")))
    parser.add_argument("--limit", type=int, default=0, help="send only the last N readings (0 = all)")
    parser.add_argument("--delay", type=float, default=0.2, help="seconds between posts")
    args = parser.parse_args()

    if not args.url or not args.device:
        print("Set WEBHOOK_URL and DEVICE at the top of send_to_datacake.py, then run it again.")
        return
    if not os.path.exists(args.events):
        print("No simulated data yet. Run simulator/simulate.py first.")
        return
    with open(args.events) as f:
        events = [json.loads(line) for line in f if line.strip()]
    if args.limit:
        events = events[-args.limit:]
    shift = time.time() - events[-1]["when"]

    sent = 0
    for ev in events:
        try:
            post(args.url, notehub_envelope(ev, args.device, shift))
            sent += 1
        except urllib.error.URLError as err:
            print("post failed:", err)
            break
        if sent % 25 == 0:
            print(f"sent {sent} of {len(events)}")
        time.sleep(args.delay)
    print(f"Done: sent {sent} readings. Check Datacake's decoder logs and your dashboard.")


if __name__ == "__main__":
    main()
