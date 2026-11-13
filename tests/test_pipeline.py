"""Whole-system test: every module working together through the simulator.
If your module passes its own tests but this fails, the problem is usually
an interface: a field name, a type, or a missing key."""

import os
import tempfile

from load_events import load_events
from simulate import simulate
from telemetry import DATA_FIELDS


def test_full_pipeline():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "events.jsonl")
        n = simulate(hours=48, out_path=out)
        df = load_events(out, DATA_FIELDS)
    assert len(df) == n
    assert df["rising"].any(), "the simulated storm should be detected"
    assert df["level_mm"].notna().mean() > 0.9
    # Failed reads must come back as NaN, not 0, even though LoRa drops zeros.
    assert df.loc[~df["ok"], "level_mm"].isna().all()


def test_field_that_is_always_false_still_loads():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "events.jsonl")
        with open(out, "w") as f:
            f.write('{"when": 1790000000, "body": {"level_mm": 100.0, "ok": true}}\n')
        df = load_events(out, DATA_FIELDS)
    assert "rising" in df.columns and not df["rising"].any()
