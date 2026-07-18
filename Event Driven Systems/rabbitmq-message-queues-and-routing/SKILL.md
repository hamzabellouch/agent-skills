---
name: rabbitmq-message-queues-and-routing
description: Architecting high-availability RabbitMQ messaging systems, exchange topologies (direct, fanout, topic, headers, consistent-hash), AMQP protocol patterns, prefetch tuning, publisher confirms, consumer acknowledgements, Quorum Queues, and dead-lettering. Use when implementing AMQP queue-based routing, work queues, RPC over messaging, or resilient message delivery.
---

# RabbitMQ Message Queues & Advanced Routing Guide

## 1. Overview & Topology Fundamentals

RabbitMQ is an enterprise message broker implementing the AMQP 0-9-1 protocol (alongside MQTT and STOMP support). Unlike log-centric event streams, RabbitMQ emphasizes **smart broker / dumb consumer** routing: producers publish messages to *exchanges*, which route messages into *queues* based on *bindings* and *routing keys*. Queues hold messages until consumers process and acknowledge them.

### Key Architectural Axioms
- **Decoupled Topology**: Producers do not know which queues receive their messages; they publish solely to exchanges.
- **Explicit Acknowledgments**: Messages remain in queues until explicitly acknowledged by consumers (`basic.ack`) or rejected/nacked (`basic.nack`/`basic.reject`).
- **Quorum Queues as Default**: Legacy mirrored classic queues are deprecated. Production High Availability requires **Quorum Queues** backed by the Raft consensus algorithm.

---

## 2. Exchange Routing Strategies & Topologies

```
                     ┌───────────────┐
                     │ Direct Exch   │─── "orders.created" ───► [ Queue: Billing ]
                     └───────────────┘
                             │
                             ▼
[ Producer ] ──────► ┌───────────────┐
                     │ Topic Exch    │─── "orders.*"       ───► [ Queue: Analytics ]
                     └───────────────┘
                             │
                             ▼
                     ┌───────────────┐
                     │ Fanout Exch   │─── (Broadcast)      ───► [ Queue: AuditLog ]
                     └───────────────┘
```

### 2.1 Exchange Matrix

| Exchange Type | Matching Logic | Common Use Case |
| :--- | :--- | :--- |
| **Direct** | Exact match between routing key and binding key (`routing_key == binding_key`) | Targeted worker task queues, point-to-point command routing. |
| **Fanout** | Ignores routing key; broadcasts to all bound queues | System-wide notification fan-out, audit logging, cache invalidation. |
| **Topic** | Wildcard matching (`*` matches 1 word, `#` matches 0 or more words) | Domain event hierarchies (e.g., `europe.orders.created`, `*.orders.#`). |
| **Headers** | Matches message header key-value pairs (`x-match: all` or `any`) | Routing based on structured metadata (e.g., region, tenant_id, format). |
| **Consistent-Hash** | Hashes routing key or header to distribute messages across queues | Load balancing across multiple dedicated processing queues while maintaining hash key ordering. |

---

## 3. High Availability, Durability & Delivery Guarantees

### 3.1 Quorum Queue Architecture
Always declare production queues with `x-queue-type: quorum`.
- Provides data replication across cluster nodes via Raft consensus.
- Handles leader elections automatically without data corruption risk.
- Configurable delivery limits (`x-delivery-limit`) to drop or dead-letter persistent poison pills.

### 3.2 Publisher Confirms (At-Least-Once Publishing)
Producers must enable **Publisher Confirms** on AMQP channels.
- The broker sends an `ack` back to the publisher once the message is written to disk or replicated across quorum followers.
- If storage fails, broker sends `nack`, prompting the publisher to retry or route to persistent local storage.

### 3.3 Consumer QoS & Prefetch Tuning
`basic.qos(prefetch_count)` dictates how many unacknowledged messages a broker will push to a consumer over a channel.

$$\text{Optimal Prefetch} = \frac{\text{Mean Processing Time per Message}}{\text{Network Round Trip Time (RTT)}} \times \text{Target Concurrency}$$

- **Prefetch = 1**: Safest for heavy, long-running processing (prevents task starvation on busy workers).
- **Prefetch = 100 - 500**: Optimal for high-throughput micro-tasks (prevents consumer idle time waiting for broker pushes).
- **Prefetch = 0 (Unbounded)**: **DANGEROUS**. Saturates consumer memory and causes broker out-of-memory crashes.

---

## 4. Dead Letter Exchanges (DLX) & Retry Mechanisms

When a message is rejected (`basic.nack(requeue=false)`), expires via TTL, or exceeds queue length limits, the broker automatically forwards it to a designated Dead Letter Exchange.

### 4.1 Topology for Delayed Retry Loops

```
[ Primary Exchange ] ──► [ Primary Queue ] 
                             │ (Processing Error / Nack)
                             ▼
[ DLX Exchange ]     ──► [ TTL Wait Queue (TTL: 60s) ]
                             │ (Message Expires)
                             ▼
[ Retry Exchange ]   ──► [ Primary Queue ]
```

