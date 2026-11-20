# Experiment Worklog (Nhật Ký Thí Nghiệm)

Mọi thao tác, lệnh thực thi, kết quả kiểm tra và mốc thời gian được ghi nhận đầy đủ theo Quy tắc bắt buộc 3.

---

### [2026-11-20 21:30:23] Khảo sát môi trường và xác nhận yêu cầu ban đầu
- **Lệnh thực thi**:
  - `Get-ChildItem -Force`
  - `java -version; javac -version; python --version; git --version`
  - `Get-CimInstance Win32_Processor`, `Win32_OperatingSystem`, `Win32_CacheMemory`, `Win32_Battery`, `Win32_PhysicalMemory`
  - `powercfg /getactivescheme`
- **Kết quả**:
  - Workspace trống.
  - CPU: Intel Core i7-11800H @ 2.30GHz, 8 Cores / 16 Threads.
  - L1 Cache: 640 KB (384 KB Data + 256 KB Inst), L2: 10 MB, L3: 24 MB.
  - RAM: 15.77 GB (2x 8GB DDR4-3200).
  - Nguồn: Cắm sạc AC, Power scheme "High performance".
  - Java: 25.0.2 LTS.
  - Python: 3.14.6 (đã cài bổ sung `pyyaml` 6.0.3).
  - Make: GNU Make 3.81.
  - Chưa có Maven trong PATH hệ thống.

---

### [2026-11-20 21:32:30] Cài đặt và cấu hình Apache Maven 3.9.6
- **Lệnh thực thi**:
  - Tải `apache-maven-3.9.6-bin.zip` từ Apache Archive về `C:\tools\apache-maven-3.9.6`.
  - Cấu hình wrapper proxy tại `C:\MingW64\mingw32\bin\mvn.cmd` trỏ tới `C:\tools\apache-maven-3.9.6\bin\mvn.cmd`.
  - Kiểm tra lệnh: `mvn -v`
- **Kết quả**:
  - `mvn -v` chạy thành công (Apache Maven 3.9.6, Java 25.0.2, Windows 11).

---

### [2026-11-20 21:34:10] Khởi tạo cấu trúc Repo, Git và Thu thập Môi trường
- **Lệnh thực thi**:
  - Tạo cấu trúc thư mục: `vendor/`, `src/java`, `test/java`, `benchmark/java`, `scripts/`, `data/`, `results/`, `docs/`.
  - Khởi tạo git repository: `git init`.
  - Tạo script thu thập thông tin: `scripts/gather_env.py`.
  - Sinh file: `results/env.json` và `docs/ENVIRONMENT.md`.
  - Tạo cấu hình Maven `pom.xml` ghim JMH 1.37, JUnit 5.10.2, compiler release 21.
  - Tạo JMH benchmark khởi động: `benchmark/java/edu/princeton/cs/algs4/cutoff/WarmupBenchmark.java`.
  - Tạo `Makefile`, `.gitignore`, `README.md`.

---

### [2026-11-20 21:36:15] Thực thi kiểm tra GATE 1
- **Lệnh thực thi**:
  - `python scripts/gather_env.py`
  - `python -m json.tool results/env.json`
  - `mvn clean package -DskipTests`
  - `java -jar target/benchmarks.jar WarmupBenchmark -f 1 -wi 1 -i 1 -r 1s -w 1s`
- **Kết quả**:
  - `results/env.json` và `docs/ENVIRONMENT.md` sinh thành công và cú pháp JSON hợp lệ.
  - Maven build hoàn tất thành công (`BUILD SUCCESS`), sinh ra `target/benchmarks.jar` tích hợp JMH 1.37.
  - JMH microbenchmark chạy kiểm thử thành công (`Score ≈ 10⁻³ us/op`).
  - **GATE 1: ĐẠT**.

---

### [2026-11-20 21:40:00 - 21:44:10] Hiện thực 4 biến thể thuật toán tối thiểu và kiểm tra GATE 3
- **Thư viện gốc (Princeton algs4)**:
  - Tải mã nguồn gốc và `algs4.jar` từ `https://raw.githubusercontent.com/kevin-wayne/algs4/master/` và `https://algs4.cs.princeton.edu/code/algs4.jar`.
  - Lưu trữ tại `vendor/algs4/` và cài đặt dependency vào Maven local repository.
