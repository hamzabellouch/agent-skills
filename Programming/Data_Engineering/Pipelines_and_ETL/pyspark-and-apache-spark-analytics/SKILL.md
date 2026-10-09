---
name: pyspark-and-apache-spark-analytics
description: Master production PySpark and Apache Spark analytics, distributed data pipelines, Delta Lake/Iceberg optimization, memory management, and skew resolution.
---

# PySpark & Apache Spark Analytics

Comprehensive engineering guide for architecting, optimizing, and operating large-scale distributed data processing pipelines using PySpark and Apache Spark 3.x/4.x.

---

## 1. Core Principles & Architecture

### 1.1 Execution Model
- **Driver**: Plans execution, constructs DAGs, manages SparkSession, coordinates tasks, and collects metrics.
- **Executors**: Worker processes executing task threads, maintaining in-memory storage (RAM), and handling spill to disk.
- **Transformations vs Actions**:
  - **Narrow Transformations**: Operations where each input partition maps to at most one output partition (`map`, `filter`, `flatmap`). No network shuffle.
  - **Wide Transformations**: Operations requiring data exchange across cluster partitions (`groupByKey`, `reduceByKey`, `join`, `distinct`, `repartition`). Triggers a **Shuffle Stage**.
  - **Actions**: Trigger execution of physical execution plan (`count`, `collect`, `write`, `first`, `take`).

### 1.2 Data Lake storage Formats: Delta Lake & Apache Iceberg
- **Acid Transactions**: Transaction log (`_delta_log` or Iceberg metadata trees) providing ACID semantics, time travel, and rollback.
- **Medallion Architecture**:
  - **Bronze (Raw)**: Append-only ingestion layer preserving original schema (JSON, CSV, Parquet).
  - **Silver (Cleaned/Enriched)**: Deduplicated, typed, normalized, and joined domain entities.
  - **Gold (Aggregated/Business)**: Star-schema dimensions/facts, aggregated metrics, wide tables optimized for BI/ML queries.

---

## 2. Idempotency & Partitioning Strategies

### 2.1 Dynamic Partition Overwrite & Upserts
Idempotence guarantees that re-running a pipeline execution produces identical state without duplicate records or partial writes.

#### PySpark Dynamic Partition Overwrite
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("IdempotentPartitionWriter") \
    .config("spark.sql.sources.partitionOverwriteMode", "dynamic") \
    .getOrCreate()

# Ensures only affected partitions are replaced upon re-run
df_processed.write \
    .format("parquet") \
    .mode("overwrite") \
    .partitionBy("event_date") \
    .save("s3a://data-warehouse/silver/user_events/")
```

#### Delta Lake MERGE (Upsert) Pattern
```python
from delta.tables import DeltaTable

def upsert_to_delta(micro_batch_df, batch_id):
    delta_table = DeltaTable.forPath(spark, "s3a://data-warehouse/silver/user_profiles")
    
    delta_table.alias("target").merge(
        micro_batch_df.alias("updates"),
        "target.user_id = updates.user_id"
    ).whenMatchedUpdate(set={
        "email": "updates.email",
        "updated_at": "updates.updated_at",
        "status": "updates.status"
    }).whenNotMatchedInsert(values={
        "user_id": "updates.user_id",
        "email": "updates.email",
        "created_at": "updates.created_at",
        "updated_at": "updates.updated_at",
        "status": "updates.status"
    }).execute()
```

---

## 3. Performance Optimization & Tuning

### 3.1 Skew Mitigation Techniques
Data skew occurs when one partition receives disproportionately more data, stalling stage completion (99% task completion syndrome).

#### Salting Technique for Skewed Joins
```python
from pyspark.sql import functions as F

SALT_FACTOR = 8

# Add random salt to skewed left table
df_skewed = df_large.withColumn("salt", (F.rand() * SALT_FACTOR).cast("integer"))

# Explode right table to match all salt keys
df_small_salted = df_small.withColumn("salt_array", F.array([F.lit(i) for i in range(SALT_FACTOR)])) \
    .withColumn("salt", F.explode("salt_array")) \
    .drop("salt_array")

