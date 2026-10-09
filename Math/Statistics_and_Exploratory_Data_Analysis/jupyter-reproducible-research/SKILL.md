---
name: jupyter-reproducible-research
metadata:
  category: Data Science and Exploratory Analysis
description: Establish production-grade reproducible research workflows in Jupyter notebooks, kernel environment lockfiles, notebook linting, nbconvert automated execution, parameterization with Papermill, and modularized code extraction. Trigger when creating Jupyter notebooks, setting up data science project structures, or building automated notebook pipelines.
compatibility: Python 3.9+, JupyterLab 4.0+, Papermill, Jupytext, nbconvert, uv / conda
---

# Jupyter Reproducible Research Skill Guide

This skill provides standards, directory layouts, environment lockfile workflows, parameterization patterns, and testing harnesses for building fully reproducible data science research pipelines using Jupyter.

---

## 1. Directory Structure Standard

Follow the standardized **Cookiecutter Data Science** project layout:

```text
research-project/
├── README.md              # Project overview and reproduction instructions
├── pyproject.toml         # Python project dependencies & tool configurations
├── uv.lock                # Deterministic package environment lockfile
├── .jupytext.toml         # Jupytext pairing configuration
├── data/
│   ├── raw/               # Read-only original data inputs
│   ├── processed/         # Cleaned, transformed intermediate datasets
│   └── final/             # Output datasets ready for modeling
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_exploratory_analysis.ipynb
│   └── 03_model_evaluation.ipynb
├── src/
│   ├── __init__.py
│   ├── data/              # Data processing scripts extracted from notebooks
│   │   └── clean.py
│   └── features/          # Feature engineering logic
│       └── build_features.py
├── reports/
│   └── figures/           # Generated charts, graphs, and artifacts
└── tests/
    └── test_notebooks.py  # Automated notebook execution tests
```

---

## 2. Jupytext Configuration (`.jupytext.toml`)

Never store raw non-deterministic JSON `.ipynb` files in Git without pairing them with lightweight markdown (`.md`) or Python (`.py`) scripts:

```toml
# Pair all notebooks in notebooks/ with percent-format Python scripts
default_jupytext_formats = "ipynb,py:percent"

# Strip metadata on save to reduce git diff noise
ipynb_metadata_filter = "-all"
cell_metadata_filter = "-all"
```

---

## 3. Parameterizing Notebooks with Papermill

Mark a specific notebook cell with the `parameters` tag to allow automated execution with variable overrides.

### A. Parameterized Notebook Cell (`notebooks/02_exploratory_analysis.ipynb`)

```python
# Parameters cell (tagged with "parameters" in Jupyter metadata)
REGION_NAME = "NORTH_AMERICA"
START_DATE = "2025-01-01"
OUTPUT_DIR = "reports/figures/"
```

### B. Execution Script using Papermill API (`src/run_pipeline.py`)

```python
import papermill as pm
from pathlib import Path

def run_parameterized_analysis(region: str, start_date: str):
    output_dir = Path("reports/exec_logs")
    output_dir.mkdir(parents=True, exist_ok=True)

    pm.execute_notebook(
        input_path="notebooks/02_exploratory_analysis.ipynb",
        output_path=f"reports/exec_logs/output_{region}.ipynb",
        parameters={
            "REGION_NAME": region,
            "START_DATE": start_date,
            "OUTPUT_DIR": f"reports/figures/{region}/",
        },
        kernel_name="python3"
    )

if __name__ == "__main__":
    run_parameterized_analysis(region="EMEA", start_date="2025-06-01")
```

---

## 4. Environment Lockfile Reproducibility Commands

```bash
# 1. Initialize deterministic project environment using uv
uv venv .venv
source .venv/bin/activate

# 2. Install dependencies and lock exact build hashes
uv add pandas polars jupyterlab papermill jupytext pytest nbconvert
uv lock

# 3. Register Jupyter kernel for current environment
python -m ipykernel install --user --name=research-env --display-name "Python (Research Env)"

# 4. Convert notebook to HTML report for sharing
jupyter nbconvert --to html notebooks/02_exploratory_analysis.ipynb --output-dir=reports/
```

---

## 5. Automated Notebook Quality Gate & Testing

Validate notebook execution from top-to-bottom without cached cell outputs in CI pipelines:

```python
# tests/test_notebooks.py
import subprocess
import pytest

NOTEBOOKS = [
    "notebooks/01_data_ingestion.ipynb",
    "notebooks/02_exploratory_analysis.ipynb",
]

@pytest.mark.parametrize("notebook_path", NOTEBOOKS)
def test_notebook_executes_cleanly(notebook_path: str):
    """Execute notebook from top to bottom ensuring zero runtime exceptions."""
    cmd = [
        "jupyter", "nbconvert",
        "--to", "notebook",
        "--execute",
        "--ExecutePreprocessor.timeout=600",
        "--output", "/tmp/out.ipynb",
        notebook_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Notebook {notebook_path} failed execution:\n{res.stderr}"
```

---

## 6. Anti-Patterns & Best Practices

| Anti-Pattern | Reproducibility Failure | Production Best Practice |
| :--- | :--- | :--- |
| **Out-of-order cell execution** | Notebook succeeds during live edit but crashes when rerun top-to-bottom. | Regularly execute `Kernel -> Restart & Run All` before committing. |
| **Hardcoding absolute local paths (`/Users/dev/data.csv`)** | Fails immediately when run by collaborators or on CI servers. | Use relative paths anchored to project root or `pathlib.Path(__file__)`. |
| **Leaving heavy logic embedded in notebook cells** | Inhibits code reuse, unit testing, and static analysis. | Refactor reusable functions into `src/` modules and import them into notebooks. |
| **Committing raw `.ipynb` output blobs to Git** | Causes massive repository bloat and merge conflicts. | Pair notebooks with Jupytext (`.ipynb` + `.py:percent`) and filter metadata. |
