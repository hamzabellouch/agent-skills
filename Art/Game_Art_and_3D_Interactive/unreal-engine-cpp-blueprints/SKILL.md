---
name: unreal-engine-cpp-blueprints
description: Production guidance for Unreal Engine C++ and Blueprints hybrid architecture, UObject memory management, Unreal Smart Pointers, Gameplay Ability System (GAS), Subsystems, Task Graph multithreading, and performance optimization.
---

# Unreal Engine C++ & Blueprints Architecture

This skill guide provides production-grade architectural patterns, memory management protocols, C++/Blueprint boundary rules, frame budget optimization techniques, and multi-threading patterns for Unreal Engine applications.

---

## 1. C++ vs. Blueprint Architectural Boundaries

### 1.1 Division of Responsibilities
To maintain performance and maintainability in large scale AAA codebases, follow strict layer isolation:

```
+-------------------------------------------------------------------+
|                        Blueprint Layer                            |
|  - Visual Tweaking & Cosmetic Properties (Materials, FX, Audio)   |
|  - UI Widget Event Hooks (UMG Data Bindings)                      |
|  - Level-Specific Scripting & Animation Blueprint Blending        |
+-------------------------------------------------------------------+
                                  ^
                                  | Exposes UPROPERTY / UFUNCTION
                                  v
+-------------------------------------------------------------------+
|                           C++ Engine Layer                        |
|  - Math & Heavy Computations (Spatial Queries, Pathing, Physics)  |
|  - Core Data Structures & Base Classes (ACharacter, UActorComponent)|
|  - Networking & RPC Serialization (Replication Logic)             |
|  - Subsystems, GAS AttributeSets, and Task Graph Multithreading   |
+-------------------------------------------------------------------+
```

### 1.2 Subsystem Architecture
Unreal Engine Subsystems (`UGameInstanceSubsystem`, `UWorldSubsystem`, `ULocalPlayerSubsystem`) provide managed singletons tied automatically to object lifecycles without manual instance creation or teardown.

### 1.3 Gameplay Ability System (GAS) Setup
Keep GAS core logic strictly in C++:
* **`UAbilitySystemComponent`**: Attach via base C++ classes (`ACharacter`).
* **`UAttributeSet`**: Define all attributes, clamping logic (`PreAttributeChange`, `PostGameplayEffectExecute`), and network replication macros in C++.
* **`UGameplayAbility`**: Implement complex execution calculations in C++; subclass in Blueprints only for montage timing and FX triggers.

---

## 2. Memory Management & Garbage Collection

### 2.1 UObject Ownership & `UPROPERTY()` GC Sweeps
Unreal Engine uses a reflection-driven Garbage Collection system. Any `UObject` raw pointer **must** be tracked by the GC framework, otherwise it risks premature collection or dangling pointer crashes.

```cpp
// CRITICAL: Prevent GC sweep of instantiated UObject
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Inventory")
TObjectPtr<UInventoryItemAsset> CachedItem;
```

### 2.2 Unreal Smart Pointers vs UObject Weak References

| Pointer Type | Target Object Type | Use Case | GC Tracked? |
| :--- | :--- | :--- | :--- |
| `TObjectPtr<T>` | `UObject` subclasses | Standard member variables in headers. | Yes (`UPROPERTY`) |
| `TWeakObjectPtr<T>` | `UObject` subclasses | Non-owning reference to UObjects (prevents circular retention). | No (GC-safe query) |
| `TSharedPtr<T>` | Non-`UObject` C++ structs | Engine-agnostic C++ data structures. | Ref-counted |
| `TSharedRef<T>` | Non-`UObject` C++ structs | Non-nullable shared pointer reference. | Ref-counted |
| `TUniquePtr<T>` | Non-`UObject` C++ structs | Exclusive ownership raw C++ memory management. | Manual / Scope |

### 2.3 Container Allocation Strategy & Slack Management
Unreal's `TArray<T>` dynamically reallocates memory upon expansion. Avoid heap fragmentation during execution loops:

```cpp
// Reserve slack before populating large arrays
TArray<FVector> PathNodes;
PathNodes.Reserve(1000); // Allocates memory block upfront

// Fast clear without freeing allocated memory block for frame reuse
PathNodes.Reset(); // Keeps memory slack intact
// PathNodes.Empty(); // WRONG: Frees memory block to heap!
```

---

## 3. Frame Budget & Multithreading

### 3.1 Tick Management & Optimization Rules
By default, `AActor::Tick` is enabled, causing high overhead across thousands of actors.

1. **Disable Unnecessary Ticks**: Set `PrimaryActorTick.bCanEverTick = false;` in constructor.
2. **Tick Interval**: For non-critical logic, set `PrimaryActorTick.TickInterval = 0.1f;` (10Hz instead of frame-rate).
3. **Tick Groups**: Assign tick dependency groups (`TG_PrePhysics`, `TG_DuringPhysics`, `TG_PostPhysics`) to ensure data availability without frame stalls.

### 3.2 Threading with Task Graph & ParallelFor
For heavy compute tasks (e.g., procedural mesh generation, pathing algorithms), offload work from the Game Thread:

```cpp
// Multi-threaded loop execution across CPU worker threads
ParallelFor(1000, [](int32 Index)
{
    // Thread-safe math operations on non-UObject data arrays
    ProcessRaycastPoint(Index);
});
```

---

## 4. Production Code Examples

