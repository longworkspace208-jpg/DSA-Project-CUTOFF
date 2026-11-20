package edu.princeton.cs.algs4.counts;

/**
 * Instrumented version of MergeXParam.
 * Tracks comparisons, array writes, skips, and insertion sort operations.
 */
public class InstrumentedMergeXParam {

    private InstrumentedMergeXParam() { }

    private static void merge(Comparable[] src, Comparable[] dst, int lo, int mid, int hi) {
        OperationCounter.recordMerge();
        int i = lo, j = mid + 1;
        for (int k = lo; k <= hi; k++) {
            if      (i > mid)              { dst[k] = src[j++]; OperationCounter.recordArrayWrite(1); }
            else if (j > hi)               { dst[k] = src[i++]; OperationCounter.recordArrayWrite(1); }
            else if (less(src[j], src[i])) { dst[k] = src[j++]; OperationCounter.recordArrayWrite(1); }
            else                           { dst[k] = src[i++]; OperationCounter.recordArrayWrite(1); }
        }
    }

    private static void sort(Comparable[] src, Comparable[] dst, int lo, int hi, int cutoff) {
        if (hi <= lo + cutoff) {
            InstrumentedInsertion.sort(dst, lo, hi + 1);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(dst, src, lo, mid, cutoff);
        sort(dst, src, mid + 1, hi, cutoff);

        if (!less(src[mid + 1], src[mid])) {
            System.arraycopy(src, lo, dst, lo, hi - lo + 1);
            OperationCounter.recordArrayWrite(hi - lo + 1);
            return;
        }

        merge(src, dst, lo, mid, hi);
    }

    public static void sort(Comparable[] a, int cutoff) {
        Comparable[] aux = a.clone();
        OperationCounter.recordArrayWrite(a.length);
        sort(aux, a, 0, a.length - 1, cutoff);
    }

    private static boolean less(Comparable v, Comparable w) {
        return v.compareTo(w) < 0;
    }
}
