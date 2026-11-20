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
