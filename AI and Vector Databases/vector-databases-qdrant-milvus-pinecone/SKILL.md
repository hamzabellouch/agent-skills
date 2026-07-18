---
name: vector-databases-qdrant-milvus-pinecone
description: Architect, deploy, and optimize production-grade vector search engines using Qdrant, Milvus, and Pinecone. Covers index selection (HNSW, IVF, DiskANN), vector quantization (Scalar, Product, Binary), distance metrics, payload filtering, multi-tenancy, and performance tuning.
---

# Vector Databases Architect Skill: Qdrant, Milvus, & Pinecone

## 1. Architectural Taxonomy & Selection Matrix

| Feature / Criteria | Qdrant | Milvus | Pinecone |
| :--- | :--- | :--- | :--- |
| **Deployment Model** | Self-hosted (Rust, Single/Distributed) or Qdrant Cloud | Self-hosted (Go/C++, Cloud-Native K8s) or Zilliz Cloud | Fully Managed Serverless / Pods (SaaS) |
| **Primary Indexing** | In-Memory HNSW, On-Disk HNSW, Memmap Vectors | HNSW, IVF_FLAT, IVF_PQ, SCaNN, DiskANN | Proprietary Graph / Serverless Blob-backed |
| **Quantization Support** | Scalar (SQ8), Product (PQ), Binary (BQ) | Scalar (SQ8), Product (PQ), Binary | Handled internally in Serverless |
| **Filter Engine** | Native Payload Indexing (B-Tree, Keyword, Geo) | Dynamic Schema & Expression Parsing | Metadata Filtering (JSON-like) |
| **Hardware Efficiency** | Extremely low memory footprint via Memmap + Quantization | High-throughput distributed scaling, GPU acceleration | Pay-per-read/write scaling |
| **Best Used For** | Low-latency, cost-efficient self-hosted or hybrid cloud RAG | Enterprise scale (>100M+ vectors), distributed K8s, GPU search | Zero-Ops managed scaling, quick time-to-market |

---

## 2. Index Selection, Memory Estimation & Quantization Math

### Indexing Mechanisms
1. **HNSW (Hierarchical Navigable Small World)**
   - *m (Max Edges per node)*: Default 16. Higher values (32-64) improve recall for high-dimensional vectors (>1024d) at the cost of memory and build time.
   - *ef_construction*: Default 100-200. Controls index build precision.
   - *ef_search*: Dynamic search depth. Higher = higher recall, lower QPS.
2. **IVF (Inverted File Index)**
   - *nlist*: Number of cluster centroids (e.g., $\sqrt{N}$ to $4\sqrt{N}$).
   - *nprobe*: Number of centroids queried during search.
3. **DiskANN / Vamana**
   - Stores vectors on NVMe SSD with in-memory compressed graph edges. Crucial for massive scale (>1B vectors) with constrained RAM.

### Quantization Techniques
- **Scalar Quantization (SQ8)**: Maps 32-bit floats (`float32`) to 8-bit integers (`int8`). Reduces RAM by ~75% with minimal recall drop (<1%).
- **Product Quantization (PQ)**: Splits high-dim vector into $m$ sub-vectors and quantizes each into centroid IDs (`uint8`). Reduces RAM by up to 90-95%, with minor accuracy tradeoff.
- **Binary Quantization (BQ)**: Quantizes positive floats to `1` and negative to `0` (1 bit per dimension). 32x reduction in size and ultra-fast Hamming distance, best combined with dense re-ranking.

### RAM Estimation Formula
$$\text{Memory (GB)} \approx \frac{N \times (D \times S_{bytes} + 8 \times M_{edges}) \times 1.2}{10^9}$$
Where:
- $N$ = Number of vectors
- $D$ = Vector Dimensions (e.g., 1536)
- $S_{bytes}$ = Bytes per scalar (4 for Float32, 1 for SQ8, 0.125 for BQ)
- $M_{edges}$ = HNSW $m$ connections (e.g., 16)
- $1.2$ = 20% overhead for payload indexes and system buffers.

---

## 3. Best Practices & Anti-Patterns

### Best Practices
- **Payload/Metadata Indexing**: Always create explicit index fields for filtered attributes (e.g., `user_id`, `tenant_id`, `category`) before performing filtered ANN searches.
- **Batching & Concurrent Writes**: Ingest vectors in chunks of 500–2,000 vectors with parallel threads to saturate network I/O without overloading memory.
- **Over-fetching for Re-ranking**: When using heavy payload filters or Binary Quantization, fetch $k \times 3$ or $k \times 5$ candidate results, then re-score or filter down to top $k$.
- **Multi-Tenancy**: Use tenant isolation keys in a shared collection/namespace for $<1,000$ tenants; use dedicated collections/namespaces for massive tenants requiring strict data isolation.

