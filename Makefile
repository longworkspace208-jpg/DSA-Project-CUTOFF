# Makefile for Java Sorting Cutoff Experiment

SHELL := cmd.exe

.PHONY: all test data bench counts analyze report verify clean env

all: data counts bench analyze report
	@echo [ALL] Complete experiment pipeline executed successfully.

env:
	python scripts/gather_env.py
	python -m json.tool results/env.json > nul
	@echo [ENV] Environment collected and verified.

test:
	mvn clean test
	@echo [TEST] Unit tests passed.

data:
	python scripts/generate_data.py
	@echo [DATA] Datasets generated.

bench:
	mvn package -DskipTests
	java -jar target/benchmarks.jar ".*SortingBenchmark.*" -rf csv -rff results/bench_raw.csv
	@echo [BENCH] Benchmarks completed.

counts:
	python scripts/run_operation_counts.py
	@echo [COUNTS] Operation counting completed.

analyze:
	python scripts/analyze_results.py
	@echo [ANALYZE] Statistical analysis and figures generated.

report:
	python scripts/generate_report.py
	@echo [REPORT] REPORT.md updated from raw data.

verify: test
	python -m json.tool results/env.json > nul
	python scripts/verify_experiment.py
	@echo [VERIFY] Experiment verification passed.

clean:
	mvn clean