### 4.2 Queue Arguments Definition (JSON / AMQP Table)
```json
{
  "x-queue-type": "quorum",
  "x-dead-letter-exchange": "orders.dlx",
  "x-dead-letter-routing-key": "orders.dead",
  "x-delivery-limit": 5
}
```

---

## 5. Connection & Channel Management Rules

- **Long-Lived Connections**: Maintain a single TCP connection per application process. Do NOT open/close connections per message.
- **Short-Lived Channels**: Open dynamic channels for discrete operational threads/tasks, then close them. Channels are cheap; TCP connections are expensive.
- **Thread Safety**: AMQP channels are **NOT thread-safe**. Never share a single channel across parallel concurrent threads or async tasks.

---

## 6. Critical Anti-Patterns & Production Warnings

1. **Auto-ACK (`autoAck=true`) on Consumers**: Acknowledges message arrival immediately upon network socket write. If the application crashes before logic finishes, the message is permanently lost.
2. **Channel per Message Anti-Pattern**: Rapidly opening and closing channels per message creates severe broker CPU contention and socket starvation.
3. **Queue Sprawl**: Creating dynamic temporary queues per customer or per event type overloads Mnesia DB and cluster sync overhead. Keep queue topologies static.
4. **Ignoring Broker Alarm Blockers**: Ignoring memory/disk high-watermarks causes RabbitMQ to block incoming connections without throwing application-level publishing exceptions unless handles are configured.
5. **Requeueing Failed Messages to Top of Queue (`requeue=true`)**: Creates an infinite tight loop CPU spin when encountering unparseable poison pills.

---

## 7. Production Code Reference

### 7.1 Python: Robust Publisher with Publisher Confirms (pika)

```python
import pika
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_connection():
    credentials = pika.PlainCredentials('prod_user', 'secure_pass123')
    parameters = pika.ConnectionParameters(
        host='rabbitmq.prod.internal',
        port=5672,
        virtual_host='/vhosts/orders',
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=300
    )
    return pika.BlockingConnection(parameters)

connection = create_connection()
channel = connection.channel()

# Enable Publisher Confirms
channel.confirm_delivery()

# Declare durable Exchange and Quorum Queue
channel.exchange_declare(exchange='orders.direct', exchange_type='direct', durable=True)
channel.queue_declare(
    queue='orders.process',
    durable=True,
    arguments={
        'x-queue-type': 'quorum',
        'x-dead-letter-exchange': 'orders.dlx',
        'x-dead-letter-routing-key': 'orders.poison'
    }
)
channel.queue_bind(exchange='orders.direct', queue='orders.process', routing_key='order.new')

payload = {
    'order_id': 'ORD-8812',
    'total': 149.50,
    'timestamp': '2026-07-18T14:30:00Z'
}

try:
    channel.basic_publish(
        exchange='orders.direct',
        routing_key='order.new',
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent, # Message durability
            content_type='application/json',
            headers={'x-correlation-id': 'corr-771239'}
        ),
        mandatory=True # Return message if unroutable
    )
    logger.info("Message successfully acknowledged by broker (Publisher Confirm).")
except pika.exceptions.UnroutableError:
    logger.error("Message was returned by broker as unroutable!")
except pika.exceptions.NackError:
    logger.error("Message was NACKed by broker! Retrying or saving to local outbox...")
finally:
    connection.close()
```

### 7.2 Node.js / TypeScript: Resilient Consumer with QoS & Manual Ack/Nack (amqplib)

```typescript
import amqp, { Connection, Channel, ConsumeMessage } from 'amqplib';

async function startConsumer(): Promise<void> {
  const connUrl = 'amqp://prod_user:secure_pass123@rabbitmq.prod.internal:5672/vhosts/orders';
  const connection: Connection = await amqp.connect(connUrl);
  const channel: Channel = await connection.createChannel();

  const queueName = 'orders.process';
  
  // Set explicit prefetch (QoS)
  await channel.prefetch(10);

  console.log(`[*] Waiting for messages in ${queueName}. To exit press CTRL+C`);

  await channel.consume(
    queueName,
    async (msg: ConsumeMessage | null) => {
      if (!msg) return;

      const correlationId = msg.properties.headers['x-correlation-id'];
      const rawContent = msg.content.toString();

      try {
        const order = JSON.parse(rawContent);
        console.log(`[Processing] Order=${order.order_id}, Correlation=${correlationId}`);
        
        await processOrderBusinessLogic(order);

        // Explicit acknowledgment after successful execution
        channel.ack(msg);
      } catch (err: any) {
        console.error(`[Error] Failed processing message: ${err.message}`);

        const deliveryCount = msg.properties.headers['x-delivery-count'] || 1;
        
        if (deliveryCount >= 3) {
          // Reject without requeue -> routes automatically to DLX
          console.warn(`[DLX] Exceeded max retries. Rejecting to DLX.`);
          channel.nack(msg, false, false);
        } else {
          // Requeue for transient retry
          console.warn(`[Retry] Requeueing message for attempt ${deliveryCount + 1}`);
          channel.nack(msg, false, true);
        }
      }
    },
    { noAck: false } // Force explicit manual acknowledgments
  );
}

async function processOrderBusinessLogic(order: any): Promise<void> {
  // Business logic implementation
}

startConsumer().catch(console.error);
```
