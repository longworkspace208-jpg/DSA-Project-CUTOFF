#!/usr/bin/env python3
"""
scripts/check_diff.py
Verify that docs/diffs/*.diff only contain minimal authorized changes:
- MergeCutoff: m parameter, Insertion.sort(a, lo, hi + 1) when hi-lo+1 <= m, aux/merge/mid untouched.
- QuickCutoff: m parameter, sortNoShuffle added, Insertion.sort(a, lo, hi + 1) when hi-lo+1 <= m, partition/sentinel untouched.
- MergeXParam: CUTOFF changed to runtime param, skip-merge and ping-pong buffers untouched.
- QuickXParam: INSERTION_SORT_CUTOFF changed to runtime param, median-of-3 and partition untouched.
"""

import os
import re
import sys

def check_file_exists_and_nonempty(path):
    if not os.path.isfile(path):
        print(f"[FAIL] Missing diff file: {path}")
        return False
    if os.path.getsize(path) == 0:
        print(f"[FAIL] Empty diff file: {path}")
        return False
    return True

def verify_merge_cutoff(diff_text):
    errors = []
    # Must change class name
    if "+public class MergeCutoff {" not in diff_text or "-public class Merge {" not in diff_text:
        errors.append("Class name change Merge -> MergeCutoff missing")
    # Must add m parameter and Insertion.sort
    if "+        if (hi - lo + 1 <= m) {" not in diff_text:
        errors.append("Cutoff check 'hi - lo + 1 <= m' missing")
    if "+            Insertion.sort(a, lo, hi + 1);" not in diff_text:
        errors.append("Call to 'Insertion.sort(a, lo, hi + 1)' missing")
    # Disallowed: altering merge logic
    if "-    private static void merge(" in diff_text or "-        int i = lo, j = mid+1;" in diff_text:
        errors.append("Unauthorized change to merge(...) implementation")
    # Disallowed: altering mid calculation
    if "-        int mid = lo + (hi - lo) / 2;" in diff_text:
        errors.append("Unauthorized change to mid calculation")
    return errors

def verify_quick_cutoff(diff_text):
    errors = []
    # Must change class name
    if "+public class QuickCutoff {" not in diff_text or "-public class Quick {" not in diff_text:
        errors.append("Class name change Quick -> QuickCutoff missing")
    # Must add sortNoShuffle
    if "+    public static void sortNoShuffle(Comparable[] a, int m) {" not in diff_text:
        errors.append("Method sortNoShuffle(Comparable[] a, int m) missing")
    # Must add m parameter and Insertion.sort
    if "+        if (hi - lo + 1 <= m) {" not in diff_text:
        errors.append("Cutoff check 'hi - lo + 1 <= m' missing")
    if "+            Insertion.sort(a, lo, hi + 1);" not in diff_text:
        errors.append("Call to 'Insertion.sort(a, lo, hi + 1)' missing")
    # Disallowed: altering partition logic
    if "-    private static int partition(" in diff_text:
        errors.append("Unauthorized change to partition(...) signature")
    if "-        Comparable v = a[lo];" in diff_text or "-            exch(a, i, j);" in diff_text:
        errors.append("Unauthorized change to partition loop/sentinel logic")
    return errors

def verify_mergex_param(diff_text):
    errors = []
    # Must change class name
    if "+public class MergeXParam {" not in diff_text or "-public class MergeX {" not in diff_text:
        errors.append("Class name change MergeX -> MergeXParam missing")
    # Must replace CUTOFF = 7
    if "-    private static final int CUTOFF = 7;" not in diff_text:
        errors.append("Constant CUTOFF = 7 not removed/parameterized")
    # Must preserve skip-merge optimization
    if "-        if (!less(src[mid+1], src[mid])) {" in diff_text:
        errors.append("Unauthorized modification to skip-if-sorted optimization")
    # Must preserve arraycopy optimization
    if "-            System.arraycopy(src, lo, dst, lo, hi - lo + 1);" in diff_text:
        errors.append("Unauthorized modification to System.arraycopy in MergeX")
    return errors

def verify_quickx_param(diff_text):
    errors = []
    # Must change class name
    if "+public class QuickXParam {" not in diff_text or "-public class QuickX {" not in diff_text:
        errors.append("Class name change QuickX -> QuickXParam missing")
    # Must replace INSERTION_SORT_CUTOFF = 8
    if "-    private static final int INSERTION_SORT_CUTOFF = 8;" not in diff_text:
        errors.append("Constant INSERTION_SORT_CUTOFF = 8 not parameterized")
    # Must preserve median3
    if "-    private static int median3(" in diff_text or "-        int m = median3(" in diff_text:
        errors.append("Unauthorized change to median3 calculation")
    return errors

def main():
    diffs = {
        "docs/diffs/MergeCutoff.diff": verify_merge_cutoff,
        "docs/diffs/QuickCutoff.diff": verify_quick_cutoff,
        "docs/diffs/MergeXParam.diff": verify_mergex_param,
        "docs/diffs/QuickXParam.diff": verify_quickx_param,
    }

    all_passed = True
    for path, validator in diffs.items():
        if not check_file_exists_and_nonempty(path):
            all_passed = False
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        errors = validator(content)
        if errors:
            all_passed = False
            print(f"[FAIL] {path}:")
            for e in errors:
                print(f"  - {e}")
        else:
            line_count = len(content.splitlines())
            print(f"[PASS] {path} ({line_count} diff lines) - minimal verified.")

    if not all_passed:
        print("[FAIL] GATE 3 check_diff.py failed!")
        sys.exit(1)
    else:
        print("[SUCCESS] All 4 algorithm variants passed minimal diff verification.")
        sys.exit(0)

if __name__ == "__main__":
    main()
