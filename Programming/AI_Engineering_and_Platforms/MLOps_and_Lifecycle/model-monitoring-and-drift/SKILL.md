---
name: model-monitoring-and-drift
metadata:
  category: Machine Learning Operations (MLOps)
description: >-
  Implement automated machine learning model performance monitoring, statistical data drift (KS-test, PSI, Wasserstein distance),
  concept drift detection, and prediction quality evaluation in production ML systems using Evidently AI, NannyML, SciPy, and Prometheus.
  Triggers when establishing model observability, real-time feature drift middleware, automated HTML drift reporting, or retraining trigger alerts.
compatibility: Python (>= 3.9), Evidently AI (>= 0.4.0), SciPy, Prometheus Client, FastAPI / Flask
---

# Model Monitoring & Drift Detection

Production patterns for measuring Data Drift, Concept Drift, and Performance Decay in live machine learning applications.

---

## 1. Drift Monitoring Conceptual Framework

| Drift Category | Definition | Statistical Metric | Remediation Strategy |
| :--- | :--- | :--- | :--- |
| **Data Drift (Covariate Shift)** | Distribution of input features $P(X)$ changes over time. | Kolmogorov-Smirnov Test, Population Stability Index (PSI), Wasserstein Distance | Feature re-normalization, Retraining on recent data window |
| **Concept Drift** | Relationship between input features and target $P(Y \mid X)$ changes. | Cramér's V, Wasserstein Distance, Accuracy/F1 degradation | Architecture update, Label re-annotation, Retraining |
| **Prior Probability Shift** | Target label distribution $P(Y)$ changes. | Chi-Square Goodness-of-Fit, Jensen-Shannon Divergence | Decision threshold re-calibration |

---

## 2. Statistical Data Drift Engine (`drift_engine.py`)

A pure Python + SciPy statistical drift evaluator for batch production datasets.

```python
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, chi2_contingency
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatisticalDriftDetector:
    def __init__(self, reference_data: pd.DataFrame, alpha: float = 0.05, psi_threshold: float = 0.2):
        self.reference_data = reference_data
        self.alpha = alpha
        self.psi_threshold = psi_threshold

    def calculate_psi(self, reference: np.ndarray, current: np.ndarray, num_buckets: int = 10) -> float:
        """Calculates Population Stability Index (PSI) for continuous variables."""
        # Define bucket boundaries using reference quantiles
        percentiles = np.linspace(0, 100, num_buckets + 1)
        buckets = np.percentile(reference, percentiles)
        buckets[0] = -np.inf
        buckets[-1] = np.inf

        # Calculate counts per bucket
        ref_counts, _ = np.histogram(reference, bins=buckets)
        cur_counts, _ = np.histogram(current, bins=buckets)

        # Convert to proportions with zero-handling smoothing
        ref_props = np.where(ref_counts == 0, 1e-4, ref_counts) / len(reference)
        cur_props = np.where(cur_counts == 0, 1e-4, cur_counts) / len(current)

        # Calculate PSI formula
        psi_value = np.sum((cur_props - ref_props) * np.log(cur_props / ref_props))
        return float(psi_value)

    def evaluate_numerical_feature(self, feature_name: str, current_data: pd.DataFrame) -> dict:
        ref_col = self.reference_data[feature_name].dropna().values
        cur_col = current_data[feature_name].dropna().values

        # Kolmogorov-Smirnov Test
        ks_stat, p_value = ks_2samp(ref_col, cur_col)
        drift_detected_ks = p_value < self.alpha

        # Population Stability Index
        psi_val = self.calculate_psi(ref_col, cur_col)
        drift_detected_psi = psi_val > self.psi_threshold

        return {
            "feature": feature_name,
            "type": "numerical",
            "ks_statistic": float(ks_stat),
            "p_value": float(p_value),
            "psi_value": psi_val,
            "drift_detected": drift_detected_ks or drift_detected_psi
        }

    def evaluate_categorical_feature(self, feature_name: str, current_data: pd.DataFrame) -> dict:
        ref_counts = self.reference_data[feature_name].value_counts()
        cur_counts = current_data[feature_name].value_counts()

        # Combine counts into contingency table
        df_contingency = pd.DataFrame({'ref': ref_counts, 'cur': cur_counts}).fillna(0)
        chi2_stat, p_value, _, _ = chi2_contingency(df_contingency.T)

        return {
            "feature": feature_name,
            "type": "categorical",
            "chi2_statistic": float(chi2_stat),
            "p_value": float(p_value),
            "drift_detected": p_value < self.alpha
        }

    def run_drift_analysis(self, current_data: pd.DataFrame) -> dict:
        results = []
        drifted_count = 0

        for col in self.reference_data.columns:
            if np.issubdtype(self.reference_data[col].dtype, np.number):
                res = self.evaluate_numerical_feature(col, current_data)
            else:
                res = self.evaluate_categorical_feature(col, current_data)
            
            if res["drift_detected"]:
                drifted_count += 1
            results.append(res)

        dataset_drift_ratio = drifted_count / len(self.reference_data.columns)

        return {
            "dataset_drift_ratio": dataset_drift_ratio,
            "dataset_drift_detected": dataset_drift_ratio >= 0.3,
            "feature_metrics": results
        }
```

