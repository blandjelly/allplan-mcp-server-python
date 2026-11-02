"""Run every tests/test*.py module in parallel worker processes.

Equivalent coverage to ``python -m unittest discover -s tests``: every module
is assigned to workers exactly once, either whole or, when it is heavy, as
disjoint chunks ``module@i/n`` (the worker loads the full module and runs
tests ``i::n`` of its sorted test IDs, so chunks cover it completely). Each
worker puts ``tests`` first on ``sys.path`` as discover does. Tests already
use temporary directories and ephemeral ports, so they are independent.
The run fails if any worker fails or ran no tests, or if the assignment does
not cover every discovered module exactly once.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
SUMMARY = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)


def modules(directory=TESTS):
    """Top-level test modules, as discover's default ``test*.py`` pattern finds them."""
    return sorted(path.stem for path in directory.glob("test*.py") if path.is_file())


def plan(names, workers, weight):
    """Split heavy modules into chunks, then assign longest-first.

    A module heavier than an even share of the total is run as several
    disjoint chunks so that one slow module cannot dominate the wall time.
    """
    workers = max(1, workers)
    share = sum(weight(name) for name in names) / workers
    units = []
    for name in names:
        chunks = max(1, min(workers, int(-(-weight(name) // share)) if share else 1))
        units += [(f"{name}@{index}/{chunks}" if chunks > 1 else name, weight(name) / chunks)
                  for index in range(chunks)]
    covered = {}
    for unit, _ in units:
        name, _, chunk = unit.partition("@")
        covered.setdefault(name, set()).add(chunk or "0/1")
    if sorted(covered) != sorted(names) or any(
            len(chunks) != int(next(iter(chunks)).split("/")[1]) for chunks in covered.values()):
        raise RuntimeError("Test assignment does not cover every module exactly once")
    buckets = [[] for _ in range(min(workers, len(units)))]
    loads = [0.0] * len(buckets)
    for unit, cost in sorted(units, key=lambda item: (-item[1], item[0])):
        index = loads.index(min(loads))
        buckets[index].append(unit)
        loads[index] += cost
    return [sorted(bucket) for bucket in buckets if bucket]


def file_weight(name):
    # File size approximates cost. HTTP modules start servers; the smoke module
    # starts one MCP server process per test (about 40% of a sequential run).
    size = (TESTS / f"{name}.py").stat().st_size
    if name == "test_mcp_smoke":
        return size * 6
    return size * (3 if name.endswith("_http") else 1)


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def run_worker(specs):
    """Run whole modules or ``module@i/n`` chunks in this process."""
    sys.path.insert(0, str(TESTS))
    loader, suite = unittest.TestLoader(), unittest.TestSuite()
    for spec in specs:
        name, _, chunk = spec.partition("@")
        tests = sorted(flatten(loader.loadTestsFromName(name)), key=lambda test: test.id())
        if chunk:
            index, count = (int(part) for part in chunk.split("/"))
            if not 0 <= index < count:
                raise ValueError(f"Invalid chunk {spec}")
            tests = tests[index::count]
        suite.addTests(tests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    parser.add_argument("--worker", nargs="+", metavar="MODULE[@I/N]", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker:
        return run_worker(args.worker)
    names = modules()
    if not names:
        print("No test modules found", file=sys.stderr)
        return 1
    # Windows runners default to a legacy console code page; test output holds
    # Polish names, so workers and this process exchange and print UTF-8.
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    # Only stdio changes; file I/O defaults stay as under plain discover.
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    started = time.monotonic()

    def run(bucket):
        # Each worker's pipe is drained by its own thread, so a verbose worker
        # never blocks on a full pipe buffer while another is being read.
        begun = time.monotonic()
        process = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker", *bucket],
                                 cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 encoding="utf-8", errors="replace")
        return bucket, process.returncode, process.stdout, time.monotonic() - begun

    buckets = plan(names, args.workers, file_weight)
    with ThreadPoolExecutor(max_workers=len(buckets)) as pool:
        results = list(pool.map(run, buckets))
    failed, total = False, 0
    for index, (bucket, returncode, output, elapsed) in enumerate(results, 1):
        ran = SUMMARY.search(output)
        count = int(ran.group(1)) if ran else 0
        total += count
        ok = returncode == 0 and count > 0
        failed |= not ok
        print(f"::group::worker {index}: {len(bucket)} units, {count} tests, "
              f"{elapsed:.1f}s, {'OK' if ok else 'FAILED'}")
        print("units: " + ", ".join(bucket))
        print(output)
        print("::endgroup::")
        if not ok:
            print(f"Worker {index} FAILED (exit {returncode}, {count} tests): "
                  + ", ".join(bucket), file=sys.stderr)
    print(f"Ran {total} tests in {len(names)} modules with {len(buckets)} workers "
          f"in {time.monotonic() - started:.1f}s: {'FAILED' if failed else 'OK'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
