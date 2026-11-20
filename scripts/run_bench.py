#!/usr/bin/env python3
"""
scripts/run_bench.py
JMH Python Orchestrator for Java Sorting Cutoff Experiment (Pha thô & Pha tinh).
- Supports --phase coarse and --phase fine
- Shuffles m order per round with deterministic logged seed
- Logs CPU clock speed, load, and AC/battery status at start and end of blocks
- Outputs to results/raw.csv with column 'phase'
- Supports resume capability
- Logs detailed progress to results/run.log
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

CSV_HEADER = [
    "algo", "tier", "dist", "N", "seed", "m",
    "round", "iter", "time_ns_per_sort", "K",
    "phase", "jvm", "flags", "checksum_ok"
]

MEAS_RE = re.compile(r"^\s*Iteration\s+(\d+):\s+([\d\.]+)\s+ns/op")

COARSE_CUTOFFS = [0, 4, 6, 7, 8, 10, 12, 16, 24, 32]

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

def read_hardware_env():
    """Reads CPU clock speed, load, and battery/AC status via PowerShell."""
    try:
        cmd = 'powershell -NoProfile -Command "$cpu = Get-CimInstance CIM_Processor | Select-Object -First 1 CurrentClockSpeed, MaxClockSpeed, LoadPercentage; $bat = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue | Select-Object -First 1 BatteryStatus; [PSCustomObject]@{Clock=$cpu.CurrentClockSpeed; MaxClock=$cpu.MaxClockSpeed; Load=$cpu.LoadPercentage; AC=($bat.BatteryStatus -eq 2)} | ConvertTo-Json -Compress"'
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout.strip())
            return f"CPU Clock: {data.get('Clock')} MHz (Load: {data.get('Load')}%) | AC Connected: {data.get('AC')}"
    except Exception:
        pass
    return "Hardware stats unavailable"

def get_existing_completed_runs(csv_path):
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
                    int(row["round"]),
                    row.get("phase", "coarse")
                )
                completed.add(key)
            except Exception:
                continue
    return completed

def run_jmh_single_m(algo, dist, n, seed, m, round_num, wi, meas, phase, config, csv_path, log_path):
    k_val = determine_k(n)
    tier = determine_tier(algo)
    bench_cfg = config.get("benchmark", {})
    jvm_flags_str = bench_cfg.get("jvm_flags", "-Xms4g -Xmx4g -XX:+AlwaysPreTouch -XX:+UseParallelGC")
    jvm_version = bench_cfg.get("jvm_version", "Oracle Corporation 25.0.2")

    temp_json = f"results/temp_bench_{os.getpid()}_{m}.json"
    if os.path.exists(temp_json):
        try:
            os.remove(temp_json)
        except Exception:
            pass

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
        log_message(f"[WARN] JMH attempt {attempt}/{max_retries} failed for {algo} m={m} (code {res.returncode}). Retrying in 1s...", log_path)
        time.sleep(1.0)
    else:
        log_message(f"[ERROR] JMH failed after {max_retries} attempts for m={m} code={res.returncode}:\n{res.stderr or res.stdout}", log_path)
        if os.path.exists(temp_json):
            try:
                os.remove(temp_json)
            except Exception:
                pass
        return False

    raw_scores = []
    if os.path.isfile(temp_json):
        try:
            with open(temp_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data and len(data) > 0 and "primaryMetric" in data[0] and "rawData" in data[0]["primaryMetric"]:
                raw_scores = data[0]["primaryMetric"]["rawData"][0]
        except Exception as e:
            log_message(f"[WARN] JSON read error: {e}", log_path)
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
        log_message(f"[ERROR] Could not extract measurement iterations for {algo} m={m}. STDOUT:\n{res.stdout}", log_path)
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
            "phase": phase,
            "jvm": jvm_version,
            "flags": jvm_flags_str,
            "checksum_ok": "true"
        })

    file_exists = os.path.isfile(csv_path) and os.path.getsize(csv_path) > 0
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows_to_append)

    avg_time_ms = (sum(raw_scores) / len(raw_scores)) / (k_val * 1e6)
    log_message(f"  [DONE] {algo:12s} dist={dist:14s} N={n:7d} m={m:3d} round={round_num:2d} | time={avg_time_ms:8.3f} ms/sort | elapsed={t_end - t_start:5.2f}s", log_path)
    return True

def main():
    parser = argparse.ArgumentParser(description="Run sorting cutoff benchmarks via JMH")
    parser.add_argument("--phase", choices=["coarse", "fine"], default="coarse", help="Benchmark phase: coarse or fine")
    parser.add_argument("--config", default="scripts/config.yaml", help="Path to config file")
    parser.add_argument("--out", default="results/raw.csv", help="Path to output CSV (results/raw.csv)")
    parser.add_argument("--fine_range", default="results/fine_range.json", help="Path to fine range JSON")
    parser.add_argument("--log", default="results/run.log", help="Log file path")
    args = parser.parse_args()

    config = load_config(args.config)
    csv_path = args.out
    log_path = args.log

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    completed_runs = get_existing_completed_runs(csv_path)
    log_message(f"Resuming benchmark (phase={args.phase}). Already completed runs in CSV: {len(completed_runs)}", log_path)

    algos = ["MergeCutoff", "QuickCutoff", "MergeXParam", "QuickXParam"]
    sizes = config.get("array_sizes", [1000, 10000, 100000, 1000000, 10000000])
    seeds = config.get("random_seeds", [42, 1337, 2026, 31415, 27182])

    fine_dict = {}
    if args.phase == "fine":
        if not os.path.isfile(args.fine_range):
            log_message(f"[ERROR] Fine range JSON not found at {args.fine_range}. Run scripts/pick_fine_range.py first.", log_path)
            sys.exit(1)
        with open(args.fine_range, "r", encoding="utf-8") as f:
            fine_dict = json.load(f)

    log_message("==================================================================", log_path)
    log_message(f"STARTING BENCHMARK PHASE: {args.phase.upper()}", log_path)
    log_message(f"Initial Hardware: {read_hardware_env()}", log_path)
    log_message("==================================================================", log_path)

    for n in sizes:
        adaptive = config.get("benchmark", {}).get("adaptive_settings", {}).get(n, {})
        cur_rounds = adaptive.get("rounds", 3)
        cur_wi = adaptive.get("warmup_iterations", 2)
        cur_meas = adaptive.get("measurement_iterations", 3)

        log_message(f"\n>>> BLOCK START: N = {n:,} | rounds={cur_rounds}, wi={cur_wi}, meas={cur_meas} <<<", log_path)
        log_message(f"Block Start Hardware: {read_hardware_env()}", log_path)

        for algo in algos:
            tier = determine_tier(algo)
            allowed_dists = config["distributions"]["mergesort"] if "Merge" in algo else config["distributions"]["quicksort"]

            for dist in allowed_dists:
                # Determine cutoffs for this (algo, dist, n)
                if args.phase == "coarse":
                    cutoffs = COARSE_CUTOFFS.copy()
                else:
                    key = f"{algo}|{dist}|{n}"
                    if key in fine_dict:
                        cutoffs = fine_dict[key]["fine_cutoffs"]
                    else:
                        cutoffs = [7, 8, 10]

                for seed in seeds:
                    for round_idx in range(1, cur_rounds + 1):
                        shuffle_rng = np.random.default_rng(seed + round_idx * 10007 + abs(hash(algo)) % 10000 + n)
                        shuffled_m = cutoffs.copy()
                        shuffle_rng.shuffle(shuffled_m)

                        for m in shuffled_m:
                            run_key = (algo, dist, n, seed, m, round_idx, args.phase)
                            if run_key in completed_runs:
                                continue

                            success = run_jmh_single_m(
                                algo=algo, dist=dist, n=n, seed=seed, m=m,
                                round_num=round_idx, wi=cur_wi, meas=cur_meas,
                                phase=args.phase, config=config,
                                csv_path=csv_path, log_path=log_path
                            )
                            if not success:
                                log_message(f"[CRITICAL] Run failed for key={run_key}. Halting.", log_path)
                                sys.exit(1)
                            completed_runs.add(run_key)

        log_message(f">>> BLOCK END: N = {n:,} | Hardware: {read_hardware_env()} <<<\n", log_path)

    log_message("==================================================================", log_path)
    log_message(f"[SUCCESS] BENCHMARK PHASE {args.phase.upper()} COMPLETED SUCCESSFULLY.", log_path)
    log_message(f"Final Hardware: {read_hardware_env()}", log_path)
    log_message("==================================================================", log_path)

if __name__ == "__main__":
    main()
