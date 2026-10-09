---
name: event-driven-architecture-saga-patterns
description: Designing resilient, eventual-consistency distributed transactions using the Saga Pattern (Choreography and Orchestration). Includes Outbox Pattern, Change Data Capture (CDC), idempotent consumers, compensating transactions, dual-write prevention, and saga recovery mechanisms. Use when implementing distributed multi-service workflows without two-phase commit (2PC).
---

# Event-Driven Architecture: Saga Patterns & Eventual Consistency Guide

## 1. Architectural Foundations: BASE over ACID

In microservices architectures, each service maintains its own private database to ensure loose coupling and independent scalability. This renders distributed ACID transactions impossible without two-phase commit (2PC). However, 2PC introduces high latency, synchronous blocking, single points of failure, and deadlocks across service boundaries.

The **Saga Pattern** manages distributed transactions as a sequence of local transactions. Each local transaction updates a single service's database and emits an event or message to trigger the next step. If a step fails, the Saga executes **compensating transactions** in reverse order to undo changes and restore data consistency.

### 1.1 Transaction Classification

```
[ Local Tx 1: Compensable ] ──► [ Local Tx 2: Pivot ] ──► [ Local Tx 3: Retryable ]
        │                             │                         │
   (Rollbackable)              (Point of No Return)       (Guaranteed Success)
```

- **Compensable Transactions**: Transactions that can be undone by running an explicit compensating transaction.
- **Pivot Transaction**: The critical decision point of the Saga. Once the pivot transaction succeeds, the Saga MUST go to completion. It cannot be compensated.
- **Retryable Transactions**: Transactions that follow the pivot point and are guaranteed to eventually succeed through retries.

---

## 2. Saga Execution Models: Choreography vs. Orchestration

```
CHOREOGRAPHY:
[ Order Service ] ── OrderCreated ──► [ Payment Service ] ── PaymentProcessed ──► [ Inventory Service ]

ORCHESTRATION:
                        ┌──► [ Payment Service ]
                        │
[ Saga Orchestrator ] ──┼──► [ Inventory Service ]
                        │
                        └──► [ Shipping Service ]
```

### 2.1 Comparative Analysis

| Dimension | Choreography Saga | Orchestration Saga |
| :--- | :--- | :--- |
| **Control Model** | Decentralized; services react to domain events. | Centralized; dedicated orchestrator directs participants. |
| **Coupling** | Loosely coupled; services know events, not handlers. | Moderate coupling; orchestrator knows participant APIs. |
| **State Visibility** | Distributed across service logs; hard to query global status. | Centralized state store; easy to track saga status. |
| **Complexity** | Simple for small flows (2-3 steps); cyclic dependencies in large flows. | High initial setup; manages complex branching & parallel paths easily. |
| **Failure Handling** | Complex cascading compensation logic across events. | Explicit compensation routines directed by orchestrator. |

### 2.2 Decision Matrix
- **Choose Choreography** when workflows are simple (2-3 microservices), linear, and teams want maximum domain event decoupling.
- **Choose Orchestration** when workflows involve 4+ services, complex conditional branching, parallel execution steps, or require strict operational auditing.

---

## 3. Dual-Write Prevention: Transactional Outbox & CDC

A major vulnerability in event-driven systems is the **Dual-Write Problem**: attempting to update a database and publish a message to a broker in a single code block without atomic guarantees.

```
WRONG (Dual Write Risk):
db.orders.insert(order);       // Success
broker.publish("OrderCreated"); // Network Failure! -> DB & Broker state out of sync!
```

### 3.1 Transactional Outbox Pattern Architecture

```
[ Business Logic ]
       │
       ▼ (Single ACID Local DB Transaction)
┌──────────────────────────────────────────────┐
│  Service Database                            │
│  ├── Orders Table:   [ Insert Order ]        │
│  └── Outbox Table:   [ Insert Outbox Event ] │
└──────────────────────────────────────────────┘
       │
       ▼ (Async Log Tailing / CDC)
[ Debezium / Outbox Publisher ] ──► [ Message Broker (Kafka / RabbitMQ) ]
```

