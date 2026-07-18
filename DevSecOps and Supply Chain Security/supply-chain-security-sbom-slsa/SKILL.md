---
name: supply-chain-security-sbom-slsa
description: Comprehensive framework for software supply chain security incorporating Software Bill of Materials (SBOM) generation/validation, SLSA (Supply-chain Levels for Software Artifacts) provenance compliance, image signing with Cosign/Sigstore, and automated pipeline verification.
---

# Supply Chain Security: SBOM, SLSA, & Artifact Attestation

## Overview
This skill provides production-ready patterns, automation templates, and Zero-Trust validation gates for securing software supply chains. It establishes end-to-end provenance verification, artifact integrity signing using Sigstore/Cosign, and automated SBOM analysis against vulnerability intelligence feeds.

---

## 1. Core Architectural Principles & Zero-Trust Governance

1. **Explicit Provenance Verification**: Never trust unverified build outputs. Every container image, binary, and package must present verifiable SLSA Level 3+ provenance signed by ephemeral OIDC tokens.
2. **Deterministic & Reproducible Builds**: Strive for hermetic build execution environments where identical source inputs yield bit-for-bit identical outputs.
3. **Continuous Cryptographic Verification**: Validate signatures, SBOM attestations, and vulnerability thresholds at admission control (Kubernetes Policy Engine / Kyverno / Gatekeeper) and before deployment.
4. **Least Privilege Build Identities**: Build pipelines must operate with short-lived, identity-bound tokens (e.g., GitHub OIDC federated to cloud IAM) rather than static, long-lived credentials.

---

## 2. Pipeline Gates & Policy Enforcement

| Gate Phase | Tooling | Enforcement Rules |
| :--- | :--- | :--- |
| **Source / Pre-Build** | Git Commit Signing, Dependency-Check | Block unverified commits; block dependencies with known critical CVEs without approved exception annotations. |
| **Build Time** | SLSA Generator, Syft, Cosign | Generate SPDX/CycloneDX SBOM; produce in-toto provenance attestation; sign artifacts via Keyless Sigstore. |
| **Post-Build Validation** | Grype, Trivy, Cosign Verify | Block image pushing/deployment if unverified signatures exist or high/critical vulnerabilities violate SLA. |
| **Deploy / Admission** | Kyverno / Policy Controller | Enforce image signature verification, SLSA provenance check, and minimum required SBOM attestation. |

---

## 3. Anti-Patterns & Risk Vectors

* **Anti-Pattern: Static API Keys in Build Systems**
  * *Risk*: Long-lived cloud keys leaked in runner logs or cached workspaces.
  * *Remediation*: Use Workload Identity Federation / OIDC with dynamic keyless Sigstore signing.
* **Anti-Pattern: Unattached / Post-Hoc SBOM Generation**
  * *Risk*: Generating SBOMs after deployment or outside the build pipeline creates drift between artifact reality and cataloged components.
  * *Remediation*: Embed SBOM generation into the build pipeline and cryptographically attach attestations using `cosign attest`.
* **Anti-Pattern: Floating Tags & Dynamic Dependencies**
  * *Risk*: Pulling `:latest` base images or unbounded dependency versions (`*` or `^`) enables upstream dependency confusion and typosquatting attacks.
  * *Remediation*: Pin dependencies and base images strictly by immutable cryptographic SHA-256 digests.

---

## 4. Production Code Examples

### A. GitHub Actions Workflow: SBOM, SLSA Provenance, & Keyless Cosign Signing (`.github/workflows/supply-chain.yml`)

```yaml
name: Supply Chain Security Pipeline

on:
  push:
    branches: [ "main" ]
    tags: [ "v*.*.*" ]

permissions:
  contents: read
  id-token: write # Required for GitHub OIDC federated authentication & Sigstore keyless signing
  packages: write

jobs:
  build-and-secure:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout source code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Install Cosign & Syft
        uses: sigstore/cosign-installer@v3.5.0

      - name: Install Syft
        run: curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Metadata & Digest
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: type=semver,pattern={{version}},default=latest

      - name: Build and Push OCI Image
        id: build-image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          provenance: false # Explicitly generating SLSA provenance below

      - name: Generate CycloneDX SBOM
        run: |
          syft ghcr.io/${{ github.repository }}@${{ steps.build-image.outputs.digest }} \
            -o cyclonedx-json=sbom.cdx.json

      - name: Attach SBOM Attestation with Cosign
        run: |
          cosign attest --yes \
            --type cyclonedx \
            --predicate sbom.cdx.json \
            ghcr.io/${{ github.repository }}@${{ steps.build-image.outputs.digest }}

      - name: Sign Container Image Keylessly (Sigstore OIDC)
        run: |
          cosign sign --yes \
            ghcr.io/${{ github.repository }}@${{ steps.build-image.outputs.digest }}

  # SLSA Level 3 Provenance Generator
  provenance:
    needs: [build-and-secure]
    permissions:
      actions: read
      id-token: write
      contents: write
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v2.0.0
    with:
      image: ghcr.io/${{ github.repository }}
      digest: ${{ needs.build-and-secure.outputs.digest }}
    secrets:
      registry-username: ${{ github.actor }}
      registry-password: ${{ secrets.GITHUB_TOKEN }}
```

