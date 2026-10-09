---
name: hashicorp-vault-secret-management
description: Enterprise secrets lifecycle management pattern using HashiCorp Vault. Enforces Zero-Trust access controls, dynamic database credential leasing, secret rotation engines, AppRole/Kubernetes authentication, and Vault Agent sidecar injection.
---

# HashiCorp Vault Secrets Management & Lifecycle Architecture

## Overview
This skill provides production-grade templates, HCL policy configurations, and client SDK implementations for enterprise secret management via HashiCorp Vault. It eliminates static credentials through short-lived dynamic credentials, automated rotation engines, and identity-based access control.

---

## 1. Zero-Trust Secrets Architecture

1. **Eliminate Static Long-Lived Secrets**: Move away from hardcoded API keys and static database passwords. Leverage Vault dynamic engines (AWS IAM, Database, PKI) that issue credentials with short Time-To-Live (TTL).
2. **Strict Principle of Least Privilege (PoLP)**: Vault ACL policies must explicitly follow default-deny semantics. Path access is granted strictly based on workload identity (Kubernetes ServiceAccount, AWS IAM role, AppRole).
3. **Automated Secret Leasing & Renewal**: Applications must handle lease expiration, dynamic token renewal, and graceful re-authentication without downtime.
4. **Encryption in Transit & at Rest**: Force TLS 1.3 for all client communications; ensure Vault storage backends (Raft Integrated Storage) utilize AES-GCM 256-bit envelope encryption.

---

## 2. Dynamic Secret Rotation & Access Lifecycle

```
[ Application / Pod ]
      │  1. Authenticate via ServiceAccount / AppRole
      ▼
[ Vault Server / Agent ]
      │  2. Issue short-lived Token (TTL: 1h)
      │  3. Request Dynamic DB Credentials (TTL: 15m)
      ▼
[ Database Engine ] ──▶ Generates ephemeral user (e.g., v-approle-user-abc-123)
```

| Lifecycle Event | Mechanism | Standard TTL / Frequency |
| :--- | :--- | :--- |
| **Authentication** | Kubernetes ServiceAccount / AppRole | Token TTL: 1 Hour (Explicit Max TTL: 12 Hours) |
| **KV-v2 Secrets** | Soft delete / Versioning / Metadata audit | Version retention: 10 versions max |
| **Dynamic DB Passwords** | Vault DB Engine (`postgresql-database-plugin`) | Lease TTL: 15-30 Minutes; Auto-revoked on expiry |
| **PKI TLS Certificates** | Vault PKI Secret Engine | Cert TTL: 24 Hours; Managed via Cert-Manager / Vault Agent |

---

## 3. Anti-Patterns & Misconfigurations

* **Anti-Pattern: Root Token Usage in Production**
  * *Risk*: Total compromise of Vault cluster; unrevokable root privileges.
  * *Remediation*: Revoke root tokens immediately after initial unseal & configuration setup.
* **Anti-Pattern: Wildcard Path Permissions (`path "secret/*" { capabilities = ["sudo", "create", "read", "update", "delete"] }`)**
  * *Risk*: Over-privileged clients can read/modify internal credentials of unrelated microservices.
  * *Remediation*: Scope path rules tightly per environment and service name (`path "secret/data/production/payment-service/*"`).
* **Anti-Pattern: Static RoleID & SecretID in Code Repositories**
  * *Risk*: Hardcoding AppRole credentials defeats zero-trust isolation.
  * *Remediation*: Deliver SecretID via out-of-band push mechanism, Vault Agent auto-auth, or response wrapping.

---

## 4. Production Code Examples

### A. Terraform HCL: Vault Engine, AppRole, & Dynamic Database Policy Setup (`main.tf`)

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 3.24.0"
    }
  }
}

provider "vault" {
  address = "https://vault.internal.net:8200"
}

# 1. Mount KV Secrets Engine v2
resource "vault_mount" "kvv2" {
  path        = "secret"
  type        = "kv-v2"
  description = "Production Application Encrypted Secrets"
}

# 2. Scope-Restricted Vault ACL Policy
resource "vault_policy" "payment_service_policy" {
  name   = "payment-service-policy"
  policy = <<EOT
# Read production payment service secrets
path "${vault_mount.kvv2.path}/data/production/payment-service/*" {
  capabilities = ["read"]
}

# Read metadata for secret versions
path "${vault_mount.kvv2.path}/metadata/production/payment-service/*" {
  capabilities = ["list", "read"]
}

# Issue dynamic PostgreSQL credentials
path "database/creds/payment-db-role" {
  capabilities = ["read"]
}
EOT
}

# 3. AppRole Authentication Configuration
resource "vault_auth_backend" "approle" {
  type = "approle"
}

resource "vault_approle_auth_backend_role" "payment_approle" {
  backend        = vault_auth_backend.approle.path
  role_name      = "payment-service-role"
  token_policies = [vault_policy.payment_service_policy.name]
  
  token_ttl      = 3600
  token_max_ttl  = 28800
  secret_id_ttl  = 86400
}

# 4. PostgreSQL Dynamic Secrets Engine Setup
resource "vault_mount" "db" {
  path        = "database"
  type        = "database"
  description = "Dynamic Database Credentials Engine"
}

