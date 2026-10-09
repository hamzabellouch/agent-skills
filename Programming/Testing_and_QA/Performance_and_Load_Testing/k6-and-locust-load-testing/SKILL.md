---
name: k6-and-locust-load-testing
description: Production-grade load, stress, spike, and endurance testing using Grafana k6 and Python Locust. Use when designing performance test suites, defining SLAs/SLOs, simulating distributed user traffic, and automating performance regression gates in CI/CD pipelines.
---

# k6 & Locust Load Testing Architecture & Best Practices

This skill provides comprehensive patterns, architectural guidelines, SLA validation thresholds, anti-patterns, and enterprise-grade code examples for high-throughput load and performance testing using **Grafana k6** (JavaScript/TypeScript ES6) and **Python Locust**.

---

## 1. Core Concepts & Framework Selection

| Capability | Grafana k6 | Python Locust |
| :--- | :--- | :--- |
| **Runtime / Engine** | Go VM with JavaScript (Goja) | Python (Gevent async co-routines) |
| **Resource Efficiency** | Extremely High (~1,000s of VUs per CPU core) | High (~100s-1000s VUs per worker node) |
| **Scripting Language** | ES6 JavaScript / TypeScript | Native Python |
| **Protocol Support** | HTTP/1.1, HTTP/2, WebSockets, gRPC, Redis | Any protocol via Python SDK (HTTP, gRPC, WebSockets, Kafka, SQL) |
| **CI/CD Integration** | CLI native, exit codes on threshold breaches, k6 Cloud | CLI native, Locust Web UI / Headless mode |
| **Best Used For** | Protocol-level performance testing, high-concurrency benchmarks, CI/CD automated gates | Complex user flows, Python ecosystem integration (ML models, Custom protocols, DB validation) |

---

## 2. Grafana k6 Implementation Standard

### Architectural Principles
1. **Separation of Concerns**: Split scenarios, test data generators, API client helpers, and SLA threshold definitions into modular files.
2. **Deterministic Stages**: Model ramp-up, steady-state (plateau), and ramp-down using `scenarios` with specific executors (`ramping-arrival-rate`, `ramping-vus`).
3. **Strict Thresholds**: Map metrics to strict Service Level Agreements (SLAs) so CI pipelines automatically fail when p95/p99 latency or error rates exceed budgets.

### Production k6 Framework Example

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom Metrics
const errorRate = new Rate('custom_error_rate');
const apiLatency = new Trend('api_transaction_latency');
const totalOrders = new Counter('total_orders_created');

