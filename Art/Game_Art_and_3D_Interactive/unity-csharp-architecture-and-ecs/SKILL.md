---
name: unity-csharp-architecture-and-ecs
description: Architectural patterns, Data-Oriented Technology Stack (DOTS), Unity ECS, Burst Compiler, C# Job System, memory management, zero-allocation C# patterns, and frame-budget optimization for high-performance Unity game development.
---

# Unity C# Architecture & Data-Oriented ECS

This skill guide provides production-grade architectural patterns, memory management protocols, frame budget optimization techniques, and data-oriented design patterns for Unity applications using C#, Unity DOTS (Entities, Burst, C# Job System), and ScriptableObject-driven systems.

---

## 1. Architectural Patterns

### 1.1 Data-Oriented Design (DOTS / ECS) vs Object-Oriented Component Design
High-performance Unity engines split responsibilities based on memory access patterns:
* **Object-Oriented (MonoBehaviour)**: Used for high-level lifecycle control, UI binding, scene bootstrapping, and editor tooling.
* **Data-Oriented (ECS / Entities)**: Used for mass data processing (particles, projectiles, crowd simulation, terrain processing, spatial queries) where cache layout determines performance.

```
+-------------------------------------------------------------------+
|                        MonoBehaviour Layer                        |
|   (Bootstrapping, UI Binding, Input Mapping, Authoring Components)  |
+-------------------------------------------------------------------+
                                  |
                   Baker System / Conversion World
                                  v
+-------------------------------------------------------------------+
|                        Unity DOTS ECS World                       |
|   Entity (ID) + IComponentData (Blittable) + ISystem (Burst-compiled) |
+-------------------------------------------------------------------+
```

### 1.2 ScriptableObject-Driven Architecture (Event Channels & Runtime Sets)
Decouple game systems without singletons using ScriptableObject event channels and runtime sets:
* **Event Channel**: ScriptableObjects acting as broadcast conduits. Subscribed listeners execute without direct reference to publishers.
* **Runtime Set**: ScriptableObjects holding dynamic lists of active game instances (e.g., active enemies, spatial triggers) avoiding `Object.FindObjectsOfType`.

### 1.3 Service Locator vs Dependency Injection
For MonoBehaviour-based systems:
* Use **VContainer** or **Zenject** for explicit compile-time dependency injection.
* Avoid generic untyped Service Locators that introduce hidden temporal dependencies during scene loads.

---

## 2. Memory Management & Cache Alignment

### 2.1 Native Container Lifecycle & Safety Handles
All Native collections (`NativeArray`, `NativeParallelHashMap`, `NativeList`, `NativeQueue`) require explicit allocation lifetime management:

| Allocator | Duration | Use Case |
| :--- | :--- | :--- |
| `Allocator.Temp` | Single frame (1 frame max) | Short-lived job inputs/outputs within a single method. |
| `Allocator.TempJob` | 4 frames max | Jobs spanning multiple frames; must be disposed upon completion. |
| `Allocator.Persistent` | Indefinite | Long-lived game state, spatial partition grids, resource pools. |

> **Rule**: Always pair `Allocator.Persistent` allocations with `Dispose()` in `OnDestroy()` or `OnStopRunning()`.

### 2.2 Cache Line Efficiency & Struct Packing
Cache lines on modern modern CPUs are **64 bytes**. Layout ECS structs sequentially (`[StructLayout(LayoutKind.Sequential)]`) and align data types from largest to smallest to eliminate padding bytes:

```csharp
// BAD: 24 bytes due to padding gaps
public struct UnalignedComponent : IComponentData
{
    public bool IsActive;    // 1 byte (+ 3 bytes padding)
    public double Priority;  // 8 bytes
    public byte Category;    // 1 byte (+ 3 bytes padding)
    public int Health;       // 4 bytes
}

// GOOD: 16 bytes tightly aligned
[StructLayout(LayoutKind.Sequential)]
public struct AlignedComponent : IComponentData
{
    public double Priority;  // 8 bytes
    public int Health;       // 4 bytes
    public bool IsActive;    // 1 byte
    public byte Category;    // 1 byte
    // 2 bytes automatic trailing padding to 8-byte boundary
}
```

