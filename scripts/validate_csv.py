#!/usr/bin/env python3
"""
scripts/validate_csv.py
Validates the benchmark results CSV file for GATE 6:
- Verifies full schema columns.
- Ensures no NaN, null, or empty fields.
- Verifies time_ns_per_sort > 0 and checksum_ok == true.
- Confirms that the order of m differed between rounds (proves random round shuffling).
- Outputs summary table of results.
"""

import csv
import math
import os
import sys
from collections import defaultdict
import pandas as pd

REQUIRED_COLUMNS = [
    "algo", "tier", "dist", "N", "seed", "m",
    "round", "iter", "time_ns_per_sort", "K",
    "jvm", "flags", "checksum_ok"
]

def validate_csv(csv_path="results/bench_raw.csv"):
    if not os.path.isfile(csv_path):
        print(f"[FAIL] Benchmark CSV not found at: {csv_path}")
        sys.exit(1)

    print(f"Validating CSV file: {csv_path}...")
    errors = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        for col in REQUIRED_COLUMNS:
            if col not in fields:
                errors.append(f"Missing required column: '{col}'")

        if errors:
            print("[FAIL] Schema check failed:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)

        rows = list(reader)

    if not rows:
        print("[FAIL] CSV file is empty (no data rows).")
        sys.exit(1)

    print(f"Total rows in CSV: {len(rows)}")

    # Check row values
    round_m_sequences = defaultdict(lambda: defaultdict(list))
    # Key: (algo, dist, N, seed) -> round -> [m1, m2, ...]

    for idx, row in enumerate(rows, start=1):
        for col in REQUIRED_COLUMNS:
            val = row.get(col, "").strip()
            if not val or val.lower() == "nan" or val.lower() == "null":
                errors.append(f"Row {idx}: column '{col}' has empty/NaN value")

        try:
            t = float(row["time_ns_per_sort"])
            if t <= 0 or math.isnan(t):
                errors.append(f"Row {idx}: time_ns_per_sort ({t}) must be positive and non-NaN")
        except ValueError:
            errors.append(f"Row {idx}: Invalid time_ns_per_sort format '{row['time_ns_per_sort']}'")

        chk = row.get("checksum_ok", "").strip().lower()
        if chk not in ("true", "1"):
            errors.append(f"Row {idx}: checksum_ok is '{chk}', expected 'true'")

        key = (row["algo"], row["dist"], row["N"], row["seed"])
        r_num = int(row["round"])
        m_val = int(row["m"])
        # If new m for this round, record it
        cur_list = round_m_sequences[key][r_num]
        if not cur_list or cur_list[-1] != m_val:
            cur_list.append(m_val)

    if errors:
        print(f"[FAIL] Found {len(errors)} data integrity errors:")
        for e in errors[:10]:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("[PASS] Schema check passed: all required columns present, no NaN, all time > 0, checksum_ok = true.")

    # Verify that m order actually differed between rounds
    print("\nChecking m order permutation across rounds...")
    shuffled_rounds_verified = False

    for key, round_dict in round_m_sequences.items():
        if len(round_dict) >= 2:
            rounds = sorted(round_dict.keys())
            seqs = [round_dict[r] for r in rounds]
            # Check if at least two rounds have different order
            for i in range(len(seqs)):
                for j in range(i + 1, len(seqs)):
                    if seqs[i] != seqs[j]:
                        shuffled_rounds_verified = True
                        print(f"  [PASS] {key[0]} N={key[2]} seed={key[3]}:")
                        print(f"    Round {rounds[i]} order: {seqs[i]}")
                        print(f"    Round {rounds[j]} order: {seqs[j]}")
                        break
                if shuffled_rounds_verified:
                    break
        if shuffled_rounds_verified:
            break

    if not shuffled_rounds_verified:
        print("[FAIL] Order of m was identical across all rounds! Random shuffling failed.")
        sys.exit(1)
    else:
        print("[PASS] Random shuffling of m across rounds verified.")

    # Summary table
    df = pd.DataFrame(rows)
    df["time_ns_per_sort"] = df["time_ns_per_sort"].astype(float)
    df["time_ms"] = df["time_ns_per_sort"] / 1_000_000.0
    df["m"] = df["m"].astype(int)

    summary = df.groupby(["algo", "tier", "m"])["time_ms"].agg(["count", "mean", "std", "min", "max"]).reset_index()

    print("\n" + "=" * 80)
    print("GATE 6 BENCHMARK SUMMARY (Times in ms/sort)")
    print("=" * 80)
    print(f"{'Algorithm':<14} {'Tier':<8} {'m':<6} {'Count':<8} {'Mean (ms)':<12} {'Std (ms)':<10} {'Min (ms)':<10} {'Max (ms)':<10}")
    print("-" * 80)
    for _, r in summary.iterrows():
        std_str = f"{r['std']:.3f}" if not math.isnan(r['std']) else "N/A"
        print(f"{r['algo']:<14} {r['tier']:<8} {r['m']:<6} {int(r['count']):<8} {r['mean']:<12.3f} {std_str:<10} {r['min']:<10.3f} {r['max']:<10.3f}")
    print("=" * 80)
    print("[SUCCESS] GATE 6 validation complete. All criteria satisfied.\n")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "results/bench_raw.csv"
    validate_csv(path)
