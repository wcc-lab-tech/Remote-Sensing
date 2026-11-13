"""
load_events.py -- load sensor data into a pandas DataFrame, whatever its source.

Handles three formats:
    .jsonl  one event per line (from simulate.py)
    .json   a list of events exported from Notehub
    .csv    a table exported from Notehub or Datacake (needs a time column)

Returns a DataFrame indexed by local (Pacific) time, one column per field,
with kit.MISSING (-9999) converted to NaN so it cannot sneak into an average.
"""

import json

import numpy as np
import pandas as pd

MISSING = -9999.0
TIME_COLUMNS = ("when", "time", "timestamp", "captured", "received", "date")
LOCAL_TZ = "America/Los_Angeles"


def _events_to_frame(events):
    rows = []
    for ev in events:
        body = ev.get("body") or {}
        t = ev.get("when") or body.get("_time") or ev.get("received")
        row = {"time": t}
        row.update({k: v for k, v in body.items() if not k.startswith("_")})
        rows.append(row)
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df


def load_events(path, fields=None):
    """fields: optionally, telemetry.FIELDS. Guarantees every field has a column,
    even one that was always 0 or false and so never appeared in the data."""
    if path.endswith(".jsonl"):
        with open(path) as f:
            df = _events_to_frame([json.loads(line) for line in f if line.strip()])
    elif path.endswith(".json"):
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("events", [])
        df = _events_to_frame(data)
    elif path.endswith(".csv"):
        df = pd.read_csv(path)
        tcol = next((c for c in df.columns if c.lower() in TIME_COLUMNS), None)
        if tcol is None:
            raise ValueError(f"No time column found. Expected one of {TIME_COLUMNS}")
        t = df.pop(tcol)
        unit = "s" if pd.api.types.is_numeric_dtype(t) else None
        df["time"] = pd.to_datetime(t, unit=unit, utc=True)
    else:
        raise ValueError("Expected a .jsonl, .json, or .csv file")

    for name, hint in (fields or {}).items():
        if name not in df.columns:
            df[name] = False if hint is True else 0.0
    df = df.set_index("time").sort_index()
    df.index = df.index.tz_convert(LOCAL_TZ)

    # LoRa templates drop fields whose value is 0 or false, so a blank here means
    # 0 or false. Genuinely missing readings arrive as MISSING, handled next.
    for col in df.columns:
        present = df[col].dropna()
        if len(present) and present.map(lambda v: isinstance(v, (bool, np.bool_))).all():
            df[col] = df[col].eq(True)       # a blank becomes False
        else:
            df[col] = df[col].fillna(0)
    df = df.replace(MISSING, np.nan)
    return df
