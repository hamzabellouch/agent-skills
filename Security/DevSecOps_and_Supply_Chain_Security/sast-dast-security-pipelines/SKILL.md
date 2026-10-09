---
name: sast-dast-security-pipelines
description: Industrialized DevSecOps pipeline integration combining Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), Software Composition Analysis (SCA), and Secret Scanning with automated vulnerability thresholds and SARIF reporting.
---

# SAST & DAST Automated Security Pipelines

## Overview
This skill defines production patterns for orchestrating automated SAST, DAST, SCA, and Secret Scanning engines inside CI/CD workflows. It establishes strict vulnerability SLA enforcement, standardized SARIF (Static Analysis Results Interchange Format) ingestion into GitHub Security Hub/DefectDojo, and automated deployment blocking for non-compliant security builds.

---

## 1. DevSecOps Pipeline Architecture & Principles

1. **Shift-Left Continuous Analysis**: Execute fast, lightweight SAST and Secret Scanning on every pull request; defer heavy DAST and full dynamic fuzzing to staging environment deployment gates.
2. **Standardized SARIF Telemetry**: All scanners (Semgrep, Trivy, Bandit, OWASP ZAP) must output findings formatted in standard SARIF v2.1.0 to enable centralized triage and correlation.
3. **Zero Security Debt SLA Enforcement**: Fail builds automatically if open vulnerabilities breach SLA time-to-remediate windows:
   * **Critical**: 0-day SLA (Immediate block)
   * **High**: 7-day SLA
   * **Medium**: 30-day SLA
4. **Governed False Positive Exclusions**: Code inline suppressions (`#nosec`, `//nolint`) require peer security architect code review and mandatory expiry annotations.

---

## 2. Security Pipeline Scanning Matrix & Quality Gates

| Pipeline Stage | Security Scanner | Target Focus | Gate Action |
| :--- | :--- | :--- | :--- |
| **Commit / PR** | Trufflehog / Gitleaks | Hardcoded API keys, RSA keys, AWS access tokens | **Block Commit** |
| **PR Build** | Semgrep / SonarQube | Code injection, XSS, insecure deserialization, cryptographic weaknesses | **Block PR Merge** if High/Critical |
| **Artifact Build** | Trivy / Grype | Base image OS packages, application lockfiles | **Block Image Push** if High/Critical |
| **Deploy Staging** | OWASP ZAP / Nuclei | Runtime headers, CORS misconfiguration, SQLi, Auth bypass, SSRF | **Block Prod Deployment** |

---

## 3. Anti-Patterns & Risk Vectors

* **Anti-Pattern: Ignoring DAST Authentication State**
  * *Risk*: DAST scanners running without valid session tokens or API auth headers test only unauthenticated public splash screens, missing internal microservice vulnerabilities.
  * *Remediation*: Pass ephemeral OAuth/Bearer tokens or OpenAPI/Swagger definitions to DAST engine scans.
* **Anti-Pattern: Silent / Non-Blocking CI Security Jobs (`continue-on-error: true`)**
  * *Risk*: Security scans run purely as cosmetic checks while critical findings flow into production unnoticed.
  * *Remediation*: Enforce hard build failures on critical findings unless an explicit, signed security waiver exists.
* **Anti-Pattern: Monolithic Unfiltered Scanning**
  * *Risk*: Scanning third-party vendor code (`node_modules/`, `vendor/`) generates massive noise and inflates CI execution time.
  * *Remediation*: Scope path configurations to first-party source files using explicit include/exclude patterns.

---

## 4. Production Code Examples

### A. Full CI/CD Security Pipeline: GitHub Actions (`.github/workflows/security-pipeline.yml`)

```yaml
name: DevSecOps Comprehensive Security Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  security-events: write # Required for uploading SARIF reports to GitHub Security tab

jobs:
  secret-scanning:
    name: Secret & Credential Scan
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Gitleaks Secret Scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }} # Optional if enterprise

  sast-analysis:
    name: SAST Code Analysis (Semgrep)
    runs-on: ubuntu-latest
    needs: [secret-scanning]
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Semgrep Static Analysis
        run: |
          docker run --rm -v "${{ github.workspace }}:/src" \
            semgrep/semgrep semgrep scan \
            --config "p/security-audit" \
            --config "p/owasp-top-10" \
            --sarif --output /src/semgrep.sarif

      - name: Upload Semgrep SARIF
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: semgrep.sarif

  container-sec:
    name: Container Vulnerability Scan (Trivy)
    runs-on: ubuntu-latest
    needs: [sast-analysis]
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Build Local Container Image
        run: docker build -t test-app:ci .

      - name: Run Trivy Scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'test-app:ci'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1' # Block build on Critical/High vulnerabilities

      - name: Upload Trivy SARIF
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-results.sarif

  dast-scan:
    name: Dynamic Web App Security Scan (OWASP ZAP)
    runs-on: ubuntu-latest
    needs: [container-sec]
    if: github.ref == 'refs/heads/main' # Run DAST on main branch post-deployment to staging environment
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Start Application Container
        run: |
          docker run -d --name app-staging -p 8080:8080 test-app:ci
          sleep 10 # Wait for app startup

      - name: OWASP ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.12.0
        with:
          target: 'http://localhost:8080'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'
```

