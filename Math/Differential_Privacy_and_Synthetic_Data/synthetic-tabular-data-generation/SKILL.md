---
name: synthetic-tabular-data-generation
metadata:
  category: Privacy-Preserving AI and Synthetic Data
description: Generate high-fidelity, privacy-preserving synthetic tabular datasets using generative models (CTGAN, TVAE, Gaussian Copula). Preserve complex marginal probability distributions, multi-column correlations, and conditional dependencies while passing strict empirical privacy audits (Wasserstein distance, mutual information similarity, and nearest-neighbor distance to original training data). Trigger when generating test datasets, sharing data with external vendors, or balancing imbalanced classes.
compatibility: Python 3.10+, SDV (Synthetic Data Vault) 1.10+, Scikit-Learn
---

# Synthetic Tabular Data Generation Skill Guide

This skill governs the training, sampling, validation, and privacy auditing of synthetic tabular datasets using Conditional GANs and Copula models.

---

## 1. Generative Modeling Pipeline for Tabular Data

Tabular data presents mixed continuous and discrete columns with non-Gaussian, multi-modal distributions.

```text
[ Original Sensitive Dataset ]
               |
               v
[ Data Preprocessing & Metadata Declaration ]
  |-- Discrete / Categorical Encoding (One-hot, Embedding)
  |-- Continuous Normalization via Variational Gaussian Mixture Models (VGM)
               |
               v
[ Generative Architecture Training ]
  |-- CTGAN (Conditional WGAN-GP with Generator & Discriminator)
  |-- TVAE (Tabular Variational Autoencoder)
               |
               v
[ Synthetic Sample Generation & Evaluation ]
  |-- Fidelity Evaluation (Marginal distribution match, Correlation matrices)
  |-- Privacy Audit (Distance to Closest Record [DCR], Membership leakage)
```

---

## 2. Production Code Implementations

### A. CTGAN Model Training & Synthetic Sampling (Python / SDV)

```python
import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.single_table import CTGANSynthesizer
from sdv.evaluation.single_table import evaluate_quality, run_diagnostic


def generate_synthetic_dataset(
    real_data: pd.DataFrame,
    primary_key_col: str,
    epochs: int = 300,
    num_samples: int = 10000,
) -> pd.DataFrame:
    # 1. Infer metadata schema
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data=real_data)
    metadata.set_primary_key(column_name=primary_key_col)

    # 2. Configure CTGAN Synthesizer
    synthesizer = CTGANSynthesizer(
        metadata,
        epochs=epochs,
        batch_size=500,
        verbose=True,
    )

    # 3. Train on sensitive dataset
    print("[Synthetic] Training CTGAN Synthesizer...")
    synthesizer.fit(real_data)

    # 4. Generate synthetic records
    synthetic_data = synthesizer.sample(num_rows=num_samples)

    # 5. Evaluate Data Quality
    quality_report = evaluate_quality(
        real_data=real_data,
        synthetic_data=synthetic_data,
        metadata=metadata,
    )
    print(f"[Quality] Overall Quality Score: {quality_report.get_score():.2%}")

    return synthetic_data
```

### B. Empirical Privacy Audit: Distance to Closest Record (DCR)

```python
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors


def audit_reidentification_risk(
    real_numeric_features: np.ndarray,
    synthetic_numeric_features: np.ndarray,
    min_safe_distance: float = 0.05,
) -> float:
    """Calculates the proportion of synthetic records that are dangerously close to real training rows."""
    scaler = MinMaxScaler()
    real_scaled = scaler.fit_transform(real_numeric_features)
    synth_scaled = scaler.transform(synthetic_numeric_features)

    # Fit 1-NN on real dataset
    nbrs = NearestNeighbors(n_neighbors=1, algorithm="ball_tree").fit(real_scaled)
    distances, _ = nbrs.kneighbors(synth_scaled)

    # Percentage of synthetic rows that duplicated or nearly cloned a real row
    clone_ratio = np.mean(distances.flatten() < min_safe_distance)
    return float(clone_ratio)
```

---

## 3. Best Practices & Safety Gates

1. **Remove Direct Identifiers First:** Strip explicit PII (Social Security numbers, email addresses, names) before training generative models; synthesize them using regex generators or Faker instead.
2. **Min-Max Distance Gate:** If `audit_reidentification_risk` exceeds 1.0%, discard the synthetic batch and retrain with increased regularization or differential privacy penalties.
3. **Correlation Validation:** Compare the Pearson/Spearman correlation matrices between original and synthetic datasets to verify that business logic invariants (e.g., `total_price == unit_price * quantity`) are maintained.
