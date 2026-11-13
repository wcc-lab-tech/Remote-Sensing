"""
fit_calibration.py -- fit a calibration line from reference measurements.

Input CSV columns:  counts, reference_mm
    counts        the raw reading the sensor driver stores (reading.counts)
    reference_mm  the true value you measured another way (ruler, gauge)

Usage:
    python laptop/fit_calibration.py laptop/sample_data/calibration_points.csv

Prints a slope and intercept to paste into calibration.py, the fit quality, and
each point's residual, and saves a plot. Look at the residuals, not just R^2:
a pattern in the residuals means a straight line is the wrong model.

Change the column names and units to match your sensor.
"""

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pico"))
from calibration import counts_to_volts   # noqa: E402  (same conversion the Pico uses)


def fit_line(x, y):
    """Least-squares fit y = slope * x + intercept. Returns slope, intercept, R^2."""
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((xi - mx) ** 2 for xi in x)
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
    ss_tot = sum((yi - my) ** 2 for yi in y)
    return slope, intercept, 1 - ss_res / ss_tot


def main(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    volts = [counts_to_volts(float(r["counts"])) for r in rows]
    ref = [float(r["reference_mm"]) for r in rows]

    slope, intercept, r2 = fit_line(volts, ref)
    print(f"Fit from {len(rows)} points:  level_mm = {slope:.3f} * volts {intercept:+.3f}")
    print(f"R^2 = {r2:.5f}\n")
    print(f"{'volts':>8} {'reference_mm':>13} {'fit_mm':>9} {'residual_mm':>12}")
    for v, r in zip(volts, ref):
        fit = slope * v + intercept
        print(f"{v:8.3f} {r:13.1f} {fit:9.1f} {r - fit:12.2f}")
    print("\nPaste into calibration.py:")
    print(f"SLOPE = {slope:.3f}")
    print(f"INTERCEPT = {intercept:.3f}")

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(6, 6))
    ax1.plot(volts, ref, "o", label="reference points")
    xs = [min(volts), max(volts)]
    ax1.plot(xs, [slope * x + intercept for x in xs], "-", label="linear fit")
    ax1.set_ylabel("level (mm)")
    ax1.legend()
    ax2.axhline(0, color="gray", lw=0.8)
    ax2.plot(volts, [r - (slope * v + intercept) for v, r in zip(volts, ref)], "o")
    ax2.set_xlabel("sensor output (V)")
    ax2.set_ylabel("residual (mm)")
    fig.tight_layout()
    out = os.path.join(HERE, "output", "calibration_fit.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=150)
    print(f"\nPlot saved to {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1
         else os.path.join(HERE, "sample_data", "calibration_points.csv"))
