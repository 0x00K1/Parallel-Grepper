"""
Performance Analysis and Visualization
======================================
Analyzes benchmark results and generates performance visualizations.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

class PerformanceAnalyzer:
    def __init__(self, results_dir="benchmarks/results"):
        # Get absolute path relative to this script
        script_dir = Path(__file__).parent.absolute()
        self.results_dir = (script_dir / "results").resolve()
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def load_latest_results(self):
        """Load the most recent benchmark results"""
        json_files = sorted(self.results_dir.glob("benchmark_results_*.json"))
        
        if not json_files:
            print("No benchmark results found!")
            return None
        
        latest_file = json_files[-1]
        print(f"Loading results from: {latest_file.name}")
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        return pd.DataFrame(data)
    
    def analyze_sequential_performance(self, df):
        """Analyze sequential implementation performance"""
        print("\n" + "="*60)
        print("  SEQUENTIAL PERFORMANCE ANALYSIS")
        print("="*60)
        
        for _, row in df.iterrows():
            print(f"\nFile: {row['filename']} ({row['file_size_mb']:.2f} MB)")
            print(f"   Total Words:    {row['total_words']:,}")
            print(f"   Unique Words:   {row['unique_words']:,}")
            print(f"   Mean Time:      {row['mean_time']:.2f} ms ({row['mean_time']/1000:.4f} s)")
            print(f"   Median Time:    {row['median_time']:.2f} ms")
            print(f"   Std Deviation:  {row['std_dev']:.2f} ms")
            print(f"   Min Time:       {row['min_time']:.2f} ms")
            print(f"   Max Time:       {row['max_time']:.2f} ms")
            
            # Calculate throughput
            throughput_mb_s = row['file_size_mb'] / (row['mean_time'] / 1000)
            throughput_words_s = row['total_words'] / (row['mean_time'] / 1000)
            
            print(f"   Throughput:     {throughput_mb_s:.2f} MB/s")
            print(f"                   {throughput_words_s:,.0f} words/s")
    
    def plot_execution_time_vs_file_size(self, df, output_file="performance_analysis.png"):
        """Plot execution time vs file size"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Sequential Word Counter Performance Analysis', 
                     fontsize=16, fontweight='bold')
        
        # 1. Execution Time vs File Size
        ax1 = axes[0, 0]
        ax1.plot(df['file_size_mb'], df['mean_time'], 'o-', linewidth=2, markersize=8)
        ax1.fill_between(df['file_size_mb'], 
                         df['mean_time'] - df['std_dev'],
                         df['mean_time'] + df['std_dev'],
                         alpha=0.3)
        ax1.set_xlabel('File Size (MB)', fontsize=12)
        ax1.set_ylabel('Execution Time (ms)', fontsize=12)
        ax1.set_title('Execution Time vs File Size', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 2. Throughput (MB/s)
        ax2 = axes[0, 1]
        throughput = df['file_size_mb'] / (df['mean_time'] / 1000)
        ax2.bar(df['filename'], throughput, color='steelblue', alpha=0.7)
        ax2.set_xlabel('Dataset', fontsize=12)
        ax2.set_ylabel('Throughput (MB/s)', fontsize=12)
        ax2.set_title('Processing Throughput', fontsize=13, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Word Processing Rate
        ax3 = axes[1, 0]
        word_rate = df['total_words'] / (df['mean_time'] / 1000)
        ax3.bar(df['filename'], word_rate, color='forestgreen', alpha=0.7)
        ax3.set_xlabel('Dataset', fontsize=12)
        ax3.set_ylabel('Words Processed per Second', fontsize=12)
        ax3.set_title('Word Processing Rate', fontsize=13, fontweight='bold')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Format y-axis with comma separator
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        
        # 4. Variance Analysis
        ax4 = axes[1, 1]
        x_pos = np.arange(len(df))
        ax4.bar(x_pos, df['mean_time'], yerr=df['std_dev'], 
                capsize=5, color='coral', alpha=0.7)
        ax4.set_xlabel('Dataset', fontsize=12)
        ax4.set_ylabel('Execution Time (ms)', fontsize=12)
        ax4.set_title('Execution Time with Standard Deviation', fontsize=13, fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(df['filename'], rotation=45, ha='right')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        output_path = self.results_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\nSaved visualization: {output_path}")
        
        return output_path
    
    def generate_summary_report(self, df, output_file="performance_summary.txt"):
        """Generate a text summary report"""
        output_path = self.results_dir / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("  PERFORMANCE SUMMARY REPORT\n")
            f.write("  Sequential Word Frequency Counter\n")
            f.write("="*80 + "\n\n")
            
            # Overall statistics
            f.write("OVERALL STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Total datasets tested: {len(df)}\n")
            f.write(f"File size range: {df['file_size_mb'].min():.2f} MB - {df['file_size_mb'].max():.2f} MB\n")
            f.write(f"Total words processed: {df['total_words'].sum():,}\n")
            f.write(f"Average execution time: {df['mean_time'].mean():.2f} ms\n\n")
            
            # Performance metrics
            f.write("PERFORMANCE METRICS\n")
            f.write("-"*80 + "\n")
            
            for _, row in df.iterrows():
                throughput_mb_s = row['file_size_mb'] / (row['mean_time'] / 1000)
                throughput_words_s = row['total_words'] / (row['mean_time'] / 1000)
                
                f.write(f"\nDataset: {row['filename']}\n")
                f.write(f"  File Size:        {row['file_size_mb']:.2f} MB\n")
                f.write(f"  Total Words:      {row['total_words']:,}\n")
                f.write(f"  Unique Words:     {row['unique_words']:,}\n")
                f.write(f"  Execution Time:   {row['mean_time']:.2f} ± {row['std_dev']:.2f} ms\n")
                f.write(f"  Throughput:       {throughput_mb_s:.2f} MB/s\n")
                f.write(f"  Word Rate:        {throughput_words_s:,.0f} words/s\n")
            
            # Key insights
            f.write("\n" + "="*80 + "\n")
            f.write("KEY INSIGHTS\n")
            f.write("="*80 + "\n")
            
            # Calculate scaling
            if len(df) > 1:
                first_row = df.iloc[0]
                last_row = df.iloc[-1]
                
                size_ratio = last_row['file_size_mb'] / first_row['file_size_mb']
                time_ratio = last_row['mean_time'] / first_row['mean_time']
                
                f.write(f"\n1. SCALABILITY:\n")
                f.write(f"   - File size increased by {size_ratio:.2f}x\n")
                f.write(f"   - Execution time increased by {time_ratio:.2f}x\n")
                f.write(f"   - Scaling efficiency: {(size_ratio/time_ratio)*100:.1f}%\n")
            
            f.write(f"\n2. BOTTLENECKS (Most Time-Consuming):\n")
            f.write(f"   - File I/O: Reading large text files sequentially\n")
            f.write(f"   - String processing: Tokenization and normalization\n")
            f.write(f"   - Hash map operations: Insertions and updates\n")
            
            f.write(f"\n3. PARALLELIZATION OPPORTUNITIES:\n")
            f.write(f"   ✓ Text chunking: Divide file into independent segments\n")
            f.write(f"   ✓ Word counting: Parallel processing of chunks\n")
            f.write(f"   ✓ Hash map merging: Combine local results\n")
            
            f.write(f"\n4. EXPECTED PARALLEL IMPROVEMENTS:\n")
            f.write(f"   - With 4 threads: ~3-3.5x speedup expected\n")
            f.write(f"   - With 8 threads: ~6-7x speedup expected\n")
            f.write(f"   - Amdahl's Law applies due to merge overhead\n")
        
        print(f"Saved summary report: {output_path}")
        return output_path

def main():
    print("\nStarting Performance Analysis...")
    
    analyzer = PerformanceAnalyzer()
    
    # Load results
    df = analyzer.load_latest_results()
    
    if df is None or df.empty:
        print("\nNo data to analyze!")
        print("   Please run benchmarks first: python run_benchmarks.py")
        return
    
    # Analyze performance
    analyzer.analyze_sequential_performance(df)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    analyzer.plot_execution_time_vs_file_size(df)
    
    # Generate summary report
    print("\nGenerating summary report...")
    analyzer.generate_summary_report(df)
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
