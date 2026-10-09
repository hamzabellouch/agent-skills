---
name: apache-kafka-event-streaming-and-schema-registry
description: Production-grade guidance for Apache Kafka event streaming, partition strategies, consumer group management, transactional messaging, and Confluent Schema Registry integration (Avro/Protobuf/JSON Schema). Use when designing Kafka topics, configuring producers/consumers for idempotency and ordering, enforcing schema evolution policies, or implementing dead-letter queues.
---

# Apache Kafka Event Streaming & Schema Registry Guide

## 1. Overview & Core Philosophy

Apache Kafka is an append-only distributed commit log designed for high-throughput, fault-tolerant event streaming. Unlike traditional message queues (e.g., RabbitMQ) that delete messages upon consumer ACK, Kafka retains messages for a configurable retention window, allowing multiple heterogeneous consumer groups to read and re-read event streams independently.

### Key Architectural Axioms
- **Log Ordering Guarantee**: Total order is guaranteed **only within a single partition**, not across partitions in a topic.
- **Partitioning as Unit of Parallelism**: Maximum concurrency for a consumer group is bounded by the number of partitions in a topic.
- **Decoupled State via Schema Registry**: Producers and consumers must share data contracts via explicit schemas (Avro, Protobuf, or JSON Schema) registered in a Schema Registry rather than untyped payloads.
- **Zero-Data-Loss Default**: Production setups must enforce strict durability constraints (`acks=all`, `min.insync.replicas=2`, `replication.factor=3`).

---

## 2. Topic Architecture & Partitioning Strategy

### 2.1 Partition Key Selection & Distribution
Selecting an optimal partition key is critical for balance and ordering.

- **Natural Entity Keys**: Key by domain entity ID (e.g., `order_id`, `customer_id`) when state updates for that specific entity must arrive in order.
- **Custom Partitioner**: Implement custom hashing (or murmur2 default) to prevent skew when entity keys follow power-law distributions (hotspot keys).
- **Null Keys (Round-Robin / Sticky)**: Use only for high-throughput append logs where ordering across events is irrelevant.

### 2.2 Topic Configuration Checklist
```ini
# Production Durability & Retention Standard
replication.factor=3
min.insync.replicas=2
cleanup.policy=delete # or compact for state tables
retention.ms=604800000 # 7 days
segment.bytes=1073741824 # 1GB
unclean.leader.election.enable=false
```

### 2.3 Compacted Topics
Use `cleanup.policy=compact` for changelog topics (e.g., Kafka Streams state stores or KSQLDB tables).
- Requires non-null message keys.
- Retains at least the latest record value for each key.
- Tombstone messages (null payload) trigger log garbage collection for key deletion.

---

## 3. Reliable Producer & Consumer Engineering

### 3.1 Producer Idempotency & Durability Matrix

| Setting | Value | Rationale |
| :--- | :--- | :--- |
| `acks` | `all` (`-1`) | Leader waits for full ISR acknowledgment. |
| `enable.idempotence` | `true` | Assigns Producer ID (PID) and sequence numbers to eliminate network retries duplicate writes. |
| `max.in.flight.requests.per.connection` | `5` (when idempotent) | Maintains strict ordering while enabling pipeline throughput. |
| `retries` | `2147483647` (INT_MAX) | Producer retries transient broker errors indefinitely until `delivery.timeout.ms` expires. |

### 3.2 Transactional Producer (Exactly-Once Semantics across Topics)
When consuming from topic `A` and producing to topic `B` (read-process-write loop):
```python
producer.init_transactions()
try:
    producer.begin_transaction()
    # Send messages
    producer.send("topic-B", key=key, value=val)
    # Send consumer offsets to transaction
    producer.send_offsets_to_transaction(offsets, consumer_group_id)
    producer.commit_transaction()
except Exception as e:
    producer.abort_transaction()
```

### 3.3 Consumer Group & Rebalance Management
- **Manual Offset Commit**: Disable `enable.auto.commit=false`. Commit offsets synchronously (`commitSync`) after batch processing, or asynchronously (`commitAsync`) with error callbacks.
- **Cooperative Sticky Assignor**: Configure `partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor` to minimize stop-the-world rebalances.
- **Processing Timeouts**: Ensure `max.poll.interval.ms` exceeds maximum batch processing duration to prevent unwanted consumer group eviction.

---

## 4. Schema Governance & Schema Registry Integration

Confluent Schema Registry decouples payload structure from business code by serving as a central authority for data contracts.

### 4.1 Schema Compatibility Modes

```
               [ Producer ] ---> Registers Schema Version N
                                      |
                              [ Schema Registry ]
                                      | Validates Rules
               [ Consumer ] <--- Fetches Schema Version N
```

- **BACKWARD (Default Recommended)**: Consumers using schema $N$ can read messages written with schema $N-1$. Fields can be deleted, or optional fields added.
- **FORWARD**: Consumers using schema $N-1$ can read messages written with schema $N$. New fields can be added, or optional fields deleted.
- **FULL**: Bidirectional compatibility. Fields can be added or deleted, but must always have default values.

### 4.2 Avro Schema Evolution Rules
- **Adding a Field**: MUST specify a `default` value (e.g., `{"name": "status", "type": "string", "default": "PENDING"}`).
- **Removing a Field**: Only remove fields that previously had default values.
- **Changing Types**: Only promote narrow types to wider types (e.g., `int` to `long`). Never change string to integer directly.

