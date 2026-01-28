#!/usr/bin/env python3
"""Benchmark script for Aletheia sidecar."""

import argparse
import sys
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any

# Add sidecar to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def find_test_files(input_dir: Path) -> Dict[str, List[Path]]:
    """Find test files by type."""
    files = {
        "pdf": list(input_dir.glob("**/*.pdf")),
        "image": list(input_dir.glob("**/*.png")) + list(input_dir.glob("**/*.jpg")),
    }
    return files


def benchmark_parse(file_path: Path, orchestrator) -> float:
    """Benchmark parsing a single file, return time in ms."""
    start = time.perf_counter()
    try:
        orchestrator.process_file(file_path)
    except Exception as e:
        print(f"    Error parsing {file_path.name}: {e}")
        return -1
    return (time.perf_counter() - start) * 1000


def run_benchmark(input_dir: Path, iterations: int = 10):
    """Run parsing benchmarks."""
    print(f"Running benchmark with {iterations} iterations...")
    print(f"Input directory: {input_dir}")
    print()

    # Find test files
    files = find_test_files(input_dir)
    total_files = sum(len(f) for f in files.values())

    if total_files == 0:
        print("No test files found. Add PDFs or images to the examples folder.")
        return

    print(f"Found {total_files} test files:")
    for ftype, flist in files.items():
        print(f"  {ftype}: {len(flist)}")
    print()

    # Initialize pipeline
    try:
        from app.pipeline.orchestrator import PipelineOrchestrator
        orchestrator = PipelineOrchestrator()
    except Exception as e:
        print(f"Failed to initialize pipeline: {e}")
        return

    results: Dict[str, List[float]] = {
        "pdf_parse_ms": [],
        "image_parse_ms": [],
    }

    # Warmup run
    print("Warmup run...")
    for ftype, flist in files.items():
        if flist:
            benchmark_parse(flist[0], orchestrator)

    # Benchmark runs
    print(f"\nRunning {iterations} iterations...")
    for i in range(iterations):
        print(f"  Iteration {i + 1}/{iterations}", end="\r")

        for pdf_file in files["pdf"][:3]:  # Limit to 3 files per type
            t = benchmark_parse(pdf_file, orchestrator)
            if t >= 0:
                results["pdf_parse_ms"].append(t)

        for img_file in files["image"][:3]:
            t = benchmark_parse(img_file, orchestrator)
            if t >= 0:
                results["image_parse_ms"].append(t)

    print("\n")
    print("=" * 50)
    print("Benchmark Results")
    print("=" * 50)

    for metric, times in results.items():
        if times:
            avg = statistics.mean(times)
            med = statistics.median(times)
            std = statistics.stdev(times) if len(times) > 1 else 0
            print(f"\n{metric}:")
            print(f"  Count:  {len(times)}")
            print(f"  Mean:   {avg:.2f} ms")
            print(f"  Median: {med:.2f} ms")
            print(f"  StdDev: {std:.2f} ms")
            print(f"  Min:    {min(times):.2f} ms")
            print(f"  Max:    {max(times):.2f} ms")


def main():
    parser = argparse.ArgumentParser(description="Benchmark Aletheia sidecar")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "examples",
        help="Directory with test documents",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of iterations",
    )

    args = parser.parse_args()
    run_benchmark(args.input_dir, args.iterations)


if __name__ == "__main__":
    main()
