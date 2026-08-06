---
name: soc2-compliance-automation
metadata:
  category: Compliance Governance and Legal Tech
description: Best practices for implementing SOC 2 Type II compliance controls, continuous evidence collection, infrastructure policy-as-code, and automated security monitoring. Use when automating Trust Services Criteria (Security, Availability, Confidentiality, Processing Integrity, Privacy), audit logging, IAM least privilege, or CI/CD security gates.
compatibility: AWS/GCP/Azure, Terraform, Open Policy Agent (OPA), SIEM / Audit Logs, GitHub Actions
---

# SOC 2 Compliance Automation & Governance Guidelines

This skill provides technical architectures, Policy-as-Code rules, automated evidence collection routines, continuous monitoring frameworks, and IAM control standards for achieving and maintaining SOC 2 Type II compliance across cloud infrastructure.

---

## 1. SOC 2 Trust Services Criteria (TSC) Mapping

SOC 2 audits evaluate five core Trust Services Criteria:

```
+-------------------------------------------------------------------------+
|                  CC (Common Criteria / Security)                        |
|   CC6.1 (Access Controls)  | CC6.8 (Malware/Patching) | CC7.2 (Monitoring)|
+-------------------------------------------------------------------------+
       |                         |                        |
       v                         v                        v
+------------------+   +-------------------+   +--------------------+
|  Availability    |   | Confidentiality   |   | Processing Integrity|
| (A1.2 Uptime/DR) |   | (C1.1 KMS Encrypt)|   | (PI1.1 Data Valid) |
+------------------+   +-------------------+   +--------------------+
```

1. **CC6.1 (Access Control & Identity)**: Multi-Factor Authentication (MFA), SSO enforcement, Role-Based Access Control (RBAC), Least Privilege principle.
2. **CC6.6 & CC6.7 (Boundary Protection & Encryption)**: Encryption at rest (AES-256) and in transit (TLS 1.3), VPC isolation, WAF configuration.
3. **CC7.1 & CC7.2 (Change Management & Monitoring)**: Automated CI/CD branch protection, peer code review requirements, SIEM audit logging.
4. **A1.2 (Availability & Disaster Recovery)**: Multi-AZ infrastructure replication, automated database backup retention, failover testing.

---

## 2. Infrastructure-as-Code SOC 2 Policy Enforcement (Open Policy Agent / OPA)

Prevent non-compliant infrastructure provisioning during CI/CD execution using OPA Rego rules:

```rego
# policy/soc2_aws_security.rego
package terraform.soc2

import future.keywords.in

default allow = false

# Rule: Enforce S3 Bucket Public Access Block & AES-256 Encryption (CC6.6)
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not resource.change.after.server_side_encryption_configuration
    msg := sprintf("SOC 2 Violation [CC6.6]: S3 Bucket '%v' must have server-side encryption enabled.", [resource.name])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    resource.change.after.publicly_accessible == true
    msg := sprintf("SOC 2 Violation [CC6.1]: RDS Database '%v' must NOT be publicly accessible.", [resource.name])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_security_group_rule"
    resource.change.after.cidr_blocks[_] == "0.0.0.0/0"
    resource.change.after.from_port == 22
    msg := sprintf("SOC 2 Violation [CC6.1]: Security Group Rule '%v' allows SSH (Port 22) from world (0.0.0.0/0).", [resource.name])
}
```

---

## 3. Continuous Compliance Evidence Collector (Python / AWS SDK)

Automate evidence collection tasks for auditors (e.g. Vanta, Drata, Tugboat, or external CPA auditors) via python scripts:

```python
import boto3
import json
import datetime
from typing import Dict, List

class SOC2EvidenceCollector:
    def __init__(self):
        self.iam_client = boto3.client('iam')
        self.s3_client = boto3.client('s3')
        self.kms_client = boto3.client('kms')

    def Audit_CC6_1_MFA_Enforcement(self) -> Dict:
        """Audits IAM Users to ensure MFA is enabled on all active accounts."""
        users = self.iam_client.list_users()['Users']
        non_compliant_users = []
        total_users = len(users)

        for user in users:
            username = user['UserName']
            mfa_devices = self.iam_client.list_mfa_devices(UserName=username)['MFADevices']
            if not mfa_devices:
                non_compliant_users.append(username)

        result = {
            "control": "CC6.1 - Logical Access Control & MFA",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "PASS" if not non_compliant_users else "FAIL",
            "total_users": total_users,
            "non_compliant_users": non_compliant_users
        }
        return result

    def Audit_CC6_6_S3_Encryption(self) -> List[Dict]:
        """Audits all S3 buckets for default server-side encryption."""
        buckets = self.s3_client.list_buckets()['Buckets']
        audit_report = []

        for bucket in buckets:
            name = bucket['Name']
            try:
                enc = self.s3_client.get_bucket_encryption(Bucket=name)
                status = "ENCRYPTED"
            except self.s3_client.exceptions.ClientError:
                status = "UNENCRYPTED"

            audit_report.append({"bucket_name": name, "status": status})

        return audit_report

if __name__ == "__main__":
    collector = SOC2EvidenceCollector()
    mfa_report = collector.Audit_CC6_1_MFA_Enforcement()
    print(json.dumps(mfa_report, indent=2))
```

---

## 4. Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Consequence | Correct Pattern |
|---|---|---|---|
| Admin credentials without MFA | Critical | Immediate SOC 2 Audit Exception / Failure | Enforce MFA on all IAM accounts & SSO |
| Direct production database access without break-glass logs | Critical | Severe CC6.1 Audit finding | Use ephemeral Bastion host access with full session logging (Teleport/SSM) |
| Code merged to main branch without 2 PR approvals | High | CC7.1 Change Management violation | Configure GitHub Branch Protection with strict mandatory approvals |
| Static AWS keys embedded in application code | High | Secret compromise & compliance audit flag | Use IAM Roles for EC2/ECS/EKS via OIDC / Instance Profiles |
| Unencrypted database backups in S3 | High | CC6.6 Encryption violation | Enforce AWS KMS CMK encryption on all backup targets |

---

## 5. Automated CI/CD Compliance Gate (GitHub Actions)

```yaml
name: SOC 2 Compliance Gate

on:
  pull_request:
    branches: [ main ]

jobs:
  compliance-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Terraform Security Scan (tfsec)
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          soft_fail: false

      - name: Open Policy Agent SOC 2 Validation
        run: |
          curl -L -o opa https://openpolicyagent.org/downloads/v0.60.0/opa_linux_amd64_static
          chmod +x opa
          ./opa test policy/ -v
```

---

## 6. Audit Readiness Checklist

- [ ] **Continuous Evidence Gathering**: Ensure automated evidence collection scripts run daily and persist to immutable storage.
- [ ] **Access Reviews**: Document quarterly user access reviews across AWS, GitHub, Okta, and Jira.
- [ ] **Vulnerability Management**: Run weekly container vulnerability scans (Trivy) and remediate High/Critical CVEs within 14 days.
