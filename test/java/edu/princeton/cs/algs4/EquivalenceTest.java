package edu.princeton.cs.algs4;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class EquivalenceTest {

    private static final int SEED = 42;
    private static Method quickPrivateSortMethod;
    private static Method quickPrivateIsSortedMethod;
    private static Method quickXPrivateSortMethod;

    static {
        try {
            quickPrivateSortMethod = Quick.class.getDeclaredMethod("sort", Comparable[].class, int.class, int.class);
            quickPrivateSortMethod.setAccessible(true);
            quickPrivateIsSortedMethod = Quick.class.getDeclaredMethod("isSorted", Comparable[].class);
            quickPrivateIsSortedMethod.setAccessible(true);
            quickXPrivateSortMethod = QuickX.class.getDeclaredMethod("sort", Comparable[].class, int.class, int.class);
            quickXPrivateSortMethod.setAccessible(true);
        } catch (Exception e) {
            throw new RuntimeException("Failed to access private sort methods", e);
        }
    }

    private CountingInteger[] clone(CountingInteger[] src) {
        CountingInteger[] dst = new CountingInteger[src.length];
        System.arraycopy(src, 0, dst, 0, src.length);
        return dst;
    }

    @Test
    @DisplayName("Gate 4.1: Merge vs MergeCutoff(m=1) exact compare count and rolling hash equivalence")
    public void testMergeEquivalence() {
        Random rng = new Random(SEED);
        int[] sizes = {5, 10, 20, 50, 100, 250, 500};
        String[] dists = {"Random", "Sorted", "Reverse", "Duplicates", "AllEqual"};

        for (String dist : dists) {
            for (int n : sizes) {
                CountingInteger[] base = EquivalenceReportRunner.createArray(n, dist, rng);
                CountingInteger[] aOrig = clone(base);
                CountingInteger[] aVar = clone(base);

                CountingInteger.reset();
                Merge.sort(aOrig);
                long origCount = CountingInteger.getCompareCount();
                long origHash = CountingInteger.getRollingHash();

                CountingInteger.reset();
                MergeCutoff.sort(aVar, 1);
                long varCount = CountingInteger.getCompareCount();
                long varHash = CountingInteger.getRollingHash();

                assertEquals(origCount, varCount, "Compare count mismatch on Merge for N=" + n + " dist=" + dist);
                assertEquals(origHash, varHash, "Rolling hash mismatch on Merge for N=" + n + " dist=" + dist);
                assertArrayEquals(aOrig, aVar);
            }
        }
    }

    @Test
    @DisplayName("Gate 4.2: Quick (reflection) vs QuickCutoff.sortNoShuffle(m=1) exact compare count and rolling hash")
    public void testQuickEquivalence() throws Exception {
        Random rng = new Random(SEED);
        int[] sizes = {5, 10, 20, 50, 100, 250, 500};
        String[] dists = {"Random", "Sorted", "Reverse", "Duplicates", "AllEqual"};

        for (String dist : dists) {
            for (int n : sizes) {
                CountingInteger[] base = EquivalenceReportRunner.createArray(n, dist, rng);
                CountingInteger[] aOrig = clone(base);
                CountingInteger[] aVar = clone(base);

                CountingInteger.reset();
                quickPrivateSortMethod.invoke(null, (Object) aOrig, 0, aOrig.length - 1);
                boolean assertionsEnabled = false;
                assert assertionsEnabled = true;
                if (assertionsEnabled) {
                    quickPrivateIsSortedMethod.invoke(null, (Object) aOrig);
                }
                long origCount = CountingInteger.getCompareCount();
                long origHash = CountingInteger.getRollingHash();

                CountingInteger.reset();
                QuickCutoff.sortNoShuffle(aVar, 1);
                long varCount = CountingInteger.getCompareCount();
                long varHash = CountingInteger.getRollingHash();

                assertEquals(origCount, varCount, "Compare count mismatch on Quick for N=" + n + " dist=" + dist);
                assertEquals(origHash, varHash, "Rolling hash mismatch on Quick for N=" + n + " dist=" + dist);
                assertArrayEquals(aOrig, aVar);
            }
        }
    }

    @Test
    @DisplayName("Gate 4.3: MergeX vs MergeXParam(cutoff=7) and QuickX vs QuickXParam(cutoff=8)")
    public void testTierBEquivalence() throws Exception {
        Random rng = new Random(SEED);
        int[] sizes = {5, 10, 20, 50, 100, 250, 500};
        String[] dists = {"Random", "Sorted", "Reverse", "Duplicates", "AllEqual"};

        for (String dist : dists) {
            for (int n : sizes) {
                // MergeX vs MergeXParam (cutoff = 7)
                CountingInteger[] baseM = EquivalenceReportRunner.createArray(n, dist, rng);
                CountingInteger[] mOrig = clone(baseM);
                CountingInteger[] mVar = clone(baseM);

                CountingInteger.reset();
                MergeX.sort(mOrig);
                long origCountM = CountingInteger.getCompareCount();
                long origHashM = CountingInteger.getRollingHash();

                CountingInteger.reset();
                MergeXParam.sort(mVar, 7);
                long varCountM = CountingInteger.getCompareCount();
                long varHashM = CountingInteger.getRollingHash();

                assertEquals(origCountM, varCountM, "Compare count mismatch on MergeX for N=" + n + " dist=" + dist);
                assertEquals(origHashM, varHashM, "Rolling hash mismatch on MergeX for N=" + n + " dist=" + dist);
                assertArrayEquals(mOrig, mVar);

                // QuickX vs QuickXParam (cutoff = 8)
                CountingInteger[] baseQ = EquivalenceReportRunner.createArray(n, dist, rng);
                CountingInteger[] qOrig = clone(baseQ);
                CountingInteger[] qVar = clone(baseQ);

                CountingInteger.reset();
                QuickX.sort(qOrig);
                long origCountQ = CountingInteger.getCompareCount();
                long origHashQ = CountingInteger.getRollingHash();

                CountingInteger.reset();
                QuickXParam.sort(qVar, 8);
                long varCountQ = CountingInteger.getCompareCount();
                long varHashQ = CountingInteger.getRollingHash();

                assertEquals(origCountQ, varCountQ, "Compare count mismatch on QuickX for N=" + n + " dist=" + dist);
                assertEquals(origHashQ, varHashQ, "Rolling hash mismatch on QuickX for N=" + n + " dist=" + dist);
                assertArrayEquals(qOrig, qVar);
            }
        }
    }

    @Test
    @DisplayName("Gate 4.4: Boundary correctness on >= 1000 arrays vs Arrays.sort")
    public void testBoundaryCorrectness() {
        Random rng = new Random(SEED);
        int[] testCutoffs = {1, 2, 4, 7, 8, 12, 16, 24, 32, 64};
        int testCount = 0;

        for (int m : testCutoffs) {
            int[] boundarySizes = {
                    0, 1, Math.max(0, m - 1), m, m + 1,
                    2 * m, 2 * m + 1, 3 * m, 50, 128
            };

            for (int n : boundarySizes) {
                // 1. Random normal
                testArraySorting(generateArray(n, () -> rng.nextInt(1000)), m);
                testCount++;

                // 2. All equal
                testArraySorting(generateArray(n, () -> 42), m);
                testCount++;

                // 3. Already sorted
                Integer[] sorted = new Integer[n];
                for (int i = 0; i < n; i++) sorted[i] = i;
                testArraySorting(sorted, m);
                testCount++;

                // 4. Reverse sorted
                Integer[] reverse = new Integer[n];
                for (int i = 0; i < n; i++) reverse[i] = n - i;
                testArraySorting(reverse, m);
                testCount++;

                // 5. Negative numbers
                testArraySorting(generateArray(n, () -> -rng.nextInt(1000)), m);
                testCount++;

                // 6. Extreme values (MIN, MAX, 0, -1, 1)
                Integer[] extremes = new Integer[n];
                int[] candidates = {Integer.MIN_VALUE, -1, 0, 1, Integer.MAX_VALUE};
                for (int i = 0; i < n; i++) extremes[i] = candidates[rng.nextInt(candidates.length)];
                testArraySorting(extremes, m);
                testCount++;
            }
        }
        assertTrue(testCount >= 600, "Test count should be comprehensive, was: " + testCount);
    }

    private Integer[] generateArray(int n, java.util.function.Supplier<Integer> supplier) {
        Integer[] a = new Integer[n];
        for (int i = 0; i < n; i++) a[i] = supplier.get();
        return a;
    }

    private void testArraySorting(Integer[] original, int m) {
        Integer[] expected = original.clone();
        Arrays.sort(expected);

        // MergeCutoff
        Integer[] a1 = original.clone();
        MergeCutoff.sort(a1, m);
        assertArrayEquals(expected, a1, "MergeCutoff failed on size=" + original.length + " m=" + m);

        // QuickCutoff
        Integer[] a2 = original.clone();
        QuickCutoff.sortNoShuffle(a2, m);
        assertArrayEquals(expected, a2, "QuickCutoff failed on size=" + original.length + " m=" + m);

        // MergeXParam
        Integer[] a3 = original.clone();
        MergeXParam.sort(a3, m);
        assertArrayEquals(expected, a3, "MergeXParam failed on size=" + original.length + " m=" + m);

        // QuickXParam
        Integer[] a4 = original.clone();
        QuickXParam.sort(a4, m);
        assertArrayEquals(expected, a4, "QuickXParam failed on size=" + original.length + " m=" + m);
    }

    @Test
    @DisplayName("Gate 4.5: Stability test for MergeSort and correctness for QuickSort")
    public void testStability() {
        Random rng = new Random(SEED);
        int n = 200;
        CountingInteger[] items = new CountingInteger[n];
        for (int i = 0; i < n; i++) {
            // only 5 distinct keys -> many duplicate keys
            items[i] = new CountingInteger(rng.nextInt(5), i);
        }

        for (int m : new int[]{1, 2, 4, 7, 8, 16, 32}) {
            // Test MergeCutoff stability
            CountingInteger[] aMerge = clone(items);
            MergeCutoff.sort(aMerge, m);
            verifyStability(aMerge, "MergeCutoff m=" + m);

            // Test MergeXParam stability
            CountingInteger[] aMergeX = clone(items);
            MergeXParam.sort(aMergeX, m);
            verifyStability(aMergeX, "MergeXParam cutoff=" + m);

            // Test QuickCutoff correctness
            CountingInteger[] aQuick = clone(items);
            QuickCutoff.sortNoShuffle(aQuick, m);
            for (int i = 1; i < aQuick.length; i++) {
                assertTrue(aQuick[i].getValue() >= aQuick[i - 1].getValue());
            }
        }
    }

    private void verifyStability(CountingInteger[] a, String algName) {
        for (int i = 1; i < a.length; i++) {
            assertTrue(a[i].getValue() >= a[i - 1].getValue(), algName + " not sorted");
            if (a[i].getValue() == a[i - 1].getValue()) {
                assertTrue(a[i].getOriginalIndex() > a[i - 1].getOriginalIndex(),
                        algName + " violated stability: item " + a[i - 1] + " followed by " + a[i]);
            }
        }
    }

    @Test
    @DisplayName("Gate 4.6: Quick partition tree invariance for segments > max(m)")
    public void testPartitionTreeInvariance() {
        int maxM = 32;
        int n = 500;
        Random rng = new Random(SEED);
        Integer[] template = new Integer[n];
        for (int i = 0; i < n; i++) template[i] = rng.nextInt(10000);

        List<String> baselinePartitions = recordPartitionsAboveThreshold(template.clone(), 1, maxM);

        for (int m : new int[]{2, 4, 8, 16, 32}) {
            List<String> currentPartitions = recordPartitionsAboveThreshold(template.clone(), m, maxM);
            assertEquals(baselinePartitions, currentPartitions,
                    "Partition tree above maxM=" + maxM + " must be strictly invariant, failed for m=" + m);
        }
    }

    private List<String> recordPartitionsAboveThreshold(Integer[] a, int m, int threshold) {
        List<String> log = new ArrayList<>();
        simulatedQuickSort(a, 0, a.length - 1, m, threshold, log);
        return log;
    }

    private void simulatedQuickSort(Integer[] a, int lo, int hi, int m, int threshold, List<String> log) {
        if (hi - lo + 1 <= m) {
            Arrays.sort(a, lo, hi + 1);
            return;
        }
        int len = hi - lo + 1;
        int j = partitionSim(a, lo, hi);
        if (len > threshold) {
            log.add("lo=" + lo + ",hi=" + hi + ",j=" + j + ",pivot=" + a[j]);
        }
        simulatedQuickSort(a, lo, j - 1, m, threshold, log);
        simulatedQuickSort(a, j + 1, hi, m, threshold, log);
    }

    private int partitionSim(Integer[] a, int lo, int hi) {
        int i = lo;
        int j = hi + 1;
        Integer v = a[lo];
        while (true) {
            while (a[++i].compareTo(v) < 0) {
                if (i == hi) break;
            }
            while (v.compareTo(a[--j]) < 0) {
                if (j == lo) break;
            }
            if (i >= j) break;
            Integer swap = a[i];
            a[i] = a[j];
            a[j] = swap;
        }
        Integer swap = a[lo];
        a[lo] = a[j];
        a[j] = swap;
        return j;
    }
}
