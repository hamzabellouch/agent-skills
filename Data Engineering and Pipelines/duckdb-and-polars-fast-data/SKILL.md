---
name: duckdb-and-polars-fast-data
description: High-performance in-process analytics using DuckDB and Polars, zero-copy Apache Arrow integration, lazy evaluation, SIMD vectorized processing, and out-of-core data pipelines.
---

# DuckDB & Polars: Fast Local & In-Process Data Engineering

Production guide for architecting ultra-fast, single-node data processing engines using DuckDB and Polars. Ideal for sub-second analytics, serverless micro-ETL pipelines, and memory-efficient out-of-core computations.

---

## 1. Architectural Foundation & Comparison

| Feature | DuckDB | Polars |
| :--- | :--- | :--- |
| **Engine Architecture** | In-process vectorized C++ SQL OLAP Database | Multi-threaded Rust DataFrame Engine |
| **Primary Interface** | SQL, Python DB-API, Relational API | Expression API, LazyFrame / DataFrame |
| **Execution Model** | Vectorized Query Execution (Morsel Driven) | Query Engine with Expression Fusion & Pushdowns |
| **Out-Of-Core Execution**| Native automatic disk spilling for larger-than-RAM | Native `sink_parquet()` / streaming engine |
| **Data Interop** | Zero-copy Apache Arrow, Parquet, Iceberg | Zero-copy PyArrow, Arrow C Data Interface |

---

## 2. Zero-Copy Interoperability & Memory Pipeline

```
┌─────────────────────────┐     Apache Arrow Interop      ┌─────────────────────────┐
│ DuckDB (SQL Engine)     │ ◄───────────────────────────► │ Polars (Lazy Engine)    │
│ Direct Parquet Scan     │         (Zero Copy)           │ Expressions & Streaming │
└─────────────────────────┘                               └─────────────────────────┘
```

By leveraging Apache Arrow as a unified in-memory representation, datasets can be passed between DuckDB and Polars with **zero memory duplication overhead**.

---

## 3. Idempotent Write Patterns & Partitioning

### 3.1 DuckDB Atomic Partition Overwrite
```python
import duckdb

conn = duckdb.connect("analytics.duckdb")

# Atomic replacement of table partition within transaction block
conn.execute("""
BEGIN TRANSACTION;

DELETE FROM sales_fact WHERE sale_date = '2026-07-18';

INSERT INTO sales_fact 
SELECT * FROM read_parquet('s3://ingest/2026-07-18/*.parquet');

COMMIT;
""")
```

### 3.2 Polars Atomic Out-of-Core Partition Sink
```python
import polars as pl

# Write LazyFrame stream to Parquet atomically
lazy_df = pl.scan_parquet("s3://raw-events/*.parquet") \
    .filter(pl.col("event_date") == "2026-07-18") \
    .with_columns([
        (pl.col("raw_amount") * pl.col("fx_rate")).alias("amount_usd")
    ])

# Sink directly to disk with chunked memory allocation
lazy_df.sink_parquet(
    "s3://silver-events/event_date=2026-07-18/data.parquet",
    compression="snappy",
    statistics=True
)
```

---

## 4. Production Anti-Patterns

| Anti-Pattern | Performance Impact | Production Remedy |
| :--- | :--- | :--- |
| Using `.apply()` or Python loops in Polars | Kills Rust parallel acceleration & single-threaded fallback | Use native Polars **Expressions** (`pl.col().when().then()`) |
| Calling `.collect()` early on large datasets | Triggers Out-Of-Memory (OOM) load before optimizations | Chain operations on `LazyFrame` (`pl.scan_parquet()`) and sink |
| High-frequency concurrent write connections in DuckDB | Database file locking (`database is locked` error) | Use single writer process, or read-only pool (`read_only=True`) |
| Reading large CSVs line-by-line | Extreme I/O bottleneck | Use multi-threaded CSV/Parquet reader (`pl.scan_csv()`, `duckdb.read_csv()`) |
| Unnecessary conversion to pandas DataFrame | Massive memory copies and CPU serialization loss | Standardize on PyArrow or zero-copy Arrow tables |

---

## 5. Production Implementation Blueprint

### End-to-End High Performance ETL Pipeline (DuckDB + Polars Zero-Copy)

```python
import logging
from pathlib import Path
import duckdb
import polars as pl

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DuckDBPolarsPipeline")

def run_inprocess_analytics_pipeline(
    raw_parquet_pattern: str,
    output_parquet_path: str,
    target_date: str
) -> None:
    """Executes high-throughput hybrid DuckDB + Polars analytical transformation."""
    logger.info("Initializing in-process DuckDB engine...")
    
    # Configure DuckDB memory and threads for containerized execution
    db_conn = duckdb.connect(database=":memory:")
    db_conn.execute("SET memory_limit='8GB'")
    db_conn.execute("SET threads=4")

    logger.info(f"Scanning raw Parquet payloads via DuckDB for date: {target_date}")
    
    # 1. DuckDB SQL Layer for high-speed aggregated windowing
    sql_query = f"""
        SELECT 
            user_id,
            device_type,
            COUNT(event_id) AS total_events,
            SUM(session_duration) AS total_duration_sec,
            MAX(event_timestamp) AS last_event_at
        FROM read_parquet('{raw_parquet_pattern}')
        WHERE strftime(event_timestamp, '%Y-%m-%d') = '{target_date}'
        GROUP BY user_id, device_type
    """
    
    # Execute query and extract zero-copy Arrow table
    arrow_table = db_conn.execute(sql_query).arrow()
    logger.info("Zero-copy Arrow table extracted successfully from DuckDB.")

    # 2. Polars Lazy Engine Layer for complex expression scoring
    logger.info("Converting Arrow table to Polars LazyFrame with zero memory copy...")
    lazy_pipeline = pl.from_arrow(arrow_table).lazy()

    processed_lazy = lazy_pipeline.with_columns([
        # Vectorized scoring logic in Rust
        (
            pl.when(pl.col("total_events") > 50)
            .then(pl.lit("HIGH_ENGAGEMENT"))
            .when(pl.col("total_events") > 10)
            .then(pl.lit("MEDIUM_ENGAGEMENT"))
            .otherwise(pl.lit("LOW_ENGAGEMENT"))
        ).alias("user_tier"),
        (pl.col("total_duration_sec") / 60.0).alias("total_duration_min")
    ]).filter(pl.col("user_tier") != "LOW_ENGAGEMENT")

    # 3. Stream output out-of-core to disk
    logger.info(f"Sinking processed analytical results to: {output_parquet_path}")
    
    output_dir = Path(output_parquet_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    processed_lazy.sink_parquet(
        output_parquet_path,
        compression="zstd",
        compression_level=3,
        statistics=True
    )
    
    logger.info("Pipeline execution completed successfully.")

if __name__ == "__main__":
    run_inprocess_analytics_pipeline(
        raw_parquet_pattern="data/raw/events/*.parquet",
        output_parquet_path="data/gold/user_engagement/date=2026-07-18/part-0.parquet",
        target_date="2026-07-18"
    )
```