### 4.1 Production UGameInstanceSubsystem with Async Soft Loading
A production manager tracking game state and asynchronously loading data assets using soft object references (`TSoftObjectPtr`):

#### `InventorySubsystem.h`
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Engine/StreamableManager.h"
#include "InventorySubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnItemLoadedDelegate, UPrimaryDataAsset*, LoadedAsset);

UCLASS()
class GAMEENGINE_API UInventorySubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "Inventory")
    void RequestAsyncAssetLoad(TSoftObjectPtr<UPrimaryDataAsset> AssetToLoad);

    UPROPERTY(BlueprintAssignable, Category = "Inventory")
    FOnItemLoadedDelegate OnItemLoaded;

private:
    void OnAssetLoadComplete(TSoftObjectPtr<UPrimaryDataAsset> LoadedSoftPtr);

    FStreamableManager StreamableManager;
};
```

#### `InventorySubsystem.cpp`
```cpp
#include "InventorySubsystem.h"
#include "Engine/AssetManager.h"

void UInventorySubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
}

void UInventorySubsystem::Deinitialize()
{
    Super::Deinitialize();
}

void UInventorySubsystem::RequestAsyncAssetLoad(TSoftObjectPtr<UPrimaryDataAsset> AssetToLoad)
{
    if (AssetToLoad.IsNull())
    {
        return;
    }

    if (AssetToLoad.IsValid())
    {
        // Already in memory
        OnItemLoaded.Broadcast(AssetToLoad.Get());
        return;
    }

    // Initiate async streamable load
    FSoftObjectPath AssetPath = AssetToLoad.ToSoftObjectPath();
    StreamableManager.RequestAsyncLoad(
        AssetPath,
        FStreamableDelegate::CreateUObject(this, &UInventorySubsystem::OnAssetLoadComplete, AssetToLoad)
    );
}

void UInventorySubsystem::OnAssetLoadComplete(TSoftObjectPtr<UPrimaryDataAsset> LoadedSoftPtr)
{
    if (LoadedSoftPtr.IsValid())
    {
        OnItemLoaded.Broadcast(LoadedSoftPtr.Get());
    }
}
```

### 4.2 Thread-Safe C++ Task Graph Execution
Scheduling background jobs using `FFunctionGraphTask`:

```cpp
#include "Async/TaskGraphInterfaces.h"

void AGameSpatialGrid::ComputeGridAsync()
{
    // Capture data by value/shared ptr for thread safety
    TSharedPtr<TArray<FVector>, ESPMode::ThreadSafe> InputData = MakeShared<TArray<FVector>, ESPMode::ThreadSafe>();
    InputData->Reserve(5000);

    FFunctionGraphTask::CreateAndDispatchWhenReady([InputData]()
    {
        // Executed on Background Worker Thread
        for (int32 i = 0; i < 5000; ++i)
        {
            InputData->Add(FVector(i * 10.0f, i * 20.0f, 0.0f));
        }

        // Return back to Game Thread for application to UObjects
        FFunctionGraphTask::CreateAndDispatchWhenReady([InputData]()
        {
            // Executed back on Main Game Thread
            GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Green, 
                FString::Printf(TEXT("Async Compute Complete: %d elements"), InputData->Num()));
        }, TStatId(), nullptr, ENamedThreads::GameThread);

    }, TStatId(), nullptr, ENamedThreads::AnyBackgroundThreadNormalTask);
}
```

### 4.3 Robust C++ Base Class with Blueprint Native Events

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "InteractableInterface.h"
#include "BaseInteractable.generated.h"

UCLASS(Abstract, Blueprintable)
class GAMEENGINE_API ABaseInteractable : public AActor, public IInteractableInterface
{
    GENERATED_BODY()
    
public:	
    ABaseInteractable();

    // BlueprintNativeEvent provides C++ default implementation with Blueprint override capability
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "Interaction")
    bool ExecuteInteraction(APawn* InteractingPawn);
    virtual bool ExecuteInteraction_Implementation(APawn* InteractingPawn);

protected:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Interaction")
    FText InteractionPrompt;
};
```

---

## 5. Anti-Patterns & Critical Pitfalls

### ❌ Anti-Pattern 1: Un-Reflected UObject Raw Pointers
```cpp
// WRONG: Missing UPROPERTY() causes Garbage Collector to delete object mid-gameplay
class AMyCharacter : public ACharacter
{
    UEnemyManager* EnemyManager; // Raw un-tracked pointer! DANGER!
};

// RIGHT: Always wrap with UPROPERTY() or TWeakObjectPtr
class AMyCharacter : public ACharacter
{
    UPROPERTY()
    TObjectPtr<UEnemyManager> EnemyManager;
};
```

### ❌ Anti-Pattern 2: Hard Object References in Class Headers
```cpp
// WRONG: Hard asset references cause full dependency trees to load synchronously into memory
UPROPERTY(EditAnywhere)
UTexture2D* HeavyBossTexture; // Synchronously loaded on parent load!

// RIGHT: Use TSoftObjectPtr for lazy/async loading
UPROPERTY(EditAnywhere)
TSoftObjectPtr<UTexture2D> HeavyBossTexture;
```

### ❌ Anti-Pattern 3: Heavy Logic inside Blueprint Tick
Placing raycasts, string operations, or `GetAllActorsOfClass` in Blueprint `Event Tick` will ruin frame performance. Migrate heavy logic to C++ async tasks, custom timers (`FTimerManager`), or event-driven delegates.
---
