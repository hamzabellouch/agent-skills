---
name: neo4j-memgraph-cypher-queries
description: Advanced Cypher query optimization, index design, traversal strategies, and execution plan analysis for Neo4j and Memgraph graph databases.
---

# Neo4j & Memgraph Cypher Query Optimization

This skill provides actionable design patterns, query tuning strategies, execution plan diagnostic guidelines, and production-grade Python implementations for Neo4j and Memgraph graph engine workloads.

---

## 1. Indexing & Schema Strategies

### 1.1 Index Types & Usage
- **Range / Composite Indexes**: Use for scalar equality, numeric ranges, and multi-property filter combinations.
- **Text / Fulltext Indexes**: Use for fuzzy text matching, wildcard matching, and relevance-scored search (`db.index.fulltext.queryNodes`).
- **Vector Indexes**: Use for k-Nearest Neighbor (kNN) vector similarity search on node embeddings (`db.index.vector.createNodeIndex`).
- **Lookup Indexes**: Ensure entity label and relationship type lookup indexes exist for fast node/edge scan entry points.

#### Schema & Index Definition Script (Cypher)
```cypher
// 1. Uniqueness constraints (automatically creates single-property Range Index)
CREATE CONSTRAINT cstr_user_id IF NOT EXISTS
FOR (u:User) REQUIRE u.id IS UNIQUE;

CREATE CONSTRAINT cstr_product_sku IF NOT EXISTS
FOR (p:Product) REQUIRE p.sku IS UNIQUE;

// 2. Composite Range Index for multi-field filtering
CREATE INDEX idx_order_status_date IF NOT EXISTS
FOR (o:Order) ON (o.status, o.created_at);

// 3. Fulltext Index for text matching (Neo4j syntax)
CREATE FULLTEXT INDEX idx_product_fulltext IF NOT EXISTS
FOR (n:Product) ON EACH [n.name, n.description];

// 4. Vector Index for 1536-dim embeddings (Cosine distance)
CREATE VECTOR INDEX idx_document_embedding IF NOT EXISTS
FOR (d:Document) ON (d.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};
```

---

## 2. Query Optimization Patterns

### 2.1 Traversal Pruning & Anchoring
- **Anchor Nodes Early**: Always start matches from the most restrictive node pattern (leveraging unique constraints or selective indexes).
- **Inline Property Filters**: Place node filter predicates inside the `MATCH` pattern `(n:User {id: $id})` or immediately in a `WHERE` clause before expansion.
- **Specify Relationship Types and Directions**: Avoid untyped or undirected traversals `(a)--(b)`. Use explicit directional types `(a:User)-[:PURCHASED]->(b:Product)`.

### 2.2 Eliminating Eager Operators
- **Eager Operators (`Eager`, `EagerAggregation`)**: Force the execution engine to buffer all intermediate rows before proceeding, breaking streaming execution and exhausting memory.
- **Fix**: Perform aggregations or filtering **before** executing further `MATCH` traversals.

#### Optimized vs. Unoptimized Query Patterns

```cypher
// BAD: Unbounded traversal + Eager aggregation after deep path match
MATCH (u:User)-[:FOLLOWS*1..3]->(f:User)-[:LIKED]->(p:Product)
WHERE u.id = $userId AND p.category = $category
RETURN p.id, count(f) AS score;

// GOOD: Anchored starting node + bounded path + early filter + distinct aggregation
MATCH (u:User {id: $userId})
MATCH (u)-[:FOLLOWS*1..2]->(f:User)
WITH DISTINCT f
MATCH (f)-[:LIKED]->(p:Product {category: $category})
RETURN p.id AS productId, count(f) AS recommendationScore
ORDER BY recommendationScore DESC
LIMIT 20;
```

---

### 2.3 Batch Operations & Parameterization
- **Use `UNWIND` for Bulk Ingest/Updates**: Avoid sending individual Cypher queries per record. Group mutations into batched arrays (e.g., 1,000–5,000 items per transaction).
- **Explicit Parameterization**: Never concatenate raw strings into Cypher queries; dynamic query strings prevent execution plan caching and create Cypher injection vulnerabilities.