### 2.3 Zero-Allocation C# Allocation Rules
To achieve zero Garbage Collection (GC) spikes in `Update()`:
1. **No LINQ**: Replaces all `System.Linq` queries with explicit loops or `NativeArray` operations.
2. **Struct Enumerators**: Implement custom `GetEnumerator()` returning value types for custom collections.
3. **ArrayPool<T>**: Utilize `System.Buffers.ArrayPool<T>.Shared` for transient array allocations.
4. **Lambda Pre-allocation**: Cache delegates/closures into static fields instead of passing inline lambdas.

---

## 3. Frame Budget & Job System Optimizations

### 3.1 Frame Time Budget Allocation (60 FPS = 16.66ms / 120 FPS = 8.33ms)

```
Total Frame Budget (16.66ms @ 60 FPS)
├── Input & Game Logic (Update): 3.0ms
├── Physics Simulation (FixedUpdate): 4.0ms
├── ECS Job Execution (Parallel Worker Threads): 6.0ms
└── Rendering Prep & Command Buffers (LateUpdate): 3.66ms
```

### 3.2 Burst Compiler Guidelines
To ensure `[BurstCompile]` compatibility:
* Use **only** blittable primitives, value types (`struct`), and `NativeContainer` pointers.
* No managed object references (`string`, `class`, `UnityEngine.Object`).
* Set `CompileSynchronously = true` on critical hot paths to avoid fallback un-burstified execution during domain reloads.

### 3.3 Structural Change Avoidance via EntityCommandBuffer (ECB)
Executing structural changes (creating entities, destroying entities, adding/removing components) invalidates archetype chunks and forces a **Sync Point**, stalling all job worker threads.

> **Solution**: Record structural commands into `EntityCommandBuffer.ParallelWriter` within jobs, then playback deferred commands on the main thread during designated system groups (`EndSimulationEntityCommandBufferSystem`).

---

## 4. Production Code Examples

### 4.1 Production-Grade Burst-Compiled ECS System (`ISystem`)
A complete high-performance spatial translation update system for a projectile population:

```csharp
using Unity.Burst;
using Unity.Collections;
using Unity.Entities;
using Unity.Mathematics;
using Unity.Transforms;

namespace GameEngine.Architecture.ECS
{
    public struct ProjectileData : IComponentData
    {
        public float3 Velocity;
        public float LifetimeRemaining;
        public float Damage;
    }

    [BurstCompile]
    public partial struct ProjectileUpdateSystem : ISystem
    {
        private EntityQuery _query;

        [BurstCompile]
        public void OnCreate(ref SystemState state)
        {
            _query = state.GetEntityQuery(
                ComponentType.ReadWrite<LocalTransform>(),
                ComponentType.ReadWrite<ProjectileData>()
            );
            state.RequireForUpdate(_query);
        }

        [BurstCompile]
        public void OnUpdate(ref SystemState state)
        {
            float deltaTime = state.WorldUnmanaged.Time.DeltaTime;
            
            var ecbSingleton = SystemAPI.GetSingleton<EndSimulationEntityCommandBufferSystem.Singleton>();
            EntityCommandBuffer ecb = ecbSingleton.CreateCommandBuffer(state.WorldUnmanaged);

            var job = new ProjectileMovementJob
            {
                DeltaTime = deltaTime,
                Ecb = ecb.AsParallelWriter()
            };

            state.Dependency = job.ScheduleParallel(state.Dependency);
        }

        [BurstCompile]
        private partial struct ProjectileMovementJob : IJobEntity
        {
            public float DeltaTime;
            public EntityCommandBuffer.ParallelWriter Ecb;

            // Executed in parallel across worker threads per chunk
            private void Execute(
                Entity entity,
                [EntityIndexInQuery] int sortIndex,
                ref LocalTransform transform,
                ref ProjectileData projectile)
            {
                transform.Position += projectile.Velocity * DeltaTime;
                projectile.LifetimeRemaining -= DeltaTime;

                if (projectile.LifetimeRemaining <= 0f)
                {
                    // Defer structural modification to ECB without stalling worker threads
                    Ecb.DestroyEntity(sortIndex, entity);
                }
            }
        }
    }
}
```

