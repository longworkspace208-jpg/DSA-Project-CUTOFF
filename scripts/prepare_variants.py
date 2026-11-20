#!/usr/bin/env python3
"""
Generate minimal variant files from vendor/algs4 originals and produce docs/diffs/*.diff.
"""

import os
import subprocess

def prepare_merge_cutoff():
    with open("vendor/algs4/Merge.java", "r", encoding="utf-8", newline="") as f:
        content = f.read()

    # 1. Class name and constructor
    content = content.replace("public class Merge {", "public class MergeCutoff {")
    content = content.replace("private Merge() { }", "private MergeCutoff() { }")

    # 2. Private recursive sort with cutoff
    old_sort = """    // mergesort a[lo..hi] using auxiliary array aux[lo..hi]
    private static void sort(Comparable[] a, Comparable[] aux, int lo, int hi) {
        if (hi <= lo) return;
        int mid = lo + (hi - lo) / 2;
        sort(a, aux, lo, mid);
        sort(a, aux, mid + 1, hi);
        merge(a, aux, lo, mid, hi);
    }"""

    new_sort = """    // mergesort a[lo..hi] using auxiliary array aux[lo..hi] with cutoff m
    private static void sort(Comparable[] a, Comparable[] aux, int lo, int hi, int m) {
        if (hi <= lo) return;
        if (hi - lo + 1 <= m) {
            Insertion.sort(a, lo, hi + 1);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(a, aux, lo, mid, m);
        sort(a, aux, mid + 1, hi, m);
        merge(a, aux, lo, mid, hi);
    }"""
    assert old_sort in content, "Merge.java sort method pattern not found"
    content = content.replace(old_sort, new_sort)

    # 3. Public sort overload
    old_pub_sort = """    public static void sort(Comparable[] a) {
        Comparable[] aux = new Comparable[a.length];
        sort(a, aux, 0, a.length-1);
        assert isSorted(a);
    }"""

    new_pub_sort = """    public static void sort(Comparable[] a, int m) {
        Comparable[] aux = new Comparable[a.length];
        sort(a, aux, 0, a.length-1, m);
        assert isSorted(a);
    }

    public static void sort(Comparable[] a) {
        sort(a, 1);
    }"""
    assert old_pub_sort in content, "Merge.java public sort pattern not found"
    content = content.replace(old_pub_sort, new_pub_sort)

    # 4. Main
    content = content.replace("Merge.sort(a);", "MergeCutoff.sort(a);")

    dest = "src/java/edu/princeton/cs/algs4/MergeCutoff.java"
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"Generated: {dest}")


def prepare_quick_cutoff():
    with open("vendor/algs4/Quick.java", "r", encoding="utf-8", newline="") as f:
        content = f.read()

    # 1. Class name and constructor
    content = content.replace("public class Quick {", "public class QuickCutoff {")
    content = content.replace("private Quick() { }", "private QuickCutoff() { }")

    # 2. Public sort & sortNoShuffle
    old_pub_sort = """    public static void sort(Comparable[] a) {
        StdRandom.shuffle(a);
        sort(a, 0, a.length - 1);
        assert isSorted(a);
    }"""

    new_pub_sort = """    public static void sort(Comparable[] a, int m) {
        StdRandom.shuffle(a);
        sort(a, 0, a.length - 1, m);
        assert isSorted(a);
    }

    public static void sortNoShuffle(Comparable[] a, int m) {
        sort(a, 0, a.length - 1, m);
        assert isSorted(a);
    }

    public static void sort(Comparable[] a) {
        sort(a, 1);
    }"""
    assert old_pub_sort in content, "Quick.java public sort pattern not found"
    content = content.replace(old_pub_sort, new_pub_sort)

    # 3. Private sort with cutoff
    old_priv_sort = """    // quicksort the subarray from a[lo] to a[hi]
    private static void sort(Comparable[] a, int lo, int hi) {
        if (hi <= lo) return;
        int j = partition(a, lo, hi);
        sort(a, lo, j-1);
        sort(a, j+1, hi);
        assert isSorted(a, lo, hi);
    }"""

    new_priv_sort = """    // quicksort the subarray from a[lo] to a[hi] with cutoff m
    private static void sort(Comparable[] a, int lo, int hi, int m) {
        if (hi <= lo) return;
        if (hi - lo + 1 <= m) {
            Insertion.sort(a, lo, hi + 1);
            return;
        }
        int j = partition(a, lo, hi);
        sort(a, lo, j-1, m);
        sort(a, j+1, hi, m);
        assert isSorted(a, lo, hi);
    }"""
    assert old_priv_sort in content, "Quick.java private sort pattern not found"
    content = content.replace(old_priv_sort, new_priv_sort)

    # 4. Main
    content = content.replace("Quick.sort(a);", "QuickCutoff.sort(a);")
    content = content.replace("Quick.select(a, i);", "QuickCutoff.select(a, i);")

    dest = "src/java/edu/princeton/cs/algs4/QuickCutoff.java"
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"Generated: {dest}")


