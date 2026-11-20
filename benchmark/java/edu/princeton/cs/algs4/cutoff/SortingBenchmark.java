package edu.princeton.cs.algs4.cutoff;

import edu.princeton.cs.algs4.MergeCutoff;
import edu.princeton.cs.algs4.MergeXParam;
import edu.princeton.cs.algs4.QuickCutoff;
import edu.princeton.cs.algs4.QuickXParam;
import org.openjdk.jmh.annotations.Benchmark;
import org.openjdk.jmh.annotations.BenchmarkMode;
import org.openjdk.jmh.annotations.Fork;
import org.openjdk.jmh.annotations.Level;
import org.openjdk.jmh.annotations.Mode;
import org.openjdk.jmh.annotations.OutputTimeUnit;
import org.openjdk.jmh.annotations.Param;
import org.openjdk.jmh.annotations.Scope;
import org.openjdk.jmh.annotations.Setup;
import org.openjdk.jmh.annotations.State;
import org.openjdk.jmh.annotations.TearDown;
import org.openjdk.jmh.infra.Blackhole;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.FileChannel;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.concurrent.TimeUnit;

@State(Scope.Benchmark)
@BenchmarkMode(Mode.SingleShotTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Fork(1)
public class SortingBenchmark {

    @Param({"MergeCutoff"})
    public String algo;

    @Param({"random"})
    public String dist;

    @Param({"100000"})
    public int n;

    @Param({"42"})
    public int seed;

    @Param({"16"})
    public int m;

    private Integer[] orig;
    private Integer[][] copies;
    private int K;
    private String expectedSortedChecksum;

    public static int determineK(int n) {
        if (n <= 1000) return 20;
        if (n <= 10000) return 5;
        return 1;
    }

    @Setup(Level.Trial)
    public void setupTrial() throws IOException {
        K = determineK(n);
        String filename = dist + "_" + n + "_" + seed + ".bin";
        File file = new File("data/" + filename);
        if (!file.exists()) {
            throw new IllegalArgumentException("Data file not found: " + file.getAbsolutePath());
        }

        // Read binary file
        try (FileChannel channel = FileChannel.open(file.toPath(), StandardOpenOption.READ)) {
            ByteBuffer buf = ByteBuffer.allocateDirect((int) file.length()).order(ByteOrder.LITTLE_ENDIAN);
            channel.read(buf);
            buf.flip();
            orig = new Integer[n];
            for (int i = 0; i < n; i++) {
                orig[i] = buf.getInt();
            }
        }

        // Read expected sorted checksum from data/MANIFEST.csv
        File manifestFile = new File("data/MANIFEST.csv");
        if (manifestFile.exists()) {
            try (BufferedReader reader = new BufferedReader(new FileReader(manifestFile))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String[] parts = line.split(",");
                    if (parts.length >= 7 && parts[0].equals(filename)) {
                        expectedSortedChecksum = parts[6].trim();
                        break;
                    }
                }
            }
        }
    }

    @Setup(Level.Iteration)
    public void setupIteration() {
        copies = new Integer[K][n];
        for (int k = 0; k < K; k++) {
            System.arraycopy(orig, 0, copies[k], 0, n);
        }
    }

    @Benchmark
    public void sortBatch(Blackhole bh) {
        for (int k = 0; k < K; k++) {
            Integer[] target = copies[k];
            switch (algo) {
                case "MergeCutoff":
                    MergeCutoff.sort(target, m);
                    break;
                case "QuickCutoff":
                    QuickCutoff.sortNoShuffle(target, m);
                    break;
                case "MergeXParam":
                    MergeXParam.sort(target, m);
                    break;
                case "QuickXParam":
                    QuickXParam.sort(target, m);
                    break;
                default:
                    throw new IllegalArgumentException("Unknown algorithm: " + algo);
            }
            bh.consume(target);
        }
    }

    @TearDown(Level.Iteration)
    public void tearDownIteration() throws NoSuchAlgorithmException {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] buf = new byte[4];

        for (int k = 0; k < K; k++) {
            md.reset();
            Integer[] target = copies[k];
            for (int i = 0; i < n; i++) {
                int val = target[i];
                if (i > 0 && val < target[i - 1]) {
                    throw new IllegalStateException("Array copy " + k + " is not sorted at index " + i);
                }
                buf[0] = (byte) (val & 0xFF);
                buf[1] = (byte) ((val >> 8) & 0xFF);
                buf[2] = (byte) ((val >> 16) & 0xFF);
                buf[3] = (byte) ((val >> 24) & 0xFF);
                md.update(buf);
            }

            if (expectedSortedChecksum != null) {
                String actualHex = HexFormat.of().formatHex(md.digest());
                if (!actualHex.equalsIgnoreCase(expectedSortedChecksum)) {
                    throw new IllegalStateException("Sorted checksum mismatch on copy " + k
                            + "! Expected: " + expectedSortedChecksum + ", Got: " + actualHex);
                }
            }
        }
    }
}
