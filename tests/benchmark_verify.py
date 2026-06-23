"""Performance benchmark for sicario verify.

Measures verify execution time against a freshly initialized project
with all profiles loaded. Run with: python3 tests/benchmark_verify.py
"""

from __future__ import annotations

import shutil
import time
import tempfile
from pathlib import Path

from sicario_cli.cli import init_project, verify_project, build_parser


def _run_init(target: Path) -> None:
    args = build_parser().parse_args(
        [
            "init",
            str(target),
            "--profile",
            "core,appsec,cloud-iac,compliance",
            "--frameworks",
            "all",
            "--apply-to-speckit",
        ]
    )
    rc = init_project(args)
    assert rc == 0, f"init returned {rc}"


def _run_verify(target: Path) -> float:
    start = time.perf_counter()
    findings = verify_project(target, write=False)
    elapsed = time.perf_counter() - start
    return elapsed, len(findings)


def main() -> None:
    tmpdir = Path(tempfile.mkdtemp(suffix="_sicario_bench"))
    target = tmpdir / "bench-project"

    print("=== SicarioSpec Verify Benchmark ===\n")

    # 1) init the project
    print("Initialising benchmark project...")
    t0 = time.perf_counter()
    _run_init(target)
    init_time = time.perf_counter() - t0
    print(f"  init: {init_time:.3f}s")

    # 2) warm-up run
    _run_verify(target)

    # 3) measured runs
    n_runs = 10
    times = []
    findings_counts = []
    print(f"\nRunning verify {n_runs}x...")
    for i in range(n_runs):
        elapsed, count = _run_verify(target)
        times.append(elapsed)
        findings_counts.append(count)
        print(f"  run {i + 1:2d}: {elapsed:.3f}s  ({count} findings)")

    avg = sum(times) / len(times)
    print(f"\nResults ({n_runs} runs):")
    print(f"  mean:    {avg:.3f}s")
    print(f"  min:     {min(times):.3f}s")
    print(f"  max:     {max(times):.3f}s")

    # 4) rule count
    rule_files = list((target / ".sicario" / "rules").rglob("*.rule.json"))
    print(f"  rules:   {len(rule_files)} files loaded")

    # 5) findings summary
    if findings_counts:
        print(f"  avg findings: {sum(findings_counts) / len(findings_counts):.0f}")

    # 6) throughput (files / rules per second)
    src_files = sum(1 for _ in target.rglob("*") if _.is_file())
    total_rules = len(rule_files) * n_runs
    total_time = sum(times)
    print("\nThroughput:")
    print(f"  source files: {src_files}")
    print(f"  rules/sec:    {total_rules / total_time:.0f}" if total_time > 0 else "  N/A")

    # Cleanup
    shutil.rmtree(tmpdir)
    print("\nBenchmark directory cleaned up.")


if __name__ == "__main__":
    main()
