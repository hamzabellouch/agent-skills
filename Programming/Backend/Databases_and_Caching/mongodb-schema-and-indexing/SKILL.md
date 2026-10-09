---
name: mongodb-schema-and-indexing
description: Production-grade MongoDB schema design patterns, indexing strategies, ESR rule (Equality, Sort, Range), aggregation framework optimization, and sharding/partitioning architectures. Use when designing MongoDB schemas, tuning query performance, or building aggregation pipelines.
---

# MongoDB Schema Design & Indexing Optimization Guide

Comprehensive architectural reference for MongoDB schema modeling, high-performance indexing, aggregation pipeline tuning, and cluster sharding strategies.

---

## 1. Schema Modeling Framework: Embedding vs. Referencing

### Decision Matrix

```
                      Do entities have a 1:1 or 1:Few relationship?
                                     /             \
                                  YES               NO
                                  /                   \
           Embed data inside parent document         Do child documents grow unbounded?
                                                            /             \
                                                         YES               NO
                                                         /                   \
                                            Use Two-Way Referencing      Embed with Subset Pattern
```

| Factor | Embedded Subdocuments | Referenced Documents (Normalized) |
| :--- | :--- | :--- |
| **Query Performance** | Fast ($O(1)$ single read, no joins) | Requires `$lookup` or application-side joins |
| **Atomicity** | Atomic updates across whole document | Requires Multi-Document Transactions (`session`) |
| **Document Size Limit** | Subject to 16 MB BSON hard limit | Multi-document architecture bypasses limit |
| **Data Redundancy** | Possible duplication across documents | Single source of truth |

---

## 2. Advanced MongoDB Design Patterns

### 2.1 Subset Pattern
* **Problem**: Large embedded array (e.g., 5,000 product reviews) causes huge document size and slow memory loading.
* **Solution**: Keep only the 10 most recent reviews in the main product document; store all historical reviews in a separate `reviews` collection.

### 2.2 Extended Reference Pattern
* **Problem**: Frequent joins (`$lookup`) just to fetch 1 or 2 fields (e.g., `customerName` and `customerEmail` on an `Order`).
* **Solution**: Copy immutable or rarely changed target fields directly into the order document:
  ```json
  {
    "_id": ObjectId("6697a4..."),
    "totalAmount": 149.99,
    "customer": {
      "id": ObjectId("6697a2..."),
      "name": "Jane Doe",
      "email": "jane@example.com"
    }
  }
  ```

### 2.3 Bucket Pattern
* **Problem**: Time-series or IoT metric data logging creates millions of tiny documents, inflating index overhead.
* **Solution**: Group data points into hourly or daily bucket documents containing arrays of measurements:
  ```json
  {
    "sensorId": "TEMP-NODE-04",
    "timestampDay": ISODate("2026-07-18T00:00:00Z"),
    "count": 60,
    "measurements": [
      { "sec": 0, "val": 22.4 },
      { "sec": 60, "val": 22.5 }
    ]
  }
  ```

### 2.4 Schema Versioning Pattern
Add a `schemaVersion` field to every document to allow zero-downtime lazy migration across schema iterations.

---

## 3. High-Performance Indexing & The ESR Rule

### The ESR Rule (Equality, Sort, Range)
When creating compound indexes, order fields according to:
1. **E - Equality**: Fields matched on exact values first.
2. **S - Sort**: Fields used for sorting results second.
3. **R - Range**: Fields queried with inequality range operators (`$gte`, `$lte`, `$in`, `$ne`) last.

```typescript
// Example: Querying active orders for a customer sorted by creation date within a price range
// Query: db.orders.find({ customerId: "C123", status: "ACTIVE", price: { $gte: 50 } }).sort({ createdAt: -1 })

// PERFECT INDEX according to ESR:
// Equality: customerId, status
// Sort:     createdAt
// Range:    price

db.orders.createIndex({
  customerId: 1,
  status: 1,
  createdAt: -1,
  price: 1
});
```

### Specialized Index Types

* **Partial Indexes**: Index only documents matching a specific expression (reduces index memory size):
  ```typescript
  db.users.createIndex(
    { email: 1 },
    { unique: true, partialFilterExpression: { email: { $type: "string" } } }
  );
  ```
* **Compound Multikey Indexes**: Indexes over array fields. *Rule: A compound index can contain at most ONE array field.*
* **TTL Indexes**: Automatically delete documents after a specified time interval:
  ```typescript
  db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 86400 });
  ```

---

## 4. Aggregation Framework Optimization

1. **Early Filtering**: Always place `$match` and `$sort` stages at the very beginning of the pipeline to leverage indexes.
2. **Projection Pushdown**: Use `$project` or `$unset` early to eliminate unused fields before memory-heavy operations (`$group`, `$lookup`).
3. **Indexed Joins**: Ensure foreign collection fields targeted by `$lookup` have indexes:
   ```javascript
   // Requires index on 'orders.userId'
   db.users.aggregate([
     { $match: { status: "ACTIVE" } },
     {
       $lookup: {
         from: "orders",
         localField: "_id",
         foreignField: "userId",
         as: "userOrders"
       }
     }
   ]);
   ```

---

## 5. Sharding & Partitioning Architecture

### Shard Key Selection Principles
* **High Cardinality**: Ensures distinct values split across thousands of chunks.
* **Balanced Frequency**: Prevents a single value from creating a monolithic non-splitable chunk (Jumbo Chunk).
* **Targeted Operations**: Choose keys that allow query routing directly to a single shard (avoiding **Scatter-Gather** queries across all shards).

```
          [ Query Router: mongos ]
                 /        \
   (Targeted Query)      (Scatter-Gather Query)
               /            \
   [ Shard A ]                [ Shard A ] + [ Shard B ] + [ Shard C ]
```

---

## 6. Anti-Patterns & Common Pitfalls

* ❌ **Unindexed Queries in Production**: Leads to COLLSCAN (collection scans) that exhaust RAM and CPU.
* ❌ **Dynamic Field Names**: Storing keys as values (e.g., `{"attr_color": "blue"}` instead of `{"name": "color", "value": "blue"}`). Prevents effective indexing.
* ❌ **Over-Indexing**: Every index adds latency to insert/update/delete operations and consumes WiredTiger cache memory.
* ❌ **Unbounded Array Growth**: Arrays growing beyond 1,000+ items cause document move overhead and memory pressure.
