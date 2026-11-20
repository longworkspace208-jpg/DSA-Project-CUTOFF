#!/usr/bin/env python3
"""
scripts/analyze_results.py
Statistical Analysis and Visualization for Java Sorting Cutoff Experiment.
- Analyzes results/raw.csv (or results/bench_raw.csv)
- Calculates per configuration (algo, dist, N, m):
  * Mean (ms)
  * Median (ms)
  * Standard Deviation (ms)
  * Speedup and % Improvement over baseline (m = 0 or m = 1)
- Identifies optimal cutoff m* for each (algo, dist, N)
- Generates publication-grade figures in results/figures/:
  1. cutoff_vs_time.png (Runtime curves vs m)
  2. cutoff_tradeoff.png (Trade-off curve: recursion reduction vs O(k^2) insertion sort)
  3. speedup_distributions.png (% improvement across distributions)
  4. theoretical_vs_empirical.png (Operation counts vs actual runtime)
- Outputs summary table to results/analysis_summary.csv and results/optimal_cutoffs.csv
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def analyze_benchmarks(raw_csv="results/raw.csv", counts_csv="results/counts.csv",
                       figures_dir="results/figures", out_summary="results/analysis_summary.csv",
                       out_optimal="results/optimal_cutoffs.csv"):
    if not os.path.isfile(raw_csv):
        print(f"[ERROR] Raw results file not found: {raw_csv}")
        return None

    os.makedirs(figures_dir, exist_ok=True)
    df = pd.read_csv(raw_csv)
    df["time_ms"] = df["time_ns_per_sort"] / 1e6

    # Summary statistics per (algo, tier, dist, N, m)
    summary_rows = []
    groups = df.groupby(["algo", "tier", "dist", "N", "m"])
    for (algo, tier, dist, n, m), grp in groups:
        times = grp["time_ms"].values
        mean_val = np.mean(times)
        std_val = np.std(times, ddof=1) if len(times) > 1 else 0.0
        median_val = np.median(times)
        q25, q75 = np.percentile(times, [25, 75])
        iqr_val = q75 - q25
        cv_pct = (std_val / mean_val) * 100.0 if mean_val > 0 else 0.0

        summary_rows.append({
            "algo": algo,
            "tier": tier,
            "dist": dist,
            "N": int(n),
            "m": int(m),
            "samples": len(times),
            "mean_ms": mean_val,
            "std_ms": std_val,
            "median_ms": median_val,
            "iqr_ms": iqr_val,
            "cv_pct": cv_pct
        })

    df_summary = pd.DataFrame(summary_rows)

    # Compute baseline and % improvement over baseline (m=0 or m=1)
    df_summary["baseline_median_ms"] = np.nan
    df_summary["improvement_pct"] = np.nan
    df_summary["speedup"] = np.nan

    optimal_rows = []
    for (algo, dist, n), grp in df_summary.groupby(["algo", "dist", "N"]):
        # Find baseline: m=0 if available, else min m
        if 0 in grp["m"].values:
            base_row = grp[grp["m"] == 0].iloc[0]
        else:
            base_row = grp[grp["m"] == grp["m"].min()].iloc[0]
        base_median = base_row["median_ms"]

        for idx in grp.index:
            cur_median = df_summary.loc[idx, "median_ms"]
            impr = ((base_median - cur_median) / base_median) * 100.0
            spd = base_median / cur_median if cur_median > 0 else 1.0
            df_summary.loc[idx, "baseline_median_ms"] = base_median
            df_summary.loc[idx, "improvement_pct"] = impr
            df_summary.loc[idx, "speedup"] = spd

        # Identify optimal m (lowest median time)
        best_row = grp.loc[grp["median_ms"].idxmin()]
        optimal_rows.append({
            "algo": algo,
            "tier": best_row["tier"],
            "dist": dist,
            "N": int(n),
            "optimal_m": int(best_row["m"]),
            "optimal_median_ms": best_row["median_ms"],
            "baseline_median_ms": base_median,
            "improvement_pct": ((base_median - best_row["median_ms"]) / base_median) * 100.0,
            "speedup": base_median / best_row["median_ms"] if best_row["median_ms"] > 0 else 1.0
        })

    df_optimal = pd.DataFrame(optimal_rows)

    # Save summary tables
    df_summary.to_csv(out_summary, index=False)
    df_optimal.to_csv(out_optimal, index=False)
    print(f"Saved analysis summary to: {out_summary}")
    print(f"Saved optimal cutoffs to: {out_optimal}")

    # Generate Figures
    generate_analysis_figures(df_summary, df_optimal, counts_csv, figures_dir)
    return df_summary, df_optimal

def generate_analysis_figures(df_summary, df_optimal, counts_csv, figures_dir):
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # Figure 1: Runtime vs Cutoff m for representative N=100,000 across algorithms (random dist)
    fig, ax = plt.subplots(figsize=(10, 6))
    sub = df_summary[(df_summary["N"] == 100000) & (df_summary["dist"] == "random")]
    for algo in sub["algo"].unique():
        algo_sub = sub[sub["algo"] == algo].sort_values(by="m")
        ax.plot(algo_sub["m"], algo_sub["median_ms"], marker="o", linewidth=2, label=algo)
        # Highlight minimum
        min_idx = algo_sub["median_ms"].idxmin()
        best_m = algo_sub.loc[min_idx, "m"]
        best_t = algo_sub.loc[min_idx, "median_ms"]
        ax.scatter([best_m], [best_t], s=120, zorder=5, edgecolors="red", facecolors="none", linewidth=2)
        ax.annotate(f"m*={best_m}", (best_m, best_t), textcoords="offset points", xytext=(0,10), ha="center", fontsize=9, fontweight="bold")

    ax.set_title("Execution Time vs Subarray Cutoff m (N = 100,000, Random)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Cutoff Parameter m (Insertion Sort Subarray Size)", fontsize=11)
    ax.set_ylabel("Median Execution Time (ms/sort)", fontsize=11)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "cutoff_vs_time.png"), dpi=200)
    plt.close()

    # Figure 2: % Improvement over Baseline vs Cutoff m (Trade-off Curve)
    fig, ax = plt.subplots(figsize=(10, 6))
    for algo in sub["algo"].unique():
        algo_sub = sub[sub["algo"] == algo].sort_values(by="m")
        ax.plot(algo_sub["m"], algo_sub["improvement_pct"], marker="s", linewidth=2, label=f"{algo} Speedup %")

    ax.axhline(y=0, color="black", linestyle="--", alpha=0.7, label="Baseline (No Cutoff)")
    ax.set_title("Cutoff Trade-off Curve: Speedup % vs Subarray Size m (N = 100,000)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Cutoff Parameter m", fontsize=11)
    ax.set_ylabel("% Performance Improvement over Baseline", fontsize=11)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "cutoff_tradeoff.png"), dpi=200)
    plt.close()

    # Figure 3: Optimal m and Speedup across Distributions (MergeCutoff at N=100,000)
    merge_dists = df_summary[(df_summary["algo"] == "MergeCutoff") & (df_summary["N"] == 100000)]
    if not merge_dists.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        dists = merge_dists["dist"].unique()
        for d in dists:
            d_sub = merge_dists[merge_dists["dist"] == d].sort_values(by="m")
            ax.plot(d_sub["m"], d_sub["improvement_pct"], marker="o", label=f"Dist: {d}")
        ax.axhline(y=0, color="gray", linestyle=":")
        ax.set_title("MergeCutoff Speedup % Across Data Distributions (N = 100,000)", fontsize=13, fontweight="bold")
        ax.set_xlabel("Cutoff Parameter m", fontsize=11)
        ax.set_ylabel("% Improvement over Baseline", fontsize=11)
        ax.legend(fontsize=9)
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "speedup_distributions.png"), dpi=200)
        plt.close()

    # Figure 4: Theoretical Operation Counts vs Empirical Runtime
    if os.path.isfile(counts_csv):
        df_cnt = pd.read_csv(counts_csv)
        cnt_sub = df_cnt[(df_cnt["algo"] == "MergeCutoff") & (df_cnt["N"] == 100000) & (df_cnt["dist"] == "random")]
        if not cnt_sub.empty and not sub[sub["algo"] == "MergeCutoff"].empty:
            merged = pd.merge(cnt_sub, sub[sub["algo"] == "MergeCutoff"], on="m")
            fig, ax1 = plt.subplots(figsize=(10, 5))
            ax2 = ax1.twinx()

            l1 = ax1.plot(merged["m"], merged["median_ms"], color="tab:blue", marker="o", linewidth=2, label="Measured Runtime (ms)")
            l2 = ax2.plot(merged["m"], merged["compares"] / 1e6, color="tab:orange", marker="^", linestyle="--", label="Total Comparisons (Millions)")
            l3 = ax2.plot(merged["m"], merged["array_writes"] / 1e6, color="tab:green", marker="s", linestyle=":", label="Total Array Writes (Millions)")

            ax1.set_xlabel("Cutoff Parameter m", fontsize=11)
            ax1.set_ylabel("Execution Time (ms)", color="tab:blue", fontsize=11)
            ax2.set_ylabel("Operation Counts (Millions)", color="tab:orange", fontsize=11)
            ax1.set_title("Theoretical Operations vs Measured Runtime (MergeCutoff, N=100,000)", fontsize=13, fontweight="bold")

            lines = l1 + l2 + l3
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc="upper center", fontsize=9)
            plt.tight_layout()
            plt.savefig(os.path.join(figures_dir, "theoretical_vs_empirical.png"), dpi=200)
            plt.close()

    print(f"Generated analysis figures in: {figures_dir}")

def main():
    parser = argparse.ArgumentParser(description="Statistical Analysis of Sorting Benchmark Results")
    parser.add_argument("--raw", default="results/raw.csv")
    parser.add_argument("--counts", default="results/counts.csv")
    parser.add_argument("--figures", default="results/figures")
    parser.add_argument("--summary", default="results/analysis_summary.csv")
    parser.add_argument("--optimal", default="results/optimal_cutoffs.csv")
    args = parser.parse_args()

    analyze_benchmarks(args.raw, args.counts, args.figures, args.summary, args.optimal)

if __name__ == "__main__":
    main()
