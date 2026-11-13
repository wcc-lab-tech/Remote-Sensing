"""
analyze.py -- ANALYSIS AND DISPLAY MODULE
OWNER: ______________________

This template runs as-is on the sample data, so you can start in Week 1, long
before your sensor arrives. Work through the TODOs to turn it into your team's
analysis. The dashboard shows what is happening now; this script answers the
question your project is about.

How to run it: open this file in Thonny (interpreter: Local Python 3) and press F5.
It analyzes DATA_FILE, set below. Left as None, it uses the latest output of
simulator/simulate.py, or the sample storm if you have not run the simulator yet.
From a terminal you can also pass a file: python laptop/analyze.py path/to/file

YOUR JOB
    1. Data quality: how much of the data can you trust, and where are the gaps?
    2. A figure someone outside our class could read in ten seconds.
    3. A headline result: the number that answers your team's essential question.
"""

import os
import sys

import matplotlib.pyplot as plt

from load_events import load_events

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pico"))
from telemetry import DATA_FIELDS   # noqa: E402
OUT = os.path.join(HERE, "output")
SAMPLE_MINUTES = 15     # TODO: match config.SAMPLE_SECONDS / 60
DATA_FILE = None        # e.g. "../../data/my_export.json" for exported real data


def data_quality(df):
    """Summarize how complete and trustworthy the record is."""
    n = len(df)
    bad = int((~df["ok"]).sum()) if "ok" in df else 0
    gaps = df.index.to_series().diff().dt.total_seconds() / 60
    long_gaps = gaps[gaps > 2 * SAMPLE_MINUTES]
    print("DATA QUALITY")
    print(f"  {n} readings from {df.index[0]:%b %d %H:%M} to {df.index[-1]:%b %d %H:%M}")
    print(f"  {bad} failed reads ({100 * bad / n:.1f}%)")
    print(f"  {len(long_gaps)} gaps longer than {2 * SAMPLE_MINUTES} minutes")
    # TODO: add checks that matter for YOUR sensor (stuck values, spikes, drift).


def headline(df):
    """Compute the result your project reports."""
    level = df["data1"]
    peak_time = level.idxmax()
    rising = df["data2"]
    n_events = int((rising & ~rising.shift(fill_value=False)).sum())
    hours_rising = rising.sum() * SAMPLE_MINUTES / 60
    print("\nRESULTS")
    print(f"  Peak level: {level.max():.0f} mm at {peak_time:%b %d %H:%M}")
    print(f"  Baseline (median) level: {level.median():.0f} mm")
    print(f"  Rising events: {n_events}, totaling {hours_rising:.1f} h")
    # TODO: the number that answers YOUR question. Examples: time above a
    # flood-risk level, how fast the drain recovers after a storm, hours a room
    # spent above 1000 ppm CO2, energy wasted overnight.


def plot(df, path):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(df.index, df["data1"], lw=1.5, color="#4472C4", label="water level")
    ax.fill_between(df.index, 0, 1, where=df["data1"], transform=ax.get_xaxis_transform(),
                    alpha=0.15, color="#8A1E40", label="rising event")
    ax.set_ylabel("level (mm)")
    ax.set_title("Storm drain water level")   # TODO: a title that states the finding
    ax.legend(loc="upper right")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"\nFigure saved to {path}")


if __name__ == "__main__":
    sim = os.path.normpath(os.path.join(HERE, "..", "simulator", "output", "sim_events.jsonl"))
    sample = os.path.join(HERE, "sample_data", "bench_storm_event.jsonl")
    if len(sys.argv) > 1:
        src = sys.argv[1]
    elif DATA_FILE:
        src = DATA_FILE if os.path.isabs(DATA_FILE) else os.path.join(HERE, DATA_FILE)
    else:
        src = sim if os.path.exists(sim) else sample
    print("Analyzing", src)
    df = load_events(src, DATA_FIELDS)
    data_quality(df)
    headline(df)
    os.makedirs(OUT, exist_ok=True)
    plot(df, os.path.join(OUT, "level_timeseries.png"))