def prepare_mergex_param():
    with open("vendor/algs4/MergeX.java", "r", encoding="utf-8", newline="") as f:
        content = f.read()

    # 1. Class name and constructor
    content = content.replace("public class MergeX {", "public class MergeXParam {")
    content = content.replace("private MergeX() { }", "private MergeXParam() { }")

    # 2. CUTOFF constant
    old_cutoff = "    private static final int CUTOFF = 7;  // cutoff to insertion sort"
    new_cutoff = "    private static final int DEFAULT_CUTOFF = 7;  // default cutoff to insertion sort"
    assert old_cutoff in content, "MergeX CUTOFF not found"
    content = content.replace(old_cutoff, new_cutoff)

    # 3. Private sort (Comparable)
    old_priv_sort = """    private static void sort(Comparable[] src, Comparable[] dst, int lo, int hi) {
        // if (hi <= lo) return;
        if (hi <= lo + CUTOFF) {
            insertionSort(dst, lo, hi);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(dst, src, lo, mid);
        sort(dst, src, mid+1, hi);

        // if (!less(src[mid+1], src[mid])) {
        //    for (int i = lo; i <= hi; i++) dst[i] = src[i];
        //    return;
        // }

        // using System.arraycopy() is a bit faster than the above loop
        if (!less(src[mid+1], src[mid])) {
            System.arraycopy(src, lo, dst, lo, hi - lo + 1);
            return;
        }

        merge(src, dst, lo, mid, hi);
    }"""

    new_priv_sort = """    private static void sort(Comparable[] src, Comparable[] dst, int lo, int hi, int cutoff) {
        // if (hi <= lo) return;
        if (hi <= lo + cutoff) {
            insertionSort(dst, lo, hi);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(dst, src, lo, mid, cutoff);
        sort(dst, src, mid+1, hi, cutoff);

        // if (!less(src[mid+1], src[mid])) {
        //    for (int i = lo; i <= hi; i++) dst[i] = src[i];
        //    return;
        // }

        // using System.arraycopy() is a bit faster than the above loop
        if (!less(src[mid+1], src[mid])) {
            System.arraycopy(src, lo, dst, lo, hi - lo + 1);
            return;
        }

        merge(src, dst, lo, mid, hi);
    }"""
    assert old_priv_sort in content, "MergeX private sort pattern not found"
    content = content.replace(old_priv_sort, new_priv_sort)

    # 4. Public sort (Comparable)
    old_pub_sort = """    public static void sort(Comparable[] a) {
        Comparable[] aux = a.clone();
        sort(aux, a, 0, a.length-1);
        assert isSorted(a);
    }"""

    new_pub_sort = """    public static void sort(Comparable[] a, int cutoff) {
        Comparable[] aux = a.clone();
        sort(aux, a, 0, a.length-1, cutoff);
        assert isSorted(a);
    }

    public static void sort(Comparable[] a) {
        sort(a, DEFAULT_CUTOFF);
    }"""
    assert old_pub_sort in content, "MergeX public sort pattern not found"
    content = content.replace(old_pub_sort, new_pub_sort)

    # 5. Comparator versions
    old_comp_pub = """    public static void sort(Object[] a, Comparator comparator) {
        Object[] aux = a.clone();
        sort(aux, a, 0, a.length-1, comparator);
        assert isSorted(a, comparator);
    }"""

    new_comp_pub = """    public static void sort(Object[] a, Comparator comparator, int cutoff) {
        Object[] aux = a.clone();
        sort(aux, a, 0, a.length-1, comparator, cutoff);
        assert isSorted(a, comparator);
    }

    public static void sort(Object[] a, Comparator comparator) {
        sort(a, comparator, DEFAULT_CUTOFF);
    }"""
    assert old_comp_pub in content, "MergeX comparator sort pattern not found"
    content = content.replace(old_comp_pub, new_comp_pub)

    old_comp_priv = """    private static void sort(Object[] src, Object[] dst, int lo, int hi, Comparator comparator) {
        // if (hi <= lo) return;
        if (hi <= lo + CUTOFF) {
            insertionSort(dst, lo, hi, comparator);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(dst, src, lo, mid, comparator);
        sort(dst, src, mid+1, hi, comparator);

        // using System.arraycopy() is a bit faster than the above loop
        if (!less(src[mid+1], src[mid], comparator)) {
            System.arraycopy(src, lo, dst, lo, hi - lo + 1);
            return;
        }

        merge(src, dst, lo, mid, hi, comparator);
    }"""

    new_comp_priv = """    private static void sort(Object[] src, Object[] dst, int lo, int hi, Comparator comparator, int cutoff) {
        // if (hi <= lo) return;
        if (hi <= lo + cutoff) {
            insertionSort(dst, lo, hi, comparator);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(dst, src, lo, mid, comparator, cutoff);
        sort(dst, src, mid+1, hi, comparator, cutoff);

        // using System.arraycopy() is a bit faster than the above loop
        if (!less(src[mid+1], src[mid], comparator)) {
            System.arraycopy(src, lo, dst, lo, hi - lo + 1);
            return;
        }

        merge(src, dst, lo, mid, hi, comparator);
    }"""
    assert old_comp_priv in content, "MergeX comparator private sort pattern not found"
    content = content.replace(old_comp_priv, new_comp_priv)

    # 6. Main
    content = content.replace("MergeX.sort(a);", "MergeXParam.sort(a);")

    dest = "src/java/edu/princeton/cs/algs4/MergeXParam.java"
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"Generated: {dest}")