resource "vault_database_secret_backend_connection" "postgres" {
  backend       = vault_mount.db.path
  name          = "postgresql"
  allowed_roles = ["payment-db-role"]

  postgresql {
    connection_url = "postgresql://{{username}}:{{password}}@postgres.internal.net:5432/payment_db?sslmode=verify-full"
    username       = "vault_admin"
    password       = var.vault_db_admin_password
  }
}

resource "vault_database_secret_backend_role" "payment_db_role" {
  backend             = vault_mount.db.path
  name                = "payment-db-role"
  db_name             = vault_database_secret_backend_connection.postgres.name
  creation_statements = [
    "CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
    "GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";"
  ]
  default_ttl         = 1800 # 30 minutes
  max_ttl             = 7200 # 2 hours
}
```

---

### B. Vault Agent Sidecar Configuration for Kubernetes (`vault-agent.hcl`)

```hcl
exit_after_auth = false
pid_file        = "/tmp/vault-agent.pid"

auto_auth {
  method "kubernetes" {
    mount_path = "auth/kubernetes"
    config = {
      role = "payment-service-role"
    }
  }

  sink "file" {
    config = {
      path = "/vault/secrets/.vault-token"
      mode = 0600
    }
  }
}

template {
  destination = "/vault/secrets/db-credentials.json"
  contents    = <<EOF
{{- with secret "database/creds/payment-db-role" -}}
{
  "db_user": "{{ .Data.username }}",
  "db_password": "{{ .Data.password }}",
  "lease_id": "{{ .LeaseID }}",
  "lease_duration": {{ .LeaseDuration }}
}
{{- end -}}
EOF
}
```

---

### C. Python Application Integration: Auto-Renewal & Dynamic Secret Retrieval (`vault_client.py`)

```python
#!/usr/bin/env python3
"""
Production Vault Client with HVAC
Handles AppRole Authentication, Dynamic Database Secret Fetching, and Background Lease Renewal.
"""

import os
import time
import threading
import logging
import hvac

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class VaultSecretManager:
    def __init__(self, vault_url: str, role_id: str, secret_id: str):
        self.vault_url = vault_url
        self.role_id = role_id
        self.secret_id = secret_id
        self.client = hvac.Client(url=self.vault_url)
        self.token_lease_renew_thread = None
        self.running = True

        self.authenticate()

    def authenticate(self):
        """Authenticate using Vault AppRole."""
        logging.info("Authenticating with Vault via AppRole...")
        login_response = self.client.auth.approle.login(
            role_id=self.role_id,
            secret_id=self.secret_id
        )
        self.client.token = login_response['auth']['client_token']
        auth_lease_duration = login_response['auth']['lease_duration']
        
        logging.info("Authentication successful. Token lease duration: %ss", auth_lease_duration)
        self._start_token_renewal_daemon(auth_lease_duration)

    def _start_token_renewal_daemon(self, initial_ttl: int):
        """Background thread to keep Vault client token renewed."""
        def renew_loop():
            while self.running:
                sleep_time = max(10, initial_ttl // 2)
                time.sleep(sleep_time)
                try:
                    logging.info("Renewing Vault client token...")
                    renew_result = self.client.auth.token.renew_self()
                    new_ttl = renew_result['auth']['lease_duration']
                    logging.info("Token successfully renewed. New TTL: %ss", new_ttl)
                except Exception as err:
                    logging.error("Failed to renew Vault token: %s", err)
                    # Attempt re-authentication
                    self.authenticate()
                    break

        self.token_lease_renew_thread = threading.Thread(target=renew_loop, daemon=True)
        self.token_lease_renew_thread.start()

    def get_dynamic_database_credentials(self) -> dict:
        """Fetch short-lived dynamic PostgreSQL credentials."""
        logging.info("Requesting dynamic database credentials from Vault...")
        creds = self.client.secrets.database.generate_credentials(
            name="payment-db-role",
            mount_point="database"
        )
        
        db_user = creds['data']['username']
        db_pass = creds['data']['password']
        lease_id = creds['lease_id']
        lease_duration = creds['lease_duration']

        logging.info("Obtained dynamic DB credentials for user '%s' (Lease TTL: %ss)", db_user, lease_duration)
        return {
            "username": db_user,
            "password": db_pass,
            "lease_id": lease_id,
            "lease_duration": lease_duration
        }

    def close(self):
        self.running = False

if __name__ == "__main__":
    VAULT_ADDR = os.getenv("VAULT_ADDR", "https://vault.internal.net:8200")
    ROLE_ID = os.getenv("VAULT_ROLE_ID")
    SECRET_ID = os.getenv("VAULT_SECRET_ID")

    if not ROLE_ID or not SECRET_ID:
        logging.error("Missing VAULT_ROLE_ID or VAULT_SECRET_ID environment variables.")
        exit(1)

    manager = VaultSecretManager(VAULT_ADDR, ROLE_ID, SECRET_ID)
    db_credentials = manager.get_dynamic_database_credentials()
    print(f"Connecting to database with user: {db_credentials['username']}")
```
