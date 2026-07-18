---
name: dbt-data-build-tool-transformations
description: Production-grade dbt (data build tool) engineering, modular data modeling, incremental materializations, testing strategies, and macro development.
---

# dbt (Data Build Tool) Transformations

Architectural reference guide for building, testing, and maintaining analytics engineering pipelines using dbt with modern data warehouses (Snowflake, BigQuery, Databricks, PostgreSQL).

---

## 1. Data Model Layers & DAG Architecture

```
[ Raw Sources ] 
      │
      ▼
┌─────────────────────────────────────────┐
│ Staging (stg_source_entity)             │ ── Type casting, renaming, 1:1 with source
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│ Intermediate (int_domain_joined)        │ ── Business logic, aggregations, joins
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│ Marts (fct_orders, dim_customers)       │ ── Dimensional facts/dims or OBT for BI
└─────────────────────────────────────────┘
```

### 1.1 Layer Responsibilities
- **Staging (`stg_`)**: Clean, standardize data types, rename fields to snake_case, light data filtering. Strictly 1-to-1 mapping with raw source tables. Materialized as `view` or `ephemeral`.
- **Intermediate (`int_`)**: Structural transformation layer where entities are joined, complex business logic is applied, and domain prep is performed. Materialized as `ephemeral` or `view` (or `table` if complex).
- **Marts (`fct_`, `dim_`, `obt_`)**: Business-facing consumption models. Star schema (Fact/Dimension tables) or One Big Table (OBT) optimized for analytical engines. Materialized as `table` or `incremental`.

---

## 2. Idempotency & Incremental Materializations

Idempotency in dbt ensures that re-executing `dbt run` for a historical partition window updates existing records without duplicating primary keys or losing state.

### 2.1 Incremental Merging Strategy
```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',
    on_schema_change='sync_all_columns',
    cluster_by=['order_date']
) }}

WITH source_data AS (
    SELECT * 
    FROM {{ ref('stg_ecommerce__orders') }}
    {% if is_incremental() %}
        -- Lookback window (e.g. 3 days) to handle late-arriving events safely
        WHERE updated_at >= (SELECT DATEADD('day', -3, MAX(updated_at)) FROM {{ this }})
    {% endif %}
)

SELECT
    order_id,
    customer_id,
    order_status,
    total_amount_usd,
    created_at,
    updated_at
FROM source_data
```

---

## 3. Production Anti-Patterns

| Anti-Pattern | Operational Failure | Production Standard |
| :--- | :--- | :--- |
| Hardcoding table names (`FROM raw.db.orders`) | Breaks DAG lineage & multi-environment compilation | Always use `{{ source('raw', 'orders') }}` or `{{ ref('stg_orders') }}` |
| Putting heavy aggregations in `stg_` models | Fragile pipeline, duplicated business logic | Keep staging 1:1, move business transformations to `int_` |
| Omitting primary key tests (`unique`, `not_null`) | Silent data duplication in downstream BI reports | Enforce strict schema tests on all primary keys in `schema.yml` |
| Unbounded `is_incremental()` without lookback | Missed updates from late-arriving CDC records | Add a deterministic lookback period (e.g. `MAX(updated_at) - INTERVAL '3 DAYS'`) |
| Non-DRY SQL snippets duplicated across models | High maintenance burden and logic drift | Encapsulate reusable SQL logic inside dbt **Macros** |

---

## 4. Production Code Blueprints

### 4.1 Schema Definition & Automated Quality Gates (`schema.yml`)

```yaml
version: 2

sources:
  - name: ecom_raw
    database: raw_platform
    schema: mongodb
    tables:
      - name: orders
        loaded_at_field: _updated_at
        freshness:
          warn_after: {count: 12, period: hour}
          error_after: {count: 24, period: hour}

models:
  - name: fct_orders
    description: "Incremental fact table capturing processed ecommerce customer orders."
    columns:
      - name: order_id
        description: "Surrogate primary key for orders."
        tests:
          - unique
          - not_null
      - name: customer_id
        description: "Foreign key referencing dim_customers."
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: total_amount_usd
        tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
```

### 4.2 Generic Custom Macro for Deduplication (`macros/deduplicate_by_window.sql`)

```sql
{% macro deduplicate_by_window(relation, primary_key, order_by_clause) %}
    SELECT
        *
    EXCEPT (_row_num)
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY {{ primary_key }}
                ORDER BY {{ order_by_clause }}
            ) AS _row_num
        FROM {{ relation }}
    )
    WHERE _row_num = 1
{% endmacro %}
```

### 4.3 Production Incremental Fact Model (`models/marts/fct_orders.sql`)

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',
    partition_by={
      "field": "created_at",
      "data_type": "timestamp",
      "granularity": "day"
    } if target.type == 'bigquery' else none
) }}

WITH stg_orders AS (
    SELECT * FROM {{ ref('stg_ecommerce__orders') }}
    {% if is_incremental() %}
        WHERE updated_at >= (SELECT COALESCE(MAX(updated_at), '1900-01-01') FROM {{ this }})
    {% endif %}
),

stg_payments AS (
    SELECT * FROM {{ ref('stg_ecommerce__payments') }}
),

deduped_orders AS (
    {{ deduplicate_by_window('stg_orders', 'order_id', 'updated_at DESC') }}
),

final AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_status,
        COALESCE(p.payment_amount_usd, 0) AS total_amount_usd,
        o.created_at,
        o.updated_at
    FROM deduped_orders o
    LEFT JOIN stg_payments p ON o.order_id = p.order_id
)

SELECT * FROM final
```
