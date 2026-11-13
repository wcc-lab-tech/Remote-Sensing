"""
simulate.py -- run your team's Pico modules on your laptop.

Uses the fake sensor, a fake Notecard, and a simulated clock, so two days of
15-minute samples take about a second. Every reading lands in
simulator/output/sim_events.jsonl, which laptop/analyze.py and
laptop/send_to_datacake.py can use exactly like exported real data.

In Thonny: open this file and press F5, with the interpreter set to Local Python 3.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PICO = os.path.join(HERE, "..", "pico")
sys.path.insert(1, PICO)        # after this folder, so this folder's kit.py wins

import config                   # noqa: E402
import kit                      # noqa: E402  (simulator/kit.py)
import main
import sensor                   # noqa: E402
import telemetry                # noqa: E402

HOURS = 48
OUT = os.path.join(HERE, "output", "sim_events.jsonl")


def simulate(hours=HOURS, out_path=OUT):
    """Run the team's modules for the given number of simulated hours.
    Returns the number of samples taken."""
    config.USE_FAKE_SENSOR = True
    sensor._fake_step = 0
    kit.reset_memory()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    if os.path.exists(out_path):
        os.remove(out_path)

    node = kit.Node(out_path)
    node.connect(verbose=False)
    node.setup(telemetry.DATA_FIELDS)
    n = int(hours * 3600 / config.SAMPLE_SECONDS)
    for _ in range(n):
        try:
            main.run(node)
        except Exception as err:
            node.error(err)
        node.sleep()
    return n


if __name__ == "__main__":
    n = simulate()
    print(f"Simulated {n} samples ({HOURS} h). Readings written to {OUT}")
    print("Next: open laptop/analyze.py and press F5.")
