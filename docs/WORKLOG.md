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
