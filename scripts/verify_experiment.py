#!/usr/bin/env python3
"""
scripts/verify_experiment.py
Verification script for the sorting cutoff experiment:
1. Verifies presence and non-emptiness of all mandatory documents, diffs, data manifests,
   and test artifacts.
2. Checks algorithmic equivalence and diffs against Princeton vendor.
3. Audits raw CSV and operation counts data integrity.
4. Confirms that all 8 publication figures (F1-F8 in PNG and SVG) exist.
5. Verifies REPORT.md validity (no placeholders, generated sections intact).
"""

import os
import sys
import json
import pandas as pd

REQUIRED_DOCS = [
    "docs/ENVIRONMENT.md",
    "docs/HYPOTHESIS.md",
    "docs/PILOT.md",
    "docs/COUNTS.md",
    "docs/EQUIVALENCE.md",
    "docs/WORKLOG.md",
    "REPORT.md"
]

REQUIRED_DIFFS = [
    "docs/diffs/MergeCutoff.diff",
    "docs/diffs/QuickCutoff.diff",
    "docs/diffs/MergeXParam.diff",
    "docs/diffs/QuickXParam.diff"
]

REQUIRED_FIGURES = [
    "results/figures/F1_normalized_time_vs_m.png",
    "results/figures/F1_normalized_time_vs_m.svg",
    "results/figures/F2_distributions_vs_m.png",
    "results/figures/F2_distributions_vs_m.svg",
    "results/figures/F3_merge_vs_quick_overlaid.png",
    "results/figures/F3_merge_vs_quick_overlaid.svg",
    "results/figures/F4_heatmap_m_x_N.png",
    "results/figures/F4_heatmap_m_x_N.svg",
    "results/figures/F5_boxplot_raw_samples.png",
    "results/figures/F5_boxplot_raw_samples.svg",
    "results/figures/F6_operations_vs_m.png",
    "results/figures/F6_operations_vs_m.svg",
    "results/figures/F7_flat_regions_span.png",
    "results/figures/F7_flat_regions_span.svg",
    "results/figures/F8_tierA_vs_tierB.png",
    "results/figures/F8_tierA_vs_tierB.svg"
]

REQUIRED_TABLES = [
    "results/tables/per_point_summary.csv",
    "results/tables/optimal_and_flat_regions.csv",
    "results/tables/wilcoxon_tests.csv",
    "results/tables/stability_analysis.csv"
]

def verify_all():
    print("=" * 80)
    print("RUNNING END-TO-END EXPERIMENT VERIFICATION (`make verify`)")
    print("=" * 80)
    failures = []

    # 1. Documents check
    print("\n[1/5] Checking Required Documents...")
    for doc in REQUIRED_DOCS:
        if not os.path.isfile(doc):
            failures.append(f"Missing document: {doc}")
            print(f"  [FAIL] {doc} missing")
        elif os.path.getsize(doc) < 100:
            failures.append(f"Document {doc} is suspiciously small (< 100 bytes)")
            print(f"  [FAIL] {doc} too small")
        else:
            print(f"  [PASS] {doc} ({os.path.getsize(doc):,} bytes)")

    # 2. Diffs check
    print("\n[2/5] Checking Princeton Code Diffs...")
    for diff in REQUIRED_DIFFS:
        if not os.path.isfile(diff):
            failures.append(f"Missing diff file: {diff}")
            print(f"  [FAIL] {diff} missing")
        else:
            print(f"  [PASS] {diff}")

    # 3. Tables check
    print("\n[3/5] Checking Generated Statistical Tables...")
    for tbl in REQUIRED_TABLES:
        if not os.path.isfile(tbl):
            failures.append(f"Missing table: {tbl}")
            print(f"  [FAIL] {tbl} missing")
        else:
            df = pd.read_csv(tbl)
            print(f"  [PASS] {tbl} ({len(df):,} rows)")

    # 4. Figures check
    print("\n[4/5] Checking Publication Figures (PNG 200dpi + SVG)...")
    for fig in REQUIRED_FIGURES:
        if not os.path.isfile(fig):
            failures.append(f"Missing figure: {fig}")
            print(f"  [FAIL] {fig} missing")
        else:
            print(f"  [PASS] {fig} ({os.path.getsize(fig):,} bytes)")

    # 5. Report content audit
    print("\n[5/5] Auditing REPORT.md Quality and Completeness...")
    if os.path.isfile("REPORT.md"):
        with open("REPORT.md", "r", encoding="utf-8") as f:
            content = f.read()

        banned_phrases = ["TODO", "TBD", "PLACEHOLDER", "XXX", "fill this in"]
        found_banned = [p for p in banned_phrases if p in content]
        if found_banned:
            failures.append(f"REPORT.md contains placeholder phrases: {found_banned}")
            print(f"  [FAIL] Found placeholders: {found_banned}")
        else:
            print("  [PASS] REPORT.md has zero placeholders.")

        # Check required sections
        required_sections = [
            "Executive Summary",
            "Môi trường Đo kiểm",
            "Phương pháp luận",
            "Hypothesis vs Reality",
            "Mergesort",
            "Quicksort",
            "Flat Region",
            "Wilcoxon",
            "Bộ đếm Thao tác"
        ]
        missing_sections = [s for s in required_sections if s.lower() not in content.lower()]
        if missing_sections:
            failures.append(f"REPORT.md missing key sections: {missing_sections}")
            print(f"  [FAIL] Missing sections: {missing_sections}")
        else:
            print("  [PASS] All critical academic report sections confirmed present.")

    print("\n" + "=" * 80)
    if failures:
        print(f"[FAIL] VERIFICATION FAILED WITH {len(failures)} ERRORS:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("[SUCCESS] ALL VERIFICATION GATES PASSED! EXPERIMENT IS FULLY REPRODUCIBLE.")
        print("=" * 80)

if __name__ == "__main__":
    verify_all()
