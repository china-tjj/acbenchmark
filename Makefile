.PHONY: all bench analyze clean

all: bench analyze

bench:
	@echo ">>> Running benchmarks (may take 20+ min) ..."
	go test -bench=. -benchmem -count=1 -timeout=60m 2>/dev/null | tee bench.txt
	@echo ">>> Done."

analyze:
	python3 analyze.py bench.txt

clean:
	rm -f bench.txt results.md *.png
