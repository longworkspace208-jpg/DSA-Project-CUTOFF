#!/usr/bin/env python3
"""
scripts/plot.py
Publication-grade Plotting Script for Java Sorting Cutoff Experiment (GATE 10).
STRICTLY READS FROM CSV FILES ONLY (Rule 1: No fabricated numbers).
Outputs both PNG (200 dpi) and SVG to results/figures/:
- F1: Normalized time vs m, each N a line, shaded area = 95% CI, 4 algorithm panels, marking 7, 8, 10 and optimal m.
- F2: Normalized time vs m across distributions.
- F3: Merge vs Quick overlaid (normalized).
- F4: Heatmap m x N (% improvement) for each algorithm.
- F5: Raw sample boxplot at representative points.
- F6: Comparisons and exchanges vs m (from counts.csv).
- F7: Flat region bounds across N and distributions.
- F8: Tier A vs Tier B direct comparison.
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Colorblind-friendly palette
CB_COLORS = [
    "#0072B2", # Blue
    "#D55E00", # Vermilion / Red-Orange
    "#009E73", # Bluish Green
    "#CC79A7", # Reddish Purple
    "#E69F00", # Orange
    "#56B4E9", # Sky Blue
    "#F0E442", # Yellow
    "#000000"  # Black
]

def setup_matplotlib():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 8.5,
        "figure.titlesize": 13,
        "figure.autolayout": False,
        "lines.linewidth": 1.75,
        "lines.markersize": 6,
        "axes.grid": True,
        "grid.alpha": 0.35,
        "grid.linestyle": "--",
        "figure.dpi": 200
    })

def save_fig(fig, base_path):
    os.makedirs(os.path.dirname(base_path), exist_ok=True)
    fig.savefig(f"{base_path}.png", dpi=200, bbox_inches="tight")
    fig.savefig(f"{base_path}.svg", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {base_path}.png & .svg")

def generate_all_plots(raw_csv="results/raw.csv", counts_csv="results/counts.csv",
                       tables_dir="results/tables", figures_dir="results/figures"):
    setup_matplotlib()
    os.makedirs(figures_dir, exist_ok=True)

    summary_csv = os.path.join(tables_dir, "per_point_summary.csv")
    optimal_csv = os.path.join(tables_dir, "optimal_and_flat_regions.csv")

    if not os.path.isfile(summary_csv) or not os.path.isfile(optimal_csv):
        print(f"[WARN] Summary tables not found in {tables_dir}. Run scripts/analyze.py first.")
        import subprocess
        subprocess.run([sys.executable, "scripts/analyze.py"], check=True)

    df_pts = pd.read_csv(summary_csv)
    df_opt = pd.read_csv(optimal_csv)
    df_raw = pd.read_csv(raw_csv)
    df_raw["time_ms"] = df_raw["time_ns_per_sort"] / 1e6

    print("\n" + "=" * 80)
    print("GENERATING PUBLICATION FIGURES (F1 - F8)")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # F1: Normalized time vs m, each N a line, shaded = 95% CI, 4 algorithm panels
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True, sharey=True)
    algos = ["MergeCutoff", "MergeXParam", "QuickCutoff", "QuickXParam"]
    sizes = sorted(df_pts["N"].unique())

    for idx, algo in enumerate(algos):
        ax = axes[idx // 2, idx % 2]
        sub = df_pts[(df_pts["algo"] == algo) & (df_pts["dist"] == "random")]

        for s_idx, n in enumerate(sizes):
            n_sub = sub[sub["N"] == n].sort_values(by="m")
            if n_sub.empty:
                continue
            # Normalize by min median for this N
            min_med = n_sub["median_ms"].min()
            if min_med <= 0:
                continue
            y_norm = n_sub["median_ms"] / min_med
            ci_low_norm = n_sub["ci95_low_ms"] / min_med
            ci_high_norm = n_sub["ci95_high_ms"] / min_med

            color = CB_COLORS[s_idx % len(CB_COLORS)]
            ax.plot(n_sub["m"], y_norm, marker="o", label=f"N = {n:,}", color=color)
            ax.fill_between(n_sub["m"], ci_low_norm, ci_high_norm, color=color, alpha=0.15)

        # Reference lines m = 7, 8, 10
        for ref_m in [7, 8, 10]:
            ax.axvline(x=ref_m, color="gray", linestyle=":", alpha=0.6)

        # Mark optimal m*
        algo_opts = df_opt[(df_opt["algo"] == algo) & (df_opt["dist"] == "random")]
        if not algo_opts.empty:
            med_opt_m = int(algo_opts["optimal_m"].median())
            ax.axvline(x=med_opt_m, color="red", linestyle="--", alpha=0.75, label=f"Optimal m* ≈ {med_opt_m}")

        ax.set_title(f"{algo} (Random Distribution)", fontweight="bold")
        ax.set_xlabel("Cutoff Parameter m (Subarray Length)")
        ax.set_ylabel("Normalized Sort Time (T / T_min)")
        ax.set_ylim(0.95, 1.45)
        ax.legend(loc="upper right")

    fig.suptitle("F1: Normalized Sort Time vs Cutoff m across Problem Sizes (95% CI Bands)", fontsize=13, fontweight="bold", y=0.99)
    fig.tight_layout()
    save_fig(fig, os.path.join(figures_dir, "F1_normalized_time_vs_m"))

    # -------------------------------------------------------------------------
    # F2: Normalized time vs m across distributions (MergeCutoff, N=100,000)
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    target_n = 100000
    for a_idx, target_algo in enumerate(["MergeCutoff", "QuickCutoff"]):
        ax = axes[a_idx]
        sub = df_pts[(df_pts["algo"] == target_algo) & (df_pts["N"] == target_n)]
        dists = sub["dist"].unique()

        for d_idx, dist in enumerate(dists):
            d_sub = sub[sub["dist"] == dist].sort_values(by="m")
            min_med = d_sub["median_ms"].min()
            if min_med <= 0:
                continue
            y_norm = d_sub["median_ms"] / min_med
            color = CB_COLORS[d_idx % len(CB_COLORS)]
            ax.plot(d_sub["m"], y_norm, marker="s", label=f"{dist}", color=color)
            ax.fill_between(d_sub["m"], d_sub["ci95_low_ms"]/min_med, d_sub["ci95_high_ms"]/min_med, color=color, alpha=0.12)

        for ref_m in [7, 8, 10]:
            ax.axvline(x=ref_m, color="gray", linestyle=":", alpha=0.6)

        ax.set_title(f"{target_algo} (N = {target_n:,})", fontweight="bold")
        ax.set_xlabel("Cutoff Parameter m")
        ax.set_ylabel("Normalized Sort Time (T / T_min)")
        ax.legend(loc="upper right")

    fig.suptitle("F2: Cutoff Sensitivity across Data Distributions (N = 100,000)", fontsize=13, fontweight="bold", y=0.99)
    fig.tight_layout()
    save_fig(fig, os.path.join(figures_dir, "F2_distributions_vs_m"))

    # -------------------------------------------------------------------------
    # F3: Merge vs Quick overlaid (Normalized)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sub_mq = df_pts[(df_pts["N"] == target_n) & (df_pts["dist"] == "random")]

    for idx, algo in enumerate(["MergeCutoff", "QuickCutoff"]):
        a_sub = sub_mq[sub_mq["algo"] == algo].sort_values(by="m")
        min_med = a_sub["median_ms"].min()
        y_norm = a_sub["median_ms"] / min_med
        color = CB_COLORS[idx]
        ax.plot(a_sub["m"], y_norm, marker="o" if idx==0 else "^", label=f"{algo} (Random, N={target_n:,})", color=color, linewidth=2.2)
        ax.fill_between(a_sub["m"], a_sub["ci95_low_ms"]/min_med, a_sub["ci95_high_ms"]/min_med, color=color, alpha=0.18)

    ax.axvline(x=7, color="#0072B2", linestyle=":", alpha=0.8, label="Merge Reference (m=7)")
    ax.axvline(x=8, color="#D55E00", linestyle=":", alpha=0.8, label="Quick Reference (m=8)")
    ax.set_title("F3: Mergesort vs Quicksort Cutoff Curves Comparison (Overlaid)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Cutoff Parameter m (Subarray Length)")
    ax.set_ylabel("Normalized Sort Time (T / T_min)")
    ax.legend(loc="upper right")
    fig.tight_layout()
    save_fig(fig, os.path.join(figures_dir, "F3_merge_vs_quick_overlaid"))

    # -------------------------------------------------------------------------
    # F4: Heatmap m x N (% improvement over baseline) for each algorithm
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for idx, algo in enumerate(algos):
        ax = axes[idx // 2, idx % 2]
        sub = df_pts[(df_pts["algo"] == algo) & (df_pts["dist"] == "random")]
        # Pivot table: rows = m, columns = N, values = impr_vs_m1_pct or impr_vs_m0_pct
        impr_col = "impr_vs_m0_pct" if sub["impr_vs_m0_pct"].notna().sum() > 0 else "impr_vs_m1_pct"
        pvt = sub.pivot(index="m", columns="N", values=impr_col)

        c = ax.imshow(pvt.values, cmap="YlGnBu", aspect="auto", origin="lower")
        ax.set_xticks(range(len(pvt.columns)))
        ax.set_xticklabels([f"{col:,}" for col in pvt.columns], rotation=25)
        ax.set_yticks(range(len(pvt.index)))
        ax.set_yticklabels(pvt.index)

        # Annotate text
        for i in range(len(pvt.index)):
            for j in range(len(pvt.columns)):
                val = pvt.values[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f"{val:+.1f}%", ha="center", va="center", color="white" if val > 12 else "black", fontsize=8)

        ax.set_title(f"{algo} Speedup % over Baseline", fontweight="bold")
        ax.set_xlabel("Problem Size N")
        ax.set_ylabel("Cutoff m")
        fig.colorbar(c, ax=ax, label="% Improvement")

    fig.suptitle("F4: Speedup % Heatmap across Cutoff m and Problem Size N (Random)", fontsize=13, fontweight="bold", y=0.99)
    fig.tight_layout()
    save_fig(fig, os.path.join(figures_dir, "F4_heatmap_m_x_N"))

    # -------------------------------------------------------------------------
    # F5: Raw sample boxplot at representative cutoff points (N=100,000, random)
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    rep_cutoffs = [0, 4, 8, 16, 32]
    for a_idx, target_algo in enumerate(["MergeCutoff", "QuickCutoff"]):
        ax = axes[a_idx]
        sub_raw = df_raw[(df_raw["algo"] == target_algo) & (df_raw["N"] == target_n) & (df_raw["dist"] == "random") & (df_raw["m"].isin(rep_cutoffs))]

        data_to_plot = [sub_raw[sub_raw["m"] == m]["time_ms"].values for m in rep_cutoffs]
        ax.boxplot(data_to_plot, tick_labels=[f"m={m}" for m in rep_cutoffs], patch_artist=True,
                   boxprops=dict(facecolor="#56B4E9", alpha=0.6), medianprops=dict(color="red", linewidth=2))

        ax.set_title(f"{target_algo} Raw Sample Distributions (N = {target_n:,})", fontweight="bold")
        ax.set_xlabel("Cutoff Parameter m")
        ax.set_ylabel("Execution Time (ms/sort)")

    fig.suptitle("F5: Raw Timing Distributions and Outlier Inspection (Boxplots)", fontsize=13, fontweight="bold", y=0.99)
    fig.tight_layout()
    save_fig(fig, os.path.join(figures_dir, "F5_boxplot_raw_samples"))

    # -------------------------------------------------------------------------
    # F6: Comparisons and exchanges vs m (from counts.csv)
    # -------------------------------------------------------------------------
    if os.path.isfile(counts_csv):
        df_cnt = pd.read_csv(counts_csv)
        cnt_sub = df_cnt[(df_cnt["N"] == 100000) & (df_cnt["dist"] == "random")]
        if not cnt_sub.empty:
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            for a_idx, target_algo in enumerate(["MergeCutoff", "QuickCutoff"]):
                ax1 = axes[a_idx]
                a_cnt = cnt_sub[cnt_sub["algo"] == target_algo].sort_values(by="m")
                ax2 = ax1.twinx()

                l1 = ax1.plot(a_cnt["m"], a_cnt["compares"] / 1e6, color="#0072B2", marker="o", label="Comparisons (M)")
                l2 = ax2.plot(a_cnt["m"], a_cnt["insertion_exchanges"] / 1e3, color="#D55E00", marker="s", linestyle="--", label="Insertion Exchanges (k)")

                ax1.set_xlabel("Cutoff Parameter m")
                ax1.set_ylabel("Comparisons (Millions)", color="#0072B2")
                ax2.set_ylabel("Insertion Exchanges (Thousands)", color="#D55E00")
                ax1.set_title(f"{target_algo} Operations vs Cutoff m (N = 100,000)", fontweight="bold")

                lines = l1 + l2
                ax1.legend(lines, [l.get_label() for l in lines], loc="center right")

            fig.suptitle("F6: Theoretical Operation Counting: Comparisons vs Insertion Exchanges", fontsize=13, fontweight="bold", y=0.99)
            fig.tight_layout()
            save_fig(fig, os.path.join(figures_dir, "F6_operations_vs_m"))

    # -------------------------------------------------------------------------
    # F7: Flat region bounds across N and distributions
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5.5))
    df_opt_random = df_opt[df_opt["dist"] == "random"].copy()
    y_pos = 0
    y_ticks = []
    y_labels = []

    for algo in algos:
        sub_opt = df_opt_random[df_opt_random["algo"] == algo].sort_values(by="N")
        for _, r in sub_opt.iterrows():
            f_min = r["flat_region_min"]
            f_max = r["flat_region_max"]
            f_star = r["optimal_m"]
            color = CB_COLORS[algos.index(algo)]

            ax.barh(y_pos, f_max - f_min, left=f_min, height=0.45, color=color, alpha=0.35)
            ax.plot([f_star], [y_pos], marker="d", color=color, markersize=8)
            y_ticks.append(y_pos)
            y_labels.append(f"{algo} (N={r['N']:,})")
            y_pos += 1

    ax.axvline(x=7, color="gray", linestyle=":", label="m=7 (Princeton MergeX)")
    ax.axvline(x=8, color="gray", linestyle="--", label="m=8 (Princeton QuickX)")
    ax.axvline(x=10, color="gray", linestyle="-.", label="m=10 (Textbook)")
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=8)
    ax.set_xlabel("Cutoff Parameter m (Optimal Point & Flat Region Span)")
    ax.set_title("F7: Flat Regions (Within 2% or CI Overlap) and Optimal m* across N", fontsize=12, fontweight="bold")
    ax.legend(loc="upper right")
    fig.tight_layout()
    save_fig(fig, os.path.join(figures_dir, "F7_flat_regions_span"))

    # -------------------------------------------------------------------------
    # F8: Tier A vs Tier B Comparison (MergeCutoff vs MergeXParam, QuickCutoff vs QuickXParam)
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    pairs = [
        ("MergeCutoff (Tier A)", "MergeXParam (Tier B)", "Merge"),
        ("QuickCutoff (Tier A)", "QuickXParam (Tier B)", "Quick")
    ]

    for p_idx, (name_a, name_b, prefix) in enumerate(pairs):
        ax = axes[p_idx]
        sub_a = df_pts[(df_pts["algo"].str.startswith(prefix)) & (df_pts["tier"] == "TierA") & (df_pts["N"] == target_n) & (df_pts["dist"] == "random")].sort_values(by="m")
        sub_b = df_pts[(df_pts["algo"].str.startswith(prefix)) & (df_pts["tier"] == "TierB") & (df_pts["N"] == target_n) & (df_pts["dist"] == "random")].sort_values(by="m")

        if not sub_a.empty and not sub_b.empty:
            ax.plot(sub_a["m"], sub_a["median_ms"], marker="o", label=name_a, color="#0072B2", linewidth=2.2)
            ax.fill_between(sub_a["m"], sub_a["ci95_low_ms"], sub_a["ci95_high_ms"], color="#0072B2", alpha=0.15)

            ax.plot(sub_b["m"], sub_b["median_ms"], marker="^", label=name_b, color="#D55E00", linewidth=2.2)
            ax.fill_between(sub_b["m"], sub_b["ci95_low_ms"], sub_b["ci95_high_ms"], color="#D55E00", alpha=0.15)

        for ref_m in [7, 8, 10]:
            ax.axvline(x=ref_m, color="gray", linestyle=":", alpha=0.5)

        ax.set_title(f"{prefix}Sort: Tier A vs Tier B (N = {target_n:,})", fontweight="bold")
        ax.set_xlabel("Cutoff Parameter m")
        ax.set_ylabel("Execution Time (ms/sort)")
        ax.legend()

    fig.suptitle("F8: Architectural Improvement: Tier A (Minimal) vs Tier B (Optimized Textbook)", fontsize=13, fontweight="bold", y=0.99)
    fig.tight_layout()
    save_fig(fig, os.path.join(figures_dir, "F8_tierA_vs_tierB"))

    print("[SUCCESS] All 8 publication figures (PNG 200dpi + SVG) generated successfully.")

def main():
    parser = argparse.ArgumentParser(description="Generate publication-grade figures (GATE 10)")
    parser.add_argument("--raw", default="results/raw.csv")
    parser.add_argument("--counts", default="results/counts.csv")
    parser.add_argument("--tables", default="results/tables")
    parser.add_argument("--figures", default="results/figures")
    args = parser.parse_args()

    generate_all_plots(args.raw, args.counts, args.tables, args.figures)

if __name__ == "__main__":
    main()
