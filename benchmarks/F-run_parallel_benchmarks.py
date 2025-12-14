#!/usr/bin/env python3
"""
Comprehensive Parallel Benchmarking Suite
Runs parallel word counter with various configurations and collects performance metrics
"""

import os
import sys
import subprocess
import time
import json
import csv
from pathlib import Path
from datetime import datetime
import statistics

# Configuration
DATASETS = [
    "data/test_10mb.txt",
    "data/test_25mb.txt",
    "data/test_50mb.txt",
    "data/test_100mb.txt"
]

THREAD_COUNTS = [1, 2, 4, 8]
SYNC_METHODS = ["reduction", "atomic", "critical"]
RUNS_PER_CONFIG = 5

# Executables
SEQUENTIAL_EXE = "build/sequential_counter.exe"
PARALLEL_EXE = "build/parallel_counter.exe"

# Output
RESULTS_DIR = "benchmarks/results"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def run_sequential_benchmark(dataset):
    """Run sequential version and get baseline timing"""
    print(f"\n{'='*60}")
    print(f"Running SEQUENTIAL benchmark: {dataset}")
    print(f"{'='*60}")
    
    times = []
    total_words = 0
    
    for run in range(RUNS_PER_CONFIG):
        start = time.perf_counter()
        result = subprocess.run(
            [SEQUENTIAL_EXE, dataset],
            capture_output=True,
            text=True
        )
        elapsed = time.perf_counter() - start
        
        if result.returncode != 0:
            print(f"  ❌ Run {run+1} failed!")
            continue
            
        # Extract total words from output
        for line in result.stdout.split('\n'):
            if "Total Words:" in line:
                total_words = int(line.split(':')[1].strip())
                break
        
        times.append(elapsed * 1000)  # Convert to ms
        print(f"  Run {run+1}/{RUNS_PER_CONFIG}: {elapsed*1000:.2f} ms")
    
    return {
        "dataset": dataset,
        "threads": 1,
        "sync_method": "sequential",
        "times": times,
        "mean_time": statistics.mean(times),
        "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
        "min_time": min(times),
        "max_time": max(times),
        "total_words": total_words
    }


def run_parallel_benchmark(dataset, threads, sync_method):
    """Run parallel version with specific configuration"""
    print(f"\n{'='*60}")
    print(f"Parallel: {dataset} | Threads: {threads} | Sync: {sync_method}")
    print(f"{'='*60}")
    
    times = []
    total_words = 0
    
    output_file = f"results/parallel/bench_{Path(dataset).stem}_{threads}t_{sync_method}.txt"
    
    for run in range(RUNS_PER_CONFIG):
        start = time.perf_counter()
        result = subprocess.run(
            [PARALLEL_EXE, dataset, output_file, "100", str(threads), sync_method],
            capture_output=True,
            text=True
        )
        elapsed = time.perf_counter() - start
        
        if result.returncode != 0:
            print(f"  ❌ Run {run+1} failed!")
            print(f"  Error: {result.stderr}")
            continue
        
        # Extract total words from output
        for line in result.stdout.split('\n'):
            if "Total Words:" in line:
                total_words = int(line.split(':')[1].strip())
                break
        
        times.append(elapsed * 1000)  # Convert to ms
        print(f"  Run {run+1}/{RUNS_PER_CONFIG}: {elapsed*1000:.2f} ms")
    
    return {
        "dataset": dataset,
        "threads": threads,
        "sync_method": sync_method,
        "times": times,
        "mean_time": statistics.mean(times) if times else 0,
        "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
        "min_time": min(times) if times else 0,
        "max_time": max(times) if times else 0,
        "total_words": total_words
    }


def calculate_metrics(results, seq_baseline):
    """Calculate speedup, efficiency, and scalability metrics"""
    for result in results:
        if result['sync_method'] == 'sequential':
            result['speedup'] = 1.0
            result['efficiency'] = 100.0
            continue
        
        # Find matching sequential baseline
        seq_time = None
        for baseline in seq_baseline:
            if baseline['dataset'] == result['dataset']:
                seq_time = baseline['mean_time']
                break
        
        if seq_time:
            result['speedup'] = seq_time / result['mean_time']
            result['efficiency'] = (result['speedup'] / result['threads']) * 100
        else:
            result['speedup'] = 0
            result['efficiency'] = 0
    
    return results


