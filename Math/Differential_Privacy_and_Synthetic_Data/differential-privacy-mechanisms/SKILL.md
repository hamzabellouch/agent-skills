---
name: differential-privacy-mechanisms
metadata:
  category: Privacy-Preserving AI and Synthetic Data
description: Implement rigorous epsilon-delta differential privacy mechanisms (Laplace mechanism, Gaussian mechanism, Exponential mechanism) and DP-SGD (Differentially Private Stochastic Gradient Descent) using Opacus and PyTorch. Track cumulative privacy loss budgets (Rényi Differential Privacy), clip gradient norms, and prevent membership inference attacks. Trigger when training ML models on sensitive data or releasing aggregated statistical datasets.
compatibility: Python 3.10+, PyTorch 2.0+, Opacus 1.4+, NumPy
---

# Differential Privacy Mechanisms Skill Guide

This skill governs the mathematical formulation and machine learning implementation of \((\epsilon, \delta)\)-differential privacy to guarantee statistical anonymity.

---

## 1. Mathematical Fundamentals & Noise Perturbation

A randomized algorithm $\mathcal{M}$ satisfies $(\epsilon, \delta)$-differential privacy if for all neighboring datasets $D, D'$ differing by at most one individual record, and for all query outputs $S \subseteq \text{Range}(\mathcal{M})$:

$$\mathbb{P}[\mathcal{M}(D) \in S] \le e^{\epsilon} \cdot \mathbb{P}[\mathcal{M}(D') \in S] + \delta$$

```text
[ True Query Result / Gradient ] (Sensitivity = Delta f)
                 |
                 +---> Add Calibrated Noise
                         |-- Laplace Noise: Lap(scale = Delta f / epsilon)  [Pure epsilon-DP]
                         |-- Gaussian Noise: N(0, sigma^2) where            [(epsilon, delta)-DP]
                         |   sigma = sqrt(2 * ln(1.25 / delta)) * Delta f / epsilon
                 |
                 v
[ Private Sanitized Output (Mathematically bounded re-identification risk) ]
```

---

## 2. Production Code Implementations

### A. Calibrated Laplace & Gaussian Query Perturbation (Python)

```python
import numpy as np


class DPQueryEngine:
    def __init__(self, epsilon: float, delta: float = 1e-5):
        if epsilon <= 0:
            raise ValueError("Epsilon must be strictly positive")
        self.epsilon = epsilon
        self.delta = delta

    def private_count(self, true_count: int) -> int:
        """Counts have an L1 sensitivity of exactly 1."""
        scale = 1.0 / self.epsilon
        noise = np.random.laplace(0, scale)
        return max(0, int(round(true_count + noise)))

    def private_mean(self, values: list[float], lower_bound: float, upper_bound: float) -> float:
        """Clips values to [lower_bound, upper_bound] to enforce bounded sensitivity."""
        n = len(values)
        if n == 0:
            return 0.0

        clipped = np.clip(values, lower_bound, upper_bound)
        sum_sensitivity = upper_bound - lower_bound

        # Gaussian Mechanism for bounded sum
        sigma = np.sqrt(2 * np.log(1.25 / self.delta)) * sum_sensitivity / self.epsilon
        noisy_sum = np.sum(clipped) + np.random.normal(0, sigma)

        return float(noisy_sum / n)
```

### B. DP-SGD Neural Network Training with Opacus (PyTorch)

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from opacus import PrivacyEngine


def train_differentially_private_model(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    target_epsilon: float = 3.0,
    target_delta: float = 1e-5,
    max_grad_norm: float = 1.0,
    epochs: int = 5,
):
    criterion = nn.CrossEntropyLoss()

    # Attach Opacus Privacy Engine
    privacy_engine = PrivacyEngine()
    model, optimizer, train_loader = privacy_engine.make_private_with_epsilon(
        module=model,
        optimizer=optimizer,
        data_loader=train_loader,
        target_epsilon=target_epsilon,
        target_delta=target_delta,
        epochs=epochs,
        max_grad_norm=max_grad_norm,
    )

    model.train()
    for epoch in range(epochs):
        for data, target in train_loader:
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

        spent_epsilon = privacy_engine.get_epsilon(target_delta)
        print(f"Epoch {epoch+1} Complete | Current Privacy Spent: eps={spent_epsilon:.2f}, delta={target_delta}")

    return model
```

---

## 3. Best Practices Checklist

- [ ] **Data Clipping:** Never apply noise without first clipping data features into an explicit numeric range $[a, b]$; otherwise sensitivity is unbounded ($\Delta f = \infty$).
- [ ] **Privacy Budget Accounting:** Enforce a cumulative privacy budget tracker across multiple queries on the same dataset to prevent budget exhaustion.
- [ ] **Replace Batch Normalization:** In DP-SGD, replace `BatchNorm2d` with `GroupNorm` or `LayerNorm` because batch normalization leaks cross-sample statistical gradients within the batch.
