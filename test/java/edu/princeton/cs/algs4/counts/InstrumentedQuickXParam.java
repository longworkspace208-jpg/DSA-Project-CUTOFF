package edu.princeton.cs.algs4.counts;

/**
 * Instrumented version of QuickXParam.
 * Tracks comparisons, exchanges, partitions, and insertion sort operations.
 */
public class InstrumentedQuickXParam {

    private InstrumentedQuickXParam() { }

    public static void sort(Comparable[] a, int cutoff) {
        sort(a, 0, a.length - 1, cutoff);
    }

    private static void sort(Comparable[] a, int lo, int hi, int cutoff) {
        if (hi <= lo) return;

        int n = hi - lo + 1;
        if (n <= cutoff) {
            InstrumentedInsertion.sort(a, lo, hi + 1);
            return;
        }

        int j = partition(a, lo, hi);
        sort(a, lo, j - 1, cutoff);
        sort(a, j + 1, hi, cutoff);
    }

    private static int partition(Comparable[] a, int lo, int hi) {
        OperationCounter.recordPartition();
        int n = hi - lo + 1;
        int m = median3(a, lo, lo + n / 2, hi);
        exch(a, m, lo);

        int i = lo;
        int j = hi + 1;
        Comparable v = a[lo];

        while (less(a[++i], v)) {
            if (i == hi) { exch(a, lo, hi); return hi; }
        }

        while (less(v, a[--j])) {
            if (j == lo + 1) return lo;
        }

        while (i < j) {
            exch(a, i, j);
            while (less(a[++i], v)) ;
            while (less(v, a[--j])) ;
        }

        exch(a, lo, j);
        return j;
    }

    private static int median3(Comparable[] a, int i, int j, int k) {
        return (less(a[i], a[j]) ?
               (less(a[j], a[k]) ? j : less(a[i], a[k]) ? k : i) :
               (less(a[k], a[j]) ? j : less(a[k], a[i]) ? k : i));
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