def prepare_quickx_param():
    with open("vendor/algs4/QuickX.java", "r", encoding="utf-8", newline="") as f:
        content = f.read()

    # 1. Class name and constructor
    content = content.replace("public class QuickX {", "public class QuickXParam {")
    content = content.replace("private QuickX() { }", "private QuickXParam() { }")

    # 2. CUTOFF constant
    old_cutoff = "    private static final int INSERTION_SORT_CUTOFF = 8;"
    new_cutoff = "    private static final int DEFAULT_CUTOFF = 8;"
    assert old_cutoff in content, "QuickX CUTOFF not found"
    content = content.replace(old_cutoff, new_cutoff)

    # 3. Public sort
    old_pub_sort = """    public static void sort(Comparable[] a) {
        // StdRandom.shuffle(a);
        sort(a, 0, a.length - 1);
        assert isSorted(a);
    }"""

    new_pub_sort = """    public static void sort(Comparable[] a, int cutoff) {
        // StdRandom.shuffle(a);
        sort(a, 0, a.length - 1, cutoff);
        assert isSorted(a);
    }

    public static void sort(Comparable[] a) {
        sort(a, DEFAULT_CUTOFF);
    }"""
    assert old_pub_sort in content, "QuickX public sort pattern not found"
    content = content.replace(old_pub_sort, new_pub_sort)

    # 4. Private sort
    old_priv_sort = """    private static void sort(Comparable[] a, int lo, int hi) {
        if (hi <= lo) return;

        // cutoff to insertion sort (Insertion.sort() uses half-open intervals)
        int n = hi - lo + 1;
        if (n <= INSERTION_SORT_CUTOFF) {
            Insertion.sort(a, lo, hi + 1);
            return;
        }

        int j = partition(a, lo, hi);
        sort(a, lo, j-1);
        sort(a, j+1, hi);
    }"""

    new_priv_sort = """    private static void sort(Comparable[] a, int lo, int hi, int cutoff) {
        if (hi <= lo) return;

        // cutoff to insertion sort (Insertion.sort() uses half-open intervals)
        int n = hi - lo + 1;
        if (n <= cutoff) {
            Insertion.sort(a, lo, hi + 1);
            return;
        }

        int j = partition(a, lo, hi);
        sort(a, lo, j-1, cutoff);
        sort(a, j+1, hi, cutoff);
    }"""
    assert old_priv_sort in content, "QuickX private sort pattern not found"
    content = content.replace(old_priv_sort, new_priv_sort)

    # 5. Main
    content = content.replace("QuickX.sort(a);", "QuickXParam.sort(a);")

    dest = "src/java/edu/princeton/cs/algs4/QuickXParam.java"
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"Generated: {dest}")


def generate_diffs():
    os.makedirs("docs/diffs", exist_ok=True)
    pairs = [
        ("vendor/algs4/Merge.java", "src/java/edu/princeton/cs/algs4/MergeCutoff.java", "docs/diffs/MergeCutoff.diff"),
        ("vendor/algs4/Quick.java", "src/java/edu/princeton/cs/algs4/QuickCutoff.java", "docs/diffs/QuickCutoff.diff"),
        ("vendor/algs4/MergeX.java", "src/java/edu/princeton/cs/algs4/MergeXParam.java", "docs/diffs/MergeXParam.diff"),
        ("vendor/algs4/QuickX.java", "src/java/edu/princeton/cs/algs4/QuickXParam.java", "docs/diffs/QuickXParam.diff"),
    ]
    for orig, mod, diff_path in pairs:
        # Use git diff --no-index
        cmd = ["git", "diff", "--no-index", orig, mod]
        res = subprocess.run(cmd, capture_output=True, text=True)
        with open(diff_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(res.stdout)
        print(f"Generated diff: {diff_path} ({len(res.stdout.splitlines())} lines)")


def main():
    os.makedirs("src/java/edu/princeton/cs/algs4", exist_ok=True)
    prepare_merge_cutoff()
    prepare_quick_cutoff()
    prepare_mergex_param()
    prepare_quickx_param()
    generate_diffs()

if __name__ == "__main__":
    main()
