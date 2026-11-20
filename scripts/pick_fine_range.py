#!/usr/bin/env python3
"""
scripts/pick_fine_range.py
Selects the fine scanning range for the cutoff parameter m based on coarse phase results.
Rule:
1. For each (algo, dist, N), find m* with minimum median execution time.
2. Scan unit-by-unit between its adjacent coarse neighbors [m_prev, m_next].
3. Always include 7, 8, 10.
4. Outputs the selection to results/fine_range.json and prints a summary.
"""

import argparse
import json
import os
import sys
import pandas as pd

COARSE_CUTOFFS = [0, 4, 6, 7, 8, 10, 12, 16, 24, 32]
MANDATORY_CUTOFFS = {7, 8, 10}

def pick_fine_range(raw_csv="results/raw.csv", out_json="results/fine_range.json"):
    if not os.path.isfile(raw_csv):
        print(f"[ERROR] Raw CSV file not found: {raw_csv}")
        sys.exit(1)

    df = pd.read_csv(raw_csv)
    # Filter for coarse phase
    if "phase" in df.columns:
        df = df[df["phase"] == "coarse"]

    if df.empty:
        print("[ERROR] No coarse phase data found in raw CSV.")
        sys.exit(1)

    df["time_ms"] = df["time_ns_per_sort"] / 1e6

    # Group by algo, dist, N and cutoff m
    medians = df.groupby(["algo", "tier", "dist", "N", "m"])["time_ms"].median().reset_index()

    fine_selection = {}
    print("=" * 80)
    print("FINE SCANNING RANGE SELECTION (Pre-set Rule)")
    print("=" * 80)
    print(f"{'Algorithm':14s} {'Dist':15s} {'N':8s} {'m* (Optimal)':12s} {'Coarse Neighbors':18s} {'Selected Fine Range m'}")
    print("-" * 80)

    for (algo, tier, dist, n), grp in medians.groupby(["algo", "tier", "dist", "N"]):
        # Find coarse cutoff with minimal median
        best_row = grp.loc[grp["time_ms"].idxmin()]
        best_m = int(best_row["m"])

        # Find adjacent neighbors in COARSE_CUTOFFS
        sorted_coarse = sorted([int(m) for m in grp["m"].unique()])
        if best_m in sorted_coarse:
            idx = sorted_coarse.index(best_m)
            prev_m = sorted_coarse[max(0, idx - 1)]
            next_m = sorted_coarse[min(len(sorted_coarse) - 1, idx + 1)]
        else:
            prev_m = max([m for m in sorted_coarse if m < best_m], default=best_m)
            next_m = min([m for m in sorted_coarse if m > best_m], default=best_m)

        # Unit-by-unit range between prev_m and next_m
        fine_m_set = set(range(prev_m, next_m + 1))
        # Always include mandatory cutoffs
        fine_m_set.update(MANDATORY_CUTOFFS)
        fine_m_list = sorted(list(fine_m_set))

        key = f"{algo}|{dist}|{n}"
        fine_selection[key] = {
            "algo": algo,
            "tier": tier,
            "dist": dist,
            "N": int(n),
            "best_coarse_m": best_m,
            "best_median_ms": float(best_row["time_ms"]),
            "neighbor_prev": prev_m,
            "neighbor_next": next_m,
            "fine_cutoffs": fine_m_list
        }

        print(f"{algo:14s} {dist:15s} {int(n):8d} {best_m:12d} [{prev_m}, {next_m}]{'':8s} {fine_m_list}")

    print("=" * 80)
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(fine_selection, f, indent=2)
    print(f"Fine selection saved to: {out_json}")
    return fine_selection

def main():
    parser = argparse.ArgumentParser(description="Pick fine range from coarse benchmark")
    parser.add_argument("--raw", default="results/raw.csv")
    parser.add_argument("--out", default="results/fine_range.json")
    args = parser.parse_args()

    pick_fine_range(args.raw, args.out)

if __name__ == "__main__":
    main()
