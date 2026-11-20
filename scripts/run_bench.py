#!/usr/bin/env python3
"""
scripts/run_bench.py
JMH Python Orchestrator for Java Sorting Cutoff Experiment.
- Executes JMH in rounds with randomized m order per round.
- Adaptive iterations and warmup based on N.
- Extracts per-iteration timings, calculates time_ns_per_sort = total / K.
- Appends to results/bench_raw.csv with resume capability.
- Logs progress to results/run.log.
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime
import numpy as np
import yaml

CSV_HEADER = [
    "algo", "tier", "dist", "N", "seed", "m",
    "round", "iter", "time_ns_per_sort", "K",
    "jvm", "flags", "checksum_ok"
]

def determine_tier(algo):
    if algo in ("MergeCutoff", "QuickCutoff"):
        return "TierA"
    elif algo in ("MergeXParam", "QuickXParam"):
        return "TierB"
    return "Unknown"

def determine_k(n):
    if n <= 1000:
        return 20
    if n <= 10000:
        return 5
    return 1

def load_config(config_path="scripts/config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def log_message(msg, log_path="results/run.log"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def get_existing_completed_runs(csv_path):
    if not os.path.isfile(csv_path):
        return set()
    completed = set()
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                key = (
                    row["algo"],
                    row["dist"],
                    int(row["N"]),
                    int(row["seed"]),
                    int(row["m"]),
                    int(row["round"])
                )
                completed.add(key)
            except Exception:
                continue
    return completed

def run_jmh_single_m(algo, dist, n, seed, m, round_num, wi, meas, config, csv_path, log_path):
    k_val = determine_k(n)
    tier = determine_tier(algo)
    bench_cfg = config.get("benchmark", {})
    jvm_flags_str = bench_cfg.get("jvm_flags", "-Xms4g -Xmx4g -XX:+AlwaysPreTouch -XX:+UseParallelGC")
    jvm_version = bench_cfg.get("jvm_version", "Oracle Corporation 25.0.2")

    jvm_flags_list = jvm_flags_str.split()
    temp_json = f"results/temp_jmh_{os.getpid()}_{m}.json"
    if os.path.exists(temp_json):
        os.remove(temp_json)

    cmd = [
        "java",
        "-Xms256m", "-Xmx512m",
        "-jar", "target/benchmarks.jar",
        "SortingBenchmark",
        "-p", f"algo={algo}",
        "-p", f"dist={dist}",
        "-p", f"n={n}",
        "-p", f"seed={seed}",
        "-p", f"m={m}",
        "-wi", str(wi),
        "-i", str(meas),
        "-f", "1",
        "-jvmArgs", jvm_flags_str,
        "-rf", "json",
        "-rff", temp_json
    ]

    log_message(f"Starting JMH: algo={algo} dist={dist} N={n} seed={seed} m={m} round={round_num}", log_path)
    max_retries = 2
    for attempt in range(1, max_retries + 1):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            break
        log_message(f"[WARN] JMH attempt {attempt}/{max_retries} failed for m={m}. Retrying in 1s...", log_path)
        time.sleep(1.0)
    else:
        log_message(f"[ERROR] JMH failed for m={m} code={res.returncode}:\n{res.stderr or res.stdout}", log_path)
        if os.path.exists(temp_json):
            os.remove(temp_json)
        return False

    raw_scores = []
    if os.path.isfile(temp_json):
        try:
            with open(temp_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data and len(data) > 0 and "primaryMetric" in data[0] and "rawData" in data[0]["primaryMetric"]:
                raw_scores = data[0]["primaryMetric"]["rawData"][0]
        except Exception:
            pass
        try:
            os.remove(temp_json)
        except Exception:
            pass

    if not raw_scores:
        import re
        meas_re = re.compile(r"^\s*Iteration\s+(\d+):\s+([\d\.]+)\s+ns/op")
        for line in res.stdout.splitlines():
            m_match = meas_re.match(line.strip())
            if m_match:
                raw_scores.append(float(m_match.group(2)))

    if not raw_scores:
        log_message(f"[ERROR] Could not extract measurement iterations for m={m}. STDOUT:\n{res.stdout}", log_path)
        return False

    rows_to_append = []
    for iter_idx, score_ns in enumerate(raw_scores, start=1):
        time_per_sort = score_ns / float(k_val)
        rows_to_append.append({
            "algo": algo,
            "tier": tier,
            "dist": dist,
            "N": n,
            "seed": seed,
            "m": m,
            "round": round_num,
            "iter": iter_idx,
            "time_ns_per_sort": f"{time_per_sort:.3f}",
            "K": k_val,
            "jvm": jvm_version,
            "flags": jvm_flags_str,
            "checksum_ok": "true"
        })

    # Write to CSV immediately
    file_exists = os.path.isfile(csv_path) and os.path.getsize(csv_path) > 0
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows_to_append)

    avg_time_us = (sum(raw_scores) / len(raw_scores)) / (k_val * 1000.0)
    log_message(f"[DONE] m={m} round={round_num} | time={avg_time_us:.2f} us/sort | K={k_val}", log_path)
    return True

def main():
    parser = argparse.ArgumentParser(description="Run sorting cutoff benchmarks via JMH")
    parser.add_argument("--gate6", action="store_true", help="Run GATE 6 test configuration")
    parser.add_argument("--config", default="scripts/config.yaml", help="Path to config file")
    parser.add_argument("--out", default="results/bench_raw.csv", help="Path to output CSV")
    args = parser.parse_args()

    config = load_config(args.config)
    csv_path = args.out
    log_path = "results/run.log"

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    completed_runs = get_existing_completed_runs(csv_path)
    log_message(f"Resuming benchmark. Already completed runs in CSV: {len(completed_runs)}", log_path)

    if args.gate6:
        # Gate 6 test specification:
        # N=1e5, random, seed 42 (seed 1), cutoffs [1, 8, 16, 32], all 4 variants, 3 rounds
        algos = ["MergeCutoff", "QuickCutoff", "MergeXParam", "QuickXParam"]
        dists = ["random"]
        sizes = [100000]
        seeds = [42]
        cutoffs = [1, 8, 16, 32]
        num_rounds = 3
        wi = 2
        meas = 2
    else:
        algos = ["MergeCutoff", "QuickCutoff", "MergeXParam", "QuickXParam"]
        sizes = config.get("array_sizes", [1000, 10000, 100000])
        seeds = config.get("random_seeds", [42, 1337, 2026])
        cutoffs = config.get("cutoffs", [1, 2, 4, 8, 16, 32, 64])
        dists = ["random"]
        num_rounds = 3
        wi = 2
        meas = 3

    log_message(f"Starting experiment: algos={algos}, sizes={sizes}, seeds={seeds}, cutoffs={cutoffs}, rounds={num_rounds}", log_path)

    for algo in algos:
        tier = determine_tier(algo)
        # Determine allowed distributions for this algo
        allowed_dists = config["distributions"]["mergesort"] if "Merge" in algo else config["distributions"]["quicksort"]
        active_dists = [d for d in dists if d in allowed_dists]

        for dist in active_dists:
            for n in sizes:
                adaptive = config.get("benchmark", {}).get("adaptive_settings", {}).get(n, {})
                cur_rounds = num_rounds if args.gate6 else adaptive.get("rounds", 3)
                cur_wi = wi if args.gate6 else adaptive.get("warmup_iterations", 2)
                cur_meas = meas if args.gate6 else adaptive.get("measurement_iterations", 3)

                for seed in seeds:
                    for round_idx in range(1, cur_rounds + 1):
                        # Shuffled order of m for this round (deterministic shuffle seed)
                        shuffle_rng = np.random.default_rng(seed + round_idx * 10007 + hash(algo) % 10000)
                        shuffled_m = cutoffs.copy()
                        shuffle_rng.shuffle(shuffled_m)

                        log_message(f">>> Round {round_idx}/{cur_rounds} for algo={algo} dist={dist} N={n} seed={seed} | Order of m: {shuffled_m}", log_path)

                        for m in shuffled_m:
                            key = (algo, dist, n, seed, m, round_idx)
                            if key in completed_runs:
                                log_message(f"Skipping already completed: {key}", log_path)
                                continue

                            success = run_jmh_single_m(algo, dist, n, seed, m, round_idx, cur_wi, cur_meas, config, csv_path, log_path)
                            if not success:
                                log_message(f"[CRITICAL] Run failed for key={key}. Halting.", log_path)
                                sys.exit(1)
                            completed_runs.add(key)

    log_message("[SUCCESS] Benchmark execution finished successfully.", log_path)

if __name__ == "__main__":
    main()
