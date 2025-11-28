# Title: NYC 311 Database Automation – Indexing and FULLTEXT Benchmark

### Overview

This project automates loading, cleaning, and benchmarking the NYC 311 Service Requests dataset in MySQL using a Docker-based setup and Python ETL/benchmark scripts. It demonstrates how B-tree and FULLTEXT indexes change query performance and execution plans on a 200k-row sample.

### Project goals

- Load ≥100k NYC 311 rows into MySQL.
- Run scalar queries (counts, group-bys, date filters) before and after indexing.
- Run text searches using LIKE vs FULLTEXT MATCH…AGAINST.


### Tech stack

- MySQL 8 (Docker container).
- Python (pandas, PyMySQL, dotenv).
- Docker Compose for app + database orchestration.


### 1. Database setup

- docker-compose.yml defines:
    - mysql:8.0 container with:
        - MYSQL_ROOT_PASSWORD
        - MYSQL_DATABASE=nyc311
    - Persistent volume for /var/lib/mysql.
    - Optional app service to run ETL and benchmarks.
- Schema (created by scripts/etl.py):
    - service_requests:
        - unique_key BIGINT PRIMARY KEY
        - created_date DATETIME NOT NULL
        - closed_date DATETIME NULL
        - agency VARCHAR(16)
        - complaint_type VARCHAR(128)
        - descriptor VARCHAR(255)
        - borough VARCHAR(32)
        - latitude DECIMAL(9,6)
        - longitude DECIMAL(9,6)
    - Types are chosen to match NYC Open Data fields (IDs as BIGINT, timestamps as DATETIME, text as VARCHAR, coordinates as DECIMAL).


### 2. Data load and cleaning

- scripts/download_nyc311.py:
    - Downloads CSV from NYC Open Data via SoQL endpoint filtered to a single year (e.g., 2023) with a limit (e.g., 200k rows).
- scripts/etl.py:
    - Reads CSV in chunks (10k rows).
    - Cleans data:
        - Normalizes column names and selects relevant columns.
        - Parses created_date/closed_date as datetimes.
        - Casts latitude/longitude to numeric.
        - Drops rows with missing unique_key or created_date.
        - Deduplicates on unique_key.
        - Infers borough from ZIP where missing.
    - Inserts rows into service_requests with upsert on unique_key.
- After ingestion:
    - SELECT COUNT(*) FROM service_requests; returns ~200k rows, satisfying the ≥100k requirement.


### 3. Benchmark scripts

- scripts/bench_core.py:
    - Provides run_benchmarks(label, queries) that:
        - Connects to MySQL using .env.
        - Executes each query:
            - Measures execution time in ms in Python.
            - Runs EXPLAIN ANALYZE for the same SQL and prints the plan text.
- scripts/before_indexes.py:
    - Runs BASELINE_QUERIES:
        - total_rows
        - by_borough
        - year_2023_count
        - top_complaints
        - like_noise (descriptor LIKE '%noise%')
        - like_heat (descriptor LIKE '%heat%')
- scripts/after_indexes.py:
    - Runs BASELINE_QUERIES again plus FULLTEXT_QUERIES:
        - ft_noise (MATCH(descriptor) AGAINST('+noise' IN BOOLEAN MODE))
        - ft_heat_hot_water (MATCH(descriptor) AGAINST('"heat" "hot water"' IN BOOLEAN MODE))

Outputs are saved via:

- python scripts/before_indexes.py > reports/before_indexes.txt 2>\&1
- python scripts/after_indexes.py > reports/after_indexes.txt 2>\&1


### 4. Indexes

- db/indexes.sql:
    - B-tree indexes:
        - idx_created_date ON service_requests(created_date)
        - idx_borough ON service_requests(borough)
        - idx_borough_created ON service_requests(borough, created_date)
    - FULLTEXT indexes:
        - idx_ft_descriptor ON service_requests(descriptor)
        - idx_ft_desc_complaint ON service_requests(descriptor, complaint_type)
- Applied with:
    - docker exec dbautomation-assignment5-db-1 mysql -uroot -p... nyc311 < db/indexes.sql
- Verified via:
    - SHOW INDEX FROM service_requests; showing PRIMARY, B-tree, and FULLTEXT indexes.


### 5. How to run everything

1) Start MySQL:

- docker compose up -d

2) Download data:

- python scripts/download_nyc311.py

3) Ingest data:

- python scripts/etl.py

4) Run baseline benchmarks (no indexes):

- python scripts/before_indexes.py > reports/before_indexes.txt 2>\&1

5) Create indexes:

- docker exec dbautomation-assignment5-db-1 mysql -uroot -p... nyc311 < db/indexes.sql

6) Run benchmarks after indexes:

- python scripts/after_indexes.py > reports/after_indexes.txt 2>\&1
