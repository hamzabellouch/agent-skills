---
name: pandas-polars-eda
metadata:
  category: Data Science and Exploratory Analysis
description: Master high-performance exploratory data analysis (EDA) using Pandas and Polars, missing value profiling, outlier detection, data distribution analysis, correlation matrices, and vectorised pipelines. Trigger when performing EDA, data cleaning, or memory-efficient tabular analysis in Python.
compatibility: Python 3.9+, Pandas 2.0+, Polars 0.20+, PyArrow, Matplotlib, Seaborn
---

# Pandas & Polars EDA Skill Guide

This skill provides production standards, high-performance code patterns, memory optimizations, and data hygiene rules for performing Exploratory Data Analysis (EDA) using Pandas and Polars.

---

## 1. Engine Comparison: Pandas vs Polars

```text
+-----------------------+---------------------------------------+---------------------------------------+
| Feature               | Pandas (2.0+ with PyArrow)             | Polars                                |
+-----------------------+---------------------------------------+---------------------------------------+
| **Execution Engine**  | Single-threaded eager execution       | Multi-threaded query optimization     |
| **Memory Model**      | In-memory numpy / arrow backend       | Apache Arrow columnar format native   |
| **Evaluation Mode**   | Eager only                            | Eager & Lazy evaluation (`lazy()`)    |
| **Performance**       | Moderate on datasets > 1GB            | Extremely fast (10x-30x speedups)     |
+-----------------------+---------------------------------------+---------------------------------------+
```

---

## 2. Automated Data Health & Missing Value Profiling

### A. Polars Health Check Pipeline

```python
import polars as pl

def profile_polars_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    """Generate comprehensive dataset health report in Polars."""
    null_counts = df.null_count()
    dtypes = pl.DataFrame({"column": df.columns, "dtype": [str(d) for d in df.dtypes]})
    
    stats = df.describe()
    
    summary = dtypes.with_columns(
        null_count=pl.Series([df[col].null_count() for col in df.columns]),
        null_percentage=pl.Series([round((df[col].null_count() / df.height) * 100, 2) for col in df.columns]),
        n_unique=pl.Series([df[col].n_unique() for col in df.columns]),
    )
    return summary

# Usage
df = pl.read_parquet("sales_data.parquet")
health_report = profile_polars_dataframe(df)
print(health_report)
```

### B. Pandas PyArrow Data Profiling

```python
import pandas as pd

def profile_pandas_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Generate dataset health report utilizing Pandas 2.0+ PyArrow types."""
    profile = pd.DataFrame({
        "dtype": df.dtypes,
        "null_count": df.isna().sum(),
        "null_percentage": (df.isna().sum() / len(df) * 100).round(2),
        "unique_values": df.nunique(),
        "memory_mb": (df.memory_usage(deep=True) / 1024 / 1024).round(2)
    })
    return profile

# Read parquet with PyArrow backend for memory efficiency
df_pd = pd.read_parquet("sales_data.parquet", engine="pyarrow", dtype_backend="pyarrow")
print(profile_pandas_dataframe(df_pd))
```

---

## 3. High-Performance Exploratory Analysis Pipelines

### A. Polars Lazy API Data Aggregation

Always leverage Polars `.lazy()` API to allow query optimization prior to execution:

```python
import polars as pl

query = (
    pl.scan_parquet("transactions/*.parquet")
    .filter(pl.col("status") == "COMPLETED")
    .filter(pl.col("transaction_date") >= pl.date(2025, 1, 1))
    .group_by(["region", "customer_tier"])
    .agg([
        pl.col("amount").sum().alias("total_revenue"),
        pl.col("amount").mean().alias("avg_order_value"),
        pl.col("transaction_id").count().alias("transaction_count"),
        pl.col("amount").quantile(0.95).alias("p95_amount")
    ])
    .sort("total_revenue", descending=True)
)

# Execute optimized query plan
results_df = query.collect()
print(results_df)
```

### B. Vectorized Outlier Detection (Interquartile Range - IQR)

```python
def detect_outliers_iqr_polars(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    """Filter outliers using IQR bounds in Polars."""
    q25 = df[column_name].quantile(0.25)
    q75 = df[column_name].quantile(0.75)
    iqr = q75 - q25
    
    lower_bound = q25 - (1.5 * iqr)
    upper_bound = q75 + (1.5 * iqr)
    
    outliers = df.filter(
        (pl.col(column_name) < lower_bound) | (pl.col(column_name) > upper_bound)
    )
    print(f"Detected {outliers.height} outliers out of {df.height} rows for '{column_name}'.")
    return outliers
```

---

## 4. Visual Correlation & Distribution Analysis

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_correlation_heatmap(df: pd.DataFrame, output_path: str = "correlation_matrix.png"):
    """Render high-resolution correlation matrix heatmap."""
    numeric_df = df.select_dtypes(include=["number"])
    corr_matrix = numeric_df.corr(method="spearman")

    plt.figure(figsize=(12, 8), dpi=300)
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8}
    )
    plt.title("Spearman Rank Correlation Heatmap", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
```

---

## 5. Anti-Patterns & Best Practices

| Anti-Pattern | Performance / Memory Penalty | Production Best Practice |
| :--- | :--- | :--- |
| **Iterating rows using `for index, row in df.iterrows():`** | 100x-1000x slower execution speed; causes massive CPU bottleneck. | Always use vectorized expressions (`pl.col()` in Polars or vectorized Pandas methods). |
| **Loading massive CSVs into Pandas eagerly** | Causes Out-Of-Memory (OOM) crashes on large files. | Use `pl.scan_csv()` or convert raw files to Parquet format before analysis. |
| **Using `inplace=True` in Pandas** | Does not save memory and will be removed in future Pandas versions. | Assign transformed DataFrames explicitly (`df = df.drop(...)`). |
| **Ignoring column data types (`object` vs `category`/`dictionary`)** | `object` dtypes bloat memory usage by up to 10x. | Cast high-cardinality string columns to `Categorical` or `String` Arrow backend. |