### Anti-Patterns
- ❌ **Unfiltered Full Scan**: Running filtering on unindexed payload fields forcing full-vector scans across millions of items.
- ❌ **Storing Raw High-Dim Vectors in Pure RAM**: Storing 1536d Float32 vectors in RAM without memmap or SQ/PQ quantization when dataset exceeds 50M records.
- ❌ **Single-Tenant Index Explosion**: Creating thousands of separate collections/indexes for micro-tenants, leading to massive memory fragmentation and file handle exhaustion.
- ❌ **Ignoring Distance Metric Alignment**: Using `Cosine` similarity on vectors that are not normalized, or using `L2` (Euclidean) on embeddings trained strictly for `Dot Product` (e.g., OpenAI embeddings).

---

## 4. Production Code Implementations

### A. Qdrant (Python) - High Performance Collection Setup & Hybrid Search

```python
from qdrant_client import QdrantClient, models

client = QdrantClient(url="http://localhost:6333", timeout=30.0)

COLLECTION_NAME = "enterprise_knowledge_base"

# 1. Create Collection with HNSW + Scalar Quantization + On-Disk Storage
if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=1536,
            distance=models.Distance.COSINE,
            on_disk=True  # Keep raw vectors on disk
        ),
        hnsw_config=models.HnswConfigDiff(
            m=16,
            ef_construct=128,
            on_disk=False  # Keep graph index in memory for fast traversal
        ),
        quantization_config=models.ScalarQuantization(
            scalar_quantization=models.ScalarQuantizationConfig(
                type=models.ScalarType.INT8,
                quantile=0.99,
                always_ram=True  # Load quantized vectors into RAM
            )
        )
    )

# 2. Create Payload Index for Tenant Filtering
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="tenant_id",
    field_schema=models.PayloadSchemaType.KEYWORD
)

# 3. Filtered ANN Search Query
def search_knowledge_base(tenant_id: str, query_vector: list[float], limit: int = 10):
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="tenant_id",
                    match=models.MatchValue(value=tenant_id)
                )
            ]
        ),
        search_params=models.SearchParams(
            hnsw_ef=64,  # Dynamic precision at query time
            exact=False
        ),
        limit=limit
    )
    return results
```

### B. Milvus (Python) - Dynamic Schema & IVF_SQ8 / HNSW Indexing

```python
from pymilvus import (
    connections, FieldSchema, CollectionSchema, DataType, Collection, utility
)

connections.connect("default", host="localhost", port="19530")

COLLECTION_NAME = "rag_documents"

# 1. Define Schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="tenant_id", dtype=DataType.VARCHAR, max_length=64),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
]
schema = CollectionSchema(fields, description="RAG Document Vectors", enable_dynamic_field=True)

collection = Collection(name=COLLECTION_NAME, schema=schema)

# 2. Create Vector Index (HNSW)
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {"M": 16, "efConstruction": 200}
}
collection.create_index(field_name="embedding", index_params=index_params)

# 3. Create Scalar Index for Metadata Filtering
collection.create_index(field_name="tenant_id", index_name="tenant_idx")

# 4. Load Collection to Memory & Search
collection.load()

query_embedding = [0.01] * 768
search_params = {"metric_type": "COSINE", "params": {"ef": 64}}

results = collection.search(
    data=[query_embedding],
    anns_field="embedding",
    param=search_params,
    limit=5,
    expr='tenant_id == "tenant_alpha"',
    output_fields=["tenant_id"]
)
```

### C. Pinecone (Node.js / TypeScript) - Serverless Setup with Metadata Filtering

```typescript
import { Pinecone } from '@pinecone-database/pinecone';

const pc = new Pinecone({ apiKey: process.env.PINECONE_API_KEY! });
const INDEX_NAME = 'production-rag-index';

async function queryTenantData(tenantId: string, vector: number[]) {
  const index = pc.index(INDEX_NAME);

  // Perform query isolated by namespace or metadata filter
  const queryResponse = await index.namespace('document-workspace').query({
    vector: vector,
    topK: 10,
    includeMetadata: true,
    filter: {
      tenant_id: { $eq: tenantId },
      category: { $in: ['engineering', 'architecture'] }
    }
  });

  return queryResponse.matches;
}
```