### 4.2 ScriptableObject Event Channel Pattern
A zero-allocation type-safe event broadcasting channel:

```csharp
using System;
using UnityEngine;

namespace GameEngine.Architecture.Events
{
    [CreateAssetMenu(fileName = "FloatEventChannel", menuName = "Architecture/Events/Float Event Channel")]
    public class FloatEventChannelSO : ScriptableObject
    {
        private Action<float> _onEventRaised;

        public void RaiseEvent(float value)
        {
            _onEventRaised?.Invoke(value);
        }

        public void Subscribe(Action<float> action)
        {
            _onEventRaised += action;
        }

        public void Unsubscribe(Action<float> action)
        {
            _onEventRaised -= action;
        }
    }
}
```

### 4.3 High-Performance Zero-GC Array Pool & Job Processing
Processing non-ECS arrays without allocations using `NativeArray` and `IJobParallelFor`:

```csharp
using Unity.Burst;
using Unity.Collections;
using Unity.Jobs;
using UnityEngine;

namespace GameEngine.Architecture.Jobs
{
    public class NativeBatchProcessor : MonoBehaviour
    {
        [SerializeField] private int elementCount = 100000;

        private NativeArray<Vector3> _positions;
        private NativeArray<Vector3> _velocities;

        private void Awake()
        {
            _positions = new NativeArray<Vector3>(elementCount, Allocator.Persistent);
            _velocities = new NativeArray<Vector3>(elementCount, Allocator.Persistent);
        }

        private void Update()
        {
            var job = new BatchPositionJob
            {
                DeltaTime = Time.deltaTime,
                Positions = _positions,
                Velocities = _velocities
            };

            JobHandle handle = job.Schedule(elementCount, 64);
            handle.Complete(); // Complete synchronously when required by rendering pipeline
        }

        private void OnDestroy()
        {
            if (_positions.IsCreated) _positions.Dispose();
            if (_velocities.IsCreated) _velocities.Dispose();
        }

        [BurstCompile]
        private struct BatchPositionJob : IJobParallelFor
        {
            public float DeltaTime;
            public NativeArray<Vector3> Positions;
            [ReadOnly] public NativeArray<Vector3> Velocities;

            public void Execute(int index)
            {
                Positions[index] += Velocities[index] * DeltaTime;
            }
        }
    }
}
```

---

## 5. Anti-Patterns & Critical Pitfalls

### ❌ Anti-Pattern 1: Managed References in `IComponentData`
```csharp
// WRONG: Adding managed types causes compiler errors or GC tracking overhead in ECS
public struct BadComponent : IComponentData
{
    public string TargetName; // Managed reference! Breaks Burst and memory layout
    public GameObject PrefabReference; // Managed reference!
}

// RIGHT: Use fixed-size byte buffers or Entity references
public struct GoodComponent : IComponentData
{
    public FixedString64Bytes TargetName;
    public Entity PrefabEntity;
}
```

### ❌ Anti-Pattern 2: Direct Structural Changes in Parallel Jobs
Calling `EntityManager.AddComponent()` or `EntityManager.DestroyEntity()` inside a parallel job causes dynamic archetype re-allocation, corrupting memory pointers read by concurrent threads. Always pass an `EntityCommandBuffer.ParallelWriter`.

### ❌ Anti-Pattern 3: Mid-Frame GC Allocs via String Concatenation & LINQ
```csharp
// WRONG: Allocates string objects and closures every frame in Update
void Update()
{
    var activeEnemies = _enemies.Where(e => e.IsAlive).ToList();
    uiText.text = "Enemies: " + activeEnemies.Count;
}

// RIGHT: Reuse non-allocating string buffers or FixedString
private readonly char[] _scoreBuffer = new char[32];
void Update()
{
    int count = GetActiveEnemyCount();
    // Use StringBuilder or direct custom number formatters without heap allocation
}
```
---
