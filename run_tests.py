"""
run_tests.py -- run the team's tests with plain Python. No installs needed.

In Thonny: open this file and press F5 (Run). Make sure the interpreter in
Thonny's bottom-right corner says "Local Python 3", not the Pico.

It finds every file named tests/test_*.py, runs every function in it whose name
starts with test_, and reports each one as PASS or FAIL. A test passes when it
finishes without an error; a failed assert shows the line that failed.

To run only one module's tests while you work on it, set ONLY below, for
example ONLY = "test_processing". Set it back to None to run everything.
"""

import importlib
import os
import sys
import traceback

ONLY = None   # e.g. "test_processing" to run just that file

HERE = os.path.dirname(os.path.abspath(__file__))
# Order matters: simulator/kit.py must be found before pico/kit.py,
# because the Pico's kit.py needs the Pico's hardware.
for folder in ("pico", "laptop", "simulator", "tests"):
    path = os.path.join(HERE, folder)
    if path not in sys.path:
        sys.path.insert(0, path)


def find_test_files():
    names = sorted(f[:-3] for f in os.listdir(os.path.join(HERE, "tests"))
                   if f.startswith("test_") and f.endswith(".py"))
    if ONLY:
        names = [n for n in names if n == ONLY]
        if not names:
            print(f"No test file named {ONLY}.py in tests/")
    return names


def run_file(name):
    """Run every test_ function in one file. Returns (passed, failed)."""
    passed = failed = 0
    try:
        module = importlib.import_module(name)
    except Exception:
        print(f"\n{name}.py could not be loaded:")
        traceback.print_exc(file=sys.stdout)
        return 0, 1
    tests = [(n, f) for n, f in vars(module).items()
             if n.startswith("test_") and callable(f)]
    print(f"\n{name}.py")
    for test_name, test in tests:
        try:
            test()
            print(f"  PASS  {test_name}")
            passed += 1
        except Exception as err:
            failed += 1
            print(f"  FAIL  {test_name}")
            if isinstance(err, AssertionError):
                frame = traceback.extract_tb(err.__traceback__)[-1]
                print(f"        line {frame.lineno}: {frame.line}")
                if str(err):
                    print(f"        {err}")
            else:
                print("        " + "".join(traceback.format_exception_only(type(err), err)).strip())
                frame = traceback.extract_tb(err.__traceback__)[-1]
                print(f"        in {os.path.basename(frame.filename)}, line {frame.lineno}: {frame.line}")
    return passed, failed


def main():
    os.chdir(HERE)
    total_pass = total_fail = 0
    for name in find_test_files():
        p, f = run_file(name)
        total_pass += p
        total_fail += f
    print()
    if total_fail:
        print(f"{total_pass} passed, {total_fail} FAILED")
    else:
        print(f"All {total_pass} tests passed")
    return total_fail


if __name__ == "__main__":
    main()
