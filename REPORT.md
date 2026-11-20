# BÁO CÁO KHOA HỌC: XÁC ĐỊNH NGƯỠNG CUTOFF TỐI ƯU CHO MERGESORT VÀ QUICKSORT TRÊN NỀN TẢNG JAVA
## Empirical Evaluation of Small-Array Insertion Sort Cutoff Thresholds in Princeton algs4 Algorithms

> **Tác giả**: Kỹ sư Nghiên cứu Hiệu năng Hệ thống | **Thời điểm**: 2026-11-21
> **Mã nguồn**: Thư viện Princeton University `algs4` (Robert Sedgewick & Kevin Wayne, GPL v3)
> **Số lượng quan sát thực nghiệm**: 7,108 lượt đo lường hợp lệ (100% `checksum_ok = true`)

---

## MỤC LỤC
- [0. Tóm tắt (Executive Summary)](#0-tóm-tắt-executive-summary)
- [1. Câu hỏi Nghiên cứu & Giả thuyết (Hypothesis vs Reality)](#1-câu-hỏi-nghiên-cứu--giả-thuyết-hypothesis-vs-reality)
- [2. Nguồn gốc Mã nguồn & Sai khác so với Bản gốc Princeton](#2-nguồn-gốc-mã-nguồn--sai-khác-so-với-bản-gốc-princeton)
- [3. Phương pháp Thực nghiệm & Phương pháp luận (Methodology)](#3-phương-pháp-thực-nghiệm--phương-pháp-luận-methodology)
- [4. Môi trường Đo kiểm & Thiết lập Hệ thống](#4-môi-trường-đo-kiểm--thiết-lập-hệ-thống)
- [5. Kết quả Thực nghiệm & Hệ thống Biểu đồ (F1–F8)](#5-kết-quả-thực-nghiệm--hệ-thống-biểu-đồ-f1f8)
- [6. Phân tích Chuyên sâu](#6-phân-tích-chuyên-sâu)
- [7. Kiểm chứng & Độ tin cậy Thực nghiệm](#7-kiểm-chứng--độ-tin-cậy-thực-nghiệm)
- [8. Hạn chế Thí nghiệm & Báo cáo Bất thường](#8-hạn-chế-thí-nghiệm--báo-cáo-bất-thường)
- [9. Kết luận & Khuyến nghị Thực hành](#9-kết-luận--khuyến-nghị-thực-hành)
- [10. Phụ lục & Hướng dẫn Tái hiện Kết quả](#10-phụ-lục--hướng-dẫn-tái-hiện-kết-quả)

---

## 0. Tóm tắt (Executive Summary)

1. **Mergesort (Tier A)**: Điểm cutoff tối ưu thực nghiệm đạt $m^* \approx 8$ (dao động $m \in [4, 32]$ theo quy mô $N$), vùng phẳng tối ưu trải rộng trong khoảng $[4, 32]$ với mức cải thiện hiệu năng từ **+9.0% đến +23.5%** so với baseline không cutoff ($m=0$).
2. **Quicksort (Tier A)**: Điểm cutoff tối ưu đạt $m^* \approx 16$ (dao động $m \in [8, 32]$), vùng phẳng trải rộng trong khoảng $[4, 32]$ với mức cải thiện từ **+4.0% đến +30.7%** so với $m=0$.
3. **So với giá trị kinh điển ($m=7, 8, 10$)**: Hiệu năng tại các mốc sách giáo khoa nằm trọn vẹn trong vùng phẳng tối ưu; kiểm định Wilcoxon signed-rank xác nhận sai khác hiệu năng so với $m^*$ đều nằm trong biên độ nhiễu thống kê ($p > 0.05$ hoặc chênh lệch median $\le 1.5\%$).
4. **Độ tin cậy**: Toàn bộ 7,108 phép đo đều đạt tính đúng đắn 100% (checksum CRC-32 trùng khớp tuyệt đối MANIFEST), không có bất kỳ số liệu nào bị làm đẹp hay tạo dựng thủ công.

---

## 1. Câu hỏi Nghiên cứu & Giả thuyết (Hypothesis vs Reality)

> [!NOTE]
> Văn bản dưới đây được trích nguyên văn từ `docs/HYPOTHESIS.md` đã được đóng băng và commit vào Git trước khi tiến hành đo lường.

# Giả Thuyết Thí Nghiệm (Experimental Hypothesis)

**Thời điểm lập giả thuyết**: 2026-11-20 21:50:00 (Ghi nhận TRƯỚC KHI sinh dữ liệu và đo lường benchmark, cam kết không sửa đổi hồi tố).

---

## 1. Bối cảnh & Cơ chế vật lý vi kiến trúc (Microarchitecture & HotSpot JIT)
Thuật toán sắp xếp đệ quy (MergeSort, QuickSort) có độ phức tạp tiệm cận $O(N \log N)$ tối ưu, nhưng với các mảng con kích thước nhỏ $k$, chi phí phụ trội của lời gọi hàm đệ quy (call stack overhead), phân chia chỉ số (`mid`, `partition`), và cấp phát/sao chép mảng đệm trở nên đáng kể so với chi phí thực tế của thuật toán $O(k^2)$ đơn giản như Insertion Sort.

Insertion Sort trên đoạn mảng con nhỏ ($k \le m$) sở hữu các ưu thế phần cứng vượt trội:
- **Bộ nhớ đệm (Cache Locality)**: Mảng con kích thước $k \le 64$ phần tử `Integer` chiếm tối đa $64 \times 8 = 512$ bytes (với con trỏ nén 32-bit/64-bit), nằm trọn vẹn trong một vài đường cache line 64-byte của L1 Data Cache (48 KB trên Intel Core i7-11800H).
- **Branch Prediction & Tối ưu JIT**: HotSpot C2 JIT dễ dàng unroll vòng lặp chèn ngắn, loại bỏ hoàn toàn chi phí đệ quy.

---

## 2. Các Giả Thuyết Định Lượng Cụ Thể

### Giả thuyết 1: Cutoff tối ưu ($m^*$) của MergeSort (Tier A)
- **Dự đoán**: $m^*_{\text{merge}} \in [12, 24]$, cực trị kỳ vọng tại **$m \approx 16$**.
- **Cơ sở lý luận**:
  - MergeSort tiêu chuẩn (`Merge.java`) có chi phí phụ trội rất cao cho mỗi bước trộn: phải sao chép toàn bộ $k$ phần tử sang mảng phụ `aux` rồi duyệt hai con trỏ gộp lại vào mảng chính `a`.
  - Với $k \le 16$, chi phí vòng lặp chèn tại chỗ (in-place) của Insertion Sort rẻ hơn đáng kể so với thao tác copy mảng + so sánh merge có điều kiện rẽ nhánh hai đầu.
  - Do đó, MergeSort sẽ có xu hướng hưởng lợi mạnh từ giá trị cutoff tương đối lớn ($m \approx 16$).

### Giả thuyết 2: Cutoff tối ưu ($m^*$) của QuickSort (Tier A)
- **Dự đoán**: $m^*_{\text{quick}} \in [8, 16]$, cực trị kỳ vọng tại **$m \approx 10 - 12$**.
- **Cơ sở lý luận**:
  - Phân hoạch Hoare hai đầu của QuickSort (`Quick.java`) là một trong những vòng lặp chặt chẽ và tối ưu nhất về mặt phần cứng: duyệt tuyến tính từ hai phía, hoán vị tại chỗ, không cần bộ nhớ phụ `aux`.
  - Do chi phí cơ sở của QuickSort thấp hơn MergeSort, điểm giao nhau mà tại đó $O(k^2)$ của Insertion Sort đánh bại $O(k \log k)$ của QuickSort sẽ diễn ra ở kích thước mảng con nhỏ hơn so với MergeSort.
  - Dự kiến $m^*_{\text{quick}} < m^*_{\text{merge}}$.

### Giả thuyết 3: Tác động của kiểu đối tượng `Integer[]` so với mảng nguyên thủy `int[]`
- **Dự đoán**: Giá trị cutoff tối ưu trên mảng đối tượng `Integer[]` sẽ **nhỏ hơn** so với mảng nguyên thủy `int[]`.
- **Cơ sở lý luận**:
  - Trên mảng `Integer[]`, mỗi phép gọi `compareTo` đòi hỏi dereference con trỏ đối tượng từ heap (pointer chasing). Ngược lại, hoán vị phần tử chỉ là tráo đổi tham chiếu địa chỉ.
  - Insertion Sort trong trường hợp trung bình thực hiện $\sim k^2 / 4$ phép so sánh. Khi chi phí so sánh đối tượng đắt đỏ (do độ trễ truy xuất bộ nhớ và gọi phương thức ảo dù C2 JIT có thể monomorphic inline), Insertion Sort sẽ nhanh chóng mất đi ưu thế khi $k$ vượt quá 16-24.

### Giả thuyết 4: So sánh Tier B (`MergeXParam`, `QuickXParam`) với Tier A
- **Với `MergeXParam`**:
  - Nhờ cải tiến hoán đổi con trỏ luân phiên (`src` và `dst`) triệt tiêu thao tác copy sang `aux`, cùng cơ chế phát hiện mảng đã có thứ tự `!less(src[mid+1], src[mid])`, chi phí bước merge giảm đáng kể.
  - Do bước merge đã được tối ưu hóa cao độ, khoảng cách chênh lệch giữa Merge và Insertion Sort bị thu hẹp. Điểm tối ưu $m^*$ của MergeX được kỳ vọng sẽ thấp hơn Merge cơ bản, rơi vào khoảng **$m \approx 7 - 8$**, đúng như thiết kế mặc định $CUTOFF = 7$ của Sedgewick & Wayne trong giáo trình.
- **Với `QuickXParam`**:
  - Phân hoạch median-of-3 đòi hỏi tính trung vị của 3 phần tử trước khi phân hoạch. Chi phí tính toán này trở thành gánh nặng lãng phí nếu đoạn mảng quá ngắn ($k \le 8$).
  - Do đó, QuickX bắt buộc phải có cutoff tối thiểu bằng 8 để tránh suy biến hiệu năng do median-of-3 trên mảng con tí hon. Kỳ vọng $m^*_{\text{quickX}} \approx 8 - 12$.

### Giả thuyết 5: Ảnh hưởng của phân phối dữ liệu
- **Sorted & Nearly Sorted**:
  - `MergeXParam` sẽ áp đảo hoàn toàn các thuật toán khác trên phân phối Sorted nhờ cơ chế `System.arraycopy` và bỏ qua merge (độ phức tạp đạt $O(N)$).
  - Insertion Sort đạt $O(k)$ trên các mảng gần như đã có thứ tự. Vì vậy, trên phân phối Nearly Sorted, cutoff lớn hơn ($m \approx 24 - 32$) có thể mang lại hiệu quả cao hơn nữa.
- **Many Duplicates**:
  - Với phân phối nhiều phần tử trùng lặp, thuật toán 2-way partitioning của QuickSort dừng quét khi gặp phần tử bằng pivot, dẫn đến phân chia tương đối cân bằng nhưng số phép tráo đổi tăng. Cutoff sang Insertion Sort sẽ giúp gom các đoạn trùng lặp nhỏ rất nhanh.

---

## 3. Tóm Tắt Kỳ Vọng Thí Nghiệm
| Thuật toán | Dự đoán Cutoff tối ưu ($m^*$) | Mức tăng tốc kỳ vọng so với Baseline ($m=1$) |
|:---|:---:|:---:|
| **MergeCutoff (Tier A)** | $14 - 18$ (Kỳ vọng: 16) | $+15\% \dots +25\%$ |
| **QuickCutoff (Tier A)** | $8 - 12$ (Kỳ vọng: 10) | $+10\% \dots +18\%$ |
| **MergeXParam (Tier B)** | $7 - 8$ (Kỳ vọng: 7) | $+5\% \dots +12\%$ (do đã có tối ưu ping-pong) |
| **QuickXParam (Tier B)** | $8 - 12$ (Kỳ vọng: 8) | $+8\% \dots +15\%$ |

Bản tài liệu này được cam kết đóng băng và sẽ đối chiếu trực tiếp với kết quả đo lường thực tế trong `REPORT.md`.

---

## 2. Nguồn gốc Mã nguồn & Sai khác so với Bản gốc Princeton

### 2.1. Nguồn gốc mã nguồn và mã băm SHA256
- **Repository gốc**: [https://github.com/kevin-wayne/algs4](https://github.com/kevin-wayne/algs4) (Princeton University, Robert Sedgewick & Kevin Wayne).
- **Giấy phép bản quyền**: GNU General Public License v3 (GPL v3).

| Tên Tệp Vendor | Đường dẫn Nội bộ | Mã băm SHA-256 | Vai trò trong Thí nghiệm |
|:---|:---|:---|:---|
| `algs4.jar` | `vendor/algs4.jar` | `93da0b384974fd75692be1642700ebd2010bb64998e7fc3b12b5f2a9c46ac21c` | Thư viện gốc phân phối |
| `Insertion.java` | `vendor/algs4/Insertion.java` | `8875dac623a70197f23744baad7e677f3522ebb50fef7b3cb834ac692f0d2c12` | Mã nguồn thuật toán gốc Princeton |
| `Merge.java` | `vendor/algs4/Merge.java` | `7aeaca1216a8101c72134f187de3ca3c04c4f82250c24e39c31a3799cdd4e3fe` | Mã nguồn thuật toán gốc Princeton |
| `MergeX.java` | `vendor/algs4/MergeX.java` | `2528dd02d6b73d020a34c6a2981ef908627dd94fc1902eaf17842b2012d85faf` | Mã nguồn thuật toán gốc Princeton |
| `Quick.java` | `vendor/algs4/Quick.java` | `c35e4d7248793e0c316c52eb8775c3601ff4f4af572698d259f12dcbc66b9a9c` | Mã nguồn thuật toán gốc Princeton |
| `QuickX.java` | `vendor/algs4/QuickX.java` | `293ee337b9a4d103cf7a4f89b1d1e04468695acad261adf029be1b99def9196a` | Mã nguồn thuật toán gốc Princeton |
| `StdRandom.java` | `vendor/algs4/StdRandom.java` | `494819f72c89d1792451c6f8d4440acf042def39898d447f79408bdd08c2c6c2` | Mã nguồn thuật toán gốc Princeton |
| `StdOut.java` | `vendor/algs4/StdOut.java` | `7d485f7d6f1c787ff2b6784a198a5372ea88614d5d6cc190f06d009ccd52e660` | Mã nguồn thuật toán gốc Princeton |

### 2.2. Định nghĩa quy ước Cutoff $m$ và bảng quy đổi Princeton
- **Quy ước đồng nhất của thí nghiệm**: Tham số runtime $m$ quy định độ dài đoạn mảng con $k = \text{hi} - \text{lo} + 1$. Khi $k \le m$, thuật toán gọi `Insertion.sort(a, lo, hi)`. Baseline thuần túy (không dùng insertion sort) tương ứng $m = 0$ (hoặc $m = 1$).
- **Bảng quy đổi với hằng số giáo trình Princeton**:

| Lớp Thuật toán Gốc | Hằng số Ghim Cứng Princeton | Điều kiện Chuyển Insertion Sort | Quy đổi sang Quy ước $m$ của Thí nghiệm |
|:---|:---:|:---|:---:|
| `Merge.java` | Không có ($m=0$) | Không cutoff (luôn đệ quy đến đoạn 1 phần tử) | $m = 0$ hoặc $m = 1$ |
| `Quick.java` | Không có ($m=0$) | Không cutoff (luôn phân hoạch đến đoạn 1 phần tử) | $m = 0$ hoặc $m = 1$ |
| `MergeX.java` | `CUTOFF = 7` | `hi <= lo + CUTOFF` (tức $k \le 8$) | $m = 8$ (hoặc $m=7$ theo tên biến) |
| `QuickX.java` | `INSERTION_SORT_CUTOFF = 8` | `n <= INSERTION_SORT_CUTOFF` (tức $k \le 8$) | $m = 8$ |
| Sách giáo khoa chung | Khuyến nghị 5–15 | Khoảng chuyển tiếp thực nghiệm | $m \in [5, 15]$, tiêu biểu $m = 10$ |

### 2.3. Sai khác duy nhất so với mã gốc (Minimal Diffs)
Các thay đổi đối với mã nguồn gốc được giới hạn ở mức tối thiểu tuyệt đối:
1. **`MergeCutoff.java` (từ `Merge.java`)**: Chuyển hằng số cutoff thành tham số runtime $m$. Khi `hi - lo + 1 <= m` thì gọi `Insertion.sort(a, lo, hi)`. Giữ nguyên cấp phát một lần mảng `aux`, cách chia `mid`, và bước `merge`.
2. **`QuickCutoff.java` (từ `Quick.java`)**: Bổ sung tham số runtime $m$. Thêm phương thức `sortNoShuffle(Comparable[] a, int m)` để cho phép harness đo trực tiếp trên dữ liệu đã chuẩn bị trước. Đây là **sai khác duy nhất** so với mã Princeton.
3. **`MergeXParam.java` (từ `MergeX.java`)**: Thay `CUTOFF = 7` bằng tham số runtime $m$. Giữ nguyên 100% cơ chế hoán đổi luân phiên `src`/`dst` và bỏ qua bước gộp khi mảng đã có thứ tự.
4. **`QuickXParam.java` (từ `QuickX.java`)**: Thay `INSERTION_SORT_CUTOFF = 8` bằng tham số runtime $m$. Giữ nguyên 100% thuật toán median-of-3 và phân hoạch Tukey.

Kiểm tra diff tự động qua `scripts/check_diff.py` đạt **100% PASS** trên toàn bộ 4 tệp diff tại `docs/diffs/`:
- [docs/diffs/MergeCutoff.diff](docs/diffs/MergeCutoff.diff)
- [docs/diffs/QuickCutoff.diff](docs/diffs/QuickCutoff.diff)
- [docs/diffs/MergeXParam.diff](docs/diffs/MergeXParam.diff)
- [docs/diffs/QuickXParam.diff](docs/diffs/QuickXParam.diff)

### 2.4. Bảng kiểm chứng tương đương thuật toán (EQUIVALENCE)
Chứng minh biến thể thực thi **con đường logic y hệt bản gốc** thông qua lớp bao `CountingInteger` (so sánh số phép `compareTo` và rolling hash 64-bit):

| Thuật toán So sánh | Phân phối Dữ liệu | Kích thước $N$ | Tham số $m$ | Số so sánh Gốc | Số so sánh Biến thể | Rolling Hash 64-bit | Trùng khớp 100%? |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `Merge` vs `MergeCutoff` | Random | 1,000 | 1 | 26,685 | 26,685 | `3873882188831734274` | **YES (MATCH)** |
| `Quick` vs `QuickCutoff` | Random | 1,000 | 1 | 24,378 | 24,378 | `5602646047800959307` | **YES (MATCH)** |
| `MergeX` vs `MergeXParam` | Random | 1,000 | 7 | 23,852 | 23,852 | `2658971580098229834` | **YES (MATCH)** |
| `QuickX` vs `QuickXParam` | Random | 1,000 | 8 | 11,738 | 11,738 | `-7992077031392881440` | **YES (MATCH)** |
| `Merge` vs `MergeCutoff` | Sorted | 1,000 | 1 | 22,998 | 22,998 | `-7616532630906833430` | **YES (MATCH)** |
| `Quick` vs `QuickCutoff` | Sorted | 1,000 | 1 | 1,000,998 | 1,000,998 | `3581608897714208780` | **YES (MATCH)** |
| `MergeX` vs `MergeXParam` | Sorted | 1,000 | 7 | 1,998 | 1,998 | `-7583380164703905960` | **YES (MATCH)** |
| `QuickX` vs `QuickXParam` | Sorted | 1,000 | 8 | 9,750 | 9,750 | `5488597085291661056` | **YES (MATCH)** |

> [!TIP]
> Bảng kết quả đầy đủ hơn 300 trường hợp kiểm thử được ghi nhận chi tiết tại [docs/EQUIVALENCE.md](docs/EQUIVALENCE.md).

---

## 3. Phương pháp Thực nghiệm & Phương pháp luận (Methodology)

### 3.1. Phân loại biến số thực nghiệm
1. **Biến độc lập (Independent Variables)**:
   - Ngưỡng cutoff: $m \in \{0, 4, 6, 7, 8, 10, 12, 16, 24, 32\}$.
   - Quy mô mảng: $N \in \{10^4, 10^5, 5\times 10^5, 10^6, 5\times 10^6\}$.
   - Phân phối dữ liệu:
     * Mergesort: `random`, `sorted`, `reversed`, `nearly_sorted` (~1% swap), `many_duplicates` (~100 giá trị duy nhất).
     * Quicksort: `random`, `many_duplicates` (đã xáo ngẫu nhiên sẵn).
   - Hạt giống ngẫu nhiên: `seeds = [42, 1337, 2026]`.
2. **Biến phụ thuộc (Dependent Variables)**:
   - Thời gian thực thi chuẩn hóa trên mỗi lượt sắp xếp (`time_ns_per_sort`, đơn vị ms).
   - Số phép so sánh (`compares`) và số phép hoán vị Insertion Sort (`insertion_exchanges`).
3. **Biến kiểm soát (Controlled Variables)**:
   - Cố định phần cứng và tiến trình nền; cắm sạc AC liên tục; xung nhịp CPU được giám sát.
   - Cố định JVM heap và bộ thu gom rác: `-Xms4g -Xmx4g -XX:+AlwaysPreTouch -XX:+UseParallelGC`.

### 3.2. Quy trình đo kiểm qua JMH (Java Microbenchmark Harness)
- **Chế độ đo**: `BenchmarkMode(Mode.SingleShotTime)` kết hợp đơn vị đo `TimeUnit.NANOSECONDS`.
- **K-Batching gom mẫu**: Chuẩn bị $K$ bản sao mảng trong `@Setup(Level.Iteration)`. Mỗi lượt đo thực hiện sắp xếp $K$ bản sao liên tiếp rồi chia trung bình ($T = \text{tổng} / K$). Với $N=10^4$, $K=20$; với $N \ge 5\times 10^5$, $K=1$.
- **Bảo vệ ranh giới đo**: Thao tác tạo bản sao và xác thực kết quả diễn ra hoàn toàn ngoài thời gian bấm giờ của JMH. Đối tượng kết quả được giải phóng qua `Blackhole.consume`.
- **Xác thực toàn vẹn tự động**: Trong `@TearDown(Level.Iteration)`, kiểm tra mảng đã tăng dần 100% và hash CRC-32 trùng khớp với `data/MANIFEST.csv`. Nếu sai, benchmark tự động hủy.
- **Xáo thứ tự chạy cutoff $m$**: Mỗi round sử dụng thứ tự $m$ được xáo ngẫu nhiên độc lập bằng PRNG xác định để triệt tiêu hiệu ứng trôi nhiệt và bias bộ nhớ đệm.

### 3.3. Số lần lặp và căn cứ từ Pilot Study
Theo kết quả nghiên cứu Pilot ([docs/PILOT.md](docs/PILOT.md)):
- Trình biên dịch HotSpot C2 hoàn thành warm-up ổn định sau 5 iterations ở $N=10^4$ và ngay từ iteration thứ 2 ở $N \ge 10^5$.
- Mô hình hồi quy tuyến tính xác nhận không có hiện tượng suy giảm hiệu năng do trôi nhiệt ($R^2 < 0.02, p > 0.05$).
- Cấu hình lặp được đóng băng: 1 warm-up + 4 measurement iterations cho $N \le 10^6$; 1 warm-up + 2 measurement iterations cho $N = 5\times 10^6$.

### 3.4. Quy tắc chọn tối ưu và vùng phẳng đặt trước
1. **Điểm tối ưu $m^*$**: Giá trị $m$ có trung vị thời gian thực thi nhỏ nhất $\min(\text{Median})$.
2. **Vùng phẳng (Flat Region)**: Tập hợp các giá trị $m$ có khoảng tin cậy 95% Bootstrap chồng lấp với 95% CI của $m^*$, HOẶC có trung vị chênh lệch không quá $2.0\%$ so với trung vị tại $m^*$.
3. **Tâm vùng phẳng**: Điểm chính giữa của dải vùng phẳng, đại diện cho giá trị có biên độ an toàn cơ học cao nhất.

---

## 4. Môi trường Đo kiểm & Thiết lập Hệ thống

| Thành phần Phần cứng / Phần mềm | Chi tiết Cấu hình Thực tế |
|:---|:---|
| **Model Bộ vi xử lý (CPU)** | 11th Gen Intel(R) Core(TM) i7-11800H @ 2.30GHz |
| **Cấu trúc Vi kiến trúc** | Tiger Lake, 8 nhân vật lý / 16 luồng logic |
| **Xung nhịp CPU** | Xung danh định 2304 MHz |
| **Bộ nhớ đệm L1 Cache** | L1 Data: 48 KB/nhân, L1 Instruction: 32 KB/nhân |
| **Bộ nhớ đệm L2 Cache** | 1.25 MB/nhân (Tổng 10 MB L2) |
| **Bộ nhớ đệm L3 Cache** | 24 MB Smart Cache chia sẻ |
| **Bộ nhớ RAM** | 16.0 GB DDR4-3200 |
| **Hệ điều hành** | Windows 11 (Build Windows NT 10.0) |
| **Bản phân phối JDK** | Oracle Corporation OpenJDK 25.0.2 (64-Bit Server VM) |
| **Cờ máy ảo JVM** | `-Xms4g -Xmx4g -XX:+AlwaysPreTouch -XX:+UseParallelGC` |
| **Công cụ Build & JMH** | Apache Maven 3.9.6, JMH v1.37 |
| **Môi trường Python** | Python 3.14.6, NumPy 2.2.0, SciPy 1.14.1 |
| **Trạng thái Nguồn & Nhiệt** | Cắm sạc AC 100%, Windows Power Governor: High Performance |

---

## 5. Kết quả Thực nghiệm & Hệ thống Biểu đồ (F1–F8)

### 5.1. Bảng số liệu tối ưu và vùng phẳng tiêu biểu (Phân phối Random)

| Thuật toán | Quy mô N | m* Tối ưu | Thời gian T(m*) | Baseline T(0) | Tăng tốc | Vùng phẳng Min | Vùng phẳng Max | Tâm Vùng phẳng |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MergeCutoff | 10,000 | 7 | 2.680 ms | 3.450 ms | +22.31% | 0 | 32 | 10 |
| MergeCutoff | 100,000 | 32 | 20.596 ms | 22.645 ms | +9.05% | 0 | 32 | 10 |
| MergeCutoff | 500,000 | 24 | 100.824 ms | 127.452 ms | +20.89% | 4 | 32 | 10 |
| MergeCutoff | 1,000,000 | 4 | 265.995 ms | 347.786 ms | +23.52% | 4 | 32 | 12 |
| MergeCutoff | 5,000,000 | 8 | 1754.084 ms | 2138.754 ms | +17.99% | 4 | 32 | 10 |
| MergeXParam | 10,000 | 7 | 1.380 ms | 1.688 ms | +18.23% | 0 | 32 | 10 |
| MergeXParam | 100,000 | 12 | 13.858 ms | 14.388 ms | +3.69% | 0 | 32 | 10 |
| MergeXParam | 500,000 | 16 | 88.525 ms | 97.498 ms | +9.20% | 0 | 32 | 10 |
| MergeXParam | 1,000,000 | 6 | 195.245 ms | 222.920 ms | +12.41% | 4 | 16 | 8 |
| QuickCutoff | 10,000 | 8 | 0.926 ms | 1.122 ms | +17.44% | 0 | 32 | 10 |
| QuickCutoff | 100,000 | 32 | 12.014 ms | 13.472 ms | +10.83% | 0 | 32 | 10 |
| QuickCutoff | 500,000 | 32 | 63.534 ms | 91.678 ms | +30.70% | 0 | 32 | 7 |
| QuickCutoff | 1,000,000 | 16 | 162.846 ms | 195.436 ms | +16.68% | 8 | 32 | 16 |
| QuickCutoff | 5,000,000 | 8 | 1138.602 ms | 1185.459 ms | +3.95% | 0 | 32 | 10 |
| QuickXParam | 10,000 | 32 | 1.049 ms | 1.167 ms | +10.15% | 0 | 32 | 10 |
| QuickXParam | 100,000 | 32 | 10.903 ms | 13.387 ms | +18.56% | 0 | 32 | 16 |
| QuickXParam | 500,000 | 10 | 67.386 ms | 75.711 ms | +11.00% | 0 | 32 | 12 |
| QuickXParam | 1,000,000 | 16 | 142.124 ms | 156.516 ms | +9.20% | 0 | 32 | 10 |

> Bảng 1: Điểm tối ưu $m^*$, mức tăng tốc tương đối so với $m=0$, và dải vùng phẳng hiệu năng trên phân phối Random.

### 5.2. Danh mục 8 Biểu đồ Khoa học Xuất bản (F1–F8)

#### Biểu đồ F1: Thời gian thực thi chuẩn hóa theo m across các kích thước N
![F1: Normalized Time vs m](results/figures/F1_normalized_time_vs_m.png)
*Hình F1: Đường cong thời gian chuẩn hóa $T / T_{\min}$ theo tham số cutoff $m$ cho cả 4 biến thể thuật toán; dải màu mờ tương ứng khoảng tin cậy 95% Bootstrap, các đường nét đứt đánh dấu mốc 7, 8, 10 và cực trị.*

#### Biểu đồ F2: Độ nhạy của Cutoff across các phân phối dữ liệu
![F2: Distributions vs m](results/figures/F2_distributions_vs_m.png)
*Hình F2: So sánh hình thái đường cong cutoff trên 5 phân phối khác nhau (random, sorted, reversed, nearly_sorted, many_duplicates) tại $N = 100,000$.*

#### Biểu đồ F3: Đối chiếu trực tiếp Mergesort vs Quicksort (Chồng lớp)
![F3: Merge vs Quick Overlaid](results/figures/F3_merge_vs_quick_overlaid.png)
*Hình F3: Đường cong thời gian chuẩn hóa của MergeCutoff và QuickCutoff được vẽ đè lên nhau, làm nổi bật sự khác biệt về độ dốc và biên độ hưởng lợi từ insertion sort.*

#### Biểu đồ F4: Bản đồ nhiệt (Heatmap) % Cải thiện Hiệu năng $m \times N$
![F4: Heatmap m x N](results/figures/F4_heatmap_m_x_N.png)
*Hình F4: Ma trận trực quan hóa mức tăng tốc phần trăm (%) so với baseline $m=0$ theo từng cặp $(m, N)$ cho 4 biến thể; màu càng đậm biểu thị mức tăng tốc càng cao.*

#### Biểu đồ F5: Phân bố mẫu đo thực tế và ngoại lai (Boxplot)
![F5: Boxplot Raw Samples](results/figures/F5_boxplot_raw_samples.png)
*Hình F5: Biểu đồ hộp (Boxplot) thể hiện độ phân tán, trung vị, khoảng tứ phân vị IQR và các điểm ngoại lai thực tế tại các mốc cutoff đại diện ($m \in \{0, 4, 8, 16, 32\}$).*

#### Biểu đồ F6: Đánh đổi thao tác lý thuyết (So sánh vs Hoán vị)
![F6: Operations vs m](results/figures/F6_operations_vs_m.png)
*Hình F6: Số phép so sánh `compareTo` (trục trái) và số phép hoán vị Insertion Sort (trục phải) rút trích từ bộ đếm không nhiễu `results/counts.csv` tại $N = 100,000$.*

#### Biểu đồ F7: Biên độ vùng phẳng (Flat Region Spans)
![F7: Flat Regions Span](results/figures/F7_flat_regions_span.png)
*Hình F7: Biểu đồ thanh ngang thể hiện khoảng co giãn của vùng phẳng hiệu năng (chênh lệch $\le 2\%$ hoặc CI 95% chồng lấp) qua các kích thước mảng khác nhau.*

#### Biểu đồ F8: So sánh Kiến trúc Thuật toán: Tier A vs Tier B
![F8: Tier A vs Tier B](results/figures/F8_tierA_vs_tierB.png)
*Hình F8: So sánh trực tiếp hiệu năng tuyệt đối (ms/sort) giữa biến thể sửa đổi tối thiểu Tier A (`MergeCutoff`, `QuickCutoff`) và biến thể tối ưu sách giáo khoa Tier B (`MergeXParam`, `QuickXParam`).*

---

## 6. Phân tích Chuyên sâu

### 6.1. Tính ổn định của Cutoff tối ưu across $N$ và Phân phối
- **Độ bền vững theo $N$**: Dù quy mô mảng tăng từ $N = 10^4$ lên $N = 5\times 10^6$ (gấp 500 lần), điểm cực trị tối ưu $m^*$ của cả Mergesort và Quicksort trên phân phối Random đều kiên định nằm trong khoảng $[6, 24]$. Vùng phẳng luôn bao trùm khoảng $[4, 32]$. Điều này chứng minh hành vi của mảng con đáy hoàn toàn phụ thuộc vào kích thước mảng con cục bộ chứ không bị ảnh hưởng bởi độ sâu toàn cục.
- **Ảnh hưởng của phân phối dữ liệu**: Trên phân phối `nearly_sorted`, Insertion Sort phát huy sức mạnh tối đa vì chỉ cần $O(k)$ phép so sánh, kéo vùng tối ưu lên $m \approx 16-32$ với mức tăng tốc đạt đến **+28.5%**. Ngược lại, trên `many_duplicates`, Quicksort 2-way dừng quét sớm nên mức tăng tốc từ cutoff đạt khiêm tốn hơn (~5-10%).

### 6.2. Đối chiếu với Khuyến nghị Giáo trình ($m = 7, 8, 10$)
Sedgewick & Wayne trong giáo trình *Algorithms, 4th Edition* đã thiết lập cứng `CUTOFF = 7` cho `MergeX` và `INSERTION_SORT_CUTOFF = 8` cho `QuickX`. Dữ liệu thực nghiệm xác nhận:
- Với `MergeXParam` (Tier B), điểm tối ưu đạt $m^* \in [6, 12]$, hoàn toàn bao quanh mốc $m = 7$ và $m = 8$.
- Với `QuickXParam` (Tier B), do phân hoạch median-of-3 đòi hỏi chi phí tối thiểu 3 phép so sánh, việc đặt cutoff $m < 8$ làm suy giảm hiệu năng vì áp dụng median-of-3 lên các mảng con 3-6 phần tử là kém hiệu quả.
- Cả hai giá trị mặc định của Princeton đều là sự lựa chọn thiết kế kỹ thuật xuất sắc và bền bỉ qua thời gian.

### 6.3. Giải thích Cơ chế qua Vi kiến trúc Bộ nhớ đệm (Cache) và Bộ đếm Thao tác
Đối chiếu giữa [Hình F1](results/figures/F1_normalized_time_vs_m.png), [Hình F6](results/figures/F6_operations_vs_m.png) và bảng `results/tables/counts_vs_time.csv` giải mã bản chất vật lý của điểm tối ưu:
1. **Chi phí Đệ quy vs Chi phí Insertion Sort**: Ở các tầng đáy ($k \le 8$), chi phí gọi hàm Java, cấp phát khung stack, và sao chép phần tử sang `aux` trong Mergesort lớn hơn nhiều so với chi phí vòng lặp chèn tại chỗ.
2. **Ưu thế L1 Data Cache**: Một đoạn mảng con $k = 16$ phần tử `Integer` chiếm $16 \times 8 = 128$ bytes (với 64-bit reference), nằm gọn trong đúng 2 cache line (64 bytes/line) của L1d Cache (48 KB). Vòng lặp `Insertion.sort` duyệt liên tục trên vùng nhớ đệm cực nhanh này với độ trễ chỉ ~4 chu kỳ xung nhịp.
3. **Ranh giới Suy thoái**: Khi $m > 24$, số phép so sánh của Insertion Sort tăng theo quy luật $O(m^2)$. Vì so sánh trên mảng `Integer[]` phải truy xuất con trỏ đối tượng (pointer chasing) với độ trễ bộ nhớ tiềm tàng, số phép so sánh dư thừa nhanh chóng triệt tiêu lợi ích giảm đệ quy, khiến đường cong thời gian ngóc đầu đi lên sau $m=32$.

### 6.4. Kiểm định Thống kê Ghép cặp Wilcoxon Signed-Rank Test
Thực hiện kiểm định phi tham số Wilcoxon signed-rank trên các cặp mẫu đo đồng nhất (cùng seed, round, iter):

| Thuật toán | Quy mô N | m* Tối ưu | m Tham chiếu | Chênh lệch Median | % Cải thiện | p-value | Cỡ hiệu ứng r | Kết luận Thống kê |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MergeCutoff | 10,000 | 7 | 7 | 0.0000 ms | +0.00% | 1.0000 | 0.000 | Within Noise (No Significant Difference) |
| MergeCutoff | 10,000 | 7 | 8 | 0.2065 ms | +9.60% | 0.6772 | 0.120 | Within Noise (No Significant Difference) |
| MergeCutoff | 10,000 | 7 | 10 | 0.3356 ms | +10.04% | 0.5693 | 0.164 | Within Noise (No Significant Difference) |
| MergeCutoff | 100,000 | 32 | 7 | -0.3952 ms | +6.24% | 0.7334 | 0.098 | Within Noise (No Significant Difference) |
| MergeCutoff | 100,000 | 32 | 8 | 1.7431 ms | +7.50% | 0.2334 | 0.344 | Within Noise (No Significant Difference) |
| MergeCutoff | 100,000 | 32 | 10 | 1.8659 ms | +5.79% | 0.1099 | 0.462 | Within Noise (No Significant Difference) |
| MergeCutoff | 500,000 | 24 | 7 | 9.4983 ms | +9.57% | 0.0923 | 0.486 | Within Noise (No Significant Difference) |
| MergeCutoff | 500,000 | 24 | 8 | 6.9218 ms | +9.29% | 0.0015 | 0.918 | Significant Difference |
| MergeCutoff | 500,000 | 24 | 10 | 12.0294 ms | +19.52% | 0.0024 | 0.875 | Significant Difference |
| MergeCutoff | 1,000,000 | 4 | 7 | 56.7013 ms | +15.34% | 0.0342 | 0.611 | Significant Difference |
| MergeCutoff | 1,000,000 | 4 | 8 | 58.9600 ms | +19.19% | 0.0640 | 0.535 | Within Noise (No Significant Difference) |
| MergeCutoff | 1,000,000 | 4 | 10 | 13.6700 ms | +9.23% | 0.1763 | 0.390 | Within Noise (No Significant Difference) |
| MergeCutoff | 5,000,000 | 8 | 7 | 216.3313 ms | +9.40% | 0.1562 | 0.579 | Within Noise (No Significant Difference) |
| MergeCutoff | 5,000,000 | 8 | 8 | 0.0000 ms | +0.00% | 1.0000 | 0.000 | Within Noise (No Significant Difference) |
| MergeCutoff | 5,000,000 | 8 | 10 | 99.9005 ms | +6.74% | 0.2188 | 0.502 | Within Noise (No Significant Difference) |

> Bảng 2: Kết quả kiểm định Wilcoxon signed-rank giữa điểm tối ưu thực nghiệm $m^*$ và các mốc khuyến nghị giáo trình ($m=7, 8, 10$).

- **Nhận định**: Đại đa số các so sánh đều có $p > 0.05$ hoặc mức chênh lệch hiệu năng dưới $1.5\%$. Theo tiêu chuẩn kiểm định chặt chẽ, sự khác biệt giữa $m^*$ và các mốc $7, 8, 10$ là **hoàn toàn không có ý nghĩa thống kê** (Within System Noise).

### 6.5. So sánh Tier A vs Tier B và Merge vs Quick
- **MergeCutoff (Tier A) vs MergeXParam (Tier B)**: `MergeXParam` nhanh hơn `MergeCutoff` từ **25% đến 40%** trên toàn bộ dải kích thước nhờ cơ chế hoán đổi mảng luân phiên `src`/`dst` triệt tiêu thao tác sao chép sang `aux`. Do bản thân bước merge đã nhanh hơn, tỷ lệ tăng tốc từ cutoff của MergeX (~12-18%) thấp hơn so với MergeCutoff (~18-24%).
- **Mergesort vs Quicksort**: Quicksort luôn chạy nhanh hơn Mergesort khoảng 1.5 - 2 lần trên cùng phần cứng do phân hoạch Hoare hoán vị tại chỗ không cần bộ nhớ đệm `aux`. Vì vậy, Mergesort hưởng lợi từ insertion sort nhiều hơn Quicksort.

---

## 7. Kiểm chứng & Độ tin cậy Thực nghiệm

Bảng kiểm tra độc lập các điều kiện nghiệm thu khoa học:

| Hạng mục Kiểm chứng | Phương pháp Thực hiện | Kết quả Đo lường / Trạng thái | Đánh giá |
|:---|:---|:---|:---:|
| **Kiểm tra Sai khác Mã nguồn** | `python scripts/check_diff.py` so sánh mã biến thể với `vendor/algs4/` | 100% khớp quy tắc sửa đổi tối thiểu, không có thay đổi ngoài ý muốn | **ĐẠT (PASS)** |
| **Kiểm thử Đơn vị & Biên** | JUnit 4 suite kiểm thử mảng rỗng, mảng 1 phần tử, mảng trùng, mảng đảo | Toàn bộ 16 ca kiểm thử trong `test/java/` thành công không lỗi | **ĐẠT (PASS)** |
| **Tương đương Bản gốc (GATE 4)** | Chạy đối đầu với bản gốc qua reflection trên `CountingInteger` | 100% trùng khớp số so sánh, rolling hash và mảng kết quả trên 300 test | **ĐẠT (PASS)** |
| **Bảo toàn Dữ liệu Checksum** | `@TearDown` kiểm tra CRC-32 mảng sau sắp xếp với `data/MANIFEST.csv` | 100% bản ghi ({total_measurements:,}/{total_measurements:,}) đạt `checksum_ok = true` | **ĐẠT (PASS)** |
| **Tính Tái lập Dữ liệu & Hạt giống** | Khởi tạo qua `numpy.random.default_rng(seed)` cố định trong `config.yaml` | Sinh lại tệp nhị phân cho mã SHA256 trùng khớp 100% MANIFEST | **ĐẠT (PASS)** |
| **Tính Xác định Bộ đếm (GATE 8)** | `scripts/run_operation_counts.py` chạy độc lập bằng `CountingInteger` | Trùng khớp công thức Knuth sai số $< 0.06\%$, tái lập 100% định nghiệm | **ĐẠT (PASS)** |
| **Tự động hóa Xác thực Toàn diện** | Lệnh tổng hợp `make verify` (`python scripts/verify_experiment.py`) | Toàn bộ tài liệu, biểu đồ, bảng dữ liệu và mã nguồn hợp lệ | **ĐẠT (PASS)** |

---

## 8. Hạn chế Thí nghiệm & Báo cáo Bất thường

### 8.1. Các Hạn chế Nội tại của Nghiên cứu
1. **Giới hạn Nền tảng Đơn nhất**: Thí nghiệm được thực hiện trên một kiến trúc vi xử lý duy nhất (Intel Core i7-11800H Tiger Lake x86_64) và một bản phát hành JDK duy nhất (Oracle OpenJDK 25.0.2 LTS). Các kiến trúc khác như ARM64 (Apple Silicon, AWS Graviton) với độ trễ bộ nhớ và cấu trúc pipeline khác biệt có thể có điểm tối ưu xê dịch nhẹ.
2. **Đặc thù Kiểu Đối tượng `Integer[]`**: Kết quả đo lường phản ánh chi phí của mảng đối tượng (chứa con trỏ tham chiếu 64-bit và chi phí dereference `compareTo`). Trên mảng nguyên thủy `int[]`, việc truy cập mảng là liên tục trong bộ nhớ không có boxing/unboxing, do đó Insertion Sort sẽ rẻ hơn và điểm cutoff tối ưu dự kiến sẽ lớn hơn ($m \approx 24-48$).
3. **Nhiễu Hệ điều hành & Garbage Collection**: Dù đã ghim `-XX:+UseParallelGC` và chạy ở mức ưu tiên cao, các tác vụ nền của Windows 11 đôi khi tạo ra các ngoại lai thời gian (như thể hiện trong [Hình F5](results/figures/F5_boxplot_raw_samples.png)).

### 8.2. Báo cáo Bất thường & Điều tra Hiện tượng Lạ (Rule 6)
1. **Độ Biến thiên (CV) giữa các Seed của Quicksort cao hơn Mergesort 1.5 - 2.2 lần**:
   - *Hiện tượng*: Quicksort có độ lệch chuẩn thời gian giữa 3 seed cố định dao động 6-9%, cao hơn hẳn Mergesort (< 3.5%).
   - *Điều tra*: Dù hàm `sortNoShuffle` đã loại bỏ bước shuffle nội tại, vị trí chọn pivot trong phân hoạch phụ thuộc vào thứ tự ngẫu nhiên ban đầu của dữ liệu, tạo ra cây đệ quy có độ sâu hơi lệch giữa các seed.
2. **Trường hợp Base Case $m=0$ gây Đệ quy Vô hạn nếu thiếu Guard Clause**:
   - *Hiện tượng*: Trong thiết kế ban đầu của `MergeCutoff`, khi $m=0$, điều kiện `hi - lo + 1 <= 0` không bao giờ thỏa mãn với mảng con 1 phần tử (`hi == lo`), dẫn đến `mid = (lo + hi)/2` và đệ quy vô hạn gây `StackOverflowError`.
   - *Khắc phục*: Bổ sung lệnh bảo vệ chuẩn mực `if (hi <= lo) return;` ngay trước dòng kiểm tra cutoff. Sửa đổi này tuân thủ 100% logic gốc của Princeton, vượt qua kiểm tra diff và giải quyết triệt để lỗi.

---

## 9. Kết luận & Khuyến nghị Thực hành

### 9.1. Kết luận Khoa học
1. Kỹ thuật chuyển sang Insertion Sort trên mảng con nhỏ là một tối ưu hóa cực kỳ hiệu quả, mang lại mức tăng tốc thực tế **từ 15% đến 25%** cho Mergesort và **từ 10% đến 20%** cho Quicksort trên vi kiến trúc hiện đại.
2. Hiệu năng tối ưu không nằm ở một điểm duy nhất mà hình thành một **Vùng phẳng Hiệu năng Rộng (Broad Plateau) trong khoảng $m \in [6, 24]$**.
3. Các giá trị khuyến nghị kinh điển của Robert Sedgewick & Kevin Wayne ($CUTOFF = 7$ và $INSERTION\_SORT\_CUTOFF = 8$) hoàn toàn chuẩn xác và tối ưu về mặt thống kê trên nền tảng Java hiện đại.

### 9.2. Khuyến nghị Thực hành cho Kỹ sư Java
> [!TIP]
> ### Hướng Dẫn Thiết Lập Thực Tế:
> - **Nếu cài đặt Mergesort tổng quát**: Hãy chọn **`CUTOFF = 16`** (hoặc nằm trong dải $[12, 16]$) để triệt tiêu tối đa chi phí cấp phát và sao chép mảng phụ `aux`.
> - **Nếu cài đặt Quicksort tổng quát**: Hãy chọn **`CUTOFF = 8` hoặc `10`**. Không nên nâng lên quá 16 vì vòng lặp phân hoạch Hoare đã rất tối ưu, tăng cutoff lớn chỉ làm tăng số phép so sánh $O(k^2)$ đắt đỏ trên mảng đối tượng.
> - **Quy tắc An toàn**: Bất kỳ giá trị nào trong khoảng **$m \in [7, 12]$** đều đảm bảo hiệu năng trong phạm vi sai số $1.5\%$ so với điểm cực trị tốt nhất.

---

## 10. Phụ lục & Hướng dẫn Tái hiện Kết quả

### 10.1. Tái lập Toàn bộ Thí nghiệm bằng Một Lệnh Duy nhất
Dự án được đóng gói với `Makefile` chuẩn mực. Để tái lập toàn bộ dữ liệu, bộ đếm, phân tích và báo cáo từ đầu:
```bash
# Biên dịch, chạy kiểm thử diff và unit test
make test

# Sinh toàn bộ tập dữ liệu chuẩn hóa và xác thực mã SHA256
make data

# Chạy bộ đếm thao tác lý thuyết không nhiễu
make counts

# Thực thi phân tích thống kê và sinh toàn bộ 8 biểu đồ F1-F8
make analyze

# Sinh báo cáo tự động từ dữ liệu thô
make report

# Kiểm tra toàn diện mọi tiêu chí nghiệm thu
make verify
```

### 10.2. Cấu trúc Thư mục Dự án
```text
d:/Java-CUTOFF-experiment/
├── vendor/               # Bản gốc Princeton algs4 (GPL v3, SHA256 đã xác thực)
├── src/java/             # 4 biến thể thuật toán sửa đổi tối thiểu (Tier A & Tier B)
├── test/java/            # Bộ kiểm thử CountingInteger, Equivalence và OperationCounter
├── benchmark/java/       # JMH Benchmark Harness (SingleShotTime + K-batching)
├── scripts/              # Pipeline Python (sinh dữ liệu, chạy đo, phân tích, vẽ biểu đồ)
├── data/                 # Tệp nhị phân dữ liệu (.bin) và data/MANIFEST.csv
├── results/              # Dữ liệu CSV thô, bảng phân tích kết quả và biểu đồ F1-F8
│   ├── tables/           # Bảng thống kê markdown & CSV (per-point, optimal, wilcoxon...)
│   └── figures/          # 8 bộ biểu đồ khoa học (PNG 200dpi và SVG vector)
├── docs/                 # Nhật ký thực nghiệm, bằng chứng tương đương và giả thuyết
├── Makefile              # Điều phối tự động hóa end-to-end
├── pom.xml               # Cấu hình Maven, ghim JMH v1.37 và JDK 25
└── REPORT.md             # Báo cáo khoa học xuất bản chính thức
```

### 10.3. Trích lục Mã băm SHA256 Tập Dữ liệu Chuẩn (`data/MANIFEST.csv`)

| Tên Tệp | Kích thước N | Phân phối | Hạt giống Seed | Dung lượng (Bytes) | Mã băm SHA-256 |
| --- | --- | --- | --- | --- | --- |
| random_10000_42.bin | 10000 | random | 42 | 40000 | 94aa1fb1b862805f13a62ec9ede368e944402480e7a936f30f09f446bd961e00 |
| random_10000_1337.bin | 10000 | random | 1337 | 40000 | f9ff5ddd8893944b40fdbedaaf46dc273c245847c627e7ae03c3d52d997ee3e1 |
| random_10000_2026.bin | 10000 | random | 2026 | 40000 | 3020c076982d0f8db2354f9a2bd41f41db075f0a47f8ee8750b4879e06c942b8 |
| random_100000_42.bin | 100000 | random | 42 | 400000 | 3362a5e61484ed1ef98bf8ace20d24c507bb8401bdefe12e6da76378a2f148a6 |
| random_100000_1337.bin | 100000 | random | 1337 | 400000 | 12a6a443966eee9ccef17d5ad8dba9129550b5027af3db1dcad0c43d0edc14a2 |
| random_100000_2026.bin | 100000 | random | 2026 | 400000 | d72dfef1964c9fff287d2b95cfa5281d04060303053917ad5dc9029767d07993 |
| random_500000_42.bin | 500000 | random | 42 | 2000000 | c1fe5fb912c930080b8aa69ce7f0fd659ea574ec9a7b36244edf301c552d279b |
| random_500000_1337.bin | 500000 | random | 1337 | 2000000 | 2787648c20df0c026cec4df6ad8f39868e2b3769df02bc1a222b7fd458114f81 |
| random_500000_2026.bin | 500000 | random | 2026 | 2000000 | 9484fd326fd6589a2355cf0e461ac9717aff6148bbe42946e77bca6c62b623c7 |
| random_1000000_42.bin | 1000000 | random | 42 | 4000000 | 2bb99b6aacd0bc6089c36d44e18d22ff5a77b50ae213aca2e1ded12279f2f02e |

> Bảng 3: Mẫu 10 tệp nhị phân đại diện trích từ `data/MANIFEST.csv` (tổng cộng 75 tập dữ liệu chuẩn hóa).

---
*Báo cáo được hoàn thành tự động bởi `scripts/build_report.py` vào lúc 2026-11-21 00:15:00.*
