package edu.princeton.cs.algs4.counts;

import edu.princeton.cs.algs4.CountingInteger;

/**
 * OperationCounter maintains exact operation counts during execution:
 * - Comparisons (via CountingInteger)
 * - Array writes
 * - Element exchanges
 * - Insertion sort calls, compares, and exchanges
 * - Merge calls / Partition calls
 */
public class OperationCounter {

    private static long arrayWrites = 0L;
    private static long exchanges = 0L;
    private static long insertionSortCalls = 0L;
    private static long insertionCompares = 0L;
    private static long insertionExchanges = 0L;
    private static long mergeCalls = 0L;
    private static long partitionCalls = 0L;

    private static long insertionStartCompares = 0L;

    public static synchronized void reset() {
        CountingInteger.reset();
        arrayWrites = 0L;
        exchanges = 0L;
        insertionSortCalls = 0L;
        insertionCompares = 0L;
        insertionExchanges = 0L;
        mergeCalls = 0L;
        partitionCalls = 0L;
        insertionStartCompares = 0L;
    }

    public static synchronized void recordArrayWrite(long count) {
        arrayWrites += count;
    }

    public static synchronized void recordExch() {
        exchanges++;
        arrayWrites += 2; // a[i] = a[j]; a[j] = swap;
    }

    public static synchronized void startInsertionSort() {
        insertionSortCalls++;
        insertionStartCompares = CountingInteger.getCompareCount();
    }

    public static synchronized void endInsertionSort() {
        long comps = CountingInteger.getCompareCount() - insertionStartCompares;
        insertionCompares += comps;
    }

    public static synchronized void recordInsertionExch() {
        insertionExchanges++;
        exchanges++;
        arrayWrites += 2;
    }

    public static synchronized void recordMerge() {
        mergeCalls++;
    }

    public static synchronized void recordPartition() {
        partitionCalls++;
    }

    public static synchronized long getCompares() {
        return CountingInteger.getCompareCount();
    }

    public static synchronized long getArrayWrites() {
        return arrayWrites;
    }

    public static synchronized long getExchanges() {
        return exchanges;
    }

    public static synchronized long getInsertionSortCalls() {
        return insertionSortCalls;
    }

    public static synchronized long getInsertionCompares() {
        return insertionCompares;
    }

    public static synchronized long getInsertionExchanges() {
        return insertionExchanges;
    }

    public static synchronized long getMergeCalls() {
        return mergeCalls;
    }

    public static synchronized long getPartitionCalls() {
        return partitionCalls;
    }
}
