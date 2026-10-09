---
name: redis-caching-and-pubsub
description: Architecting high-performance caching strategies, Cache-Aside/Write-Through/Write-Behind patterns, Redis Pub/Sub, Streams, eviction policies, distributed locking (Redlock), and memory optimization. Use when implementing Redis caching, real-time messaging, rate limiting, or session management.
---

# Redis Caching & Pub/Sub Architecture Guide

Production-grade guide for designing, implementing, and scaling Redis as a high-performance cache, session store, real-time pub/sub message broker, and distributed coordinator.

---

## 1. Caching Strategies & Design Patterns

### 1.1 Cache-Aside (Lazy Loading)
The application reads from the cache first. On a cache miss, it reads from the primary database, updates the cache, and returns the result.

```
+-------------+      1. Read Key      +-------+
| Application | --------------------> | Cache |
|             | <-------------------- |       |
+-------------+     2. Cache Hit      +-------+
       |
       | 3. Cache Miss
       v
+---------------+
| Primary DB    |
+---------------+
```

* **Best For**: Read-heavy workloads with unpredictable access patterns.
* **Trade-off**: Stale data risk if DB writes don't invalidate/update cache; higher latency on cache miss.

### 1.2 Write-Through Caching
The application writes data directly to the cache, and the cache synchronously writes to the database.

* **Best For**: Mission-critical reads where cache staleness cannot be tolerated.
* **Trade-off**: Higher write latency; potential cache pollution with infrequently read data.

### 1.3 Write-Behind (Write-Back) Caching
The application writes to the cache immediately, and an asynchronous process flushes cache updates to the underlying DB in batches.

* **Best For**: Write-heavy systems (e.g., analytics, metrics aggregators, counter updates).
* **Trade-off**: Risk of data loss if Redis crashes before flushing to primary DB.

### 1.4 Cache Stampede (Thundering Herd) Mitigation
When a popular cache key expires, thousands of concurrent requests hit the backend database simultaneously.

#### Solution A: Distributed Mutex / Lock
Acquire a lock to recompute the cache value; force other concurrent requests to wait or return stale data.

#### Solution B: Probabilistic Early Expiration (XFetch Algorithm)
As a key nears expiration, probabilistically refresh it in the background before it expires.

$$\Delta - \beta \cdot \ln(\text{rand}()) > \text{TTL}$$

---

## 2. Redis Data Structures & Scalable Usage Patterns

| Data Structure | Primary Use Cases | Recommended Max Size / Rule |
| :--- | :--- | :--- |
| **Strings** | Simple key-value, HTML fragments, JSON payloads, counters (`INCRBY`) | Limit single string value to $< 100\text{ KB}$ |
| **Hashes** | User objects, entity fields, session attributes | Use fields instead of JSON strings for partial updates |
| **Sets** | Unique tags, IP blacklists, mutual friends, deduplication | Max set size $< 10,000$ members for fast bulk operations |
| **Sorted Sets (ZSET)** | Leaderboards, rate limit sliding windows, priority queues | High efficiency ($O(\log N)$ inserts/searches) |
| **HyperLogLog** | Unique visitor counting (Cardinality estimation) | Constant $12\text{ KB}$ footprint with $0.81\%$ standard error |
| **Bitmaps** | User daily active status, feature toggles | $512\text{ MB}$ max space = $4.29$ billion flags |
| **Streams** | Append-only event logs, persistent pub/sub, message processing queues | Use `XADD` with explicit trimming (`MAXLEN ~ 10000`) |

---

## 3. Real-Time Messaging: Pub/Sub vs. Streams

### Pub/Sub (At-Most-Once)
* **Behavior**: Fire-and-forget message delivery. Messages are not persisted. If a subscriber is disconnected during publication, the message is lost.
* **Use Cases**: Live UI updates, websocket notifications, ephemeral chat messages.

### Redis Streams (At-Least-Once)
* **Behavior**: Append-only log with Consumer Groups, message ACK, pending entry lists (PEL), and replay capability.
* **Use Cases**: Async task processing, distributed event sourcing, reliable messaging workflows.

