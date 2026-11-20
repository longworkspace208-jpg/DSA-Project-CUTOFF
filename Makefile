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
	python scripts/check_diff.py
	mvn test
	@echo [TEST] Diff checks and unit tests passed.

data:
	python scripts/gen_data.py
	python scripts/verify_data.py
	@echo [DATA] Datasets generated and verified.

bench:
	mvn package -DskipTests
	python scripts/run_bench.py
	python scripts/validate_csv.py
	@echo [BENCH] Benchmarks completed and validated.

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
