package edu.princeton.cs.algs4;

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

public class EquivalenceReportRunner {

    public static class EquivalenceResult {
        public String algorithm;
        public String distribution;
        public int size;
        public int seed;
        public int cutoffParam;
        public long origCompares;
        public long varCompares;
        public boolean countMatch;
        public long origHash;
        public long varHash;
        public boolean hashMatch;
        public boolean arrayMatch;

        public boolean isFullyEquivalent() {
            return countMatch && hashMatch && arrayMatch;
        }
    }

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
        } catch (NoSuchMethodException e) {
            throw new RuntimeException("Reflection failed to access Princeton quicksort methods", e);
        }
    }

    public static CountingInteger[] createArray(int n, String dist, Random rng) {
        CountingInteger[] a = new CountingInteger[n];
        switch (dist) {
            case "Random":
                for (int i = 0; i < n; i++) a[i] = new CountingInteger(rng.nextInt(10000), i);
                break;
            case "Sorted":
                for (int i = 0; i < n; i++) a[i] = new CountingInteger(i, i);
                break;
            case "Reverse":
                for (int i = 0; i < n; i++) a[i] = new CountingInteger(n - i, i);
                break;
            case "Duplicates":
                for (int i = 0; i < n; i++) a[i] = new CountingInteger(rng.nextInt(5), i);
                break;
            case "AllEqual":
                for (int i = 0; i < n; i++) a[i] = new CountingInteger(42, i);
                break;
            default:
                throw new IllegalArgumentException("Unknown distribution: " + dist);
        }
        return a;
    }

    public static CountingInteger[] cloneArray(CountingInteger[] src) {
        CountingInteger[] dst = new CountingInteger[src.length];
        System.arraycopy(src, 0, dst, 0, src.length);
        return dst;
    }

    public static EquivalenceResult testMerge(int n, String dist, int seed) {
        Random rng = new Random(seed);
        CountingInteger[] base = createArray(n, dist, rng);
        CountingInteger[] aOrig = cloneArray(base);
        CountingInteger[] aVar = cloneArray(base);

        // Run Original Merge
        CountingInteger.reset();
        Merge.sort(aOrig);
        long origCount = CountingInteger.getCompareCount();
        long origHash = CountingInteger.getRollingHash();

        // Run Variant MergeCutoff (m = 1)
        CountingInteger.reset();
        MergeCutoff.sort(aVar, 1);
        long varCount = CountingInteger.getCompareCount();
        long varHash = CountingInteger.getRollingHash();

        EquivalenceResult res = new EquivalenceResult();
        res.algorithm = "Merge vs MergeCutoff";
        res.distribution = dist;
        res.size = n;
        res.seed = seed;
        res.cutoffParam = 1;
        res.origCompares = origCount;
        res.varCompares = varCount;
        res.countMatch = (origCount == varCount);
        res.origHash = origHash;
        res.varHash = varHash;
        res.hashMatch = (origHash == varHash);
        res.arrayMatch = Arrays.equals(aOrig, aVar);
        return res;
    }

    public static EquivalenceResult testQuick(int n, String dist, int seed) {
        Random rng = new Random(seed);
        CountingInteger[] base = createArray(n, dist, rng);
        CountingInteger[] aOrig = cloneArray(base);
        CountingInteger[] aVar = cloneArray(base);

        // Run Original Quick (via reflection sort without shuffle)
        CountingInteger.reset();
        try {
            quickPrivateSortMethod.invoke(null, (Object) aOrig, 0, aOrig.length - 1);
            boolean assertionsEnabled = false;
            assert assertionsEnabled = true;
            if (assertionsEnabled) {
                quickPrivateIsSortedMethod.invoke(null, (Object) aOrig);
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
        long origCount = CountingInteger.getCompareCount();
        long origHash = CountingInteger.getRollingHash();

        // Run Variant QuickCutoff.sortNoShuffle (m = 1)
        CountingInteger.reset();
        QuickCutoff.sortNoShuffle(aVar, 1);
        long varCount = CountingInteger.getCompareCount();
        long varHash = CountingInteger.getRollingHash();

        EquivalenceResult res = new EquivalenceResult();
        res.algorithm = "Quick vs QuickCutoff";
        res.distribution = dist;
        res.size = n;
        res.seed = seed;
        res.cutoffParam = 1;
        res.origCompares = origCount;
        res.varCompares = varCount;
        res.countMatch = (origCount == varCount);
        res.origHash = origHash;
        res.varHash = varHash;
        res.hashMatch = (origHash == varHash);
        res.arrayMatch = Arrays.equals(aOrig, aVar);
        return res;
    }

    public static EquivalenceResult testMergeX(int n, String dist, int seed) {
        Random rng = new Random(seed);
        CountingInteger[] base = createArray(n, dist, rng);
        CountingInteger[] aOrig = cloneArray(base);
        CountingInteger[] aVar = cloneArray(base);

        // Run Original MergeX (CUTOFF = 7)
        CountingInteger.reset();
        MergeX.sort(aOrig);
        long origCount = CountingInteger.getCompareCount();
        long origHash = CountingInteger.getRollingHash();

        // Run Variant MergeXParam (cutoff = 7)
        CountingInteger.reset();
        MergeXParam.sort(aVar, 7);
        long varCount = CountingInteger.getCompareCount();
        long varHash = CountingInteger.getRollingHash();

        EquivalenceResult res = new EquivalenceResult();
        res.algorithm = "MergeX vs MergeXParam";
        res.distribution = dist;
        res.size = n;
        res.seed = seed;
        res.cutoffParam = 7;
        res.origCompares = origCount;
        res.varCompares = varCount;
        res.countMatch = (origCount == varCount);
        res.origHash = origHash;
        res.varHash = varHash;
        res.hashMatch = (origHash == varHash);
        res.arrayMatch = Arrays.equals(aOrig, aVar);
        return res;
    }

    public static EquivalenceResult testQuickX(int n, String dist, int seed) {
        Random rng = new Random(seed);
        CountingInteger[] base = createArray(n, dist, rng);
        CountingInteger[] aOrig = cloneArray(base);
        CountingInteger[] aVar = cloneArray(base);

        // Run Original QuickX (INSERTION_SORT_CUTOFF = 8)
        CountingInteger.reset();
        QuickX.sort(aOrig);
        long origCount = CountingInteger.getCompareCount();
        long origHash = CountingInteger.getRollingHash();

        // Run Variant QuickXParam (cutoff = 8)
        CountingInteger.reset();
        QuickXParam.sort(aVar, 8);
        long varCount = CountingInteger.getCompareCount();
        long varHash = CountingInteger.getRollingHash();

        EquivalenceResult res = new EquivalenceResult();
        res.algorithm = "QuickX vs QuickXParam";
        res.distribution = dist;
        res.size = n;
        res.seed = seed;
        res.cutoffParam = 8;
        res.origCompares = origCount;
        res.varCompares = varCount;
        res.countMatch = (origCount == varCount);
        res.origHash = origHash;
        res.varHash = varHash;
        res.hashMatch = (origHash == varHash);
        res.arrayMatch = Arrays.equals(aOrig, aVar);
        return res;
    }

    public static void generateReport(String outputPath) throws IOException {
        int[] sizes = {10, 50, 100, 500, 1000};
        String[] distributions = {"Random", "Sorted", "Reverse", "Duplicates", "AllEqual"};
        int[] seeds = {42, 1337, 2026};

        List<EquivalenceResult> results = new ArrayList<>();

        for (int seed : seeds) {
            for (String dist : distributions) {
                for (int n : sizes) {
                    results.add(testMerge(n, dist, seed));
                    results.add(testQuick(n, dist, seed));
                    results.add(testMergeX(n, dist, seed));
                    results.add(testQuickX(n, dist, seed));
                }
            }
        }

        boolean allMatched = true;
        for (EquivalenceResult r : results) {
            if (!r.isFullyEquivalent()) {
                allMatched = false;
                System.err.println("DISCREPANCY: " + r.algorithm + " dist=" + r.distribution + " N=" + r.size
                        + " orig=" + r.origCompares + " var=" + r.varCompares + " origHash=" + r.origHash + " varHash=" + r.varHash);
            }
        }

        try (PrintWriter out = new PrintWriter(new FileWriter(outputPath))) {
            out.println("# Chứng Minh Tính Tương Đương (Equivalence Proof)");
            out.println();
            out.println("Báo cáo kiểm thử trung thành với bản gốc Princeton algs4.");
            out.println("Mỗi phép đo so sánh bản gốc (chạy qua reflection để bỏ shuffle ngẫu nhiên với Quick) và bản biến thể trên cùng một mảng đối tượng `CountingInteger`.");
            out.println();
            out.println("## 1. Tiêu chuẩn đánh giá:");
            out.println("- **Số so sánh (Compare Count)**: Số lần gọi `compareTo` phải trùng khớp 100%.");
            out.println("- **Rolling Hash**: Hash chạy 64-bit của chuỗi cặp phần tử được so sánh theo đúng thứ tự gọi phải trùng khớp 100% (chứng minh đường đi thực thi y hệt).");
            out.println("- **Mảng kết quả**: Từng phần tử của mảng sau sắp xếp phải hoàn toàn giống nhau.");
            out.println();
            out.println("## 2. Bảng kết quả tổng hợp (Mẫu đại diện Seed=42):");
            out.println();
            out.println("| Thuật toán | Phân phối | N | Tham số m | So sánh Gốc | So sánh Biến thể | Khớp số? | Hash Gốc | Hash Biến thể | Khớp Hash? | Kết quả mảng |");
            out.println("|:---|:---|---:|---:|---:|---:|:---:|---:|---:|:---:|:---:|");

            for (EquivalenceResult r : results) {
                if (r.seed == 42) {
                    out.printf("| %s | %s | %d | %d | %d | %d | %s | %d | %d | %s | %s |\n",
                            r.algorithm, r.distribution, r.size, r.cutoffParam,
                            r.origCompares, r.varCompares, r.countMatch ? "YES" : "NO",
                            r.origHash, r.varHash, r.hashMatch ? "YES" : "NO",
                            r.arrayMatch ? "MATCH" : "DIFF");
                }
            }

            out.println();
            out.println("## 3. Tổng kết:");
            out.println("- Tổng số phép thử so sánh: " + results.size());
            out.println("- Số phép thử trùng khớp 100%: " + results.stream().filter(EquivalenceResult::isFullyEquivalent).count() + " / " + results.size());
            out.println("- Trạng thái Gate 4: " + (allMatched ? "**ĐẠT (PASSED)** - Chứng minh biến thể trung thành 100% với bản gốc." : "**THẤT BẠI (FAILED)**"));
        }

        if (!allMatched) {
            throw new IllegalStateException("Equivalence verification failed!");
        }
        System.out.println("Equivalence report successfully written to: " + outputPath);
    }

    public static void main(String[] args) throws Exception {
        String path = "docs/EQUIVALENCE.md";
        if (args.length > 0) path = args[0];
        generateReport(path);
    }
}
