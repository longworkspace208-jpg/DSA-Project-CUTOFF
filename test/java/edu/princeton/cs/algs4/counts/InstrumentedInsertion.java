package edu.princeton.cs.algs4.counts;

/**
 * Instrumented version of Insertion sort from Princeton algs4.
 * Tracks operations via OperationCounter.
 */
public class InstrumentedInsertion {

    private InstrumentedInsertion() { }

    public static void sort(Comparable[] a, int lo, int hi) {
        OperationCounter.startInsertionSort();
        try {
            for (int i = lo + 1; i < hi; i++) {
                for (int j = i; j > lo && less(a[j], a[j-1]); j--) {
                    exch(a, j, j-1);
                }
            }
        } finally {
            OperationCounter.endInsertionSort();
        }
    }

    private static boolean less(Comparable v, Comparable w) {
        return v.compareTo(w) < 0;
    }

    private static void exch(Object[] a, int i, int j) {
        Object swap = a[i];
        a[i] = a[j];
        a[j] = swap;
        OperationCounter.recordInsertionExch();
    }
}