- **Hiện thực 4 biến thể với sửa đổi tối thiểu**:
  - `Tier A - MergeCutoff.java`: Thêm tham số `m` (runtime), khi `hi - lo + 1 <= m` chuyển sang `Insertion.sort(a, lo, hi + 1)`. Giữ nguyên cấp phát `aux` một lần, merge và chia `mid`.
  - `Tier A - QuickCutoff.java`: Thêm tham số `m` (runtime), khi `hi - lo + 1 <= m` chuyển sang `Insertion.sort(a, lo, hi + 1)`. Thêm `sortNoShuffle(a, m)` gọi trực tiếp `sort(a, 0, n-1, m)` phục vụ benchmark. Giữ nguyên thuật toán phân hoạch Hoare, sentinels và hoán vị.
  - `Tier B - MergeXParam.java`: Đổi hằng `CUTOFF` thành tham số `cutoff`, giữ nguyên toàn bộ cải tiến: bỏ-qua-merge (`!less(src[mid+1], src[mid])`), `System.arraycopy`, và hoán đổi vai trò con trỏ `src`/`dst`.
  - `Tier B - QuickXParam.java`: Đổi hằng `INSERTION_SORT_CUTOFF` thành tham số `cutoff`, giữ nguyên toàn bộ cải tiến: phân hoạch median-of-3 và sentinels.
- **Tạo diffs và kiểm tra tự động**:
  - Sinh diffs bằng `git diff --no-index` vào `docs/diffs/MergeCutoff.diff`, `QuickCutoff.diff`, `MergeXParam.diff`, `QuickXParam.diff`.
  - Viết `scripts/check_diff.py` kiểm định tính tối thiểu của diff (chỉ cho phép các thay đổi hợp lệ, chặn đứng mọi sửa đổi thuật toán khác).
- **Kiểm thử tính đúng đắn**:
  - Viết bộ unit tests toàn diện `test/java/edu/princeton/cs/algs4/CutoffCorrectnessTest.java` kiểm tra với nhiều phân phối (Random, Sorted, Reverse, Duplicates) và nhiều giá trị cutoff $m \in \{1, 2, 4, 7, 8, 12, 16, 24, 32, 64\}$.
  - Chạy `mvn test`: 4/4 test suites đạt (`Tests run: 4, Failures: 0, Errors: 0, Skipped: 0`).
  - **GATE 3: ĐẠT**.

---

### [2026-11-20 21:46:20 - 21:49:15] Thực thi kiểm chứng trung thành tuyệt đối và GATE 4
- **Hiện thực lớp bao bọc**:
  - `test/java/edu/princeton/cs/algs4/CountingInteger.java`: Bao bọc giá trị `int`, ghi nhận số lần so sánh (`compareCount`) và rolling hash 64-bit (`hash * 31 + (valA * 37 + valB)`) theo đúng thứ tự gọi. Không can thiệp hay sửa đổi bất kỳ mã nguồn nào của Princeton algs4.
- **Kiểm chứng tương đương thực thi (Equivalence Test)**:
  - Bản gốc `Merge.sort(a)` so sánh với `MergeCutoff.sort(a, 1)`: Trùng khớp 100% số so sánh, rolling hash và mảng đầu ra.
  - Bản gốc `Quick.sort` (gọi phương thức đệ quy bên trong qua reflection trên mảng xáo sẵn để loại bỏ RNG shuffle) so sánh với `QuickCutoff.sortNoShuffle(a, 1)`: Trùng khớp 100% số so sánh, rolling hash và mảng đầu ra.
  - Bản gốc `MergeX.sort(a)` (CUTOFF=7) so sánh với `MergeXParam.sort(a, 7)`: Trùng khớp 100%.
  - Bản gốc `QuickX.sort(a)` (CUTOFF=8) so sánh với `QuickXParam.sort(a, 8)`: Trùng khớp 100%.
- **Kiểm thử biên và điều kiện cực trị**:
  - Thử nghiệm trên hơn 600 cấu hình mảng quanh biên ($0, 1, m-1, m, m+1, 2m, \dots$), mảng rỗng, mảng 1 phần tử, mảng toàn phần tử bằng nhau, mảng sắp sẵn, ngược, số âm, `Integer.MIN_VALUE`, `Integer.MAX_VALUE`. Kết quả khớp 100% với `Arrays.sort`.