1. Business record update and message metadata insertion are committed into the service's local database within a **single local ACID transaction**.
2. A separate process (e.g., Debezium CDC or a dedicated polling worker) reads the `outbox` table and safely forwards events to the message broker with **at-least-once** delivery guarantees.

---

## 4. Idempotency & De-duplication Engineering

Because event delivery is **at-least-once**, consumers WILL receive duplicate events. Consumers must be designed to be completely **idempotent**.

### 4.1 Idempotent Consumer Design Patterns

1. **Natural Unique Key Constraints**: Insert incoming event processing results using database unique constraints (e.g., `PRIMARY KEY (payment_id)`).
2. **Idempotency Key / Deduplication Table**:
   ```sql
   CREATE TABLE processed_events (
       event_id VARCHAR(128) PRIMARY KEY,
       consumer_group VARCHAR(64) NOT NULL,
       processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );
   ```
   Before processing logic begins, attempt atomic insertion into `processed_events`. If duplicate key violation occurs, skip processing and immediately ACK message.
3. **State Machine Guardrails**: Only allow state transitions that are valid from the current state (e.g., `UPDATE orders SET status = 'PAID' WHERE id = :id AND status = 'PENDING'`).

---

## 5. Compensating Transactions & Failure Recovery

Compensating transactions are inverse operations that semantically undo completed local transactions.

### 5.1 Rules for Compensating Actions
- **Must Be Idempotent**: A compensating step may be retried multiple times during recovery.
- **Must Never Fail Permanently**: If a compensating action encounters transient errors, it must retry until successful. If business invariants prevent auto-compensation, route to a **Human-in-the-Loop (HITL)** DLQ queue.
- **Semantic Rollback**: Compensation does not necessarily mean "deleting" rows. It often means applying a counter-action (e.g., issuing a credit refund rather than un-writing a credit charge).

---

## 6. Critical Anti-Patterns & Production Traps

1. **Dual Writes without Outbox Pattern**: Updating local DB state and calling `broker.publish()` directly without outbox tables or transactional CDC.
2. **Missing Compensating Triggers**: Implementing forward execution steps without defining corresponding inverse compensation handlers.
3. **Cyclic Choreography Dependencies**: Service A triggers Service B, which triggers Service C, which triggers Service A again, creating un-traceable infinite loops.
4. **Non-Idempotent Compensations**: Compensating transactions that double-credit or double-refund when retried.
5. **Synchronous REST Calls inside Sagas**: Mixing blocking HTTP calls within asynchronous event-driven sagas, leading to thread pool exhaustion and cascading failures.

---

## 7. Production Code Reference

### 7.1 Transactional Outbox Pattern in Python (SQLAlchemy)

```python
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    id = Column(String(64), primary_key=True)
    customer_id = Column(String(64), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(32), nullable=False)

class OutboxEvent(Base):
    __tablename__ = 'outbox'
    id = Column(String(64), primary_key=True)
    aggregate_type = Column(String(64), nullable=False)
    aggregate_id = Column(String(64), nullable=False)
    event_type = Column(String(64), nullable=False)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

engine = create_engine("postgresql://app_user:secret@db.prod.internal:5432/orders_db")
SessionLocal = sessionmaker(bind=engine)

def create_order_with_outbox(customer_id: str, amount: float) -> str:
    session = SessionLocal()
    order_id = f"ord-{uuid.uuid4()}"
    event_id = f"evt-{uuid.uuid4()}"
    
    order = Order(
        id=order_id,
        customer_id=customer_id,
        total_amount=amount,
        status="PENDING_PAYMENT"
    )
    
    event_payload = json.dumps({
        "event_id": event_id,
        "order_id": order_id,
        "customer_id": customer_id,
        "amount": amount,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    outbox_entry = OutboxEvent(
        id=event_id,
        aggregate_type="Order",
        aggregate_id=order_id,
        event_type="OrderCreated",
        payload=event_payload,
        created_at=datetime.now(timezone.utc)
    )

    try:
        # Atomic single local ACID transaction
        session.add(order)
        session.add(outbox_entry)
        session.commit()
        return order_id
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Failed to create order atomically: {str(e)}")
    finally:
        session.close()
```

