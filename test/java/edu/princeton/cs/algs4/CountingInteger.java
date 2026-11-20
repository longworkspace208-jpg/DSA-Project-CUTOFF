package edu.princeton.cs.algs4;

import java.util.Objects;

/**
 * CountingInteger wraps an int value and tracks the number of compareTo calls
 * as well as a rolling hash of all comparison operands in order of invocation.
 * Does not modify any Princeton algs4 classes.
 */
public class CountingInteger implements Comparable<CountingInteger> {

    private final int value;
    private final int originalIndex;

    private static long compareCount = 0L;
    private static long rollingHash = 0L;
    private static boolean trackingEnabled = true;

    public CountingInteger(int value, int originalIndex) {
        this.value = value;
        this.originalIndex = originalIndex;
    }

    public CountingInteger(int value) {
        this(value, 0);
    }

    public int getValue() {
        return value;
    }

    public int getOriginalIndex() {
        return originalIndex;
    }

    public static synchronized void reset() {
        compareCount = 0L;
        rollingHash = 0L;
        trackingEnabled = true;
    }

    public static synchronized void setTrackingEnabled(boolean enabled) {
        trackingEnabled = enabled;
    }

    public static synchronized long getCompareCount() {
        return compareCount;
    }

    public static synchronized long getRollingHash() {
        return rollingHash;
    }

    @Override
    public int compareTo(CountingInteger other) {
        if (trackingEnabled) {
            compareCount++;
            // 64-bit polynomial rolling hash
            rollingHash = rollingHash * 31L + ((long) this.value * 37L + (long) other.value);
        }
        return Integer.compare(this.value, other.value);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof CountingInteger that)) return false;
        return this.value == that.value && this.originalIndex == that.originalIndex;
    }

    @Override
    public int hashCode() {
        return Objects.hash(value, originalIndex);
    }

    @Override
    public String toString() {
        return value + "(@idx=" + originalIndex + ")";
    }
}
