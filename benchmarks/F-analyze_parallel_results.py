#!/usr/bin/env python3
"""
Parallel Performance Analyzer and Visualizer
Generates comprehensive performance graphs and analysis tables
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import sys

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10

def load_latest_results():
    """Load the most recent benchmark results"""
    results_dir = Path("benchmarks/results")
    json_files = list(results_dir.glob("parallel_benchmark_*.json"))
    
    if not json_files:
        print("❌ No benchmark results found!")
        return None
    
    # Get the most recent file
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"📂 Loading: {latest_file}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data

def create_speedup_plots(df_par, df_seq):
    """Create speedup vs threads plots for each dataset and sync method"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Speedup vs Thread Count (by Dataset and Sync Method)', 
                 fontsize=16, fontweight='bold')
    
    datasets = sorted(df_par['dataset'].unique())
    sync_methods = sorted(df_par['sync_method'].unique())
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx // 2, idx % 2]
        
        # Get sequential baseline
        seq_time = df_seq[df_seq['dataset'] == dataset]['mean_time'].iloc[0]
        
        for sync in sync_methods:
            data = df_par[(df_par['dataset'] == dataset) & 
                         (df_par['sync_method'] == sync)]
            threads = data['threads']
            speedup = data['speedup']
            
            ax.plot(threads, speedup, marker='o', linewidth=2, 
                   markersize=8, label=sync.capitalize())
        
        # Add ideal speedup line
        max_threads = df_par['threads'].max()
        ideal_threads = np.arange(1, max_threads + 1)
        ax.plot(ideal_threads, ideal_threads, 'k--', alpha=0.5, 
               label='Ideal (Linear)')
        
        ax.set_xlabel('Number of Threads', fontweight='bold')
        ax.set_ylabel('Speedup', fontweight='bold')
        ax.set_title(f'{Path(dataset).stem}', fontweight='bold')
        ax.legend(frameon=True, shadow=True)
        ax.grid(True, alpha=0.3)
        ax.set_xticks([1, 2, 4, 8])
    
    plt.tight_layout()
    plt.savefig('benchmarks/results/speedup_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: speedup_analysis.png")
    plt.close()

def create_efficiency_plots(df_par):
    """Create efficiency vs threads plots"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Parallel Efficiency vs Thread Count', 
                 fontsize=16, fontweight='bold')
    
    datasets = sorted(df_par['dataset'].unique())
    sync_methods = sorted(df_par['sync_method'].unique())
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx // 2, idx % 2]
        
        for sync in sync_methods:
            data = df_par[(df_par['dataset'] == dataset) & 
                         (df_par['sync_method'] == sync)]
            threads = data['threads']
            efficiency = data['efficiency']
            
            ax.plot(threads, efficiency, marker='s', linewidth=2, 
                   markersize=8, label=sync.capitalize())
        
        # Add 100% efficiency line
        ax.axhline(y=100, color='k', linestyle='--', alpha=0.5, label='Ideal (100%)')
        
        ax.set_xlabel('Number of Threads', fontweight='bold')
        ax.set_ylabel('Efficiency (%)', fontweight='bold')
        ax.set_title(f'{Path(dataset).stem}', fontweight='bold')
        ax.legend(frameon=True, shadow=True)
        ax.grid(True, alpha=0.3)
        ax.set_xticks([1, 2, 4, 8])
        ax.set_ylim([0, 120])
    
    plt.tight_layout()
    plt.savefig('benchmarks/results/efficiency_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: efficiency_analysis.png")
    plt.close()

def create_sync_comparison(df_par):
    """Compare synchronization methods across datasets"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Execution Time Comparison: Synchronization Methods', 
                 fontsize=16, fontweight='bold')
    
    datasets = sorted(df_par['dataset'].unique())
    thread_counts = sorted(df_par['threads'].unique())
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx // 2, idx % 2]
        
        data = df_par[df_par['dataset'] == dataset]
        
        # Prepare data for grouped bar chart
        sync_methods = sorted(data['sync_method'].unique())
        x = np.arange(len(thread_counts))
        width = 0.25
        
        for i, sync in enumerate(sync_methods):
            times = []
            for threads in thread_counts:
                time_val = data[(data['threads'] == threads) & 
                               (data['sync_method'] == sync)]['mean_time'].values
                times.append(time_val[0] if len(time_val) > 0 else 0)
            
            ax.bar(x + i*width, times, width, label=sync.capitalize(), alpha=0.8)
        
        ax.set_xlabel('Number of Threads', fontweight='bold')
        ax.set_ylabel('Execution Time (ms)', fontweight='bold')
        ax.set_title(f'{Path(dataset).stem}', fontweight='bold')
        ax.set_xticks(x + width)
        ax.set_xticklabels(thread_counts)
        ax.legend(frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('benchmarks/results/sync_method_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: sync_method_comparison.png")
    plt.close()

def create_scalability_plot(df_par, df_seq):
    """Create strong scalability plot"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Use 100MB dataset for scalability analysis
    dataset = 'data/test_100mb.txt'
    sync = 'reduction'  # Best performing method
    
    data = df_par[(df_par['dataset'] == dataset) & 
                 (df_par['sync_method'] == sync)]
    seq_time = df_seq[df_seq['dataset'] == dataset]['mean_time'].iloc[0]
    
    threads = data['threads'].values
    times = data['mean_time'].values
    speedup = data['speedup'].values
    
    # Plot execution time
    ax.plot(threads, times, 'bo-', linewidth=2, markersize=10, label='Parallel Time')
    ax.axhline(y=seq_time, color='r', linestyle='--', linewidth=2, label='Sequential Time')
    
    # Add ideal speedup curve
    ideal_times = [seq_time / t for t in threads]
    ax.plot(threads, ideal_times, 'g--', linewidth=2, alpha=0.7, label='Ideal Parallel')
    
    ax.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Strong Scalability Analysis (100MB Dataset, Reduction)', 
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, frameon=True, shadow=True)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(threads)
    
    # Add speedup annotations
    for t, time, sp in zip(threads, times, speedup):
        ax.annotate(f'{sp:.2f}x', xy=(t, time), xytext=(5, 10), 
                   textcoords='offset points', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('benchmarks/results/scalability_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: scalability_analysis.png")
    plt.close()

def generate_performance_table(df_par, df_seq):
    """Generate LaTeX-formatted performance table"""
    output = []
    output.append("% Performance Summary Table - Copy to LaTeX document\n")
    output.append("\\begin{table}[h]")
    output.append("\\centering")
    output.append("\\caption{Parallel Performance Summary}")
    output.append("\\small")
    output.append("\\begin{tabular}{|l|r|l|r|r|r|}")
    output.append("\\hline")
    output.append("\\textbf{Dataset} & \\textbf{Threads} & \\textbf{Sync} & "
                 "\\textbf{Time (ms)} & \\textbf{Speedup} & \\textbf{Efficiency} \\\\")
    output.append("\\hline")
    
    for dataset in sorted(df_par['dataset'].unique()):
        # Add sequential baseline
        seq = df_seq[df_seq['dataset'] == dataset].iloc[0]
        output.append(f"{Path(dataset).stem} & 1 & Sequential & "
                     f"{seq['mean_time']:.2f} & 1.00x & 100.0\\% \\\\")
        
        # Add parallel results (only best results for each thread count)
        for threads in sorted(df_par['threads'].unique()):
            # Get best sync method for this configuration
            data = df_par[(df_par['dataset'] == dataset) & 
                         (df_par['threads'] == threads)]
            best = data.loc[data['speedup'].idxmax()]
            
            output.append(f" & {threads} & {best['sync_method'].capitalize()} & "
                         f"{best['mean_time']:.2f} & {best['speedup']:.2f}x & "
                         f"{best['efficiency']:.1f}\\% \\\\")
        
        output.append("\\hline")
    
    output.append("\\end{tabular}")
    output.append("\\end{table}")
    
    table_file = "benchmarks/results/performance_table.tex"
    with open(table_file, 'w') as f:
        f.write('\n'.join(output))
    
    print(f"✅ Saved: {table_file}")
    return '\n'.join(output)

def print_summary_statistics(df_par, df_seq):
    """Print summary statistics"""
    print("\n" + "="*80)
    print(" PERFORMANCE SUMMARY STATISTICS")
    print("="*80)
    
    # Best overall speedup
    best = df_par.loc[df_par['speedup'].idxmax()]
    print(f"\n🏆 Best Speedup: {best['speedup']:.2f}x")
    print(f"   Configuration: {Path(best['dataset']).stem}, "
          f"{best['threads']} threads, {best['sync_method']}")
    print(f"   Efficiency: {best['efficiency']:.1f}%")
    
    # Average speedup by thread count
    print(f"\n📊 Average Speedup by Thread Count:")
    for threads in sorted(df_par['threads'].unique()):
        avg_speedup = df_par[df_par['threads'] == threads]['speedup'].mean()
        avg_eff = df_par[df_par['threads'] == threads]['efficiency'].mean()
        print(f"   {threads} threads: {avg_speedup:.2f}x speedup, {avg_eff:.1f}% efficiency")
    
    # Best sync method
    print(f"\n⚡ Average Performance by Sync Method:")
    for sync in sorted(df_par['sync_method'].unique()):
        avg_speedup = df_par[df_par['sync_method'] == sync]['speedup'].mean()
        avg_eff = df_par[df_par['sync_method'] == sync]['efficiency'].mean()
        print(f"   {sync.capitalize()}: {avg_speedup:.2f}x speedup, {avg_eff:.1f}% efficiency")
    
    print("\n" + "="*80)

def main():
    print("\n" + "="*80)
    print(" PARALLEL PERFORMANCE ANALYZER")
    print("="*80)
    
    # Load results
    data = load_latest_results()
    if not data:
        return 1
    
    # Convert to DataFrames
    df_seq = pd.DataFrame(data['sequential_baseline'])
    df_par = pd.DataFrame(data['parallel_results'])
    
    print(f"\n📈 Analyzing {len(df_par)} parallel configurations...")
    print(f"   Datasets: {len(df_seq)}")
    print(f"   Thread counts: {sorted(df_par['threads'].unique())}")
    print(f"   Sync methods: {sorted(df_par['sync_method'].unique())}")
    
    # Generate visualizations
    print("\n🎨 Generating visualizations...")
    create_speedup_plots(df_par, df_seq)
    create_efficiency_plots(df_par)
    create_sync_comparison(df_par)
    create_scalability_plot(df_par, df_seq)
    
    # Generate LaTeX table
    print("\n📝 Generating LaTeX table...")
    generate_performance_table(df_par, df_seq)
    
    # Print summary
    print_summary_statistics(df_par, df_seq)
    
    print("\n✅ Analysis complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