### 7.2 Saga Orchestrator State Machine in TypeScript / Node.js

```typescript
type SagaState = 'STARTED' | 'PAYMENT_RESERVED' | 'INVENTORY_RESERVED' | 'COMPLETED' | 'FAILED' | 'COMPENSATING';

interface SagaContext {
  sagaId: string;
  orderId: string;
  customerId: string;
  amount: number;
  items: Array<{ sku: string; qty: number }>;
  currentState: SagaState;
  failureReason?: string;
}

export class OrderSagaOrchestrator {
  private context: SagaContext;

  constructor(context: SagaContext) {
    this.context = context;
  }

  async executeSaga(): Promise<void> {
    try {
      // Step 1: Reserve Payment (Compensable)
      await this.executeStep('PAYMENT_RESERVED', 
        () => this.callPaymentService('/payments/reserve', { amount: this.context.amount }),
        () => this.callPaymentService('/payments/refund', { amount: this.context.amount })
      );

      // Step 2: Reserve Inventory (Compensable)
      await this.executeStep('INVENTORY_RESERVED', 
        () => this.callInventoryService('/inventory/reserve', { items: this.context.items }),
        () => this.callInventoryService('/inventory/release', { items: this.context.items })
      );

      // Step 3: Pivot Point - Approve Order (Retryable)
      this.context.currentState = 'COMPLETED';
      await this.updateSagaState('COMPLETED');
      await this.callOrderService(`/orders/${this.context.orderId}/approve`, {});

    } catch (error: any) {
      console.error(`Saga ${this.context.sagaId} failed at state ${this.context.currentState}: ${error.message}`);
      this.context.failureReason = error.message;
      await this.compensateSaga();
    }
  }

  private async executeStep(
    targetState: SagaState, 
    action: () => Promise<void>, 
    compensation: () => Promise<void>
  ): Promise<void> {
    try {
      await action();
      this.context.currentState = targetState;
      await this.updateSagaState(targetState);
    } catch (err) {
      // Register compensation step for reverse execution
      this.compensations.push(compensation);
      throw err;
    }
  }

  private compensations: Array<() => Promise<void>> = [];

  private async compensateSaga(): Promise<void> {
    this.context.currentState = 'COMPENSATING';
    await this.updateSagaState('COMPENSATING');

    // Run compensations in reverse order
    for (const compensation of this.compensations.reverse()) {
      let retryCount = 0;
      let success = false;
      
      while (!success && retryCount < 5) {
        try {
          await compensation();
          success = true;
        } catch (compErr) {
          retryCount++;
          console.error(`Compensation retry ${retryCount} failed:`, compErr);
          await new Promise(res => setTimeout(res, 1000 * Math.pow(2, retryCount)));
        }
      }

      if (!success) {
        // Escalate to Human-In-The-Loop / DLQ Alerting
        console.error(`CRITICAL: Compensation failed permanently for Saga ${this.context.sagaId}`);
        await this.routeToHumanInterventionDLQ(this.context);
      }
    }

    this.context.currentState = 'FAILED';
    await this.updateSagaState('FAILED');
  }

  private async updateSagaState(state: SagaState): Promise<void> {/* DB state update */}
  private async callPaymentService(path: string, payload: any): Promise<void> {/* HTTP/gRPC */}
  private async callInventoryService(path: string, payload: any): Promise<void> {/* HTTP/gRPC */}
  private async callOrderService(path: string, payload: any): Promise<void> {/* HTTP/gRPC */}
  private async routeToHumanInterventionDLQ(context: SagaContext): Promise<void> {/* DLQ Alert */}
}
```