---

## 3. Real-Time Inference Monitoring Middleware (FastAPI + Prometheus Exporter)

Export real-time feature drift statistics directly to Prometheus from your inference endpoints.

```python
from fastapi import FastAPI, Request
from prometheus_client import Gauge, Counter, make_asgi_app
import numpy as np
import time

app = FastAPI(title="ML Model Serving with Drift Exporter")

# Prometheus Metrics Definition
PREDICTION_COUNT = Counter("model_predictions_total", "Total inference requests executed")
FEATURE_DRIFT_GAUGE = Gauge("model_feature_psi", "Population Stability Index per Feature", ["feature_name"])
DATASET_DRIFT_STATUS = Gauge("model_dataset_drift_detected", "1 if dataset level drift detected else 0")

# Reference baseline mean and std for online z-score check
BASELINE_STATS = {
    "income": {"mean": 65000.0, "std": 15000.0},
    "credit_score": {"mean": 710.0, "std": 45.0}
}

@app.post("/predict")
async def predict_endpoint(payload: dict):
    start_time = time.time()
    PREDICTION_COUNT.inc()

    features = payload.get("features", {})
    
    # Online Z-score Outlier & Drift Metric Export
    for feature_name, val in features.items():
        if feature_name in BASELINE_STATS:
            mean = BASELINE_STATS[feature_name]["mean"]
            std = BASELINE_STATS[feature_name]["std"]
            z_score = abs((val - mean) / std)
            
            # Export Z-Score as online proxy for drift
            FEATURE_DRIFT_GAUGE.labels(feature_name=feature_name).set(z_score)

    # Perform prediction logic (mocked)
    score = np.random.random()

    return {"credit_decision": "approved" if score > 0.5 else "rejected", "score": score}

# Expose /metrics endpoint for Prometheus scrapers
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## 4. Evidently AI Automated HTML Drift Reporting (`generate_report.py`)

Generate offline interactive HTML drift and data quality reports using Evidently AI.

```python
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset, DataQualityPreset

def generate_evidently_drift_report(reference_df: pd.DataFrame, current_df: pd.DataFrame, output_filepath: str):
    """Generates an HTML Data & Target Drift Report."""
    report = Report(metrics=[
        DataDriftPreset(),
        DataQualityPreset(),
        TargetDriftPreset()
    ])

    report.run(reference_data=reference_df, current_data=current_df)
    report.save_html(output_filepath)
    print(f"Drift report generated successfully at: {output_filepath}")

if __name__ == "__main__":
    ref = pd.DataFrame({"income": [50000, 60000, 70000, 80000], "target": [0, 1, 0, 1]})
    cur = pd.DataFrame({"income": [90000, 120000, 110000, 95000], "target": [1, 1, 1, 1]})
    generate_evidently_drift_report(ref, cur, "drift_report.html")
```

---

## 5. Retraining Trigger & Alerting Integration

```python
import requests
import json

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR_WORKSPACE/YOUR_CHANNEL/YOUR_WEBHOOK_TOKEN"

def send_drift_alert(drift_results: dict):
    if drift_results["dataset_drift_detected"]:
        payload = {
            "text": ":warning: *ML Model Drift Alert*",
            "attachments": [
                {
                    "color": "#FF0000",
                    "fields": [
                        {"title": "Dataset Drift Ratio", "value": f"{drift_results['dataset_drift_ratio']:.2%}", "short": True},
                        {"title": "Status", "value": "CRITICAL - Retraining Triggered", "short": True}
                    ]
                }
            ]
        }
        requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

        # Trigger Retraining Airflow DAG or GitHub Actions Workflow
        requests.post(
            "https://airflow.prod.internal/api/v1/dags/retrain_churn_model/dagRuns",
            auth=('admin', 'admin_password'),
            json={"conf": {"reason": "data_drift_exceeded_threshold"}}
        )
```

---

## 6. Best Practices

1. **Reference Dataset Hygiene**: Freeze and version reference datasets matching exact training validation splits; update references only when a newly retrained model is deployed to production.
2. **Sampling Windows**: Select appropriate drift calculation windows (e.g., 7-day rolling window for high-volume endpoints) to prevent false alerts caused by transient weekend noise.
3. **Alerting Thresholds**: Set PSI warning thresholds at `0.1 <= PSI < 0.2` (slight shift) and critical alert thresholds at `PSI >= 0.2` (significant shift requiring action).
