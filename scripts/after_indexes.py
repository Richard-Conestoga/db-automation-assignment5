from bench_core import run_benchmarks, BASELINE_QUERIES, FULLTEXT_QUERIES

if __name__ == "__main__":
    # scalar + LIKE queries after indexes
    run_benchmarks("after_indexes", BASELINE_QUERIES)
    # FULLTEXT queries after FULLTEXT indexes exist
    run_benchmarks("after_indexes_fulltext", FULLTEXT_QUERIES)