// SLA Thresholds & Execution Scenarios
export const options = {
  scenarios: {
    // Ramping Arrival Rate (Open Model: controls throughput independent of target response times)
    checkout_load_test: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 500,
      stages: [
        { duration: '2m', target: 50 },  // Ramp up to 50 req/sec
        { duration: '5m', target: 50 },  // Sustained load at 50 req/sec
        { duration: '2m', target: 150 }, // Spike to 150 req/sec
        { duration: '5m', target: 150 }, // Sustained spike
        { duration: '2m', target: 0 },   // Cool down
      ],
      gracefulStop: '30s',
    },
  },
  thresholds: {
    // Global SLAs
    'http_req_failed': ['rate<0.01'],             // Error rate < 1%
    'http_req_duration': ['p(95)<300', 'p(99)<800'], // 95% < 300ms, 99% < 800ms
    'custom_error_rate': ['rate<0.005'],          // Application error rate < 0.5%
    'api_transaction_latency': ['p(95)<250'],     // Transaction-specific SLA
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://api.staging.example.com';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'bearer-secret-token';

export function setup() {
  // Pre-test setup: Fetch reference data or seed test DB
  const res = http.get(`${BASE_URL}/v1/health`, {
    headers: { Authorization: AUTH_TOKEN },
  });
  check(res, { 'system healthy': (r) => r.status === 200 });
  return { startTime: new Date().toISOString() };
}

export default function (data) {
  const payload = JSON.stringify({
    item_id: 'prod_99182',
    quantity: 1,
    idempotency_key: `idempotency_${__VU}_${__ITER}_${Date.now()}`,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': AUTH_TOKEN,
      'X-Correlation-ID': `k6-test-${__VU}-${__ITER}`,
    },
    tags: { name: 'POST /v1/orders' },
  };

  const startTime = Date.now();
  const res = http.post(`${BASE_URL}/v1/orders`, payload, params);
  const duration = Date.now() - startTime;

  // Record metrics
  apiLatency.add(duration);

  const success = check(res, {
    'status is 201 Created': (r) => r.status === 201,
    'order ID present': (r) => r.json('order_id') !== undefined,
    'response under 500ms': (r) => r.timings.duration < 500,
  });

  if (success) {
    totalOrders.add(1);
    errorRate.add(false);
  } else {
    errorRate.add(true);
  }

  // Pacing / Think Time (Random jitter between 1s and 3s)
  sleep(1 + Math.random() * 2);
}

export function teardown(data) {
  // Clean up resources or output test execution metadata
  console.log(`Test completed. Started at: ${data.startTime}`);
}
```

---

## 3. Python Locust Implementation Standard

### Architectural Principles
1. **User Behavior Modeling**: Group API flows into task sets with weights representing real user path distributions.
2. **State Management**: Maintain user session state (auth tokens, basket contents) on the `User` instance.
3. **Event Hooks**: Use `events.request` and `events.quitting` for customized SLA verification, metric shipping, or telemetry injection.

### Production Locust Framework Example

```python
import time
import uuid
import logging
from locust import HttpUser, task, between, events, SequentialTaskSet
from locust.exception import StopUser

logger = logging.getLogger("locust.loadtest")

class UserCheckoutJourney(SequentialTaskSet):
    """Sequential tasks simulating an e-commerce purchasing journey."""
    
    def on_start(self):
        """Executed when a Virtual User initiates this TaskSet."""
        self.client.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "LocustLoadTest/2.0",
        })
        self.auth_token = self._authenticate()

    def _authenticate(self) -> str:
        with self.client.post(
            "/api/v1/auth/login",
            json={"username": "load_user", "password": "secure_password"},
            catch_response=True,
            name="/api/v1/auth/login"
        ) as response:
            if response.status_code == 200:
                token = response.json().get("access_token")
                self.client.headers["Authorization"] = f"Bearer {token}"
                return token
            else:
                response.failure(f"Auth failed with status {response.status_code}")
                raise StopUser()

    @task(3)
    def browse_catalog(self):
        with self.client.get(
            "/api/v1/products?category=electronics&limit=20",
            catch_response=True,
            name="/api/v1/products"
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200 OK, got {response.status_code}")
            elif response.elapsed.total_seconds() > 0.4:
                response.failure(f"SLA Breach: Latency > 400ms ({response.elapsed.total_seconds()}s)")

    @task(2)
    def add_to_cart(self):
        payload = {"product_id": "p_88721", "quantity": 1}
        self.client.post("/api/v1/cart/items", json=payload, name="/api/v1/cart/items")

    @task(1)
    def checkout(self):
        idempotency_key = str(uuid.uuid4())
        headers = {"X-Idempotency-Key": idempotency_key}
        
        with self.client.post(
            "/api/v1/checkout",
            json={"payment_method": "credit_card"},
            headers=headers,
            catch_response=True,
            name="/api/v1/checkout"
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Checkout error: {response.text}")


class ECommerceLoadUser(HttpUser):
    """Virtual User runner with weighted task distributions."""
    wait_time = between(1.5, 3.5)
    tasks = [UserCheckoutJourney]
    host = "https://api.staging.example.com"


# Event Hooks for Custom Automated SLA Verification in Headless / CI mode
@events.quitting.add_listener
def verify_slas(environment, **kwargs):
    stats = environment.stats.total
    fail_ratio = stats.fail_ratio
    p95 = stats.get_response_time_percentile(0.95)
    p99 = stats.get_response_time_percentile(0.99)
    
    logger.info(f"Test summary: Fail Ratio={fail_ratio:.4f}, p95={p95}ms, p99={p99}ms")

    # Automated Gate Criteria
    sla_failed = False
    if fail_ratio > 0.01:
        logger.error(f"SLA VIOLATION: Failure rate {fail_ratio * 100:.2f}% exceeds limit of 1.0%")
        sla_failed = True
    if p95 > 300:
        logger.error(f"SLA VIOLATION: 95th percentile latency {p95}ms exceeds limit of 300ms")
        sla_failed = True
    if p99 > 800:
        logger.error(f"SLA VIOLATION: 99th percentile latency {p99}ms exceeds limit of 800ms")
        sla_failed = True

    if sla_failed:
        environment.process_exit_code = 1
```

---

## 4. SLA Verification & Threshold Metrics

When designing enterprise performance tests, define SLAs based on standard 4 Golden Signals (Latency, Traffic, Errors, Saturation):

| Metric | Target SLA Standard | k6 Threshold Expression | Locust Verification logic |
| :--- | :--- | :--- | :--- |
| **Http Failure Rate** | `< 0.5%` | `'http_req_failed': ['rate<0.005']` | `stats.fail_ratio < 0.005` |
| **p95 Latency** | `< 250 ms` | `'http_req_duration': ['p(95)<250']` | `stats.get_response_time_percentile(0.95) < 250` |
| **p99 Latency** | `< 500 ms` | `'http_req_duration': ['p(99)<500']` | `stats.get_response_time_percentile(0.99) < 500` |
| **Throughput (RPS)** | `> 500 RPS` | `'http_reqs': ['count>300000']` | `stats.total_rps >= 500` |

---

## 5. Anti-Patterns & Pitfalls to Avoid

### 1. Closed Model vs Open Model Misunderstanding
* **Anti-Pattern**: Using VU-based ramping (Closed Model) when simulating public HTTP endpoints. As response latency increases under load, VUs spend more time waiting for responses, decreasing throughput (RPS) and hiding performance degradation.
* **Solution**: Use `ramping-arrival-rate` in k6 or Constant Throughput Timer models in Locust to enforce RPS regardless of system latency.

### 2. Lack of Pacing / Think Time
* **Anti-Pattern**: Executing infinite tight loops without think times (`sleep()`), causing unrealistically high request rates per VU and overloading load generator network cards before target system limits are reached.
* **Solution**: Apply realistic Poisson or uniform random think times (`sleep(1 + Math.random() * 2)` in k6 or `between(1, 3)` in Locust).

### 3. Hardcoded Test Data & Shared Session IDs
* **Anti-Pattern**: Re-using the same user ID or authentication token across 500 VUs, causing DB lock contention on a single row or hitting single-user rate limits.
* **Solution**: Parameterize test data using JSON data files, synthetic UUID generation, or unique VU iteration identifiers (`__VU`, `__ITER`).

### 6. Logging Overhead During High Load
* **Anti-Pattern**: Using `console.log()` or `print()` inside the main test function for every request during a 10,000 VU load test, maxing out CPU I/O.
* **Solution**: Log only on failure conditions (`if (!success) { ... }`).