---

### B. Python Script: Automated Vulnerability & Policy Validation Gate (`verify_sbom.py`)

```python
#!/usr/bin/env python3
"""
Automated SBOM Vulnerability Policy Validator
Analyzes CycloneDX SBOM files against CVE severity thresholds and policy requirements.
"""

import json
import sys
import subprocess
from typing import Dict, Any, List

SEVERITY_FAIL_THRESHOLD = ["CRITICAL", "HIGH"]
FORBIDDEN_LICENSES = ["GPL-3.0", "AGPL-3.0"]

def run_grype_sbom_scan(sbom_path: str) -> Dict[str, Any]:
    """Execute Anchore Grype on local CycloneDX SBOM."""
    cmd = ["grype", f"sbom:{sbom_path}", "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)

def parse_cdx_licenses(sbom_path: str) -> List[str]:
    """Extract component licenses from CycloneDX SBOM."""
    with open(sbom_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    licenses = []
    for component in data.get("components", []):
        for lic in component.get("licenses", []):
            if "license" in lic and "id" in lic["license"]:
                licenses.append(lic["license"]["id"])
    return licenses

def evaluate_security_policy(vulnerabilities: Dict[str, Any], licenses: List[str]) -> bool:
    """Enforce Zero-Trust vulnerability and compliance policy gates."""
    violations = []

    # Check Vulnerabilities
    for match in vulnerabilities.get("matches", []):
        vuln = match.get("vulnerability", {})
        severity = vuln.get("severity", "").upper()
        cve_id = vuln.get("id")
        pkg_name = match.get("artifact", {}).get("name")

        if severity in SEVERITY_FAIL_THRESHOLD:
            violations.append(f"[CVE] {severity} - {cve_id} in package '{pkg_name}'")

    # Check Licenses
    for lic in licenses:
        if lic in FORBIDDEN_LICENSES:
            violations.append(f"[LICENSE] Non-compliant license detected: {lic}")

    if violations:
        print("\n❌ SECURITY POLICY GATE FAILED:")
        for v in violations:
            print(f"  - {v}")
        return False

    print("\n✅ SECURITY POLICY GATE PASSED: Zero critical/high CVEs or policy violations detected.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_sbom.py <path_to_sbom.cdx.json>")
        sys.exit(1)

    sbom_file = sys.argv[1]
    print(f"[*] Scanning SBOM file: {sbom_file}")
    
    try:
        scan_results = run_grype_sbom_scan(sbom_file)
        sbom_licenses = parse_cdx_licenses(sbom_file)
        success = evaluate_security_policy(scan_results, sbom_licenses)
        if not success:
            sys.exit(1)
    except Exception as err:
        print(f"[-] Policy Enforcement Error: {err}")
        sys.exit(1)
```

---

### C. Kyverno Policy: Enforce Cosign Signature & SLSA Attestation in Kubernetes (`kyverno-policy.yaml`)

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: enforce-signature-and-slsa
  annotations:
    policies.kyverno.io/title: Verify Image Cosign Signatures & SLSA Provenance
    policies.kyverno.io/subject: Pod, Container
spec:
  validationFailureAction: Enforce
  background: false
  rules:
    - name: verify-image-signature
      match:
        any:
        - resources:
            kinds:
              - Pod
      verifyImages:
        - imageReferences:
            - "ghcr.io/your-org/*"
          keyless:
            issuer: "https://token.actions.githubusercontent.com"
            subject: "https://github.com/your-org/*"
          attestations:
            - predicateType: https://slsa.dev/provenance/v0.2
              attestors:
                - entries:
                    - keyless:
                        issuer: "https://token.actions.githubusercontent.com"
                        subject: "https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@refs/tags/v2.0.0"
```