# Perform join on join_key AND salt key
df_joined = df_skewed.join(
    df_small_salted,
    on=["join_key", "salt"],
    how="inner"
).drop("salt")
```

### 3.2 Adaptive Query Execution (AQE)
Enable AQE to dynamically re-optimize execution plans based on runtime statistics:
```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")
```

### 3.3 Broadcast Join Tuning
Avoid network shuffles for small lookup tables (<10MB default, up to 1GB with tuning):
```python
from pyspark.sql.functions import broadcast

# Explicitly hint Spark to broadcast small dimension
df_fact.join(broadcast(df_dim_small), "dim_id", "inner")
```

---

## 4. Production Anti-Patterns

| Anti-Pattern | Operational Risk | Production Remedy |
| :--- | :--- | :--- |
| Calling `.collect()` on large DataFrames | Driver Out-Of-Memory (OOM) crash | Use `.take(n)`, write directly to storage, or sample data |
| Using `DataFrame.toPandas()` in distributed loop | Serialization bottleneck & Driver OOM | Use PySpark Pandas API or PyArrow UDFs (`pandas_udf`) |
| Unpartitioned `.repartition(1)` before write | Single executor bottleneck & disk spill | Use `.coalesce(n)` or dynamic partition overwrites |
| Row-by-row `.iterrows()` in Python UDFs | Context switching overhead (JVM to Python) | Native Spark SQL functions or vectorized `pandas_udf` |
| Over-partitioning (tiny files problem) | NameNode / S3 metadata strain, slow listing | Target ~128MB - 512MB file sizes, run `OPTIMIZE` / `VORDER` |

---

## 5. Production Implementation Blueprint

### Scalable Pipeline with Vectorized UDFs & Structural Monitoring

```python
import sys
import logging
from typing import Iterator
import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, StructType, StructField, StringType, TimestampType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SparkAnalyticsEngine")

def build_spark_session(app_name: str) -> SparkSession:
    """Configures high-throughput Spark session optimized for S3/Delta processing."""
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

# Vectorized Pandas UDF for scalable ML/Analytical scoring
@F.pandas_udf(DoubleType())
def calculate_risk_score_udf(amount_series: pd.Series, velocity_series: pd.Series) -> pd.Series:
    """Vectorized calculation executed in Arrow batches across worker nodes."""
    return (amount_series * 0.45) + (velocity_series * 1.85)

def process_transaction_bronze_to_silver(
    spark: SparkSession,
    bronze_path: str,
    silver_path: str,
    partition_date: str
) -> None:
    """Idempotent Bronze-to-Silver transformation pipeline."""
    logger.info(f"Ingesting Bronze payload from {bronze_path} for date: {partition_date}")

    raw_df = spark.read.format("delta").load(bronze_path) \
        .filter(F.col("event_date") == partition_date)

    # Data Quality Cleanse & Deduplication
    cleaned_df = raw_df \
        .filter(F.col("transaction_id").isNotNull()) \
        .dropDuplicates(["transaction_id"]) \
        .withColumn("amount", F.col("amount").cast(DoubleType())) \
        .withColumn("velocity", F.col("velocity").cast(DoubleType())) \
        .withColumn("risk_score", calculate_risk_score_udf(F.col("amount"), F.col("velocity"))) \
        .withColumn("processed_at", F.current_timestamp())

    logger.info("Writing clean records to Silver Delta table with partition isolation...")
    
    cleaned_df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("replaceWhere", f"event_date = '{partition_date}'") \
        .save(silver_path)

    logger.info(f"Successfully processed Silver partition: {partition_date}")

if __name__ == "__main__":
    spark = build_spark_session("ProductionSparkPipeline")
    try:
        process_transaction_bronze_to_silver(
            spark=spark,
            bronze_path="s3a://enterprise-datalake/bronze/transactions",
            silver_path="s3a://enterprise-datalake/silver/transactions",
            partition_date="2026-07-18"
        )
    except Exception as e:
        logger.error(f"Pipeline execution failure: {str(e)}")
        sys.exit(1)
    finally:
        spark.stop()
```
