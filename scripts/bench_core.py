# scripts/bench_core.py
import os
import time
import pymysql
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("MYSQL_HOST", "localhost")
PORT = int(os.getenv("MYSQL_PORT", 3306))
USER = os.getenv("MYSQL_USER", "root")
PWD = os.getenv("MYSQL_PASSWORD", "")
DB = os.getenv("MYSQL_DB", "nyc311")

BASELINE_QUERIES = [
    ("total_rows", "SELECT COUNT(*) FROM service_requests"),
    ("by_borough", "SELECT borough, COUNT(*) FROM service_requests GROUP BY borough"),
    ("year_2023_count",
     "SELECT COUNT(*) FROM service_requests "
     "WHERE created_date BETWEEN '2023-01-01' AND '2023-12-31'"),
    ("top_complaints",
     "SELECT complaint_type, COUNT(*) AS c "
     "FROM service_requests GROUP BY complaint_type "
     "ORDER BY c DESC LIMIT 10"),
    ("like_noise",
     "SELECT COUNT(*) FROM service_requests WHERE descriptor LIKE '%noise%'"),
    ("like_heat",
     "SELECT COUNT(*) FROM service_requests WHERE descriptor LIKE '%heat%'"),
]

FULLTEXT_QUERIES = [
    ("ft_noise",
     "SELECT COUNT(*) FROM service_requests "
     "WHERE MATCH(descriptor) AGAINST ('+noise' IN BOOLEAN MODE)"),
    ("ft_heat_hot_water",
     "SELECT COUNT(*) FROM service_requests "
     "WHERE MATCH(descriptor) AGAINST ('\"heat\" \"hot water\"' IN BOOLEAN MODE)"),
]


def run_benchmarks(label: str, queries):
    conn = pymysql.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PWD,
        database=DB,
        charset="utf8mb4",
        autocommit=True,
    )
    with conn.cursor() as cur:
        for name, sql in queries:
            print(f"\n=== [{label}] Query: {name} ===")
            t0 = time.time()
            cur.execute(sql)
            rows = cur.fetchall()
            elapsed = (time.time() - t0) * 1000
            print(f"Time: {elapsed:.2f} ms, rows returned: {len(rows)}")

            cur.execute(f"EXPLAIN ANALYZE {sql}")
            explain_rows = cur.fetchall()
            print("EXPLAIN ANALYZE:")
            for r in explain_rows:
                print(r[0])
    conn.close()