---

## 5. Resilience: Retries, Backpressure & Dead Letter Queues (DLQ)

Processing failures in Kafka consumers must never block the main partition processing loop indefinitely.

### 5.1 Non-Blocking Retry Topic Architecture

```
[ Main Topic: orders ] 
       │ (Error)
       ▼
[ Retry Topic 1: orders-retry-1m ] ──► (Delay 1m) ──► Re-attempt
       │ (Error)
       ▼
[ Retry Topic 2: orders-retry-5m ] ──► (Delay 5m) ──► Re-attempt
       │ (Failed Max Attempts)
       ▼
[ Dead Letter Queue: orders-dlq ] ──► Manual Inspection / Alerting
```

- Main topic consumers immediately push unprocessable messages to a dedicated retry topic with error metadata in message headers (`x-exception-message`, `x-original-topic`, `x-retry-count`).
- A dedicated retry consumer consumes from retry topics with backoff delays before republishing.

---

## 6. Critical Anti-Patterns & Production Warnings

1. **Auto-Committing Offsets (`enable.auto.commit=true`)**: Causes silent data loss when application crashes midway through processing polled batches.
2. **Blocking Operations inside Consumer Poll Loop**: Long-running HTTP/DB calls in `poll()` thread cause `max.poll.interval.ms` timeout, triggering constant rebalance cascades.
3. **Partition Skew via Uniform Null Keys on High-Throughput Topics**: Leads to broker disk imbalance and bottlenecking single consumer instances.
4. **Publishing Schemaless JSON Payloads**: Results in runtime breaking changes when field types or names change downstream.
5. **Ignoring `min.insync.replicas`**: Setting `acks=all` with `min.insync.replicas=1` provides no multi-node durability if two brokers fail simultaneously.

---

## 7. Production Code Reference

### 7.1 Python: Robust Producer with Schema Registry (confluent-kafka)

```python
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

schema_str = """
{
  "type": "record",
  "name": "OrderCreated",
  "namespace": "com.events.orders",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "customer_id", "type": "string"},
    {"name": "amount", "type": "double"},
    {"name": "created_at", "type": "long"}
  ]
}
"""

sr_config = {'url': 'http://schema-registry.prod.internal:8081'}
schema_registry_client = SchemaRegistryClient(sr_config)

avro_serializer = AvroSerializer(
    schema_registry_client,
    schema_str,
    to_dict=lambda obj, ctx: obj
)

producer_config = {
    'bootstrap.servers': 'kafka-1.prod.internal:9092,kafka-2.prod.internal:9092',
    'key.serializer': StringSerializer('utf_8'),
    'value.serializer': avro_serializer,
    'acks': 'all',
    'enable.idempotence': True,
    'max.in.flight.requests.per.connection': 5,
    'retries': 1000000,
    'delivery.timeout.ms': 120000
}

producer = SerializingProducer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        # Trigger alerting system / persistent fallback log
        print(f"Message delivery failed for key {msg.key()}: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] offset {msg.offset()}")

payload = {
    "order_id": "ord-99214",
    "customer_id": "cust-4410",
    "amount": 299.99,
    "created_at": 1721310000000
}

producer.produce(
    topic="orders.v1",
    key=payload["order_id"],
    value=payload,
    on_delivery=delivery_report
)
producer.flush()
```

### 7.2 Node.js / TypeScript: Resilient Consumer with Manual Ack & Retry DLQ (KafkaJS)

```typescript
import { Kafka, Consumer, EachMessagePayload, PartitionAssigners } from 'kafkajs';

const kafka = new Kafka({
  clientId: 'order-processing-service',
  brokers: ['kafka-1.prod.internal:9092', 'kafka-2.prod.internal:9092']
});

const consumer: Consumer = kafka.consumer({
  groupId: 'order-processors-v1',
  partitionAssigners: [PartitionAssigners.cooperativeSticky],
  sessionTimeout: 30000,
  heartbeatInterval: 3000,
});

async function processOrderMessage({ topic, partition, message }: EachMessagePayload): Promise<void> {
  const orderId = message.key?.toString();
  const rawValue = message.value?.toString();
  
  if (!rawValue) return;

  try {
    const orderData = JSON.parse(rawValue);
    // Execute domain business logic idempotently
    await executeBusinessRules(orderData);
  } catch (err: any) {
    console.error(`Error processing order key=${orderId}:`, err);
    
    // Route to DLQ Producer
    await sendToDLQ({
      originalTopic: topic,
      originalPartition: partition,
      offset: message.offset,
      key: message.key,
      value: message.value,
      headers: {
        ...message.headers,
        'x-error-message': Buffer.from(err.message || 'Unknown processing error'),
        'x-failed-at': Buffer.from(new Date().toISOString())
      }
    });
  }
}

async function start(): Promise<void> {
  await consumer.connect();
  await consumer.subscribe({ topic: 'orders.v1', fromBeginning: false });

  await consumer.run({
    autoCommit: false, // Enforce explicit manual commit controls
    eachMessage: async (payload) => {
      await processOrderMessage(payload);
      
      // Explicit manual offset commit per processed message
      const { topic, partition, message } = payload;
      await consumer.commitOffsets([
        { topic, partition, offset: (BigInt(message.offset) + 1n).toString() }
      ]);
    }
  });
}

start().catch(console.error);
async function executeBusinessRules(data: any) {}
async function sendToDLQ(dlqPayload: any) {}
```
