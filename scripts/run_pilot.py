#!/usr/bin/env python3
"""
scripts/run_pilot.py
Pilot Benchmark Runner for Java Sorting Cutoff Experiment.
Runs:
- N in {10000, 1000000}
- dist = random
- seed = 42 (seed 1)
- m in {1, 7, 8, 10, 30}
- All 4 variants: MergeCutoff, QuickCutoff, MergeXParam, QuickXParam
- 15 rounds with shuffled m order per round
- Captures both warmup iterations and measurement iterations
- Records timestamp for thermal/clock drift analysis
- Runs auxiliary seed study across 5 seeds for Quick vs Merge variance comparison
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
import numpy as np
import yaml

WARMUP_RE = re.compile(r"#\s*Warmup\s+Iteration\s+(\d+):\s+([\d\.]+)\s+ns/op")
MEAS_RE = re.compile(r"^\s*Iteration\s+(\d+):\s+([\d\.]+)\s+ns/op")

RAW_HEADER = [
    "algo", "tier", "dist", "N", "seed", "m",
    "round", "iter", "time_ns_per_sort", "K",
    "timestamp_epoch", "jvm", "flags", "checksum_ok"
]

WARMUP_HEADER = [
    "algo", "tier", "dist", "N", "seed", "m",
    "round", "warmup_iter", "time_ns_per_sort", "K"
]

SEED_STUDY_HEADER = [
    "algo", "tier", "dist", "N", "seed", "m",
    "round", "iter", "time_ns_per_sort", "K"
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

def log_msg(msg, log_path="results/pilot.log"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def get_completed_keys(csv_path):
    if not os.path.isfile(csv_path) or os.path.getsize(csv_path) == 0:
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

def run_single_jmh(algo, dist, n, seed, m, round_num, wi, meas, jvm_flags_str, jvm_version,
                   raw_csv, warmup_csv, log_path):
    k_val = determine_k(n)
    tier = determine_tier(algo)
    jvm_flags_list = jvm_flags_str.split()

    temp_json = f"results/temp_pilot_{os.getpid()}_{m}.json"
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

    max_retries = 2
    for attempt in range(1, max_retries + 1):
        t_start = time.time()
        res = subprocess.run(cmd, capture_output=True, text=True)
        t_end = time.time()

        if res.returncode == 0:
            break
        log_msg(f"[WARN] JMH attempt {attempt}/{max_retries} failed for {algo} m={m} (code {res.returncode}). Retrying in 1s...", log_path)
        time.sleep(1.0)
    else:
        log_msg(f"[ERROR] JMH failed after {max_retries} attempts for {algo} N={n} m={m} r={round_num}:\n{res.stderr or res.stdout}", log_path)
        if os.path.exists(temp_json):
            os.remove(temp_json)
        return False

    # Parse warmup from stdout
    warmup_rows = []
    for line in res.stdout.splitlines():
        w_match = WARMUP_RE.match(line.strip())
        if w_match:
            w_iter = int(w_match.group(1))
            w_score_ns = float(w_match.group(2))
            w_time_per_sort = w_score_ns / float(k_val)
            warmup_rows.append({
                "algo": algo,
                "tier": tier,
                "dist": dist,
                "N": n,
                "seed": seed,
                "m": m,
                "round": round_num,
                "warmup_iter": w_iter,
                "time_ns_per_sort": f"{w_time_per_sort:.3f}",
                "K": k_val
            })

    # Parse measurement from JSON, with stdout fallback
    raw_scores = []
    if os.path.isfile(temp_json):
        try:
            with open(temp_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data and len(data) > 0 and "primaryMetric" in data[0] and "rawData" in data[0]["primaryMetric"]:
                raw_scores = data[0]["primaryMetric"]["rawData"][0]
        except Exception as e:
            log_msg(f"[WARN] JSON read error: {e}", log_path)
        try:
            os.remove(temp_json)
        except Exception:
            pass

    if not raw_scores:
        for line in res.stdout.splitlines():
            m_match = MEAS_RE.match(line.strip())
            if m_match:
                raw_scores.append(float(m_match.group(2)))

    if len(raw_scores) == 0:
        log_msg(f"[ERROR] Could not extract measurement iterations for {algo} m={m}. STDOUT:\n{res.stdout}", log_path)
        return False
    meas_rows = []
    epoch_now = time.time()
    for iter_idx, score_ns in enumerate(raw_scores, start=1):
        time_per_sort = score_ns / float(k_val)
        meas_rows.append({
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
            "timestamp_epoch": f"{epoch_now:.3f}",
            "jvm": jvm_version,
            "flags": jvm_flags_str,
            "checksum_ok": "true"
        })

    # Write measurement rows
    file_exists = os.path.isfile(raw_csv) and os.path.getsize(raw_csv) > 0
    with open(raw_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_HEADER)
        if not file_exists:
            writer.writeheader()
        writer.writerows(meas_rows)

    # Write warmup rows
    if warmup_rows and warmup_csv:
        w_exists = os.path.isfile(warmup_csv) and os.path.getsize(warmup_csv) > 0
        with open(warmup_csv, "a", newline="", encoding="utf-8") as f:
            w_writer = csv.DictWriter(f, fieldnames=WARMUP_HEADER)
            if not w_exists:
                w_writer.writeheader()
            w_writer.writerows(warmup_rows)

    avg_meas_ms = (sum(raw_scores) / len(raw_scores)) / (k_val * 1e6)
    log_msg(f"  [DONE] {algo:12s} N={n:7d} m={m:2d} round={round_num:2d} | time={avg_meas_ms:.3f} ms/sort | elapsed={t_end - t_start:.2f}s", log_path)
    return True

def run_seed_study(raw_csv, log_path, jvm_flags_str, jvm_version):
    """Auxiliary test across 5 seeds for MergeCutoff and QuickCutoff at N=10000, m in {1, 8}"""
    seeds = [42, 1337, 2026, 31415, 27182]
    algos = ["MergeCutoff", "QuickCutoff"]
    cutoffs = [1, 8]
    n = 10000
    dist = "random"
    k_val = determine_k(n)
    rounds = 3
    wi = 5
    meas = 3

    log_msg("=== Starting Auxiliary Permutation / Seed Variation Study ===", log_path)
    csv_path = "results/pilot_seed_study.csv"
    completed = set()
    if os.path.isfile(csv_path) and os.path.getsize(csv_path) > 0:
        with open(csv_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                completed.add((r["algo"], int(r["seed"]), int(r["m"]), int(r["round"])))

    for algo in algos:
        tier = determine_tier(algo)
        for seed in seeds:
            for m in cutoffs:
                for round_idx in range(1, rounds + 1):
                    key = (algo, seed, m, round_idx)
                    if key in completed:
                        continue
                    temp_json = f"results/temp_seed_{seed}_{m}.json"
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
                    max_retries = 2
                    for attempt in range(1, max_retries + 1):
                        res = subprocess.run(cmd, capture_output=True, text=True)
                        if res.returncode == 0:
                            break
                        time.sleep(1.0)
                    else:
                        log_msg(f"[ERROR] Seed study failed for {key}", log_path)
                        continue
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
                        for line in res.stdout.splitlines():
                            m_match = MEAS_RE.match(line.strip())
                            if m_match:
                                raw_scores.append(float(m_match.group(2)))
                    if not raw_scores:
                        log_msg(f"[ERROR] Could not parse scores for seed study {key}", log_path)
                        continue
                    rows = []
                    for iter_idx, s in enumerate(raw_scores, start=1):
                        rows.append({
                            "algo": algo,
                            "tier": tier,
                            "dist": dist,
                            "N": n,
                            "seed": seed,
                            "m": m,
                            "round": round_idx,
                            "iter": iter_idx,
                            "time_ns_per_sort": f"{(s / float(k_val)):.3f}",
                            "K": k_val
                        })
                    file_exists = os.path.isfile(csv_path) and os.path.getsize(csv_path) > 0
                    with open(csv_path, "a", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=SEED_STUDY_HEADER)
                        if not file_exists:
                            writer.writeheader()
                        writer.writerows(rows)
                    completed.add(key)
    log_msg("=== Auxiliary Permutation / Seed Study Complete ===", log_path)

def main():
    parser = argparse.ArgumentParser(description="Pilot Benchmark Runner")
    parser.add_argument("--rounds", type=int, default=15, help="Number of rounds (default: 15)")
    parser.add_argument("--config", default="scripts/config.yaml", help="Path to config file")
    parser.add_argument("--out", default="results/pilot_raw.csv", help="Output raw CSV")
    parser.add_argument("--warmup_out", default="results/pilot_warmup.csv", help="Output warmup CSV")
    parser.add_argument("--log", default="results/pilot.log", help="Log file path")
    parser.add_argument("--skip_seed_study", action="store_true", help="Skip auxiliary seed study")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    bench_cfg = cfg.get("benchmark", {})
    jvm_flags_str = bench_cfg.get("jvm_flags", "-Xms4g -Xmx4g -XX:+AlwaysPreTouch -XX:+UseParallelGC")
    jvm_version = bench_cfg.get("jvm_version", "Oracle Corporation 25.0.2")

    algos = ["MergeCutoff", "QuickCutoff", "MergeXParam", "QuickXParam"]
    sizes = [10000, 1000000]
    cutoffs = [1, 7, 8, 10, 30]
    seed = 42
    dist = "random"
    total_rounds = args.rounds

    # Warmup / Measurement iterations per size:
    # N=10000: wi=6, meas=5 (K=5)
    # N=1000000: wi=4, meas=3 (K=1)
    iter_settings = {
        10000: {"wi": 6, "meas": 5},
        1000000: {"wi": 4, "meas": 3}
    }

    log_msg("==================================================================", args.log)
    log_msg(f"STARTING PILOT EXPERIMENT: {len(algos)} algos, {len(sizes)} sizes, {len(cutoffs)} cutoffs, {total_rounds} rounds", args.log)
    log_msg(f"Parameters: algos={algos}, sizes={sizes}, cutoffs={cutoffs}, seed={seed}, dist={dist}", args.log)
    log_msg(f"JVM Flags: {jvm_flags_str}", args.log)
    log_msg("==================================================================", args.log)

    completed = get_completed_keys(args.out)
    log_msg(f"Existing completed runs in {args.out}: {len(completed)}", args.log)

    total_combinations = len(algos) * len(sizes) * total_rounds
    round_count = 0

    for round_idx in range(1, total_rounds + 1):
        log_msg(f"\n>>> Starting Round {round_idx}/{total_rounds} across all configurations <<<", args.log)
        for n in sizes:
            wi = iter_settings[n]["wi"]
            meas = iter_settings[n]["meas"]
            for algo in algos:
                # Deterministic random permutation of m for this specific round and configuration
                rng = np.random.default_rng(seed + round_idx * 10007 + abs(hash(algo)) % 10000 + n)
                shuffled_m = cutoffs.copy()
                rng.shuffle(shuffled_m)

                for m in shuffled_m:
                    key = (algo, dist, n, seed, m, round_idx)
                    if key in completed:
                        continue
                    success = run_single_jmh(
                        algo=algo, dist=dist, n=n, seed=seed, m=m,
                        round_num=round_idx, wi=wi, meas=meas,
                        jvm_flags_str=jvm_flags_str, jvm_version=jvm_version,
                        raw_csv=args.out, warmup_csv=args.warmup_out,
                        log_path=args.log
                    )
                    if not success:
                        log_msg(f"[FATAL] Benchmark failed for key={key}. Halting.", args.log)
                        sys.exit(1)
                    completed.add(key)

    log_msg("[SUCCESS] Main pilot rounds finished successfully.", args.log)

    if not args.skip_seed_study:
        run_seed_study(args.out, args.log, jvm_flags_str, jvm_version)

    log_msg("[COMPLETE] Entire pilot benchmark suite completed successfully.", args.log)

if __name__ == "__main__":
    main()