```typescript
// Redis Streams Consumer Group Pattern (TypeScript Example)
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL!);
const STREAM_KEY = 'events:orders';
const GROUP_NAME = 'order-processing-group';
const CONSUMER_NAME = `worker-${process.pid}`;

async function initializeStreamGroup() {
  try {
    await redis.xgroup('CREATE', STREAM_KEY, GROUP_NAME, '$', 'MKSTREAM');
  } catch (err: any) {
    if (!err.message.includes('BUSYGROUP')) throw err;
  }
}

async function processOrderEvents() {
  await initializeStreamGroup();

  while (true) {
    // Read up to 10 new unconsumed messages for this group
    const results = await redis.xreadgroup(
      'GROUP', GROUP_NAME, CONSUMER_NAME,
      'BLOCK', 2000,
      'COUNT', 10,
      'STREAMS', STREAM_KEY, '>'
    ) as any;

    if (!results) continue;

    for (const [stream, messages] of results) {
      for (const [id, fields] of messages) {
        try {
          const payload = JSON.parse(fields[1]);
          await handleOrderEvent(payload);
          // Acknowledge successful processing
          await redis.xack(STREAM_KEY, GROUP_NAME, id);
        } catch (error) {
          console.error(`Failed to process message ${id}:`, error);
          // Failed messages remain in PEL for retry/dead-letter inspection
        }
      }
    }
  }
}
```

---

## 4. Distributed Locking (Redlock & Atomic Lua)

### Single Instance Atomic Locking with Renewal & Release

To safely acquire and release locks, use a cryptographically random token and release via Lua script to avoid releasing another client's lock.

```typescript
import Redis from 'ioredis';
import { randomBytes } from 'crypto';

export class RedisDistributedLock {
  private redis: Redis;

  constructor(redisClient: Redis) {
    this.redis = redisClient;
  }

  /**
   * Acquire a distributed lock.
   */
  async acquire(key: string, ttlMs: number): Promise<string | null> {
    const lockToken = randomBytes(16).toString('hex');
    const acquired = await this.redis.set(
      `lock:${key}`,
      lockToken,
      'PX',
      ttlMs,
      'NX'
    );
    return acquired === 'OK' ? lockToken : null;
  }

  /**
   * Release lock safely using an atomic Lua script.
   */
  async release(key: string, lockToken: string): Promise<boolean> {
    const luaScript = `
      if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
      else
        return 0
      end
    `;
    const result = await this.redis.eval(luaScript, 1, `lock:${key}`, lockToken);
    return result === 1;
  }
}
```

---

## 5. Eviction Policies & Memory Tuning

### Redis Eviction Policies (`maxmemory-policy`)

1. **`volatile-lru`**: Evict keys with an explicit expiration using Least Recently Used algorithm.
2. **`allkeys-lru`**: Recommended for general caching. Evicts any key based on LRU regardless of TTL.
3. **`volatile-lfu` / `allkeys-lfu`**: Evicts based on Least Frequently Used frequency counters.
4. **`noeviction`**: Returns Out-Of-Memory errors on writes when limit is reached. Required when Redis acts as a primary database.

### Memory Optimization Rules
* Set `maxmemory` explicitly (e.g., $75\%$ of total instance RAM) to leave overhead for replication buffers and BGSAVE copy-on-write fork allocation.
* Enable **Listpack / Ziplist** encoding for small Hashes and Sets:
  ```ini
  hash-max-listpack-entries 512
  hash-max-listpack-value 64
  ```

---

## 6. Anti-Patterns & Production Pitfalls

* ❌ **Running `KEYS *` in Production**: Blocks single-threaded Redis execution loop. **Use `SCAN`** with cursor iteration instead.
* ❌ **Hot Key Bottlenecks**: Single key accessed by thousands of app instances concurrently causing network NIC saturation. *Fix: Implement local in-memory L1 cache (e.g., LRU cache) alongside Redis L2.*
* ❌ **Big Keys ($> 10\text{ MB}$ collections/strings)**: Unlinking/deleting large collections causes latency spikes. **Use `UNLINK`** instead of `DEL` for async garbage collection.
* ❌ **Missing Key Namespaces**: Keys without structured prefixes leads to collisions and unsafe bulk flush actions. *Pattern: `app:domain:entity:id` (e.g., `shop:user:profile:10948`).*
* ❌ **Unbounded Collection Growth**: Sets, Lists, or Hashes left to grow indefinitely without TTLs or trimming logic.