#### Production Bulk Ingestion Query
```cypher
UNWIND $batch AS row
MERGE (u:User {id: row.userId})
ON CREATE SET u.createdAt = datetime(), u.name = row.userName
MERGE (p:Product {sku: row.productSku})
MERGE (u)-[r:VIEWED]->(p)
ON CREATE SET r.timestamp = datetime(row.viewTimestamp), r.count = 1
ON MATCH SET r.count = r.count + 1, r.lastViewed = datetime(row.viewTimestamp);
```

---

## 3. Execution Plan Analysis (`EXPLAIN` vs. `PROFILE`)

### 3.1 Key Operators & Metrics
- **`EXPLAIN`**: Returns the predicted execution plan without executing the query (zero side effects).
- **`PROFILE`**: Executes the query and records actual metrics. Focus on **DbHits** and **Rows**.
- **Metrics to Watch**:
  - **DbHits**: Count of storage layer memory operations. High `DbHits` per returned row (>100:1 ratio) indicates inefficient graph scanning.
  - **CartesianProduct**: Indicates disconnected `MATCH` clauses. Red flag for explosive $O(N \times M)$ memory growth.
  - **NodeByLabelScan / NodeUniqueIndexSeek**: Ensure queries start with `NodeUniqueIndexSeek` or `NodeIndexSeek` rather than full `NodeByLabelScan`.

---

## 4. Production Python Implementation

The following script demonstrates production query execution, batch parameterization, and connection pool management using `neo4j` official driver.

```python
import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver, Session, ManagedTransaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CypherQueryExecutor:
    def __init__(self, uri: str, auth: tuple, max_connection_pool_size: int = 50):
        self.driver: Driver = GraphDatabase.driver(
            uri,
            auth=auth,
            max_connection_pool_size=max_connection_pool_size,
            connection_acquisition_timeout=30.0
        )

    def close(self) -> None:
        self.driver.close()

    def execute_read_recommendations(
        self, user_id: str, category: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Executes an optimized recommendation query using read transaction retries.
        """
        query = """
        MATCH (u:User {id: $userId})
        MATCH (u)-[:FOLLOWS*1..2]->(f:User)
        WITH DISTINCT f
        MATCH (f)-[:LIKED]->(p:Product {category: $category})
        RETURN p.sku AS sku, p.name AS productName, count(f) AS score
        ORDER BY score DESC
        LIMIT $limit
        """
        params = {"userId": user_id, "category": category, "limit": limit}

        with self.driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run(query, params).data()
            )
            return result

    def bulk_upsert_user_views(
        self, view_events: List[Dict[str, Any]], batch_size: int = 1000
    ) -> int:
        """
        Processes bulk edge creation with UNWIND and batching.
        """
        query = """
        UNWIND $batch AS row
        MATCH (u:User {id: row.userId})
        MATCH (p:Product {sku: row.sku})
        MERGE (u)-[r:VIEWED]->(p)
        ON CREATE SET r.firstViewed = timestamp(), r.viewCount = 1
        ON MATCH SET r.viewCount = r.viewCount + 1, r.lastViewed = timestamp()
        """
        total_processed = 0

        for i in range(0, len(view_events), batch_size):
            chunk = view_events[i : i + batch_size]
            with self.driver.session() as session:
                session.execute_write(
                    lambda tx: tx.run(query, batch=chunk).consume()
                )
            total_processed += len(chunk)
            logger.info("Ingested batch %d to %d", i, i + len(chunk))

        return total_processed
```

---

## 5. Common Anti-Patterns & Pitfalls

| Anti-Pattern | Operational Risk | Corrective Action |
| :--- | :--- | :--- |
| **Unbounded Path Traversal `(a)-[*]->(b)`** | Traverses entire graph component; memory crash or infinite execution loop. | Bound maximum depth: `(a)-[*1..4]->(b)`. |
| **Disconnected MATCH Clauses** | Implicit Cartesian Product ($N \times M$ combinations). | Connect patterns or use `WITH` to bind variables explicitly. |
| **Collecting Whole Graph Entities** | `RETURN collect(node)` buffers massive object heaps in memory. | Project only required properties `RETURN node.id, node.name`. |
| **Updating Nodes inside Deep Loops** | Eager lock acquisitions cause lock escalation and transaction deadlocks. | Aggregated updates or batch with `CALL { ... } IN TRANSACTIONS`. |
| **Missing Node Labels in Patterns** | Engine searches across all nodes in database instead of labeled subset. | Always specify node label e.g. `(n:Customer)` instead of `(n)`. |