def save_results(results, seq_baseline):
    """Save results in multiple formats"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # JSON format
    json_file = f"{RESULTS_DIR}/parallel_benchmark_{TIMESTAMP}.json"
    with open(json_file, 'w') as f:
        json.dump({
            "sequential_baseline": seq_baseline,
            "parallel_results": results,
            "timestamp": TIMESTAMP
        }, f, indent=2)
    print(f"\n✅ JSON saved: {json_file}")
    
    # CSV format
    csv_file = f"{RESULTS_DIR}/parallel_benchmark_{TIMESTAMP}.csv"
    with open(csv_file, 'w', newline='') as f:
        fieldnames = ['dataset', 'threads', 'sync_method', 'mean_time', 'std_dev', 
                      'min_time', 'max_time', 'speedup', 'efficiency', 'total_words']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({k: result.get(k, '') for k in fieldnames})
    print(f"✅ CSV saved: {csv_file}")
    
    # Summary text
    summary_file = f"{RESULTS_DIR}/parallel_summary_{TIMESTAMP}.txt"
    with open(summary_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("PARALLEL BENCHMARKING SUMMARY\n")
        f.write("="*80 + "\n\n")
        
        for dataset in DATASETS:
            f.write(f"\nDataset: {dataset}\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Threads':<10} {'Sync':<12} {'Time(ms)':<12} {'Speedup':<10} {'Efficiency':<12}\n")
            f.write("-"*80 + "\n")
            
            # Sequential baseline
            seq = next((r for r in seq_baseline if r['dataset'] == dataset), None)
            if seq:
                f.write(f"{'1':<10} {'sequential':<12} {seq['mean_time']:<12.2f} {'1.00x':<10} {'100.00%':<12}\n")
            
            # Parallel results
            for result in sorted([r for r in results if r['dataset'] == dataset], 
                                key=lambda x: (x['threads'], x['sync_method'])):
                f.write(f"{result['threads']:<10} {result['sync_method']:<12} "
                       f"{result['mean_time']:<12.2f} {result['speedup']:<10.2f}x "
                       f"{result['efficiency']:<12.2f}%\n")
            f.write("\n")
    
    print(f"✅ Summary saved: {summary_file}")


def main():
    print("\n" + "="*80)
    print(" PARALLEL WORD COUNTER - COMPREHENSIVE BENCHMARKING SUITE")
    print("="*80)
    print(f"\nDatasets: {len(DATASETS)}")
    print(f"Thread counts: {THREAD_COUNTS}")
    print(f"Sync methods: {SYNC_METHODS}")
    print(f"Runs per config: {RUNS_PER_CONFIG}")
    print(f"Total benchmarks: {len(DATASETS) * (1 + len(THREAD_COUNTS) * len(SYNC_METHODS)) * RUNS_PER_CONFIG}")
    
    # Check executables exist
    if not os.path.exists(SEQUENTIAL_EXE):
        print(f"\n❌ Sequential executable not found: {SEQUENTIAL_EXE}")
        print("   Run build script first!")
        return 1
    
    if not os.path.exists(PARALLEL_EXE):
        print(f"\n❌ Parallel executable not found: {PARALLEL_EXE}")
        print("   Run build script first!")
        return 1
    
    # Step 1: Run sequential benchmarks (baseline)
    print("\n" + "="*80)
    print(" PHASE 1: SEQUENTIAL BASELINE")
    print("="*80)
    seq_baseline = []
    for dataset in DATASETS:
        if not os.path.exists(dataset):
            print(f"\n⚠️  Dataset not found: {dataset}")
            continue
        result = run_sequential_benchmark(dataset)
        seq_baseline.append(result)
    
    # Step 2: Run parallel benchmarks
    print("\n" + "="*80)
    print(" PHASE 2: PARALLEL BENCHMARKS")
    print("="*80)
    parallel_results = []
    for dataset in DATASETS:
        if not os.path.exists(dataset):
            continue
        for threads in THREAD_COUNTS:
            for sync_method in SYNC_METHODS:
                result = run_parallel_benchmark(dataset, threads, sync_method)
                parallel_results.append(result)
    
    # Step 3: Calculate metrics
    print("\n" + "="*80)
    print(" PHASE 3: CALCULATING PERFORMANCE METRICS")
    print("="*80)
    parallel_results = calculate_metrics(parallel_results, seq_baseline)
    
    # Step 4: Save results
    print("\n" + "="*80)
    print(" PHASE 4: SAVING RESULTS")
    print("="*80)
    save_results(parallel_results, seq_baseline)
    
    # Print summary
    print("\n" + "="*80)
    print(" BENCHMARK COMPLETE!")
    print("="*80)
    print(f"\n📊 Best speedup achieved:")
    best = max(parallel_results, key=lambda x: x.get('speedup', 0))
    print(f"   {best['dataset']} with {best['threads']} threads ({best['sync_method']}): "
          f"{best['speedup']:.2f}x speedup, {best['efficiency']:.1f}% efficiency")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