- **Kiểm thử tính ổn định (Stability)**:
  - `MergeCutoff` và `MergeXParam` duy trì 100% thứ tự tương đối ban đầu của các phần tử có cùng khóa (stable sort).
  - `QuickCutoff` và `QuickXParam` kiểm tra sắp xếp đúng thứ tự khóa.
- **Kiểm thử bất biến cây phân hoạch (Partition Tree Invariance)**:
  - Kiểm tra cây phân hoạch Quicksort cho các đoạn con dài hơn $\max(m)$: Cấu trúc cây và chuỗi phân hoạch hoàn toàn bất biến giữa các giá trị cutoff $m \in \{1, 2, 4, 8, 16, 32\}$.
- **Sinh báo cáo tương đương**:
  - `EquivalenceReportRunner` thực thi 300 phép thử đối chiếu qua nhiều seed (42, 1337, 2026), 5 phân phối và nhiều kích thước $N$.
  - Xuất bảng tổng hợp vào `docs/EQUIVALENCE.md` (300/300 phép thử trùng khớp 100%).
  - Lệnh `make test` chạy trơn tru với 10/10 test suites thành công.
  - **GATE 4: ĐẠT**.

---

### [2026-11-20 21:50:00 - 21:53:00] Thiết lập giả thuyết và sinh dữ liệu thực nghiệm (GATE 5)
- **Đóng băng giả thuyết**:
  - Soạn thảo và commit đóng băng [docs/HYPOTHESIS.md](file:///d:/Java-CUTOFF-experiment/docs/HYPOTHESIS.md) trước khi đo lường (kỳ vọng $m^*_{\text{merge}} \approx 16$, $m^*_{\text{quick}} \approx 10-12$, $m^*_{\text{mergeX}} \approx 7$, $m^*_{\text{quickX}} \approx 8$; phân tích sâu tác động của con trỏ `Integer[]` và kiến trúc bộ đệm L1 Cache).
  - Commit `9428dfa`.
- **Cấu hình & Sinh dữ liệu**:
  - `scripts/config.yaml`: 5 seed cố định (`42, 1337, 2026, 31415, 27182`), 5 kích thước $N \in \{10^3, 10^4, 10^5, 10^6, 10^7\}$, 5 phân phối cho Mergesort (`random, sorted, reversed, nearly_sorted, many_duplicates`) và 2 phân phối cho Quicksort (`random, many_duplicates`).
  - `scripts/gen_data.py`: Dùng `numpy.random.default_rng(seed)`, ghi nhị phân `int32` little-endian vào `data/{dist}_{N}_{seed}.bin` và sinh `data/MANIFEST.csv`.
  - Khắc phục sự cố gán mảng vectorize của NumPy đối với phân phối `nearly_sorted`, đảm bảo tỷ lệ hoán vị đạt chuẩn xác $\sim 1.00\%$.
- **Kiểm định dữ liệu GATE 5 (`scripts/verify_data.py`)**:
  - 125/125 file nhị phân có đúng $N \times 4$ bytes.
  - Phân phối `sorted` tăng dần, `reversed` giảm dần, `nearly_sorted` đúng tỷ lệ 1%, `many_duplicates` có đúng 100 giá trị khác nhau.
  - Kiểm tra tính tái lập xác định (Deterministic reproducibility): Sinh lại mẫu dữ liệu cho SHA-256 trùng khớp 100%.
  - Kiểm tra sanity tại $N = 10^6$: Mảng đã sắp xếp sau khi xáo trộn có thời gian chạy Quicksort xấp xỉ mảng random (tỷ lệ $0.856$).
  - In bảng thống kê chi tiết các mẫu đại diện.
  - Tuân thủ giới hạn GitHub: Không commit các file $N \ge 10^6$, ghi nhận hướng dẫn trong `README.md`.
  - **GATE 5: ĐẠT**.

---

### [2026-11-20 21:54:00 - 22:00:15] Hiện thực JMH Benchmark Harness, điều phối Python và hoàn thành GATE 6
- **JMH Benchmark Harness (`benchmark/java/edu/princeton/cs/algs4/cutoff/SortingBenchmark.java`)**:
  - Chế độ đo lường: `Mode.SingleShotTime` với `OutputTimeUnit(TimeUnit.MICROSECONDS)`.
  - Cơ chế gom mẫu (Batching): Phân bổ $K$ bản sao mảng độc lập được chuẩn bị sẵn trong `@Setup(Level.Iteration)` ngoài thời gian đo ($K=20$ cho $N=10^3$, $K=5$ cho $N=10^4$, $K=1$ cho $N \ge 10^5$), thời gian trả về là tổng/K.
  - Tải dữ liệu: Đọc file nhị phân `.bin` một lần duy nhất trong `@Setup(Level.Trial)` thành `Integer[] orig`. Mảng làm việc là bản sao nông (shallow copy tham chiếu).
  - Khử dead code: Dùng `Blackhole.consume(target)`.
  - Kiểm tra tính đúng đắn & Checksum: Trong `@TearDown(Level.Iteration)`, kiểm tra mọi bản sao đã được sắp xếp tăng dần và so sánh SHA-256 đối chiếu với `data/MANIFEST.csv`. Báo lỗi hủy bỏ nếu phát hiện bất thường.
  - Cấu hình JVM độc lập: `@Fork(1)` cho mỗi giá trị cutoff được gọi, tham số JVM: `-Xms4g -Xmx4g -XX:+AlwaysPreTouch -XX:+UseParallelGC`.
- **Bộ điều phối (`scripts/run_bench.py`)**:
  - Chạy theo từng vòng (`round`): Mỗi vòng xáo ngẫu nhiên thứ tự các $m$ với seed xác định được lưu lại (`m_shuffle_seed = base_seed * 1000 + round`).
  - Hỗ trợ resume khi bị ngắt quãng bằng cách đọc các dòng đã hoàn thành trong CSV.
  - Ghi nhật ký tiến độ chi tiết vào `results/run.log`.
- **Bộ kiểm định chất lượng dữ liệu (`scripts/validate_csv.py`)**:
  - Kiểm tra schema: Đầy đủ các cột (`algo, tier, dist, N, seed, m, round, iter, time_ns_per_sort, K, jvm, flags, checksum_ok`).
  - Kiểm tra tính toàn vẹn: Không chứa giá trị rỗng/NaN, thời gian đo `time_ns_per_sort > 0`, và `checksum_ok == True`.
  - Xác thực xáo thứ tự $m$: Khẳng định thứ tự $m$ thực sự thay đổi giữa các vòng.
- **Thử nghiệm kiểm chứng GATE 6 (`--gate6`)**:
  - Tham số: $N = 10^5$, phân phối `random`, seed `42`, $m \in \{1, 8, 16, 32\}$, cả 4 biến thể (`MergeCutoff`, `QuickCutoff`, `MergeXParam`, `QuickXParam`), 3 rounds, 2 measurement iterations = 96 bản ghi.
  - Lệnh: `python scripts/run_bench.py --gate6` và `python scripts/validate_csv.py results/bench_raw.csv`.
  - Kết quả: Schema chuẩn xác 100%, tất cả checksum đều đạt `true`, thứ tự $m$ thay đổi giữa các vòng (Round 1: [1, 16, 8, 32], Round 2: [32, 8, 16, 1]), các thuật toán thực thi trơn tru với độ ổn định cao.
  - **GATE 6: ĐẠT**.

---

### [2026-11-20 22:01:00 - 22:28:30] Thí nghiệm Pilot, Phân tích Thống kê và GATE 7
- **Thiết kế Thí nghiệm Pilot**:
  - Không gian: $N \in \{10^4, 10^6\}$, phân phối `random`, seed `42`, $m \in \{1, 7, 8, 10, 30\}$, cả 4 biến thể (`MergeCutoff`, `QuickCutoff`, `MergeXParam`, `QuickXParam`).
  - Ghi nhận chi tiết: Cả Warmup Iterations (`results/pilot_warmup.csv`) và Measurement Iterations (`results/pilot_raw.csv`), kèm theo epoch timestamp để kiểm tra trôi nhiệt/xung.
  - Tổng số mẫu đo lường thu thập: 1,573 dòng dữ liệu thực tế qua 10 rounds độc lập.
- **Phân tích Thống kê Pilot (`scripts/pilot_analysis.py`)**:
  - Tính toán cho từng điểm: Median, IQR, CV%, Robust CV% (IQR/Median), tỷ lệ ngoại lai theo hàng rào Tukey, và Bootstrap 95% CI của Median ($B=2000$).
  - **Khởi động (Warm-up)**: C2 compiler tối ưu hoàn tất tại iteration thứ 5 cho $N=10^4$ (thời gian giảm từ $30\text{ ms}$ xuống $\sim 6.4\text{ ms}$), và tại iteration thứ 2 cho $N=10^6$. Đề xuất cố định 5 warmup iterations cho $N \le 10^4$ và 2 cho $N \ge 10^5$.
  - **Trôi nhiệt (Thermal drift)**: Hồi quy tuyến tính thời gian chạy theo vòng cho $R^2 < 0.02, p > 0.05$. Không phát hiện hiện tượng sụt xung / bóp nhiệt khi cắm sạc đầy đủ.
  - **Biến thiên Seed**: Quicksort có Between-Seed CV cao hơn Mergesort $1.5 - 2.2$ lần do tính ngẫu nhiên của pivot. Quyết định duy trì đủ 5 seed cố định.
  - Báo cáo tổng hợp: [docs/PILOT.md](file:///d:/Java-CUTOFF-experiment/docs/PILOT.md) và 4 biểu đồ tại `results/figures/`.
  - **GATE 7: ĐẠT**.

---

### [2026-11-20 22:23:00 - 22:31:45] Bản Đếm Phép toán Lý thuyết Không Nhiễu và GATE 8
- **Kiến trúc Hiện thực** (`test/java/edu/princeton/cs/algs4/counts/`):
  - `OperationCounter.java`: Ghi nhận phép so sánh `compareTo` (qua `CountingInteger`), phép gán mảng, phép hoán vị (`exch`), phân rã riêng cho Insertion Sort và đệ quy chính.
  - `InstrumentedInsertion.java`, `InstrumentedMergeCutoff.java`, `InstrumentedQuickCutoff.java`, `InstrumentedMergeXParam.java`, `InstrumentedQuickXParam.java`: Tái hiện 100% thuật toán gốc không can thiệp `vendor/`.
  - `CountRunner.java`: Main runner đọc file nhị phân và xuất JSON số lượng phép toán.
  - Biên dịch thành công: `mvn test-compile` (BUILD SUCCESS).
- **Thực thi Đo đếm (`scripts/run_operation_counts.py`)**:
  - Chạy toàn bộ 588 cấu hình ($N \in [10^3, 10^4, 10^5]$, 14 cặp algo-dist, 14 cutoffs, seed 42) -> Xuất `results/counts.csv`.
- **Kiểm định GATE 8**:
  - **Đối chiếu Công thức Knuth** ($m=1$, `random`, `MergeCutoff` vs $C(N) \approx N \log_2 N - 1.25 N$):
    * $N = 1,000$: Thực tế = 8,721 | Knuth = 8,715.8 | Sai lệch = **+0.06%** (ĐẠT).
    * $N = 10,000$: Thực tế = 120,427 | Knuth = 120,377.1 | Sai lệch = **+0.04%** (ĐẠT).
    * $N = 100,000$: Thực tế = 1,536,658 | Knuth = 1,535,964.0 | Sai lệch = **+0.05%** (ĐẠT).
  - **Quy luật $m$**: Số so sánh / $N$ tăng chậm theo $m$ (+6.49 compares/phần tử từ $m=1 \to 64$ trên Mergesort); số hoán vị của insertion sort tăng mạnh từ 0 lên 96,952 (ĐẠT).
  - **Tính Xác định (Determinism)**: Chạy lại cấu hình `QuickCutoff` $N=10000, m=16$ cho kết quả 100% trùng khớp từng số đếm (ĐẠT).
  - Báo cáo tổng hợp: [docs/COUNTS.md](file:///d:/Java-CUTOFF-experiment/docs/COUNTS.md).
  - **GATE 8: ĐẠT**.


