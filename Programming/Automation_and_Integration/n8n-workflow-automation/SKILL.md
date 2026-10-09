---
name: n8n-workflow-automation
metadata:
  category: No-Code Low-Code and Workflow Automation
description: Production guidelines for building scalable, resilient n8n workflow automation pipelines. Use when designing self-hosted n8n instances, custom Code nodes (JS/Python), Webhook triggers, error-handling workflows, multi-node queue mode, community node integration, or enterprise credential management.
compatibility: n8n v1.0+, Node.js 18+, Docker/Kubernetes, PostgreSQL, Redis
---

# n8n Workflow Automation Production Guidelines

This skill provides architectural patterns, custom node development strategies, error-handling topologies, and self-hosted queue deployment standards for enterprise n8n workflow automation environments.

---

## 1. Core Architecture & Scaling Topology

### 1.1 Scaling Modes (Single Instance vs. Queue Mode)

Production n8n deployments scaling beyond basic workloads require **Queue Mode** using Redis and PostgreSQL:

```
                      +-------------------+
                      |   Reverse Proxy   |
                      |   (Nginx / Caddy) |
                      +---------+---------+
                                |
               +----------------+----------------+
               |                                 |
      +--------v-------+                +--------v-------+
      |  n8n Main Web  |                |   n8n Webhook  |
      |   (UI / API)   |                |    Instance    |
      +--------+-------+                +--------+-------+
               |                                 |
               +----------------+----------------+
                                |
                      +---------v---------+
                      |   Redis Broker    |
                      | (Bull Queue / Job)|
                      +---------+---------+
                                |
               +----------------+----------------+
               |                                 |
      +--------v-------+                +--------v-------+
      |  n8n Worker 1  |                |  n8n Worker 2  |
      | (Exec Engine)  |                | (Exec Engine)  |
      +--------+-------+                +--------+-------+
               |                                 |
               +----------------+----------------+
                                |
                      +---------v---------+
                      |    PostgreSQL     |
                      |   (State/Logs)    |
                      +-------------------+
```

- **Main Instance**: Handles UI administration, REST API, workflow creation, and scheduled trigger evaluation.
- **Webhook Instance**: Lightweight dedicated nodes exposing `/webhook/*` endpoints to handle incoming external HTTP payloads without UI overhead.
- **Worker Nodes**: Headless instances consuming jobs from Redis queue, performing heavy data processing and external API calls.
- **PostgreSQL**: Stores persistent workflows, credentials, execution history, and binary data pointers.

### 1.2 Execution Memory & Resource Management

- **Execution Pruning**: In production, execution log retention must be capped to prevent DB bloat:
  ```env
  EXECUTIONS_DATA_PRUNE=true
  EXECUTIONS_DATA_MAX_AGE=168 # hours (7 days)
  EXECUTIONS_DATA_PRUNE_MAX_COUNT=50000
  ```
- **Memory Optimization**: Avoid loading large binary files directly into memory. Use disk offloading:
  ```env
  N8N_DEFAULT_BINARY_DATA_MODE=filesystem
  N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
  ```

---

## 2. Custom Code Nodes & Data Context

### 2.1 Data Processing in Code Nodes (JavaScript / Python)

n8n passes data between nodes as an array of JSON objects structured as `[{ json: { ... } }]`.

#### JavaScript Context (`$input`, `$json`, `$vars`)
```javascript
// Access input items array
const items = $input.all();
const processedItems = [];

for (let i = 0; i < items.length; i++) {
  const currentItem = items[i].json;
  
  // Cleanse and transform payload
  processedItems.push({
    json: {
      id: currentItem.id,
      full_name: `${currentItem.first_name || ''} ${currentItem.last_name || ''}`.trim(),
      email: String(currentItem.email || '').toLowerCase(),
      processed_at: new Date().toISOString(),
      metadata: {
        source: 'webhook_ingest',
        workflow_id: $workflow.id,
        execution_id: $executionId
      }
    }
  });
}

return processedItems;
```

#### Python Context
```python
# Access items via _input
input_items = _input.all()
output_items = []

for item in input_items:
    data = item.get("json", {})
    output_items.append({
        "json": {
            "user_id": data.get("id"),
            "score": float(data.get("metrics", {}).get("raw_score", 0)) * 1.5,
            "status": "APPROVED" if data.get("verified") else "PENDING"
        }
    })

return output_items
```

---

## 3. Resilience, Error Handling & Sub-workflows

### 3.1 Global Error Workflows

Every production workflow must configure a dedicated **Error Trigger** workflow:

```
[ Primary Workflow ]                                 [ Error Workflow ]
  Trigger Node                                         Error Trigger Node
       |                                                        |
  Business Logic  -- (On Error) --> Trigger Error Flow ---> Extract Execution ID
       |                                                        |
  Output Action                                        Format Alert (Slack/PagerDuty)
                                                                |
                                                       Log to Sentry / DB
```

### 3.2 Retry Policies & Circuit Breaking

- Set **Continue On Fail** or **Retry On Fail** on network-bound HTTP Request nodes:
  - **Max Tries**: `3`
  - **Wait Between Tries (ms)**: `2000` (Exponential Backoff recommended)
- **Sub-workflow Encapsulation**: Modularize reusable logic (e.g., Auth token refresh, DB write) into dedicated sub-workflows called via `Execute Workflow` node.

---

## 4. Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Consequence | Correct Pattern |
|---|---|---|---|
| Storing hardcoded secrets in Code Nodes | Critical | Credential leakage in workflow exports / Git | Use n8n Enterprise Credentials or Environment Variables (`$env`) |
| Unbound execution retention (No Pruning) | High | PostgreSQL disk exhaustion, DB query slowdown | Set `EXECUTIONS_DATA_PRUNE=true` with strict age caps |
| Loading large files (>50MB) into JS memory | Critical | Node.js process Out-Of-Memory (OOM) crash | Use `N8N_DEFAULT_BINARY_DATA_MODE=filesystem` |
| Monolithic single workflows (>50 nodes) | Medium | Hard to debug, unmaintainable, memory spikes | Modularize into Sub-workflows with `Execute Workflow` node |
| Polling APIs without state pointers | Medium | Duplicate event processing | Store last sync timestamp/ID using n8n `Static Data` (`$getWorkflowStaticData('global')`) |

---

## 5. Production Infrastructure & Code Templates

### 5.1 Production Docker Compose Topology with Worker Nodes

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U n8n"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  n8n-main:
    image: n8nio/n8n:latest
    restart: always
    command: start
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - EXECUTIONS_MODE=queue
      - QUEUE_BULL_REDIS_HOST=redis
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168
      - N8N_DEFAULT_BINARY_DATA_MODE=filesystem
    ports:
      - "5678:5678"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  n8n-worker:
    image: n8nio/n8n:latest
    restart: always
    command: worker
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - EXECUTIONS_MODE=queue
      - QUEUE_BULL_REDIS_HOST=redis
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - N8N_DEFAULT_BINARY_DATA_MODE=filesystem
    depends_on:
      - n8n-main

volumes:
  postgres_data:
```

---

## 6. Verification & Monitoring Checklist

- [ ] **Health Monitoring**: Monitor `/healthz` on main node and ensure Redis queue depth stays near zero.
- [ ] **DB Indexes**: Verify PostgreSQL indexes exist on `execution_entity` (`id`, `startedAt`, `finished`).
- [ ] **Credential Encryption**: Confirm `N8N_ENCRYPTION_KEY` is backed up outside code/Git repositories.
- [ ] **Rate Limiting**: Enforce webserver rate limits on webhook ingestion routes (`/webhook/*`).
