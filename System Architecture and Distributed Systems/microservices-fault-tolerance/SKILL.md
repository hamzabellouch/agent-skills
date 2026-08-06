---
name: microservices-fault-tolerance
metadata:
  category: System Architecture and Distributed Systems
description: Implement resilient microservice architectures using Circuit Breakers, Exponential Backoff with Jitter, Bulkheads, Rate Limiting, Dead Letter Queues (DLQ), and Graceful Degradation patterns. Trigger when implementing service resilience, fault handling, or API gateway stability.
compatibility: Polyglot (Node.js, Go, Python, Java), Resilience4j, Polly, Envoy, Istio
---

# Microservices Fault Tolerance & Resilience Skill Guide

This skill provides design patterns, state machines, code samples, and retry algorithms for building fault-tolerant microservice architectures capable of surviving downstream service outages.

---

## 1. Resilience Pattern Matrix

```text
+-----------------------+-----------------------------------------------------------------+
| Pattern               | Core Objective                                                  |
+-----------------------+-----------------------------------------------------------------+
| **Circuit Breaker**   | Prevents cascading failures by tripping calls to failing services|
| **Backoff & Jitter**  | Prevents retry storms ("thundering herd") during outages        |
| **Bulkhead**          | Isolates resource pools so one failing service cannot drain all |
| **Rate Limiter**      | Protects services from being overwhelmed by traffic bursts      |
| **Dead Letter Queue** | Captures unprocessable messages for asynchronous replay         |
+-----------------------+-----------------------------------------------------------------+
```

---

## 2. Circuit Breaker State Machine

```text
                  +-----------------------------------+
                  |                                   |
                  |              CLOSED               | <------- Success Rate Restored
                  |  (Normal Traffic Execution)       |
                  |                                   |
                  +-----------------------------------+
                                    |
                           Failure Rate > Threshold
                                    v
                  +-----------------------------------+
                  |                                   |
                  |               OPEN                |
                  |  (Fast-Fail All Requests)         |
                  |                                   |
                  +-----------------------------------+
                                    |
                            Sleep Window Expires
                                    v
                  +-----------------------------------+
                  |                                   |
                  |            HALF-OPEN              |
                  |  (Trial Canary Requests Executed) |
                  |                                   |
                  +-----------------------------------+
```

---

## 3. Exponential Backoff with Full Jitter Math & Code

### Full Jitter Math Formula
Without jitter, concurrent clients retrying at identical backoff intervals cause thundering herd request spikes. Full Jitter distributes retries uniformly:

$$t_{\text{sleep}} = \text{random}\Big(0, \, \min\left(t_{\text{max}}, \, t_{\text{base}} \times 2^{\text{attempt}}\right)\Big)$$

### TypeScript Implementation

```typescript
export interface RetryOptions {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
}

export async function executeWithRetryAndJitter<T>(
  fn: () => Promise<T>,
  options: RetryOptions = { maxRetries: 4, baseDelayMs: 200, maxDelayMs: 5000 }
): Promise<T> {
  let attempt = 0;

  while (true) {
    try {
      return await fn();
    } catch (error) {
      attempt++;
      if (attempt > options.maxRetries) {
        throw new Error(`Execution failed after ${options.maxRetries} attempts: ${error}`);
      }

      // Calculate exponential backoff limit
      const calculatedBackoff = options.baseDelayMs * Math.pow(2, attempt);
      const cappedBackoff = Math.min(options.maxDelayMs, calculatedBackoff);

      // Apply Full Jitter
      const sleepTimeMs = Math.floor(Math.random() * cappedBackoff);

      console.warn(`[Attempt ${attempt}/${options.maxRetries}] Retrying in ${sleepTimeMs}ms...`);
      await new Promise((resolve) => setTimeout(resolve, sleepTimeMs));
    }
  }
}
```

---

## 4. Production Circuit Breaker & Fallback Implementation

```typescript
export enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN',
}

export class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount = 0;
  private successCount = 0;
  private lastStateChangeTime = Date.now();

  constructor(
    private failureThreshold = 5,
    private resetTimeoutMs = 10000,
    private halfOpenSuccessThreshold = 3
  ) {}

  async execute<T>(action: () => Promise<T>, fallback: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (Date.now() - this.lastStateChangeTime > this.resetTimeoutMs) {
        this.transitionTo(CircuitState.HALF_OPEN);
      } else {
        // Fast-fail and invoke fallback
        return fallback();
      }
    }

    try {
      const result = await action();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      return fallback();
    }
  }

  private onSuccess(): void {
    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++;
      if (this.successCount >= this.halfOpenSuccessThreshold) {
        this.transitionTo(CircuitState.CLOSED);
      }
    } else if (this.state === CircuitState.CLOSED) {
      this.failureCount = 0;
    }
  }

  private onFailure(): void {
    this.failureCount++;
    if (this.state === CircuitState.CLOSED && this.failureCount >= this.failureThreshold) {
      this.transitionTo(CircuitState.OPEN);
    } else if (this.state === CircuitState.HALF_OPEN) {
      this.transitionTo(CircuitState.OPEN);
    }
  }

  private transitionTo(newState: CircuitState): void {
    this.state = newState;
    this.lastStateChangeTime = Date.now();
    this.failureCount = 0;
    this.successCount = 0;
    console.info(`[CircuitBreaker] Transitioned state to ${newState}`);
  }
}
```

---

## 5. Dead Letter Queue (DLQ) Integration Workflow

```text
[ Producer ] ===> [ Primary Queue ] ===> [ Worker Service ]
                                              |
                                      Processing Fails
                                      (Max Retries Exceeded)
                                              |
                                              v
                                   [ Dead Letter Queue (DLQ) ]
                                              |
                                   [ Inspection & Redrive Pipeline ]
```

---

## 6. Anti-Patterns & Best Practices

| Anti-Pattern | Operational Risk | Production Best Practice |
| :--- | :--- | :--- |
| **Immediate fixed retries without backoff/jitter** | Overwhelms recovering databases and downstream APIs with massive traffic waves. | Always pair retries with Exponential Backoff and Full Jitter. |
| **Retrying non-idempotent operations (`POST /payments`)** | Causes duplicate charges or duplicate record creation. | Only auto-retry idempotent requests (`GET`, `PUT`, `DELETE`) or include unique Idempotency Keys. |
| **Infinite retry loops** | Consumes worker threads forever and locks message queues. | Enforce explicit `maxRetries` (3-5) and route failed payloads to a Dead Letter Queue (DLQ). |
| **Global shared connection pools without Bulkheads** | A slow secondary API consumes all available threads, hanging the entire application. | Isolate thread/connection pools per downstream dependency using Bulkhead isolation. |
