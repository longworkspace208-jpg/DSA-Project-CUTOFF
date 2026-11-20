package edu.princeton.cs.algs4.counts;

import edu.princeton.cs.algs4.CountingInteger;

import java.io.File;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.FileChannel;
import java.nio.file.StandardOpenOption;

public class CountRunner {

    public static void main(String[] args) throws IOException {
        if (args.length < 5) {
            System.err.println("Usage: java CountRunner <algo> <dist> <n> <seed> <m>");
            System.exit(1);
        }

        String algo = args[0];
        String dist = args[1];
        int n = Integer.parseInt(args[2]);
        int seed = Integer.parseInt(args[3]);
        int m = Integer.parseInt(args[4]);

        String filename = "data/" + dist + "_" + n + "_" + seed + ".bin";
        File file = new File(filename);
        if (!file.exists()) {
            System.err.println("Data file not found: " + file.getAbsolutePath());
            System.exit(1);
        }

        CountingInteger[] a = new CountingInteger[n];
        try (FileChannel channel = FileChannel.open(file.toPath(), StandardOpenOption.READ)) {
            ByteBuffer buf = ByteBuffer.allocateDirect((int) file.length()).order(ByteOrder.LITTLE_ENDIAN);
            channel.read(buf);
            buf.flip();
            for (int i = 0; i < n; i++) {
                a[i] = new CountingInteger(buf.getInt(), i);
            }
        }

        OperationCounter.reset();

        switch (algo) {
            case "MergeCutoff":
                InstrumentedMergeCutoff.sort(a, m);
                break;
            case "QuickCutoff":
                InstrumentedQuickCutoff.sortNoShuffle(a, m);
                break;
            case "MergeXParam":
                InstrumentedMergeXParam.sort(a, m);
                break;
            case "QuickXParam":
                InstrumentedQuickXParam.sort(a, m);
                break;
            default:
                throw new IllegalArgumentException("Unknown algorithm: " + algo);
        }

        // Verify sorted
        for (int i = 1; i < n; i++) {
            if (a[i].getValue() < a[i - 1].getValue()) {
                System.err.println("Array not sorted at index " + i);
                System.exit(2);
            }
        }

        long compares = OperationCounter.getCompares();
        long arrayWrites = OperationCounter.getArrayWrites();
        long exchanges = OperationCounter.getExchanges();
        long insComps = OperationCounter.getInsertionCompares();
        long insExchs = OperationCounter.getInsertionExchanges();
        long merges = OperationCounter.getMergeCalls();
        long partitions = OperationCounter.getPartitionCalls();

        System.out.printf(
            "{\"algo\":\"%s\",\"dist\":\"%s\",\"N\":%d,\"seed\":%d,\"m\":%d,\"compares\":%d,\"array_writes\":%d,\"exchanges\":%d,\"insertion_compares\":%d,\"insertion_exchanges\":%d,\"merges\":%d,\"partitions\":%d}%n",
            algo, dist, n, seed, m, compares, arrayWrites, exchanges, insComps, insExchs, merges, partitions
        );
    }
}
