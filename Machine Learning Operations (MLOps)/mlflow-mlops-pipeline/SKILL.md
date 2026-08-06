---
name: mlflow-mlops-pipeline
metadata:
  category: Machine Learning Operations (MLOps)
description: >-
  Build and manage end-to-end MLOps pipelines using MLflow for experiment tracking, model registry, artifact logging,
  autologging, model evaluation, and deployment serving. Triggers when integrating MLflow tracking servers, configuring
  S3/GCS backend stores, writing custom PyFunc models, automating hyperparameter tuning (Optuna), registering models,
  or building FastAPI/Docker inference services.
compatibility: Python (>= 3.9), MLflow (>= 2.8.0), scikit-learn / PyTorch / TensorFlow, PostgreSQL / S3 / GCS
---

# MLflow MLOps Pipelines & Experiment Tracking

End-to-end MLOps patterns for tracking experiments, managing model registries, versioning artifacts, evaluating metrics, and deploying models using MLflow.

---

## 1. MLOps Architecture Overview

```text
+-------------------+      +---------------------------------+      +------------------------+
|  Training Data    | ---> | ML Training Pipeline (PyTorch)  | ---> |  MLflow Tracking Server|
|  (S3 / Snowflake) |      | (Autolog + Custom PyFunc)       |      |  (PostgreSQL Backend)  |
+-------------------+      +---------------------------------+      +------------------------+
                                                                                |
                                                                                v
+-------------------+      +---------------------------------+      +------------------------+
|  Inference Client | ---> | FastAPI / MLflow Serve API      | <--- |  MLflow Model Registry |
|  (REST / gRPC)    |      | (Container App / KServe)        |      |  (S3 Artifact Store)   |
+-------------------+      +---------------------------------+      +------------------------+
```

---

## 2. Remote Tracking Server & Backend Configuration

### Environment Variables setup (`.env`)

```env
MLFLOW_TRACKING_URI=postgresql://mlflow_user:secure_password@db.prod.internal:5432/mlflow_db
MLFLOW_S3_ENDPOINT_URL=https://s3.us-east-1.amazonaws.com
MLFLOW_PYTHON_BIN=/usr/bin/python3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

---

## 3. Production Training & Tracking Pipeline (`train_pipeline.py`)

Complete Python implementation showcasing dataset logging, Optuna hyperparameter optimization, autologging, custom metrics, and model registration.

```python
import os
import sys
import logging
import optuna
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MLflow Tracking Server
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(TRACKING_URI)
EXPERIMENT_NAME = "customer_churn_prediction"
mlflow.set_experiment(EXPERIMENT_NAME)

def load_and_preprocess_data():
    """Generates synthetic dataset for illustration."""
    np.random.seed(42)
    X = np.random.randn(1000, 10)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    feature_names = [f"feature_{i}" for i in range(10)]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    return df, feature_names

def train_and_evaluate():
    df, feature_names = load_and_preprocess_data()
    X = df[feature_names]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    def objective(trial):
        with mlflow.start_run(nested=True):
            n_estimators = trial.suggest_int('n_estimators', 50, 300)
            max_depth = trial.suggest_int('max_depth', 3, 10)
            learning_rate = trial.suggest_float('learning_rate', 0.01, 0.2)

            model = GradientBoostingClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=learning_rate,
                random_state=42
            )
            model.fit(X_train, y_train)
            
            preds = model.predict(X_test)
            acc = accuracy_score(y_test, preds)
            
            # Log params & metrics for sub-run
            mlflow.log_params({
                "n_estimators": n_estimators,
                "max_depth": max_depth,
                "learning_rate": learning_rate
            })
            mlflow.log_metric("val_accuracy", acc)
            
            return acc

    # Parent MLflow Run for Hyperparameter Sweep
    with mlflow.start_run(run_name="optuna_sweep_parent") as parent_run:
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=5)

        best_params = study.best_params
        logger.info(f"Best Hyperparameters: {best_params}")

        # Train Final Champion Model
        champion_model = GradientBoostingClassifier(**best_params, random_state=42)
        champion_model.fit(X_train, y_train)

        # Evaluate Champion Model
        y_pred = champion_model.predict(X_test)
        y_proba = champion_model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba)
        }

        # Log metrics to parent run
        mlflow.log_params(best_params)
        mlflow.log_metrics(metrics)

        # Log Model Signature & Input Example
        signature = infer_signature(X_test, champion_model.predict(X_test))
        input_example = X_test.head(3)

        # Register Champion Model to MLflow Model Registry
        model_info = mlflow.sklearn.log_model(
            sk_model=champion_model,
            artifact_path="model",
            signature=signature,
            input_example=input_example,
            registered_model_name="CustomerChurnClassifier"
        )
        logger.info(f"Model logged successfully: {model_info.model_uri}")

