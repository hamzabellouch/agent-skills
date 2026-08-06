---
name: high-availability-distributed-systems
metadata:
  category: System Architecture and Distributed Systems
description: Design resilient high-availability distributed systems, active-active multi-region replication, leader election, consensus protocols (Raft), dynamic load balancing, and zero-downtime failover mechanics. Trigger when architecting HA infrastructure, multi-region database failovers, or distributed consensus.
compatibility: Distributed Linux Clusters, Cloud Infrastructure (AWS/GCP/Azure), Kubernetes, Envoy
---

# High-Availability Distributed Systems Skill Guide

This skill provides architectural principles, mathematical quorum formulas, consensus mechanics, and failover design patterns for high-availability (HA) distributed systems.

---

## 1. Availability Calculations & SLAs

High availability measures uptime percentage relative to planned and unplanned downtime.

$$\text{Availability} = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}} \times 100$$

Where **MTBF** is Mean Time Between Failures and **MTTR** is Mean Time To Repair.

| Availability SLA | Max Downtime per Year | Max Downtime per Month | Target Architecture |
| :--- | :--- | :--- | :--- |
| **99.9% ("Three Nines")** | 8.76 hours | 43.8 minutes | Single region, multi-AZ autoscaling |
| **99.99% ("Four Nines")** | 52.6 minutes | 4.38 minutes | Multi-AZ active-passive failover with automated health checks |
| **99.999% ("Five Nines")** | 5.26 minutes | 26.3 seconds | Multi-region active-active deployment with global traffic routing |

---

## 2. Distributed Consensus & Leader Election (Raft Protocol)

To maintain strong consistency across distributed nodes, systems enforce consensus via Raft or Paxos protocols.

```text
+----------------+          Heartbeat Timeout          +----------------+
|                | ----------------------------------> |                |
|   Follower     |                                     |   Candidate    |
|                | <---------------------------------- |                |
+----------------+          Votes Granted (Quorum)     +----------------+
        ^                                                      |
        |                                                      | Majority Votes
        |                   Heartbeat / AppendEntries          v
        +-------------------------------------------------+----------------+
                                                           |   Leader       |
                                                           +----------------+
```

### Quorum Math Rule
To tolerate up to $F$ node failures, a distributed cluster must contain at least $N$ nodes:

$$N = 2F + 1$$

And any write operation must achieve a majority quorum $Q$:

$$Q = \left\lfloor \frac{N}{2} \right\rfloor + 1$$

For example, a 5-node cluster tolerates $F = 2$ failures because quorum requirement is $Q = 3$.

---

## 3. High Availability Architecture Topology

### Multi-Region Active-Active Deployment

```text
                               +-----------------------+
                               | Global DNS / Anycast  |
                               | (Route 53 / Cloudflare|
                               +-----------------------+
                                   /               \
              Healthy Traffic (50%)               Healthy Traffic (50%)
                                 /                   \
                                v                     v
                  +-------------------+         +-------------------+
                  | Region A (Primary)|         | Region B (Primary)|
                  |                   |         |                   |
                  |  +-------------+  |         |  +-------------+  |
                  |  | Ingress LBs |  |         |  | Ingress LBs |  |
                  |  +-------------+  |         |  +-------------+  |
                  |         |         |         |         |         |
                  |  +-------------+  |         |  +-------------+  |
                  |  | K8s Cluster |  |         |  | K8s Cluster |  |
                  |  +-------------+  |         |  +-------------+  |
                  |         |         |         |         |         |
                  |  +-------------+  |         |  +-------------+  |
                  |  | DB Primary  | <=========>|  | DB Primary  |  |
                  +--+-------------+--+  Async  +--+-------------+--+
                                      Replication
```

---

## 4. Automated Health Checking & Health Endpoint Implementation

A production health check endpoint must distinguish between **liveness** (is the container running) and **readiness** (can it accept traffic).

```typescript
// Production Node.js Health Controller
import { Request, Response } from 'express';
import { checkDatabaseConnection, checkRedisConnection } from './services';

export async function readinessHandler(req: Request, res: Response): Promise<void> {
  const dbHealthy = await checkDatabaseConnection();
  const redisHealthy = await checkRedisConnection();

  const isReady = dbHealthy && redisHealthy;

  if (isReady) {
    res.status(200).json({
      status: 'UP',
      checks: {
        database: 'HEALTHY',
        redis: 'HEALTHY',
      },
      timestamp: new Date().toISOString(),
    });
  } else {
    res.status(503).json({
      status: 'DOWN',
      checks: {
        database: dbHealthy ? 'HEALTHY' : 'UNHEALTHY',
        redis: redisHealthy ? 'HEALTHY' : 'UNHEALTHY',
      },
      timestamp: new Date().toISOString(),
    });
  }
}
```

---

## 5. Zero-Downtime Deployment Strategies

### Strategy Comparison

```text
Blue-Green Deployment:
  V1 (Blue)  [Old Version: 100% Traffic]  --> Terminated after cutover
  V2 (Green) [New Version: 0% Traffic]    --> Promoted to 100% Traffic instantaneously

Canary Deployment:
  V1 (Stable) [90% Traffic]
  V2 (Canary) [10% Traffic]  --> Gradually increment 10% -> 25% -> 50% -> 100%
```

---

## 6. Anti-Patterns & Best Practices

| Anti-Pattern | Failover Disaster | Production Best Practice |
| :--- | :--- | :--- |
| **Even number of consensus nodes (e.g. 4 nodes)** | Network partition splits cluster into two equal halves (2 vs 2), causing split-brain or deadlock. | Always deploy an odd number of cluster nodes (3, 5, 7) for raft/etcd consensus. |
| **Deep dependency checking in Liveness Probes** | If database fluctuates, all web pods fail liveness simultaneously, triggering cascading container restarts. | Keep Liveness probes lightweight; verify external dependencies exclusively in Readiness probes. |
| **Synchronous multi-region cross-continent writes** | Adds 150ms+ latency per transaction; degrades performance and risks cascade failure. | Use asynchronous multi-region replication combined with conflict-free replicated data types (CRDTs). |
| **Manual DNS failover switching** | High human delay during outages (30-60+ mins downtime). | Implement automated, health-probe-driven Anycast/DNS failover with short TTLs (<= 60s). |