---

### B. Custom Semgrep Rule: SQL Injection Detection in Python (`.semgrep/python-sqli.yaml`)

```yaml
rules:
  - id: python-raw-sql-concatenation
    patterns:
      - pattern-either:
          - pattern: $DB.execute("..." % ...)
          - pattern: $DB.execute(f"...")
          - pattern: $DB.execute("..." + ...)
      - pattern-not: $DB.execute("...", (...))
    message: >-
      Potential SQL Injection detected. String formatting or concatenation was used 
      to build a dynamic SQL query. Use parameterized queries instead.
    metadata:
      cve: "CVE-OWASP-A03"
      owasp: "A03:2021 - Injection"
      cwe: "CWE-89: Improper Neutralization of Special Elements used in an SQL Command"
    severity: ERROR
    languages: [python]
```

---

### C. Python Script: SARIF Ingestion & SLA Violation Gate (`parse_sarif.py`)

```python
#!/usr/bin/env python3
"""
SARIF Report Aggregator & SLA Gate Enforcer
Parses SARIF files, calculates vulnerability counts, and enforces CI build failures based on SLA rules.
"""

import sys
import json
import glob
from typing import List, Dict, Any

SLA_LIMITS = {
    "error": 0,    # High / Critical
    "warning": 5   # Medium
}

def load_sarif_files(file_pattern: str) -> List[Dict[str, Any]]:
    reports = []
    for filepath in glob.glob(file_pattern):
        print(f"[*] Parsing SARIF report: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            reports.append(json.load(f))
    return reports

def evaluate_sarif_findings(reports: List[Dict[str, Any]]) -> bool:
    severity_counts = {"error": 0, "warning": 0, "note": 0}
    findings_details = []

    for report in reports:
        for run in report.get("runs", []):
            tool_name = run.get("tool", {}).get("driver", {}).get("name", "Unknown Scanner")
            results = run.get("results", [])

            for res in results:
                level = res.get("level", "warning").lower()
                rule_id = res.get("ruleId", "N/A")
                message = res.get("message", {}).get("text", "No message")
                
                severity_counts[level] = severity_counts.get(level, 0) + 1
                findings_details.append(f"[{tool_name}] [{level.upper()}] {rule_id}: {message}")

    print("\n================ SECURITY SCAN SUMMARY ================")
    print(f"  CRITICAL / HIGH (errors):   {severity_counts.get('error', 0)}")
    print(f"  MEDIUM (warnings):          {severity_counts.get('warning', 0)}")
    print(f"  LOW / INFO (notes):         {severity_counts.get('note', 0)}")
    print("=======================================================")

    failed = False
    if severity_counts["error"] > SLA_LIMITS["error"]:
        print(f"❌ BLOCK: Found {severity_counts['error']} Critical/High issues (Allowed: {SLA_LIMITS['error']}).")
        failed = True

    if severity_counts["warning"] > SLA_LIMITS["warning"]:
        print(f"❌ BLOCK: Found {severity_counts['warning']} Medium issues (Allowed: {SLA_LIMITS['warning']}).")
        failed = True

    if failed:
        print("\nTop Security Findings:")
        for finding in findings_details[:10]:
            print(f"  - {finding}")
        return False

    print("\n✅ SECURITY SLA GATE PASSED")
    return True

if __name__ == "__main__":
    sarif_glob = sys.argv[1] if len(sys.argv) > 1 else "*.sarif"
    sarif_reports = load_sarif_files(sarif_glob)
    
    if not sarif_reports:
        print("[-] No SARIF reports found matching pattern.")
        sys.exit(0)

    success = evaluate_sarif_findings(sarif_reports)
    if not success:
        sys.exit(1)
```
