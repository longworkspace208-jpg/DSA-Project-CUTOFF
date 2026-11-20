package edu.princeton.cs.algs4.counts;

/**
 * Instrumented version of MergeCutoff.
 * Tracks comparisons, array writes, and merges.
 */
public class InstrumentedMergeCutoff {

    private InstrumentedMergeCutoff() { }

    private static void merge(Comparable[] a, Comparable[] aux, int lo, int mid, int hi) {
        OperationCounter.recordMerge();

        // copy to aux[]
        for (int k = lo; k <= hi; k++) {
            aux[k] = a[k];
            OperationCounter.recordArrayWrite(1);
        }

        // merge back to a[]
        int i = lo, j = mid + 1;
        for (int k = lo; k <= hi; k++) {
            if      (i > mid)              { a[k] = aux[j++]; OperationCounter.recordArrayWrite(1); }
            else if (j > hi)               { a[k] = aux[i++]; OperationCounter.recordArrayWrite(1); }
            else if (less(aux[j], aux[i])) { a[k] = aux[j++]; OperationCounter.recordArrayWrite(1); }
            else                           { a[k] = aux[i++]; OperationCounter.recordArrayWrite(1); }
        }
    }

    private static void sort(Comparable[] a, Comparable[] aux, int lo, int hi, int m) {
        if (hi - lo + 1 <= m) {
            InstrumentedInsertion.sort(a, lo, hi + 1);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(a, aux, lo, mid, m);
        sort(a, aux, mid + 1, hi, m);
        merge(a, aux, lo, mid, hi);
    }

    public static void sort(Comparable[] a, int m) {
        Comparable[] aux = new Comparable[a.length];
        sort(a, aux, 0, a.length - 1, m);
    }

    private static boolean less(Comparable v, Comparable w) {
        return v.compareTo(w) < 0;
    }
}
