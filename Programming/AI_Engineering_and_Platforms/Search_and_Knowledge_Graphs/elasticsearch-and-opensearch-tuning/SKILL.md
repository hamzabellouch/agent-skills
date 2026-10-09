---
name: elasticsearch-and-opensearch-tuning
description: Production guidance and performance tuning strategies for Elasticsearch and OpenSearch clusters, covering indexing, query optimization, mapping design, memory management, and scaling.
---

# Elasticsearch & OpenSearch Tuning Guide

This skill provides comprehensive instructions, architectural pattern guidelines, and production-ready code examples for optimizing Elasticsearch and OpenSearch for high-throughput indexing, ultra-low latency search, and cost-effective cluster scaling.

---

## 1. Indexing & Mapping Strategies

### 1.1 Field Mapping Optimization
- **Disable `_source` selectively** only when raw document retrieval is unnecessary and storage budget is tight; otherwise keep `_source` enabled for reindexing capabilities.
- **Set `index: false`** on fields used only for storage/retrieval (e.g., metadata blobs, raw HTML strings) to prevent inverted index overhead.
- **Explicit Mappings over Dynamic Mappings**: Never rely on dynamic mapping in production. Dynamic mapping introduces field explosion risks (`keyword` + `text` dual fields by default).
- **Use `doc_values: false`** for high-cardinality text or keyword fields that will **never** be used for aggregations, sorting, or scripting.
- **Optimize Text Analysis**:
  - Disable norm storage (`norms: false`) on text fields where relevance scoring is not required (e.g., exact matches, filter-only text).
  - Use `index_options: docs` for fields where positional or phrase queries are not needed (saves term frequency and position offset storage).

#### Optimized Mapping Definition (DSL)
```json
{
  "settings": {
    "index": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "refresh_interval": "30s",
      "translog": {
        "durability": "async",
        "sync_interval": "5s",
        "flush_threshold_size": "1gb"
      },
      "codec": "best_compression"
    }
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "id": {
        "type": "keyword",
        "doc_values": true
      },
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "raw": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "body": {
        "type": "text",
        "analyzer": "standard",
        "index_options": "positions",
        "norms": true
      },
      "category_id": {
        "type": "keyword",
        "doc_values": true,
        "norms": false
      },
      "status": {
        "type": "keyword",
        "doc_values": true
      },
      "created_at": {
        "type": "date",
        "format": "strict_date_optional_time||epoch_millis"
      },
      "payload_metadata": {
        "type": "keyword",
        "index": false,
        "doc_values": false
      }
    }
  }
}
```

---

### 1.2 Bulk Ingestion & Shard Sizing
- **Bulk Batch Size**: Ideal bulk request payload is typically between **5MB to 15MB** per request (or 2,000–5,000 documents depending on doc size). Tune based on CPU and throughput benchmarks rather than fixed doc counts.
- **Shard Sizing Standard**:
  - **Search-heavy indices**: Shard size should be **10GB to 30GB**.
  - **Logging / Time-series indices**: Shard size should be **30GB to 50GB**.
  - Target total shards per GB of JVM heap: Keep under **20 shards per GB of heap**.
- **Indexing Throughput Tuning**:
  - Increase `refresh_interval` from `1s` to `30s` or `60s` during heavy bulk ingestion.
  - Set `number_of_replicas: 0` during initial bulk loading, then restore to `1` or `2` after load completes.
  - Configure `translog.durability: async` for non-critical logging workloads to eliminate synchronous disk commits on every indexing request.

---

## 2. Query Tuning & Performance Optimization

### 2.1 Query Execution: Filter vs. Query Context
- **Filter Context (`filter`, `must_not`)**: Does not compute relevance scores (`_score`). Results are cached in the **Node Query Cache** (LRU bitsets). Always place non-scoring exact-match conditions inside `filter`.
- **Query Context (`must`, `should`)**: Computes relevance scores using BM25. Use exclusively for text relevance matching.

#### Optimized Multi-Clause Search Request
```json
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "status": "active" } },
        { "range": { "created_at": { "gte": "now-7d/d" } } }
      ],
      "must": [
        {
          "match": {
            "title": {
              "query": "distributed graph database",
              "operator": "and",
              "fuzziness": "AUTO:4,8"
            }
          }
        }
      ],
      "should": [
        {
          "match_phrase": {
            "body": {
              "query": "distributed graph database",
              "slop": 2,
              "boost": 2.5
            }
          }
        }
      ]
    }
  },
  "timeout": "500ms",
  "terminate_after": 10000,
  "_source": ["id", "title", "created_at"]
}
```

---

