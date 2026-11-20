package edu.princeton.cs.algs4.counts;

/**
 * Instrumented version of QuickCutoff.
 * Tracks comparisons, exchanges, partitions, and insertion sort operations.
 */
public class InstrumentedQuickCutoff {

    private InstrumentedQuickCutoff() { }

    public static void sortNoShuffle(Comparable[] a, int m) {
        sort(a, 0, a.length - 1, m);
    }

    private static void sort(Comparable[] a, int lo, int hi, int m) {
        if (hi - lo + 1 <= m) {
            InstrumentedInsertion.sort(a, lo, hi + 1);
            return;
        }
        int j = partition(a, lo, hi);
        sort(a, lo, j - 1, m);
        sort(a, j + 1, hi, m);
    }

    private static int partition(Comparable[] a, int lo, int hi) {
        OperationCounter.recordPartition();
        int i = lo;
        int j = hi + 1;
        Comparable v = a[lo];
        while (true) {
            while (less(a[++i], v)) {
                if (i == hi) break;
            }
            while (less(v, a[--j])) {
                if (j == lo) break;
            }
            if (i >= j) break;
            exch(a, i, j);
        }
        exch(a, lo, j);
        return j;
    }

    private static boolean less(Comparable v, Comparable w) {
        return v.compareTo(w) < 0;
    }

    private static void exch(Object[] a, int i, int j) {
        Object swap = a[i];
        a[i] = a[j];
        a[j] = swap;
        OperationCounter.recordExch();
    }
}
