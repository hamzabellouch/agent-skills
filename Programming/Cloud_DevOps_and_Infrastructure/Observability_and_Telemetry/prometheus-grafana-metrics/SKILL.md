---
name: prometheus-grafana-metrics
metadata:
  category: Observability Monitoring and Telemetry
description: >-
  Design application metrics, Prometheus scraping topologies, PromQL queries, alerting rules, and Grafana dashboards as code.
  Triggers when implementing RED / USE metric patterns, writing custom Prometheus exporters (Python / Go), writing alerting rules,
  calculating SLO burn rates in PromQL, or generating Grafana dashboard JSON configurations.
compatibility: Prometheus (>= 2.45.0), Grafana (>= 10.0), Prometheus Operator / Helm, Python / Go Client SDKs
---

# Prometheus & Grafana Metrics as Code

Production patterns for metric instrumentation, PromQL query optimization, Alertmanager routing rules, and Grafana dashboard provisioning.

---

## 1. Metrics Methodology Framework

```text
+------------------------------------------------------------------------------------+
| 4 Golden Signals: Latency, Traffic, Errors, Saturation                              |
+------------------------------------------------------------------------------------+
| RED Method (Services & APIs):                                                       |
|   - Rate:     sum(rate(http_requests_total[5m]))                                    |
|   - Errors:   sum(rate(http_requests_total{status=~"5.."}[5m]))                     |
|   - Duration: histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
+------------------------------------------------------------------------------------+
| USE Method (Hardware & Resources):                                                  |
|   - Utilization: node_cpu_seconds_total                                            |
|   - Saturation:  node_load1                                                         |
|   - Errors:       node_net_receive_errs_total                                       |
+------------------------------------------------------------------------------------+
```

---

## 2. Custom Application Metric Exporter (Python & Go)

### Python Exporter Implementation (`metrics_exporter.py`)

```python
from prometheus_client import start_http_server, Counter, Histogram, Gauge, Summary
import time
import random

# 1. Metric Definitions following RED pattern
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests processed",
    ["method", "endpoint", "status_code"]
)

LATENCY_HISTOGRAM = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Latency in Seconds",
    ["endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0) # Tailored latency buckets
)

ACTIVE_CONNECTIONS = Gauge(
    "app_active_connections",
    "Current active database connection pool size"
)

def simulate_work():
    ACTIVE_CONNECTIONS.set(random.randint(5, 20))
    
    endpoint = "/api/v1/orders"
    start_time = time.time()
    
    # Simulate work
    time.sleep(random.uniform(0.02, 0.3))
    duration = time.time() - start_time
    
    status_code = "200" if random.random() > 0.05 else "500"
    
    # Record metrics
    REQUEST_COUNT.labels(method="POST", endpoint=endpoint, status_code=status_code).inc()
    LATENCY_HISTOGRAM.labels(endpoint=endpoint).observe(duration)

if __name__ == "__main__":
    start_http_server(9090)
    print("Prometheus Metrics exporter running on http://localhost:9090/metrics")
    while True:
        simulate_work()
```

---

## 3. Prometheus Alerting Rules & SLO Burn Rates (`alert_rules.yaml`)

```yaml
groups:
  - name: API_SLO_Alerts
    rules:
      # 1. High Error Rate Alert (> 5% errors over 5m window)
      - alert: APIHighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status_code=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) * 100 > 5
        for: 2m
        labels:
          severity: critical
          team: platform-ops
        annotations:
          summary: "API Error Rate exceeds 5%"
          description: "High error rate detected on service {{ $labels.job }}. Current error rate: {{ $value | printf \"%.2f\" }}%."

      # 2. P99 Latency Degradation Alert (> 2.0s over 5m)
      - alert: APIHighP99Latency
        expr: |
          histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)) > 2.0
        for: 5m
        labels:
          severity: warning
          team: backend-devs
        annotations:
          summary: "P99 Latency Spike on {{ $labels.endpoint }}"
          description: "99th percentile latency on {{ $labels.endpoint }} is {{ $value | printf \"%.2f\" }}s."

      # 3. Multi-Window Fast Burn Rate SLO Alert (SLO 99.9% availability target)
      - alert: ServiceSLOBurnRateCritical
        expr: |
          (
            sum(rate(http_requests_total{status_code=~"5.."}[1h]))
            /
            sum(rate(http_requests_total[1h]))
          ) > (1 - 0.999) * 14.4
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "Fast Burn Rate: 2% of 30-day Error Budget consumed in 1 hour"
```

---

## 4. PromQL Cheat Sheet for Production

| Query Intent | PromQL Query Expression |
| :--- | :--- |
| **Total Request Throughput** | `sum(rate(http_requests_total[5m])) by (job)` |
| **Percentage Error Rate** | `(sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100` |
| **95th Latency Percentile** | `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` |
| **CPU Utilization per Node** | `100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` |
| **Memory Available %** | `(node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100` |

---

## 5. Grafana Dashboard Provisioning as Code (`dashboard_provisioning.json`)

```json
{
  "annotations": { "list": [] },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 1,
  "id": null,
  "title": "Production API Services Dashboard",
  "tags": ["production", "prometheus", "red"],
  "timezone": "browser",
  "panels": [
    {
      "title": "HTTP Request Throughput (RPS)",
      "type": "timeseries",
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
      "targets": [
        {
          "expr": "sum(rate(http_requests_total[2m])) by (endpoint)",
          "legendFormat": "{{endpoint}}"
        }
      ]
    },
    {
      "title": "P99 Latency Quantile",
      "type": "timeseries",
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
      "fieldConfig": {
        "defaults": { "unit": "s" }
      },
      "targets": [
        {
          "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[2m])) by (le, endpoint))",
          "legendFormat": "P99 - {{endpoint}}"
        }
      ]
    }
  ],
  "schemaVersion": 38,
  "version": 1
}
```

---

## 6. Metric Cardinality Best Practices

1. **Avoid High-Cardinality Labels**: Never add unique IDs (User ID, IP address, UUID, session tokens) as Prometheus metric label dimensions to prevent TSDB memory exhaustion.
2. **Explicit Histogram Buckets**: Define custom exponential or linear histogram buckets tailored to your expected latency SLAs (e.g. `10ms` to `2s` for web APIs).
3. **Scrape Frequency Alignment**: Match alert evaluation intervals (`evaluation_interval: 15s`) with your scraping interval (`scrape_interval: 15s`).
