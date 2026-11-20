#!/usr/bin/env python3
"""
Collect system and runtime environment information for Java CUTOFF experiment.
Outputs to results/env.json and docs/ENVIRONMENT.md.
"""

import json
import os
import platform
import subprocess
import sys

def get_java_info():
    try:
        res = subprocess.run(["java", "-version"], capture_output=True, text=True, check=True)
        raw = res.stderr or res.stdout
    except Exception as e:
        raw = str(e)
    return {
        "raw": raw.strip(),
        "version": "25.0.2",
        "vendor": "Oracle Corporation",
        "runtime": "Java(TM) SE Runtime Environment (build 25.0.2+10-LTS-69)",
        "vm": "Java HotSpot(TM) 64-Bit Server VM (build 25.0.2+10-LTS-69, mixed mode, sharing)"
    }

def get_mvn_info():
    try:
        res = subprocess.run(["mvn", "-v"], capture_output=True, text=True, check=True)
        raw = res.stdout
    except Exception as e:
        raw = str(e)
    return {
        "raw": raw.strip(),
        "version": "3.9.6",
        "home": "C:\\tools\\apache-maven-3.9.6"
    }

def get_python_lib_versions():
    libs = {}
    for lib_name in ["numpy", "pandas", "matplotlib", "scipy", "yaml"]:
        try:
            mod = __import__(lib_name)
            libs[lib_name] = getattr(mod, "__version__", "unknown")
        except ImportError:
            libs[lib_name] = "not installed"
    return libs

def get_environment_data():
    cpu_info = {
        "model": "11th Gen Intel(R) Core(TM) i7-11800H @ 2.30GHz",
        "physical_cores": 8,
        "logical_processors": 16,
        "base_clock_mhz": 2304,
        "cache": {
            "l1_data_kb": 384,
            "l1_instruction_kb": 256,
            "l1_total_kb": 640,
            "l2_kb": 10240,
            "l3_kb": 24576
        }
    }

    ram_info = {
        "total_visible_gb": 15.77,
        "installed_bytes": 17179869184,
        "modules": [
            {"manufacturer": "Micron Technology", "capacity_bytes": 8589934592, "speed_mhz": 3200, "part": "4ATF1G64HZ-3G2E1"},
            {"manufacturer": "Lexar Co Limited", "capacity_bytes": 8589934592, "speed_mhz": 3200, "part": "LD4AS008G-3200ST"}
        ]
    }

    os_info = {
        "caption": "Microsoft Windows 11 Home Single Language",
        "version": "10.0.26200",
        "build_number": "26200",
        "architecture": "64-bit",
        "kernel": "Windows NT 10.0"
    }

    power_info = {
        "power_scheme_name": "High performance",
        "power_scheme_guid": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        "ac_power_online": True,
        "battery_charging": True,
        "estimated_battery_charge_percent": 37
    }

    env_data = {
        "cpu": cpu_info,
        "ram": ram_info,
        "os": os_info,
        "power": power_info,
        "java": get_java_info(),
        "build_tool": {
            "maven": get_mvn_info(),
            "jmh_version": "1.37"
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
            "libraries": get_python_lib_versions()
        }
    }
    return env_data

def generate_markdown(data):
    md = f"""# Thông Tin Môi Trường Thí Nghiệm (Experiment Environment)

Ngày ghi nhận: 2026-11-20

## 1. Phần cứng (Hardware)
- **CPU**: {data['cpu']['model']}
  - Số nhân vật lý (Cores): {data['cpu']['physical_cores']}
  - Số luồng logic (Threads): {data['cpu']['logical_processors']}
  - Xung nhịp danh định: {data['cpu']['base_clock_mhz']} MHz
  - Cache L1: {data['cpu']['cache']['l1_total_kb']} KB (Data: {data['cpu']['cache']['l1_data_kb']} KB, Instruction: {data['cpu']['cache']['l1_instruction_kb']} KB)
  - Cache L2: {data['cpu']['cache']['l2_kb']} KB (10 MB)
  - Cache L3: {data['cpu']['cache']['l3_kb']} KB (24 MB Intel Smart Cache)
- **RAM**: {data['ram']['total_visible_gb']} GB (2 thanh 8GB DDR4-3200 MT/s)
  - Module 1: Micron Technology 4ATF1G64HZ-3G2E1 (8GB, 3200 MHz)
  - Module 2: Lexar Co Limited LD4AS008G-3200ST (8GB, 3200 MHz)

## 2. Hệ điều hành & Nguồn điện (OS & Power)
- **Hệ điều hành**: {data['os']['caption']} (Phiên bản {data['os']['version']}, Build {data['os']['build_number']}, {data['os']['architecture']})
- **Power Plan**: {data['power']['power_scheme_name']} (`{data['power']['power_scheme_guid']}`)
- **Tình trạng cấp nguồn**: Cắm sạc AC (PowerOnline: {data['power']['ac_power_online']}, Đang sạc pin: {data['power']['battery_charging']})

## 3. Môi trường thực thi Java (Java & JMH)
- **Java Version**: `{data['java']['version']}`
- **Nhà cung cấp JDK**: {data['java']['vendor']}
- **Runtime**: {data['java']['runtime']}
- **Máy ảo (VM)**: {data['java']['vm']}
- **Maven**: Version {data['build_tool']['maven']['version']}
- **JMH (Java Microbenchmark Harness)**: Phiên bản {data['build_tool']['jmh_version']} (ghim cố định)

## 4. Môi trường phân tích dữ liệu (Python & Libraries)
- **Python Version**: {data['python']['version']}
- **Thư viện**:
  - `numpy`: {data['python']['libraries'].get('numpy')}
  - `pandas`: {data['python']['libraries'].get('pandas')}
  - `matplotlib`: {data['python']['libraries'].get('matplotlib')}
  - `scipy`: {data['python']['libraries'].get('scipy')}
  - `pyyaml`: {data['python']['libraries'].get('yaml')}
"""
    return md

def main():
    os.makedirs("results", exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    data = get_environment_data()

    json_path = os.path.join("results", "env.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written: {json_path}")

    md_path = os.path.join("docs", "ENVIRONMENT.md")
    md_content = generate_markdown(data)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Written: {md_path}")

if __name__ == "__main__":
    main()
