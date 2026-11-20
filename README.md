# Java Sorting Cutoff Experiment (MergeSort & QuickSort)

Nghiên cứu thực nghiệm tìm giá trị CUTOFF ($m$) tối ưu chuyển sang Insertion Sort cho mảng con nhỏ trong thuật toán MergeSort và QuickSort trên nền tảng Java 25.0.2 LTS.

Mã nguồn thuật toán được lấy trực tiếp từ thư viện **Princeton algs4** (Robert Sedgewick & Kevin Wayne), tuân thủ giấy phép GPL v3.

## Cấu trúc thư mục
- `vendor/`: Mã nguồn gốc thư viện Princeton `algs4` (GPL v3).
- `src/java/`: Mã nguồn thuật toán và bộ đếm so sánh/truy cập mảng.
- `test/java/`: Kiểm thử tính đúng đắn (JUnit 5).
- `benchmark/java/`: Bộ benchmark JMH (Java Microbenchmark Harness 1.37).
- `scripts/`: Scripts sinh dữ liệu, đếm phép toán, phân tích thống kê và tạo báo cáo.
- `data/`: Dữ liệu đầu vào thực nghiệm.
- `results/`: Kết quả đo lường thô (CSV/JSON), biểu đồ phân tích.
- `docs/`: Nhật ký công việc (`WORKLOG.md`) và thông tin môi trường (`ENVIRONMENT.md`).
- `REPORT.md`: Báo cáo kết quả thí nghiệm chi tiết.

## Yêu cầu môi trường
- Java: JDK 25.0.2 LTS
- Build: Apache Maven 3.9.6
- Python: >= 3.10 với `numpy`, `pandas`, `scipy`, `matplotlib`, `pyyaml`
- GNU Make

## Các lệnh thực thi
- `make all`: Chạy toàn bộ pipeline từ sinh dữ liệu đến tạo báo cáo.
- `make verify`: Kiểm thử tính đúng đắn và xác thực dữ liệu.
- `make test`: Chạy JUnit unit tests.
- `make bench`: Biên dịch và thực thi bộ benchmark JMH.
