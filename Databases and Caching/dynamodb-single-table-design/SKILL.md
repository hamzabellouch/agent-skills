---
name: dynamodb-single-table-design
description: Advanced Amazon DynamoDB Single-Table Design patterns, access pattern modeling, Partition Key (PK) and Sort Key (SK) strategies, Global Secondary Indexes (GSIs), sparse indexes, and transactions. Use when designing high-scale DynamoDB data layers.
---

# DynamoDB Single-Table Design Architecture Guide

Comprehensive reference for mastering Amazon DynamoDB Single-Table Design, access pattern modeling, secondary index overloading, sparse indexes, and high-concurrency transactional operations.

---

## 1. Principles of Single-Table Design

### Why Single-Table Design?
In DynamoDB, microsecond-latency scale is achieved by avoiding runtime joins. Instead of creating separate tables for each entity type, a Single-Table Design pre-joins heterogenous entities into a single physical table using generic Partition Keys (`PK`) and Sort Keys (`SK`).

```
+-------------------+--------------------+------------------------+------------------+
| PK                | SK                 | Type                   | Data Payload     |
+-------------------+--------------------+------------------------+------------------+
| USER#usr_1001     | METADATA           | UserProfile            | { name, email }  |
| USER#usr_1001     | ORDER#2026-07-01   | Order                  | { total: 49.99 } |
| USER#usr_1001     | ORDER#2026-07-18   | Order                  | { total: 89.00 } |
| ORDER#ord_9901    | METADATA           | Order                  | { status: SHIPPED|
+-------------------+--------------------+------------------------+------------------+
```

### Access Pattern Driven Design Workflow
1. **List all access patterns** (Reads, Writes, Aggregations) *before* defining keys.
2. Design Primary Partition Keys (`PK`) to group related items into logical item collections.
3. Design Primary Sort Keys (`SK`) to enable range filtering (`begins_with`, `BETWEEN`).
4. Add Global Secondary Indexes (GSIs) for alternate access vectors.

---

## 2. Primary Key & Composite Sort Key Conventions

### Common Key Formatting Conventions

* **User Entity**: `PK: USER#<userId>`, `SK: METADATA`
* **User Orders**: `PK: USER#<userId>`, `SK: ORDER#<timestamp>#<orderId>`
* **Order Details**: `PK: ORDER#<orderId>`, `SK: METADATA`
* **Order Line Items**: `PK: ORDER#<orderId>`, `SK: ITEM#<lineItemId>`

### Hierarchical Querying via Composite Keys
Sort keys can store hierarchical values separated by delimiters (`#` or `#STATUS#`):

```typescript
// Sort Key pattern: STATUS#<status>#DATE#<date>
// Example SK value: STATUS#PENDING#DATE#2026-07-18

// Access Pattern: Fetch all PENDING orders for a store created today
QueryInput = {
  KeyConditionExpression: "PK = :pk AND begins_with(SK, :skPrefix)",
  ExpressionAttributeValues: {
    ":pk": "STORE#store_880",
    ":skPrefix": "STATUS#PENDING#DATE#2026-07-18"
  }
}
```

---

## 3. Modeling Relationships & Secondary Indexes

### 3.1 1:N Relationships (Item Collections)
Fetch both parent metadata and child items in a single $O(1)$ `Query` operation:

```typescript
// Query PK = "USER#usr_1001" returns:
// 1. User Profile item (SK = "METADATA")
// 2. All user orders (SK starts with "ORDER#")
```

### 3.2 N:M Relationships (Adjacency List Pattern)
Model many-to-many associations (e.g., Users and Groups) using primary keys for forward lookup and an inverted GSI for reverse lookup.

| Index | PK | SK | Target Entity |
| :--- | :--- | :--- | :--- |
| **Base Table** | `USER#usr_1` | `GROUP#grp_100` | User Membership |
| **GSI1 (Inverted)** | `GROUP#grp_100` | `USER#usr_1` | Reverse Group Roster |

### 3.3 Sparse Indexes for State Filtering
GSIs only index items containing the index attributes. Omitting GSI key fields for items in non-target states creates a low-cost, ultra-efficient **Sparse Index**.

```typescript
// Only items with GSI1PK set (e.g. orders requiring review) appear in GSI1
const orderNeedingReview = {
  PK: "ORDER#ord_505",
  SK: "METADATA",
  GSI1PK: "ORDERS_PENDING_REVIEW",
  GSI1SK: "2026-07-18T14:30:00Z",
  status: "FLAGGED"
};
```

---

## 4. Concurrency Control, Transactions & TTL

### Optimistic Locking via Condition Expressions
Prevent race conditions during concurrent write operations without table locking:

```typescript
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, UpdateCommand } from '@aws-sdk/lib-dynamodb';

const ddocClient = DynamoDBDocumentClient.from(new DynamoDBClient({}));

async function updateAccountBalance(accountId: string, amount: number, currentVersion: number) {
  const command = new UpdateCommand({
    TableName: 'SingleTableApp',
    Key: {
      PK: `ACCOUNT#${accountId}`,
      SK: 'METADATA'
    },
    UpdateExpression: 'SET balance = balance + :val, version = version + :inc',
    ConditionExpression: 'version = :expectedVersion AND balance >= :minBalance',
    ExpressionAttributeValues: {
      ':val': amount,
      ':inc': 1,
      ':expectedVersion': currentVersion,
      ':minBalance': Math.abs(amount)
    }
  });

  return await ddocClient.send(command);
}
```

---

## 5. Anti-Patterns & Common Pitfalls

* ❌ **Relational Mindset (Multi-Table Sprawl)**: Creating a table for every entity type. Increases latency and operational overhead.
* ❌ **Using `Scan` in Production API Endpoints**: Reads every partition sequentially. Causes extreme cost and request throttling. **Always use `Query` or `GetItem`**.
* ❌ **Hot Partitions**: Structuring `PK` using low-cardinality values (e.g., `PK: GENDER#MALE`). Reaches partition IOPS limits ($1,000$ write units/sec or $3,000$ read units/sec per partition).
* ❌ **Unbounded Item Sizes**: Storing growing arrays inside a single item until reaching the $400\text{ KB}$ DynamoDB item hard limit. Split array items across sort keys instead.
* ❌ **Unnecessary `ProjectionExpression: ALL` on GSIs**: Duplicates all attribute data into secondary index storage, driving up AWS billable write units. Use `KEYS_ONLY` or `INCLUDE` where possible.
