---
name: apache-airflow-dag-orchestration
description: Enterprise Apache Airflow 2.x DAG authoring, TaskFlow API, deferrable operators, idempotent execution models, and production workflow orchestration.
---

# Apache Airflow DAG Orchestration

Comprehensive architectural guide for authoring resilient, idempotent, and scalable data pipelines using Apache Airflow 2.x+ with TaskFlow API, custom operators, and Kubernetes/Celery executors.

---

## 1. Core Architecture & Execution Model

### 1.1 Airflow Components
- **Scheduler**: Parses DAG files continuously, evaluates scheduling rules, monitors task state, and enqueues commands to the executor.
- **Webserver**: Flask/React UI displaying DAG topology, execution history, metrics, and manual triggers.
- **Worker**: Executes actual task instances (in CeleryWorker pods, K8s Pods, or LocalExecutor threads).
- **Triggerer**: Runs an asynchronous event loop (asyncio) handling **Deferrable Operators** (Sensors/Async tasks) to save worker slots.
- **Metadata Database**: PostgreSQL/MySQL database storing DAG definitions, run history, variables, connection strings, and XComs.

```
┌───────────────────────────────────────────────────────────────┐
│                   Airflow Scheduler                           │
└──────────────────────────────┬────────────────────────────────┘
                               │ Reads DAGs & Enqueues Tasks
                               ▼
 ┌───────────────────┐  ┌─────────────┐  ┌────────────────────┐
 │ Metadata Database │  │ Triggerer   │  │  Executor / Worker │
 └───────────────────┘  └─────────────┘  └────────────────────┘
```

---

## 2. Pipeline Idempotency & Backfill Guarantees

### 2.1 Deterministic Execution Logic
Every DAG run MUST be deterministic for its target `logical_date` (`data_interval_start`). Never rely on system time (`datetime.now()`) inside execution logic.

```python
# Idempotent SQL execution pattern using logical_date variables
SQL_IDEMPOTENT_WRITE = """
DELETE FROM analytics.daily_revenue 
WHERE metric_date = '{{ ds }}';

INSERT INTO analytics.daily_revenue (metric_date, total_revenue)
SELECT 
    DATE(transaction_time) AS metric_date,
    SUM(amount) AS total_revenue
FROM raw.transactions
WHERE transaction_time >= '{{ data_interval_start }}'
  AND transaction_time < '{{ data_interval_end }}'
GROUP BY 1;
"""
```

---

## 3. Production Anti-Patterns

| Anti-Pattern | Operational Failure | Production Standard |
| :--- | :--- | :--- |
| Heavy data processing in `PythonOperator` | Worker memory crash (OOM), blocks worker pool | Offload compute to Spark, Databricks, Snowflake, or EKS/ECS |
| Top-level DB / API calls in DAG `.py` files | Scheduler lag; executes query every 30s during parsing | Move all external connection calls **inside** `@task` functions |
| Pushing large DataFrames / payloads into XCom | Database bloat, serializing gigabytes in Metadata DB | Store large artifacts in S3/GCS, pass URI via XCom |
| Synchronous Sensors blocking worker slots | Exhaused worker concurrency slots waiting on external API | Use **Deferrable Sensors** (`deferrable=True`) handled by Triggerer |
| Hardcoding credentials or static dates in code | Security vulnerability, broken backfills | Use Airflow Connections/Variables and `{{ ds }}` macros |

---

## 4. Production Implementation Blueprint

### TaskFlow API DAG with Deferrable Sensor, Retries, and SLA Alerts

```python
from datetime import datetime, timedelta
import logging
from typing import Dict, Any

from airflow.decorators import dag, task
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.operators.python import get_current_context

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["data-alerts@enterprise.com"],
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "execution_timeout": timedelta(hours=2),
}

def on_failure_callback(context: Dict[str, Any]) -> None:
    """Alert handler fired on task failure."""
    task_id = context.get("task_instance").task_id
    dag_id = context.get("dag").dag_id
    execution_date = context.get("execution_date")
    error = context.get("exception")
    
    logger.error(f"ALERT: Task '{task_id}' in DAG '{dag_id}' failed on {execution_date}. Error: {error}")

@dag(
    dag_id="orchestrate_ecommerce_analytics_v1",
    default_args=DEFAULT_ARGS,
    schedule_interval="0 3 * * *",  # Daily at 03:00 UTC
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["production", "analytics", "taskflow"],
    on_failure_callback=on_failure_callback,
)
def ecommerce_analytics_dag():

    # 1. Non-blocking S3 Sensor handled by Triggerer
    wait_for_raw_data = S3KeySensor(
        task_id="wait_for_raw_s3_data",
        bucket_key="s3://enterprise-ingest/raw/{{ ds }}/orders.json",
        wildcard_match=False,
        aws_conn_id="aws_default",
        poke_interval=60,
        timeout=3600,
        deferrable=True,  # Saves worker slot
    )

    @task(task_id="extract_and_stage_payload")
    def stage_s3_payload() -> str:
        """Downloads and stages raw data URI for downstream Spark job."""
        context = get_current_context()
        logical_date = context["ds"]
        
        manifest_uri = f"s3://enterprise-ingest/raw/{logical_date}/orders.json"
        logger.info(f"Staged manifest URI: {manifest_uri}")
        return manifest_uri

    @task.external_python(python="/opt/airflow/python_envs/spark_env/bin/python")
    def trigger_spark_analytics(manifest_uri: str) -> Dict[str, int]:
        """Runs isolated PySpark analytics transformation step."""
        logger.info(f"Processing payload: {manifest_uri}")
        # Processing offloaded safely to external engine
        return {"processed_rows": 1450000, "status_code": 200}

    @task(task_id="audit_partition_quality")
    def quality_gate(metrics: Dict[str, int]) -> None:
        """Validates processed data threshold prior to downstream downstream publish."""
        processed_rows = metrics.get("processed_rows", 0)
        if processed_rows <= 0:
            raise ValueError("Data Quality Gate Failed: Zero rows processed!")
        logger.info(f"Data Quality Gate Passed. Total rows verified: {processed_rows}")

    # Set DAG Execution Topology
    manifest_path = stage_s3_payload()
    spark_job = trigger_spark_analytics(manifest_path)
    audit = quality_gate(spark_job)

    wait_for_raw_data >> manifest_path >> spark_job >> audit

# Instantiate DAG
dag_instance = ecommerce_analytics_dag()
```
