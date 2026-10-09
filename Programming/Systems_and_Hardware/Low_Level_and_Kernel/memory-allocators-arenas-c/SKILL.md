---
name: memory-allocators-arenas-c
metadata:
  category: Low-Level Systems Drivers and Kernel
description: Design, implement, and verify high-performance custom memory allocators in C and C++. Build Arena / Bump allocators, Pool / Fixed-size block allocators, and Free-List allocators. Ensure strict hardware memory alignment (alignof, power-of-two boundaries), zero-fragmentation lifecycles, and cache line locality. Trigger when building game engines, high-frequency trading (HFT) engines, or embedded runtime systems.
compatibility: C99 / C11, C++17, POSIX / Windows memory primitives
---

# Custom Memory Allocators & Arenas Skill Guide

This skill specifies algorithms, pointer arithmetic patterns, and hardware alignment requirements for implementing zero-overhead custom memory allocators in C and C++.

---

## 1. Allocator Topologies & Trade-offs

```text
+-----------------------+-----------------------+-----------------------+
| Allocator Type        | Allocation Time       | Deallocation Strategy |
+-----------------------+-----------------------+-----------------------+
| Arena (Bump)          | O(1) pointer addition | O(1) Reset all at once|
| Pool (Fixed-Size)     | O(1) pop free-list    | O(1) push free-list   |
| Free-List (Segregated)| O(N) or O(log N)      | Coalesce adjacent free|
+-----------------------+-----------------------+-----------------------+
```

---

## 2. Production C Implementation: Arena & Pool Allocators

### A. High-Performance Hardware-Aligned Arena Allocator

```c
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>

#define DEFAULT_ALIGNMENT (sizeof(void*))

typedef struct {
    uint8_t *buffer;
    size_t capacity;
    size_t offset;
    size_t prev_offset;
} MemoryArena;

static inline uintptr_t align_forward(uintptr_t ptr, size_t alignment) {
    assert((alignment & (alignment - 1)) == 0 && "Alignment must be power of two");
    uintptr_t a = (uintptr_t)alignment;
    return (ptr + a - 1) & ~(a - 1);
}

void arena_init(MemoryArena *arena, void *backing_buffer, size_t capacity) {
    arena->buffer = (uint8_t*)backing_buffer;
    arena->capacity = capacity;
    arena->offset = 0;
    arena->prev_offset = 0;
}

void *arena_alloc_aligned(MemoryArena *arena, size_t size, size_t alignment) {
    uintptr_t current_ptr = (uintptr_t)arena->buffer + (uintptr_t)arena->offset;
    uintptr_t aligned_ptr = align_forward(current_ptr, alignment);
    size_t padding = aligned_ptr - current_ptr;

    if (arena->offset + padding + size > arena->capacity) {
        return NULL; // Out of memory
    }

    arena->prev_offset = arena->offset;
    arena->offset += padding + size;

    return (void*)aligned_ptr;
}

void *arena_alloc(MemoryArena *arena, size_t size) {
    return arena_alloc_aligned(arena, size, DEFAULT_ALIGNMENT);
}

void arena_reset(MemoryArena *arena) {
    // Instant O(1) deallocation of all allocated memory
    arena->offset = 0;
    arena->prev_offset = 0;
}
```

### B. Fixed-Size Block Pool Allocator

```c
typedef struct PoolFreeNode {
    struct PoolFreeNode *next;
} PoolFreeNode;

typedef struct {
    uint8_t *buffer;
    size_t block_size;
    size_t capacity;
    PoolFreeNode *free_list;
} MemoryPool;

void pool_init(MemoryPool *pool, void *backing_buffer, size_t total_size, size_t block_size) {
    assert(block_size >= sizeof(PoolFreeNode) && "Block size must fit free node pointer");
    pool->buffer = (uint8_t*)backing_buffer;
    pool->block_size = block_size;
    pool->capacity = total_size;
    pool->free_list = NULL;

    // Chain all blocks into the free list
    size_t num_blocks = total_size / block_size;
    for (size_t i = 0; i < num_blocks; ++i) {
        PoolFreeNode *node = (PoolFreeNode*)(pool->buffer + (i * block_size));
        node->next = pool->free_list;
        pool->free_list = node;
    }
}

void *pool_alloc(MemoryPool *pool) {
    if (!pool->free_list) {
        return NULL; // Pool exhausted
    }
    PoolFreeNode *node = pool->free_list;
    pool->free_list = node->next;
    return (void*)node;
}

void pool_free(MemoryPool *pool, void *ptr) {
    if (!ptr) return;
    PoolFreeNode *node = (PoolFreeNode*)ptr;
    node->next = pool->free_list;
    pool->free_list = node;
}
```

---

## 3. Best Practices & Hardware Guidelines

1. **Power-of-Two Alignment:** Always enforce that alignments are powers of two (`(align & (align - 1)) == 0`).
2. **Cache Line Locality:** For high-throughput structs, align to 64 bytes (`alignas(64)`) to avoid false sharing across CPU cores.
3. **Double Free Elimination:** Arena allocators completely eliminate individual double-free and memory fragmentation bugs because memory is only reclaimed en masse.