### 2.2 Deep Pagination Mitigation
- **Avoid `from` + `size`** for deep page iteration (`from + size > 10,000` causes Memory Overflow and high JVM CPU utilization).
- **Use `search_after` with Point In Time (PIT)** for deterministic stateless pagination over large result sets:

#### Python Production Example: `search_after` with PIT
```python
import logging
from typing import List, Dict, Any, Generator
from opensearchpy import OpenSearch, NotFoundError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepPaginationClient:
    def __init__(self, client: OpenSearch, index_name: str):
        self.client = client
        self.index_name = index_name

    def iterate_all_documents(
        self, query: Dict[str, Any], page_size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Executes deep pagination efficiently using Point In Time (PIT) / search_after.
        """
        # Create Point In Time (PIT) context (OpenSearch / ES 7.10+)
        try:
            pit_resp = self.client.create_point_in_time(
                index=self.index_name, keep_alive="2m"
            )
            pit_id = pit_resp["pit_id"]
        except Exception as e:
            logger.error("Failed to create Point In Time context: %s", str(e))
            raise

        search_after_mark = None
        total_fetched = 0

        try:
            while True:
                body: Dict[str, Any] = {
                    "size": page_size,
                    "query": query,
                    "sort": [
                        {"created_at": {"order": "desc"}},
                        {"_shard_doc": {"order": "asc"}} # Tie-breaker
                    ],
                    "pit": {
                        "id": pit_id,
                        "keep_alive": "2m"
                    }
                }

                if search_after_mark:
                    body["search_after"] = search_after_mark

                response = self.client.search(body=body)
                hits = response["hits"]["hits"]

                if not hits:
                    break

                for hit in hits:
                    yield hit["_source"]
                    total_fetched += 1

                search_after_mark = hits[-1]["sort"]
                logger.debug("Fetched batch of %d docs. Total: %d", len(hits), total_fetched)

        finally:
            # Always release PIT resources
            try:
                self.client.delete_point_in_time(body={"pit_id": pit_id})
            except Exception as e:
                logger.warning("Failed to delete PIT context: %s", str(e))
```

---

## 3. Memory & Infrastructure Management

### 3.1 JVM Heap Allocation
- Set `-Xms` and `-Xmx` to the **exact same value** to prevent dynamic heap resizing runtime pauses.
- **Never exceed 32GB heap**: Keep JVM heap under the Compressed OOPs threshold (typically **30GB–31GB** depending on JDK version) to ensure 32-bit pointer efficiency.
- Allocate **50% of total system RAM to JVM Heap** and leave the remaining 50% for **OS Filesystem Page Cache** (crucial for Doc Values, Lucene segment caching, and bloom filters).

### 3.2 Circuit Breakers & Thread Pools
- **Parent Circuit Breaker**: Set `indices.breaker.total.use_real_memory: true` with limit `70%` to prevent OutOfMemoryError (OOM).
- **Fielddata Breaker**: Set `indices.breaker.fielddata.limit: 40%`. Avoid using `fielddata: true` on `text` fields; use `keyword` fields with `doc_values`.
- **Search Thread Pool Queue**: `thread_pool.search.queue_size: 1000`. Do not set arbitrarily high; larger queues cause task latency accumulation and high garbage collection pressure.

---

## 4. Production Anti-Patterns & Solutions

| Anti-Pattern | Operational Impact | Recommended Solution |
| :--- | :--- | :--- |
| **Dynamic Mapping Explosion** | Unbounded field creation leads to cluster state degradation and OOM. | Set `"dynamic": "strict"` in index mappings. |
| **Using `wildcard` with leading asterisk (`*foo`)** | Forces full inverted index scanning; severe CPU consumption. | Use `wildcard` field type or n-gram tokenizer (`edge_ngram`). |
| **Over-Sharding** | Thousands of small shards (<1GB) exhaust JVM heap on metadata. | Reindex/Shrink indices to maintain 10GB–50GB per shard. |
| **Deep `from` + `size` Pagination** | Linear RAM and CPU scaling ($O(N)$ memory cost per request). | Use `search_after` with PIT or `scroll` API (for batch export). |
| **Heavy `script_score` Without Caching** | High CPU overhead per doc evaluation during query phase. | Pre-compute values at ingestion or use `painless` optimized scripts. |

---

## 5. Diagnostic & Monitoring Commands

### Checking Cluster Health & Shard Distribution
```bash
# Cluster health summary
GET /_cluster/health?v

# Shard count and size per index
GET /_cat/shards?v&s=index,shard&h=index,shard,prirep,state,docs,store,node

# Circuit breaker states and memory usage
GET /_nodes/stats/breaker

# Fielddata and Query Cache memory usage
GET /_nodes/stats/indices/fielddata,query_cache,request_cache?human=true
```
