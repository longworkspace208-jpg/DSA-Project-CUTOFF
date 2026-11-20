package edu.princeton.cs.algs4;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.util.Arrays;
import java.util.Random;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class CutoffCorrectnessTest {

    private static final int SEED = 42;
    private static final int[] CUTOFFS = {1, 2, 4, 7, 8, 12, 16, 24, 32, 64};
    private static final int[] SIZES = {0, 1, 2, 5, 10, 15, 20, 50, 100, 500, 1000};

    private Integer[] generateRandomArray(int n, Random rng) {
        Integer[] a = new Integer[n];
        for (int i = 0; i < n; i++) {
            a[i] = rng.nextInt(10000);
        }
        return a;
    }

    private Integer[] generateSortedArray(int n) {
        Integer[] a = new Integer[n];
        for (int i = 0; i < n; i++) {
            a[i] = i;
        }
        return a;
    }

    private Integer[] generateReverseArray(int n) {
        Integer[] a = new Integer[n];
        for (int i = 0; i < n; i++) {
            a[i] = n - i;
        }
        return a;
    }

    private Integer[] generateDuplicateArray(int n, Random rng) {
        Integer[] a = new Integer[n];
        for (int i = 0; i < n; i++) {
            a[i] = rng.nextInt(5); // only 5 distinct values
        }
        return a;
    }

    private boolean isSorted(Comparable[] a) {
        for (int i = 1; i < a.length; i++) {
            if (a[i].compareTo(a[i - 1]) < 0) return false;
        }
        return true;
    }

    @Test
    @DisplayName("Verify MergeCutoff correctness across cutoffs and distributions")
    public void testMergeCutoff() {
        Random rng = new Random(SEED);
        for (int m : CUTOFFS) {
            for (int n : SIZES) {
                // Random
                Integer[] a = generateRandomArray(n, rng);
                Integer[] expected = a.clone();
                Arrays.sort(expected);
                MergeCutoff.sort(a, m);
                assertArrayEquals(expected, a, "MergeCutoff failed on random array n=" + n + ", m=" + m);
                assertTrue(isSorted(a));

                // Sorted
                a = generateSortedArray(n);
                expected = a.clone();
                MergeCutoff.sort(a, m);
                assertArrayEquals(expected, a);

                // Reverse
                a = generateReverseArray(n);
                expected = a.clone();
                Arrays.sort(expected);
                MergeCutoff.sort(a, m);
                assertArrayEquals(expected, a);

                // Duplicates
                a = generateDuplicateArray(n, rng);
                expected = a.clone();
                Arrays.sort(expected);
                MergeCutoff.sort(a, m);
                assertArrayEquals(expected, a);
            }
        }
    }

    @Test
    @DisplayName("Verify QuickCutoff (both sort and sortNoShuffle) correctness")
    public void testQuickCutoff() {
        Random rng = new Random(SEED);
        for (int m : CUTOFFS) {
            for (int n : SIZES) {
                // With shuffle
                Integer[] a = generateRandomArray(n, rng);
                Integer[] expected = a.clone();
                Arrays.sort(expected);
                QuickCutoff.sort(a, m);
                assertArrayEquals(expected, a);
                assertTrue(isSorted(a));

                // Without shuffle (sortNoShuffle)
                a = generateRandomArray(n, rng);
                expected = a.clone();
                Arrays.sort(expected);
                QuickCutoff.sortNoShuffle(a, m);
                assertArrayEquals(expected, a);
                assertTrue(isSorted(a));

                // Sorted
                a = generateSortedArray(n);
                expected = a.clone();
                QuickCutoff.sortNoShuffle(a, m);
                assertArrayEquals(expected, a);

                // Reverse
                a = generateReverseArray(n);
                expected = a.clone();
                Arrays.sort(expected);
                QuickCutoff.sortNoShuffle(a, m);
                assertArrayEquals(expected, a);

                // Duplicates
                a = generateDuplicateArray(n, rng);
                expected = a.clone();
                Arrays.sort(expected);
                QuickCutoff.sortNoShuffle(a, m);
                assertArrayEquals(expected, a);
            }
        }
    }

    @Test
    @DisplayName("Verify MergeXParam correctness")
    public void testMergeXParam() {
        Random rng = new Random(SEED);
        for (int cutoff : CUTOFFS) {
            for (int n : SIZES) {
                Integer[] a = generateRandomArray(n, rng);
                Integer[] expected = a.clone();
                Arrays.sort(expected);
                MergeXParam.sort(a, cutoff);
                assertArrayEquals(expected, a, "MergeXParam failed on random array n=" + n + ", cutoff=" + cutoff);
                assertTrue(isSorted(a));

                // Sorted (tests skip-if-sorted optimization)
                a = generateSortedArray(n);
                expected = a.clone();
                MergeXParam.sort(a, cutoff);
                assertArrayEquals(expected, a);

                // Reverse
                a = generateReverseArray(n);
                expected = a.clone();
                Arrays.sort(expected);
                MergeXParam.sort(a, cutoff);
                assertArrayEquals(expected, a);

                // Duplicates
                a = generateDuplicateArray(n, rng);
                expected = a.clone();
                Arrays.sort(expected);
                MergeXParam.sort(a, cutoff);
                assertArrayEquals(expected, a);
            }
        }
    }

    @Test
    @DisplayName("Verify QuickXParam correctness")
    public void testQuickXParam() {
        Random rng = new Random(SEED);
        for (int cutoff : CUTOFFS) {
            for (int n : SIZES) {
                Integer[] a = generateRandomArray(n, rng);
                Integer[] expected = a.clone();
                Arrays.sort(expected);
                QuickXParam.sort(a, cutoff);
                assertArrayEquals(expected, a, "QuickXParam failed on random array n=" + n + ", cutoff=" + cutoff);
                assertTrue(isSorted(a));

                // Sorted
                a = generateSortedArray(n);
                expected = a.clone();
                QuickXParam.sort(a, cutoff);
                assertArrayEquals(expected, a);

                // Reverse
                a = generateReverseArray(n);
                expected = a.clone();
                Arrays.sort(expected);
                QuickXParam.sort(a, cutoff);
                assertArrayEquals(expected, a);

                // Duplicates
                a = generateDuplicateArray(n, rng);
                expected = a.clone();
                Arrays.sort(expected);
                QuickXParam.sort(a, cutoff);
                assertArrayEquals(expected, a);
            }
        }
    }
}
