"""
Benchmark Suite for Word Frequency Counter
===========================================
Runs performance tests on sequential and parallel implementations
across multiple dataset sizes and thread configurations.
"""

import subprocess
import time
import json
import csv
import os
import sys
from pathlib import Path
from datetime import datetime
import statistics

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class BenchmarkRunner:
    def __init__(self, data_dir="../data", results_dir="results"):
        # Get absolute paths
        self.script_dir = Path(__file__).parent.absolute()
        self.project_root = self.script_dir.parent
        
        self.data_dir = (self.script_dir / data_dir).resolve()
        self.results_dir = (self.script_dir / results_dir).resolve()
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Check both Windows and Linux executable names
        # Look in parent directory's build folder
        self.sequential_exe = (self.project_root / "build" / "sequential_counter.exe").resolve()
        if not self.sequential_exe.exists():
            self.sequential_exe = (self.project_root / "build" / "sequential_counter").resolve()
        
    def get_test_files(self):
        """Get list of test data files sorted by size"""
        test_files = sorted(self.data_dir.glob("test_*.txt"))
        return [(f, f.stat().st_size) for f in test_files]
    
    def run_sequential_benchmark(self, input_file, runs=5):
        """Run sequential benchmark multiple times and collect statistics"""
        if not self.sequential_exe.exists():
            print(f"Sequential executable not found: {self.sequential_exe}")
            return None
        
        execution_times = []
        total_words = 0
        unique_words = 0
        
        print(f"\n  Running {runs} iterations...")
        
        for run in range(runs):
            try:
                # Create temp output directory
                temp_output = self.project_root / "results" / "sequential" / "temp_output.txt"
                temp_output.parent.mkdir(parents=True, exist_ok=True)
                
                # Setup environment with MinGW bin in PATH (for Windows DLLs)
                env = os.environ.copy()
                mingw_bin = Path(os.environ.get('LOCALAPPDATA', '')) / "Microsoft" / "WinGet" / "Packages"
                mingw_dirs = list(mingw_bin.glob("*WinLibs*/mingw64/bin"))
                if mingw_dirs:
                    env['PATH'] = str(mingw_dirs[0]) + os.pathsep + env.get('PATH', '')
                
                start = time.perf_counter()
                result = subprocess.run(
                    [str(self.sequential_exe), str(input_file.absolute()), 
                     str(temp_output), "100"],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    cwd=str(self.project_root),  # Run from project root
                    env=env  # Use modified environment
                )
                end = time.perf_counter()
                
                if result.returncode != 0:
                    print(f"    Run {run+1} failed:")
                    print(f"        Return code: {result.returncode}")
                    if result.stderr:
                        print(f"        Error: {result.stderr[:200]}")
                    if result.stdout:
                        print(f"        Output: {result.stdout[:200]}")
                    continue
                
                exec_time = (end - start) * 1000  # Convert to milliseconds
                execution_times.append(exec_time)
                
                # Parse output for statistics
                for line in result.stdout.split('\n'):
                    if "Total Words:" in line:
                        total_words = int(line.split(':')[1].strip())
                    elif "Unique Words:" in line:
                        unique_words = int(line.split(':')[1].strip())
                
                print(f"    Run {run+1}: {exec_time:.2f} ms")
                
            except subprocess.TimeoutExpired:
                print(f"    Run {run+1} timed out")
            except Exception as e:
                print(f"    Run {run+1} error: {e}")
        
        if not execution_times:
            return None
        
        return {
            'mean_time': statistics.mean(execution_times),
            'median_time': statistics.median(execution_times),
            'min_time': min(execution_times),
            'max_time': max(execution_times),
            'std_dev': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            'runs': len(execution_times),
            'total_words': total_words,
            'unique_words': unique_words,
            'all_times': execution_times
        }
    
    def run_all_benchmarks(self, runs_per_test=5):
        """Run benchmarks on all test files"""
        test_files = self.get_test_files()
        
        if not test_files:
            print("No test files found in data directory!")
            print(f"   Please run generate_dataset.py first")
            return
        
        print("\n" + "="*60)
        print("  BENCHMARK SUITE - Sequential Word Counter")
        print("="*60)
        print(f"Test Files: {len(test_files)}")
        print(f"Runs per test: {runs_per_test}")
        print(f"Results directory: {self.results_dir}")
        print("="*60)
        
        results = []
        
        for test_file, file_size in test_files:
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"\nTesting: {test_file.name} ({file_size_mb:.2f} MB)")
            print("-" * 60)
            
            benchmark_result = self.run_sequential_benchmark(test_file, runs_per_test)
            
            if benchmark_result:
                result_entry = {
                    'filename': test_file.name,
                    'file_size_mb': file_size_mb,
                    'file_size_bytes': file_size,
                    'implementation': 'sequential',
                    'threads': 1,
                    **benchmark_result
                }
                results.append(result_entry)
                
                print(f"\n  Results:")
                print(f"     Mean Time:    {benchmark_result['mean_time']:.2f} ms")
                print(f"     Median Time:  {benchmark_result['median_time']:.2f} ms")
                print(f"     Std Dev:      {benchmark_result['std_dev']:.2f} ms")
                print(f"     Total Words:  {benchmark_result['total_words']:,}")
                print(f"     Unique Words: {benchmark_result['unique_words']:,}")
        
        # Save results
        if results:
            self.save_results(results)
            print("\n" + "="*60)
            print("Benchmarking complete!")
            print("="*60)
        else:
            print("\nNo successful benchmark runs!")
    
    def save_results(self, results):
        """Save benchmark results in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = self.results_dir / f"benchmark_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved JSON: {json_file}")
        
        # Save as CSV
        csv_file = self.results_dir / f"benchmark_results_{timestamp}.csv"
        if results:
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            print(f"Saved CSV: {csv_file}")
        
        # Save as formatted text
        txt_file = self.results_dir / f"benchmark_results_{timestamp}.txt"
        with open(txt_file, 'w') as f:
            f.write("BENCHMARK RESULTS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Tests: {len(results)}\n")
            f.write("=" * 80 + "\n\n")
            
            for result in results:
                f.write(f"File: {result['filename']} ({result['file_size_mb']:.2f} MB)\n")
                f.write(f"Implementation: {result['implementation']}\n")
                f.write(f"Mean Time: {result['mean_time']:.2f} ms\n")
                f.write(f"Median Time: {result['median_time']:.2f} ms\n")
                f.write(f"Std Dev: {result['std_dev']:.2f} ms\n")
                f.write(f"Total Words: {result['total_words']:,}\n")
                f.write(f"Unique Words: {result['unique_words']:,}\n")
                f.write("-" * 80 + "\n\n")
        
        print(f"Saved TXT: {txt_file}")

def main():
    print("\nStarting Benchmark Suite...")
    
    # Check if sequential executable exists
    seq_exe = Path("../build/sequential_counter.exe")
    if not seq_exe.exists():
        seq_exe = Path("../build/sequential_counter")
    
    if not seq_exe.exists():
        print("\nError: Sequential executable not found!")
        print("   Please compile the sequential version first:")
        print("\n   Windows (PowerShell):")
        print("   .\\scripts\\build.ps1")
        print("\n   Linux/macOS:")
        print("   ./scripts/build.sh")
        print("\n   Or manually:")
        print("   g++ -std=c++17 -O3 -o build/sequential_counter src/sequential/*.cpp")
        return
    
    print(f"Found executable: {seq_exe}")
    
    runner = BenchmarkRunner()
    runner.run_all_benchmarks(runs_per_test=5)

if __name__ == "__main__":
    main()
