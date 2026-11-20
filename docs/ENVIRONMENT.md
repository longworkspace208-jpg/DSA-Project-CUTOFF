# Thông Tin Môi Trường Thí Nghiệm (Experiment Environment)

Ngày ghi nhận: 2026-11-20

## 1. Phần cứng (Hardware)
- **CPU**: 11th Gen Intel(R) Core(TM) i7-11800H @ 2.30GHz
  - Số nhân vật lý (Cores): 8
  - Số luồng logic (Threads): 16
  - Xung nhịp danh định: 2304 MHz
  - Cache L1: 640 KB (Data: 384 KB, Instruction: 256 KB)
  - Cache L2: 10240 KB (10 MB)
  - Cache L3: 24576 KB (24 MB Intel Smart Cache)
- **RAM**: 15.77 GB (2 thanh 8GB DDR4-3200 MT/s)
  - Module 1: Micron Technology 4ATF1G64HZ-3G2E1 (8GB, 3200 MHz)
  - Module 2: Lexar Co Limited LD4AS008G-3200ST (8GB, 3200 MHz)

## 2. Hệ điều hành & Nguồn điện (OS & Power)
- **Hệ điều hành**: Microsoft Windows 11 Home Single Language (Phiên bản 10.0.26200, Build 26200, 64-bit)
- **Power Plan**: High performance (`8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c`)
- **Tình trạng cấp nguồn**: Cắm sạc AC (PowerOnline: True, Đang sạc pin: True)

## 3. Môi trường thực thi Java (Java & JMH)
- **Java Version**: `25.0.2`
- **Nhà cung cấp JDK**: Oracle Corporation
- **Runtime**: Java(TM) SE Runtime Environment (build 25.0.2+10-LTS-69)
- **Máy ảo (VM)**: Java HotSpot(TM) 64-Bit Server VM (build 25.0.2+10-LTS-69, mixed mode, sharing)
- **Maven**: Version 3.9.6
- **JMH (Java Microbenchmark Harness)**: Phiên bản 1.37 (ghim cố định)

## 4. Môi trường phân tích dữ liệu (Python & Libraries)
- **Python Version**: 3.14.6
- **Thư viện**:
  - `numpy`: 2.5.3
  - `pandas`: 3.0.6
  - `matplotlib`: 3.11.2
  - `scipy`: 1.18.1
  - `pyyaml`: 6.0.3