if __name__ == "__main__":
    train_and_evaluate()
```

---

## 4. Custom PyFunc Wrapper for Preprocessing Pipelines (`custom_pyfunc.py`)

When your inference workflow requires custom pre-processing or feature transformations before executing model prediction:

```python
import mlflow.pyfunc
import numpy as np
import pandas as pd

class ChurnPipelineWrapper(mlflow.pyfunc.PythonModel):
    def __init__(self, model, scaler):
        self.model = model
        self.scaler = scaler

    def predict(self, context, model_input: pd.DataFrame) -> np.ndarray:
        """Custom inference method handling pre-processing."""
        # 1. Fill missing values
        cleaned_input = model_input.fillna(0)
        
        # 2. Scale features
        scaled_input = self.scaler.transform(cleaned_input)
        
        # 3. Model predict probabilities
        probabilities = self.model.predict_proba(scaled_input)[:, 1]
        
        return np.where(probabilities > 0.5, 1, 0)

# Save custom PyFunc model
# mlflow.pyfunc.log_model(
#     artifact_path="churn_pyfunc_model",
#     python_model=ChurnPipelineWrapper(model, scaler),
#     registered_model_name="CustomerChurnPyFunc"
# )
```

---

## 5. Automated Model Registry & Production Promotion (`promote_model.py`)

Script for CI/CD pipelines to evaluate candidate models and transition stages dynamically.

```python
import os
import logging
from mlflow.tracking import MlflowClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = MlflowClient(tracking_uri=os.getenv("MLFLOW_TRACKING_URI"))
MODEL_NAME = "CustomerChurnClassifier"

def promote_latest_model():
    # Fetch latest version of model
    latest_versions = client.get_latest_versions(MODEL_NAME, stages=["None"])
    if not latest_versions:
        logger.info("No new model versions found for promotion.")
        return

    latest_version = latest_versions[0].version
    run_id = latest_versions[0].run_id

    # Fetch metric performance
    run_data = client.get_run(run_id)
    accuracy = run_data.data.metrics.get("accuracy", 0.0)

    ACCURACY_THRESHOLD = 0.85

    if accuracy >= ACCURACY_THRESHOLD:
        logger.info(f"Model version {latest_version} passed check (Accuracy: {accuracy:.4f}). Transitioning to Production.")
        
        # Archive current Production models
        for mv in client.search_model_versions(f"name='{MODEL_NAME}'"):
            if mv.current_stage == "Production":
                client.transition_model_version_stage(
                    name=MODEL_NAME,
                    version=mv.version,
                    stage="Archived"
                )

        # Promote new model to Production
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=latest_version,
            stage="Production"
        )
    else:
        logger.warning(f"Model version {latest_version} failed validation (Accuracy: {accuracy:.4f} < {ACCURACY_THRESHOLD}).")

if __name__ == "__main__":
    promote_latest_model()
```

---

## 6. Serving MLflow Models via FastAPI (`serve_fastapi.py`)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import mlflow.pyfunc
import os

app = FastAPI(title="MLflow Model Serving API", version="1.0.0")

# Load model from MLflow Registry on startup
MODEL_URI = os.getenv("MODEL_URI", "models:/CustomerChurnClassifier/Production")
model = None

@app.on_event("startup")
def load_model():
    global model
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    model = mlflow.pyfunc.load_model(MODEL_URI)

class InferenceRequest(BaseModel):
    features: list[dict]

@app.post("/predict")
def predict(request: InferenceRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    df = pd.DataFrame(request.features)
    predictions = model.predict(df)
    return {"predictions": predictions.tolist()}
```

---

## 7. MLOps Best Practices Checklist

1. **Artifact Store Isolation**: Store artifacts in dedicated cloud bucket prefixes per environment (`s3://my-ml-artifacts-prod/`).
2. **Model Signatures**: Always log explicit inputs and outputs signatures using `mlflow.models.signature.infer_signature`.
3. **Environment Lock**: Log `conda.yaml` or `requirements.txt` environment locks alongside models to guarantee reproducible containerized deployments.
4. **Deterministic Run Names**: Set clear, human-readable run names (`mlflow.start_run(run_name="xgboost_baseline_v1")`) instead of relying on default UUID strings.
