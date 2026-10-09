---
name: opentelemetry-tracing
metadata:
  category: Observability Monitoring and Telemetry
description: >-
  Instrument distributed systems and microservices with OpenTelemetry (OTel) across Python, Node.js, and Go.
  Triggers when configuring OTel Collectors, context propagation (W3C Trace Context), trace/span generation,
  custom span attributes, OTLP exporters (Jaeger, Tempo, Datadog), or tail-based sampling rules.
compatibility: OpenTelemetry SDKs (Python, JS, Go), OpenTelemetry Collector (>= 0.90.0), Jaeger / Tempo
---

# OpenTelemetry Tracing & Telemetry

Enterprise patterns for instrumenting distributed microservices, configuring OTel Collectors, propagation protocols, and exporting trace telemetry.

---

## 1. OpenTelemetry Architecture

```text
+-----------------------+      +-----------------------+
| Python Microservice   |      | Node.js API Gateway   |
| (OTel SDK + W3C Trace)|      | (OTel SDK + W3C Trace)|
+-----------------------+      +-----------------------+
            \                              /
             \ (OTLP gRPC Port 4317)      /
              v                          v
+------------------------------------------------------+
| OpenTelemetry Collector                              |
| (Receivers -> Batch/Tail-Sampling Processors -> Exporters)
+------------------------------------------------------+
                           |
                           v
+------------------------------------------------------+
| Telemetry Backend (Grafana Tempo / Jaeger / Datadog) |
+------------------------------------------------------+
```

---

## 2. OpenTelemetry Collector Configuration (`otel-collector-config.yaml`)

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

  memory_limiter:
    check_interval: 1s
    limit_percentage: 75
    spike_limit_percentage: 15

  # Tail-based sampling to keep 100% of errors and slow traces
  tail_sampling:
    decision_wait: 10s
    num_traces: 10000
    expected_new_traces_per_sec: 2000
    policies:
      [
        {
          name: drop_health_checks,
          type: string_attribute,
          string_attribute: { key: http.target, values: [ "/healthz", "/metrics" ], enabled_regex_matching: false, invert_match: true }
        },
        {
          name: keep_errors,
          type: status_code,
          status_code: { status_codes: [ ERROR ] }
        },
        {
          name: keep_probabilistic,
          type: probabilistic,
          probabilistic: { sampling_percentage: 10.0 }
        }
      ]

exporters:
  otlp/tempo:
    endpoint: tempo.monitoring.svc.cluster.local:4317
    tls:
      insecure: true

  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, tail_sampling, batch]
      exporters: [otlp/tempo, logging]
```

---

## 3. Python Microservice Instrumentation (`tracing_python.py`)

Complete Python manual and automatic instrumentation pattern with FastAPI and custom span attributes.

```python
from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import Status, StatusCode
import time

# 1. Initialize OpenTelemetry Resource & Provider
resource = Resource.create(attributes={
    SERVICE_NAME: "payment-processing-service",
    "deployment.environment": "production",
    "service.version": "1.4.2"
})

provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)

trace.set_tracer_provider(provider)
tracer = trace.get_tracer("payment.tracer")

# 2. FastAPI Application Setup
app = FastAPI(title="Payment API with OpenTelemetry")

@app.post("/checkout")
async def checkout(request: Request, user_id: str, amount: float):
    # Obtain current span from context or start custom child span
    with tracer.start_as_current_span("process_payment_transaction") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("payment.amount", amount)
        span.set_attribute("payment.currency", "USD")

        try:
            # Simulate DB and Third-Party API Call
            result = await execute_payment(user_id, amount)
            span.set_attribute("payment.status", "SUCCESS")
            span.set_status(Status(StatusCode.OK))
            return {"status": "success", "transaction_id": result}

        except Exception as e:
            # Record exception telemetry on active span
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, description=str(e)))
            raise

async def execute_payment(user_id: str, amount: float) -> str:
    with tracer.start_as_current_span("stripe_gateway_call") as child_span:
        child_span.set_attribute("peer.service", "stripe-api")
        time.sleep(0.1) # Simulate network call
        if amount > 10000:
            raise ValueError("Credit limit exceeded")
        return "txn_99283471"

# Automatically instrument FastAPI route handlers
FastAPIInstrumentor.instrument_app(app)
```

---

## 4. Node.js / TypeScript Context Propagation (`tracing_node.ts`)

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-grpc';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { trace, context, SpanStatusCode } from '@opentelemetry/api';

// 1. Initialize Node OTel SDK before loading express
const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'order-gateway-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '2.1.0',
  }),
  traceExporter: new OTLPTraceExporter({
    url: 'grpc://otel-collector:4317',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

// 2. Custom Manual Span Creation in Node.js
const tracer = trace.getTracer('order-gateway-tracer');

export async function processOrder(orderId: string, items: string[]) {
  return tracer.startActiveSpan('processOrderSpan', async (span) => {
    span.setAttribute('order.id', orderId);
    span.setAttribute('order.item_count', items.length);

    try {
      // Logic execution
      span.setStatus({ code: SpanStatusCode.OK });
      return { success: true };
    } catch (error: any) {
      span.recordException(error);
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      throw error;
    } finally {
      span.end();
    }
  });
}
```

---

## 5. Go gRPC & HTTP Context Propagation (`main.go`)

```go
package main

import (
	"context"
	"log"
	"net/http"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.4.0"
	"go.opentelemetry.io/otel/trace"
)

func initTracer() *sdktrace.TracerProvider {
	ctx := context.Background()
	exporter, err := otlptracegrpc.New(ctx, otlptracegrpc.WithInsecure(), otlptracegrpc.WithEndpoint("otel-collector:4317"))
	if err != nil {
		log.Fatalf("failed to create trace exporter: %v", err)
	}

	res, _ := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceNameKey.String("go-inventory-service"),
		),
	)

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(res),
	)
	otel.SetTracerProvider(tp)
	return tp
}

func handleInventoryCheck(w http.ResponseWriter, r *http.Request) {
	tr := otel.Tracer("inventory-tracer")
	ctx, span := tr.Start(r.Context(), "handleInventoryCheck",
		trace.WithAttributes(attribute.String("http.method", r.Method)),
	)
	defer span.End()

	// Use ctx downstream to propagate W3C traceparent header
	_ = ctx
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"status":"in_stock"}`))
}
```

---

## 6. Best Practices

1. **W3C Trace Context**: Standardize on `traceparent` (`00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`) headers across all inter-service HTTP and gRPC calls.
2. **Cardinality Management**: Do not include dynamic high-cardinality IDs (UUIDs, credit card numbers, email strings) inside Span Names; put high-cardinality values strictly inside Span Attributes.
3. **Batch Exporter**: Always use `BatchSpanProcessor` in production rather than `SimpleSpanProcessor` to decouple network export latency from application threads.
