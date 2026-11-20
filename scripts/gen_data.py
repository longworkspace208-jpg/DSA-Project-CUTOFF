#!/usr/bin/env python3
"""
scripts/gen_data.py
Generate synthetic datasets for Java sorting cutoff experiment.
Uses numpy.random.default_rng(seed) to generate deterministic int32 little-endian binary files.
Outputs:
  data/{dist}_{N}_{seed}.bin
  data/MANIFEST.csv
"""

import csv
import hashlib
import os
import sys
import numpy as np
import yaml

def load_config(config_path="scripts/config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def generate_array(dist, n, seed, params):
    rng = np.random.default_rng(seed)

    if dist == "random":
        arr = rng.integers(low=-1_000_000_000, high=1_000_000_000, size=n, dtype=np.int32)
    elif dist == "sorted":
        raw = rng.integers(low=-1_000_000_000, high=1_000_000_000, size=n, dtype=np.int32)
        arr = np.sort(raw)
    elif dist == "reversed":
        raw = rng.integers(low=-1_000_000_000, high=1_000_000_000, size=n, dtype=np.int32)
        arr = np.sort(raw)[::-1].copy()
    elif dist == "nearly_sorted":
        raw = rng.integers(low=-1_000_000_000, high=1_000_000_000, size=n, dtype=np.int32)
        arr = np.sort(raw)
        orig = arr.copy()
        # Permute exactly ~1% of elements without replacement
        swap_ratio = params.get("nearly_sorted_swap_ratio", 0.01)
        k = max(2, int(n * swap_ratio))
        idx = rng.choice(n, size=k, replace=False)
        shuffled_idx = rng.permutation(idx)
        arr[idx] = orig[shuffled_idx]
    elif dist == "many_duplicates":
        unique_count = params.get("many_duplicates_unique_count", 100)
        unique_vals = rng.integers(low=-1_000_000, high=1_000_000, size=unique_count, dtype=np.int32)
        arr = rng.choice(unique_vals, size=n).astype(np.int32)
    else:
        raise ValueError(f"Unknown distribution: {dist}")

    # Ensure little-endian int32
    return arr.astype("<i4", copy=False)

def compute_sha256(data_bytes):
    return hashlib.sha256(data_bytes).hexdigest()

def main():
    config = load_config()
    data_dir = config.get("data_dir", "data")
    os.makedirs(data_dir, exist_ok=True)

    sizes = config.get("array_sizes", [1000, 10000, 100000, 1000000, 10000000])
    seeds = config.get("random_seeds", [42, 1337, 2026, 31415, 27182])
    params = config.get("distribution_params", {})

    all_dists = config["distributions"]["mergesort"] # superset of all distributions

    manifest_rows = []
    total_files = len(all_dists) * len(sizes) * len(seeds)
    count = 0

    print(f"Generating {total_files} binary dataset files in '{data_dir}'...")

    for dist in all_dists:
        for n in sizes:
            for seed in seeds:
                count += 1
                filename = f"{dist}_{n}_{seed}.bin"
                filepath = os.path.join(data_dir, filename)

                arr = generate_array(dist, n, seed, params)
                raw_bytes = arr.tobytes()

                # Write binary file
                with open(filepath, "wb") as f:
                    f.write(raw_bytes)

                file_size = len(raw_bytes)
                file_sha256 = compute_sha256(raw_bytes)

                # Sorted checksum for verification
                sorted_arr = np.sort(arr).astype("<i4", copy=False)
                sorted_checksum = compute_sha256(sorted_arr.tobytes())

                manifest_rows.append({
                    "file_name": filename,
                    "n": n,
                    "distribution": dist,
                    "seed": seed,
                    "size_bytes": file_size,
                    "sha256": file_sha256,
                    "sorted_checksum": sorted_checksum
                })

                if count % 25 == 0 or count == total_files:
                    print(f"  [{count}/{total_files}] Generated: {filename} ({file_size / (1024*1024):.2f} MB)")

    # Write MANIFEST.csv
    manifest_path = config.get("manifest_path", os.path.join(data_dir, "MANIFEST.csv"))
    fieldnames = ["file_name", "n", "distribution", "seed", "size_bytes", "sha256", "sorted_checksum"]
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"[SUCCESS] Dataset generation complete. Manifest written to '{manifest_path}'.")

if __name__ == "__main__":
    main()
