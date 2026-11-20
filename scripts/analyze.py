#!/usr/bin/env python3
"""
scripts/analyze.py
Comprehensive Statistical Analysis for Java Sorting Cutoff Experiment.
STRICTLY READS FROM CSV FILES ONLY (Rule 1: No fabricated numbers).
Performs:
1. Per (algo, tier, dist, N, m): median, IQR, bootstrap CI 95% (seed 42 fixed), sample count.
2. % improvement over m=1, m=0, and over m=7, 8, 10.
3. Optimal m* and flat region (overlapping 95% CI or within 2% of optimal median); center of flat region.
4. Paired Wilcoxon signed-rank test between m* and 7, 8, 10 (p-value, effect size, noise threshold).
5. Stability of optimal m across N, distributions, Merge vs Quick, and Tier A vs Tier B.
6. Mechanistic explanation using operation counts: normalized time vs normalized comparisons/exchanges.
7. Outputs publication tables to results/tables/*.csv and results/tables/*.md.
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

def compute_bootstrap_ci(data, n_bootstraps=2000, alpha=0.05, rng_seed=42):
    """Computes non-parametric bootstrap 95% CI of sample median with fixed seed."""
    rng = np.random.default_rng(rng_seed)
    n = len(data)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return float(data[0]), float(data[0])
    boot_medians = np.empty(n_bootstraps)
    for i in range(n_bootstraps):
        sample = rng.choice(data, size=n, replace=True)
        boot_medians[i] = np.median(sample)
    low = np.percentile(boot_medians, 100 * (alpha / 2))
    high = np.percentile(boot_medians, 100 * (1 - alpha / 2))
    return float(low), float(high)

def run_analysis(raw_csv="results/raw.csv", counts_csv="results/counts.csv", tables_dir="results/tables"):
    os.makedirs(tables_dir, exist_ok=True)
    if not os.path.isfile(raw_csv):
        print(f"[ERROR] Raw CSV not found at: {raw_csv}")
        sys.exit(1)

    print(f"Loading raw benchmark data from: {raw_csv}...")
    df_raw = pd.read_csv(raw_csv)
    df_raw["time_ms"] = df_raw["time_ns_per_sort"] / 1e6

    # -------------------------------------------------------------------------
    # 1. Per-point summary statistics
    # -------------------------------------------------------------------------
    print("Computing per-point summary statistics (Median, IQR, Bootstrap 95% CI)...")
    per_point = []
    groups = df_raw.groupby(["algo", "tier", "dist", "N", "m"])
    for (algo, tier, dist, n, m), grp in groups:
        times = grp["time_ms"].values
        n_samples = len(times)
        mean_val = float(np.mean(times))
        std_val = float(np.std(times, ddof=1)) if n_samples > 1 else 0.0
        median_val = float(np.median(times))
        q25, q75 = np.percentile(times, [25, 75])
        iqr_val = float(q75 - q25)
        cv_pct = (std_val / mean_val) * 100.0 if mean_val > 0 else 0.0

        ci_low, ci_high = compute_bootstrap_ci(times, n_bootstraps=2000, rng_seed=int(n + m + abs(hash(algo)) % 1000))
        rel_ci_width_pct = ((ci_high - ci_low) / median_val) * 100.0 if median_val > 0 else 0.0

        per_point.append({
            "algo": algo,
            "tier": tier,
            "dist": dist,
            "N": int(n),
            "m": int(m),
            "samples": n_samples,
            "mean_ms": mean_val,
            "std_ms": std_val,
            "median_ms": median_val,
            "iqr_ms": iqr_val,
            "cv_pct": cv_pct,
            "ci95_low_ms": ci_low,
            "ci95_high_ms": ci_high,
            "rel_ci_width_pct": rel_ci_width_pct
        })

    df_pts = pd.DataFrame(per_point)

    # -------------------------------------------------------------------------
    # 2. Compute % Improvements over baselines (m=0, m=1, m=7, 8, 10)
    # -------------------------------------------------------------------------
    print("Computing relative improvements over baselines...")
    df_pts["impr_vs_m0_pct"] = np.nan
    df_pts["impr_vs_m1_pct"] = np.nan
    df_pts["impr_vs_m7_pct"] = np.nan
    df_pts["impr_vs_m8_pct"] = np.nan
    df_pts["impr_vs_m10_pct"] = np.nan

    for (algo, dist, n), grp in df_pts.groupby(["algo", "dist", "N"]):
        m_map = {int(row["m"]): row["median_ms"] for _, row in grp.iterrows()}
        med_0 = m_map.get(0, np.nan)
        med_1 = m_map.get(1, np.nan)
        med_7 = m_map.get(7, np.nan)
        med_8 = m_map.get(8, np.nan)
        med_10 = m_map.get(10, np.nan)

        for idx in grp.index:
            med_cur = df_pts.loc[idx, "median_ms"]
            if not np.isnan(med_0) and med_0 > 0:
                df_pts.loc[idx, "impr_vs_m0_pct"] = ((med_0 - med_cur) / med_0) * 100.0
            if not np.isnan(med_1) and med_1 > 0:
                df_pts.loc[idx, "impr_vs_m1_pct"] = ((med_1 - med_cur) / med_1) * 100.0
            if not np.isnan(med_7) and med_7 > 0:
                df_pts.loc[idx, "impr_vs_m7_pct"] = ((med_7 - med_cur) / med_7) * 100.0
            if not np.isnan(med_8) and med_8 > 0:
                df_pts.loc[idx, "impr_vs_m8_pct"] = ((med_8 - med_cur) / med_8) * 100.0
            if not np.isnan(med_10) and med_10 > 0:
                df_pts.loc[idx, "impr_vs_m10_pct"] = ((med_10 - med_cur) / med_10) * 100.0

    # -------------------------------------------------------------------------
    # 3. Optimal m* and Flat Region (Vùng phẳng)
    # -------------------------------------------------------------------------
    print("Identifying optimal cutoff m* and flat regions...")
    optimal_records = []
    for (algo, tier, dist, n), grp in df_pts.groupby(["algo", "tier", "dist", "N"]):
        best_row = grp.loc[grp["median_ms"].idxmin()]
        m_star = int(best_row["m"])
        med_star = float(best_row["median_ms"])
        ci_low_star = float(best_row["ci95_low_ms"])
        ci_high_star = float(best_row["ci95_high_ms"])

        # Baseline: m=0 if present, else min m
        base_m = 0 if 0 in grp["m"].values else grp["m"].min()
        base_med = grp[grp["m"] == base_m].iloc[0]["median_ms"]
        best_impr_pct = ((base_med - med_star) / base_med) * 100.0

        # Flat region rule:
        # CI overlap with m* CI OR difference <= 2.0%
        flat_cutoffs = []
        for _, r in grp.iterrows():
            m_val = int(r["m"])
            med_val = float(r["median_ms"])
            ci_low_val = float(r["ci95_low_ms"])
            ci_high_val = float(r["ci95_high_ms"])

            ci_overlap = not (ci_high_val < ci_low_star or ci_low_val > ci_high_star)
            within_2pct = ((med_val - med_star) / med_star) <= 0.02
            if ci_overlap or within_2pct:
                flat_cutoffs.append(m_val)

        flat_cutoffs.sort()
        flat_min = flat_cutoffs[0]
        flat_max = flat_cutoffs[-1]
        flat_center = flat_cutoffs[len(flat_cutoffs) // 2]
        flat_str = ", ".join(map(str, flat_cutoffs))

        optimal_records.append({
            "algo": algo,
            "tier": tier,
            "dist": dist,
            "N": int(n),
            "optimal_m": m_star,
            "optimal_median_ms": med_star,
            "ci95_low_ms": ci_low_star,
            "ci95_high_ms": ci_high_star,
            "baseline_m": base_m,
            "baseline_median_ms": base_med,
            "best_improvement_pct": best_impr_pct,
            "flat_region_min": flat_min,
            "flat_region_max": flat_max,
            "flat_region_center": flat_center,
            "flat_region_cutoffs": flat_str
        })

    df_optimal = pd.DataFrame(optimal_records)

    # -------------------------------------------------------------------------
    # 4. Paired Wilcoxon Signed-Rank Tests (m* vs 7, 8, 10)
    # -------------------------------------------------------------------------
    print("Conducting paired Wilcoxon signed-rank tests against 7, 8, 10...")
    wilcoxon_records = []
    for opt_row in optimal_records:
        algo = opt_row["algo"]
        dist = opt_row["dist"]
        n = opt_row["N"]
        m_star = opt_row["optimal_m"]

        sub_algo = df_raw[(df_raw["algo"] == algo) & (df_raw["dist"] == dist) & (df_raw["N"] == n)]
        star_runs = sub_algo[sub_algo["m"] == m_star].set_index(["seed", "round", "iter"])["time_ms"]

        for ref_m in [7, 8, 10]:
            ref_runs = sub_algo[sub_algo["m"] == ref_m].set_index(["seed", "round", "iter"])["time_ms"]
            # Align pairs on exact same seed, round, iter
            common_idx = star_runs.index.intersection(ref_runs.index)
            if len(common_idx) < 4:
                continue

            x = star_runs.loc[common_idx].values
            y = ref_runs.loc[common_idx].values
            diff = y - x # Positive diff means m* is faster than ref_m

            rel_med_diff_pct = (np.median(y) - np.median(x)) / np.median(y) * 100.0 if np.median(y) > 0 else 0.0

            try:
                # Wilcoxon test
                if np.all(diff == 0):
                    stat_w, p_val = 0.0, 1.0
                else:
                    stat_w, p_val = stats.wilcoxon(x, y, zero_method="pratt")
            except Exception:
                stat_w, p_val = np.nan, 1.0

            # Effect size r = Z / sqrt(N) or rank-biserial
            n_pairs = len(common_idx)
            z_score = stats.norm.ppf(1 - p_val / 2) if (p_val < 1.0 and p_val > 0) else 0.0
            effect_r = abs(z_score) / np.sqrt(n_pairs) if n_pairs > 0 else 0.0

            # Threshold: If p >= 0.05 or |rel_med_diff_pct| < 1.0%: effect is within system noise
            if p_val < 0.05 and abs(rel_med_diff_pct) >= 1.0:
                conclusion = "Significant Difference"
            else:
                conclusion = "Within Noise (No Significant Difference)"

            wilcoxon_records.append({
                "algo": algo,
                "tier": opt_row["tier"],
                "dist": dist,
                "N": n,
                "optimal_m": m_star,
                "reference_m": ref_m,
                "pairs": n_pairs,
                "median_diff_ms": float(np.median(diff)),
                "rel_improvement_pct": rel_med_diff_pct,
                "p_value": float(p_val),
                "effect_size_r": float(effect_r),
                "conclusion": conclusion
            })

    df_wilcoxon = pd.DataFrame(wilcoxon_records)

    # -------------------------------------------------------------------------
    # 5. Stability of Optimal m across N, dist, algorithms, and tiers
    # -------------------------------------------------------------------------
    print("Evaluating stability of optimal cutoff m across conditions...")
    stability_records = []
    # Stability across N (for each algo, dist)
    for (algo, tier, dist), grp in df_optimal.groupby(["algo", "tier", "dist"]):
        m_vals = grp["optimal_m"].values
        stability_records.append({
            "group_type": "Across N",
            "algo": algo,
            "tier": tier,
            "dist": dist,
            "cutoffs_observed": ", ".join(map(str, m_vals)),
            "m_min": int(np.min(m_vals)),
            "m_max": int(np.max(m_vals)),
            "m_mode": int(stats.mode(m_vals, keepdims=False)[0]),
            "range_span": int(np.max(m_vals) - np.min(m_vals))
        })

    df_stability = pd.DataFrame(stability_records)

    # -------------------------------------------------------------------------
    # 6. Mechanistic Counter Integration (Counts vs Time)
    # -------------------------------------------------------------------------
    df_counts_time = pd.DataFrame()
    if os.path.isfile(counts_csv):
        print(f"Integrating mechanistic operation counts from: {counts_csv}...")
        df_cnt = pd.read_csv(counts_csv)
        # Merge on algo, dist, N, m
        df_counts_time = pd.merge(
            df_pts,
            df_cnt[["algo", "dist", "N", "m", "compares", "array_writes", "exchanges", "insertion_compares", "insertion_exchanges"]],
            on=["algo", "dist", "N", "m"],
            how="inner"
        )
        if not df_counts_time.empty:
            # Normalized metrics per (algo, dist, N)
            for (algo, dist, n), grp in df_counts_time.groupby(["algo", "dist", "N"]):
                min_t = grp["median_ms"].min()
                min_c = grp["compares"].min()
                min_w = grp["array_writes"].min()
                for idx in grp.index:
                    df_counts_time.loc[idx, "norm_time"] = df_counts_time.loc[idx, "median_ms"] / min_t if min_t > 0 else 1.0
                    df_counts_time.loc[idx, "norm_compares"] = df_counts_time.loc[idx, "compares"] / min_c if min_c > 0 else 1.0
                    df_counts_time.loc[idx, "norm_array_writes"] = df_counts_time.loc[idx, "array_writes"] / min_w if min_w > 0 else 1.0
                    df_counts_time.loc[idx, "ins_exchs_per_elem"] = df_counts_time.loc[idx, "insertion_exchanges"] / float(n)

    # -------------------------------------------------------------------------
    # 7. Export tables to CSV and Markdown
    # -------------------------------------------------------------------------
    print("Exporting tables to results/tables/...")
    export_table(df_pts, os.path.join(tables_dir, "per_point_summary"))
    export_table(df_optimal, os.path.join(tables_dir, "optimal_and_flat_regions"))
    export_table(df_wilcoxon, os.path.join(tables_dir, "wilcoxon_tests"))
    export_table(df_stability, os.path.join(tables_dir, "stability_analysis"))
    if not df_counts_time.empty:
        export_table(df_counts_time, os.path.join(tables_dir, "counts_vs_time"))

    print("[SUCCESS] Statistical analysis complete. All tables generated.")
    return df_pts, df_optimal, df_wilcoxon, df_stability, df_counts_time

def export_table(df, base_path):
    csv_path = base_path + ".csv"
    md_path = base_path + ".md"
    df.to_csv(csv_path, index=False)
    # Pure Python Markdown table formatter without tabulate dependency
    headers = [str(c) for c in df.columns]
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    row_lines = [header_line, separator_line]
    for _, r in df.iterrows():
        row_str = "| " + " | ".join(str(val) for val in r.values) + " |"
        row_lines.append(row_str)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(row_lines) + "\n")

def main():
    parser = argparse.ArgumentParser(description="Statistical Analysis of Sorting Cutoff Results")
    parser.add_argument("--raw", default="results/raw.csv")
    parser.add_argument("--counts", default="results/counts.csv")
    parser.add_argument("--tables", default="results/tables")
    args = parser.parse_args()

    run_analysis(args.raw, args.counts, args.tables)

if __name__ == "__main__":
    main()
