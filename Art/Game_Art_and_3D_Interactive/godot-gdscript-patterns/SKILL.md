---
name: godot-gdscript-patterns
description: Enterprise architecture patterns for Godot Engine 4.x using GDScript and C#, Node tree composition, Custom Resources, Signal Bus patterns, Direct Server APIs (PhysicsServer, RenderingServer), memory management, and performance profiling.
---

# Godot Engine 4.x GDScript Architecture & Patterns

This skill guide provides production-grade architectural patterns, memory management protocols, Node composition strategies, frame budget optimizations, and direct Server API patterns for Godot Engine 4.x applications using GDScript.

---

## 1. Architectural Patterns & Node Composition

### 1.1 Composition over Inheritance (Node Pattern)
In Godot 4.x, avoid deep class inheritance trees (`CharacterBody3D` -> `LivingEntity` -> `Humanoid` -> `Player`). Instead, use small, modular, self-contained `Node` components attached to entity roots:

```
Player (CharacterBody3D)
├── HealthComponent (Node)
├── HitboxComponent (Area3D)
├── InventoryComponent (Node)
└── StateMachine (Node)
    ├── IdleState (Node)
    └── MoveState (Node)
```

### 1.2 Custom Resource-Driven Architecture
Godot `Resource` objects represent scriptable data containers. Leverage Resources for:
* Shared immutable configuration (Item definitions, Ability stats).
* Decoupled state persistence (Save games, UI models).
* Modular behavior strategies (Custom AI behavior algorithms passed as Resource references).

### 1.3 Signal Bus Pattern (Global Event Conduit)
Decouple disparate systems (e.g., Combat System triggering UI Score Updates) using an Autoload Signal Bus rather than direct node references.

```
[ Combat System ] ---> emits signal ---> [ Global SignalBus (Autoload) ]
                                                    |
                                                    v
                                         [ UI Score Display Listener ]
```

---

## 2. Memory Management & Lifecycle Protocols

### 2.1 Object Types: `RefCounted` vs. `Node` / `Object`

| Class Type | Memory Strategy | Lifecycle Method | Allocation Overhead |
| :--- | :--- | :--- | :--- |
| `RefCounted` | Automatic Reference Counting | Replaced when reference count hits zero. | Very Low |
| `Node` / `Object` | Manual Garbage Management | **Must** call `queue_free()` or `free()`. | High (Node tree overhead) |

> **Critical Rule**: Always call `queue_free()` when removing Nodes from scene trees to prevent memory leaks. Use `free()` only on raw non-Node `Object` instances.

### 2.2 Array & Dictionary Memory Optimization
GDScript untyped arrays (`[]`) store variants incurring dynamic boxing allocations. In hot loops, always use **Typed Arrays** or **Packed Arrays**:

```gdscript
# BAD: Dynamic variant boxing allocation overhead
var raw_points: Array = []

# GOOD: Contiguous memory block, zero-boxing primitive arrays
var packed_points: PackedVector3Array = PackedVector3Array()
var typed_nodes: Array[Node3D] = []
```

### 2.3 Cyclic Reference Leaks in `RefCounted`
If two `RefCounted` instances hold strong references to each other, their reference counts will never drop to zero.
* **Solution**: Break circular references using `weakref(object)` or explicit `cleanup()` methods before release.

---

## 3. Frame Budget & Direct Server APIs

### 3.1 `_process` vs `_physics_process` Optimization
* `_process(delta)`: Tied to render frame rate. Use **only** for visual interpolations and non-physics UI state updates.
* `_physics_process(delta)`: Fixed step rate (default 60Hz). Use for all physics body manipulation and spatial state queries.
* **Optimization**: Disable processing on idle nodes: `set_process(false)` / `set_physics_process(false)`.

### 3.2 Direct Server APIs (`PhysicsServer3D` & `RenderingServer`)
When rendering or simulating tens of thousands of objects (bullets, vegetation, crowd agents), bypass Godot Node Tree overhead entirely using Direct Server APIs:

```
[ Node Tree Approach ]: 10,000 Nodes = 10,000 Object Headers + Scene Graph Overhead (Lag)
[ Server API Approach ]: Single Manager Node + Direct RenderingServer Rendering Calls (60+ FPS)
```

---

## 4. Production Code Examples

### 4.1 Production Global Signal Bus (Autoload)
`SignalBus.gd` registered in Project Settings Autoloads:

```gdscript
class_name SignalBus
extends Node

## Centralized Event Bus for application-wide decoupled communication

# Gameplay Signals
signal player_health_changed(current_health: float, max_health: float)
signal entity_spawn_requested(scene_res: PackedScene, transform: Transform3D)

# Inventory Signals
signal item_picked_up(item_id: StringName, amount: int)

func emit_player_health_changed(current_health: float, max_health: float) -> void:
	player_health_changed.emit(current_health, max_health)

func emit_entity_spawn_requested(scene_res: PackedScene, transform: Transform3D) -> void:
	entity_spawn_requested.emit(scene_res, transform)
```

### 4.2 Node-Based Finite State Machine (FSM)
Implementation of clean state transitions using Node composition:

#### `State.gd` (Base Class)
```gdscript
class_name State
extends Node

signal transitioned(state_name: StringName)

func enter() -> void:
	pass

func exit() -> void:
	pass

func update(_delta: float) -> void:
	pass

func physics_update(_delta: float) -> void:
	pass
```

#### `StateMachine.gd` (Controller)
```gdscript
class_name StateMachine
extends Node

@export var initial_state: State

private var _current_state: State
private var _states: Dictionary = {}

func _ready() -> void:
	await owner.ready
	
	for child in get_children():
		if child is State:
			_states[child.name.StringName()] = child
			child.transitioned.connect(_on_state_transitioned)

	if initial_state:
		_current_state = initial_state
		_current_state.enter()

func _process(delta: float) -> void:
	if _current_state:
		_current_state.update(delta)

func _physics_process(delta: float) -> void:
	if _current_state:
		_current_state.physics_update(delta)

func _on_state_transitioned(new_state_name: StringName) -> void:
	var new_state: State = _states.get(new_state_name)
	if not new_state or new_state == _current_state:
		return

	if _current_state:
		_current_state.exit()

	_current_state = new_state
	_current_state.enter()
```

### 4.3 High-Performance Direct `RenderingServer` Bullet Particle System
Rendering 20,000 particle instances bypassing Node instances:

```gdscript
class_name ServerParticleRenderer
extends Node3D

@export var mesh: Mesh
@export var count: int = 10000

private var _multimesh_rid: RID
private var _instance_rid: RID

func _ready() -> void:
	# Create MultiMesh via RenderingServer directly
	_multimesh_rid = RenderingServer.multimesh_create()
	RenderingServer.multimesh_allocate_data(_multimesh_rid, count, RenderingServer.MULTIMESH_TRANSFORM_3D)
	RenderingServer.multimesh_set_mesh(_multimesh_rid, mesh.get_rid())

	# Attach MultiMesh instance to current world RID
	_instance_rid = RenderingServer.instance_create()
	RenderingServer.instance_set_base(_instance_rid, _multimesh_rid)
	RenderingServer.instance_set_scenario(_instance_rid, get_world_3d().scenario)

	# Batch update instance transforms in memory
	_populate_particles()

func _populate_particles() -> void:
	var xform: Transform3D = Transform3D.IDENTITY
	for i in range(count):
		xform.origin = Vector3(
			randf_range(-50.0, 50.0),
			randf_range(0.0, 20.0),
			randf_range(-50.0, 50.0)
		)
		RenderingServer.multimesh_instance_set_transform(_multimesh_rid, i, xform)

func _exit_tree() -> void:
	# Manual cleanup of Server Resource IDs (RIDs)
	if _instance_rid.is_valid():
		RenderingServer.free_rid(_instance_rid)
	if _multimesh_rid.is_valid():
		RenderingServer.free_rid(_multimesh_rid)
```

---

## 5. Anti-Patterns & Critical Pitfalls

### ❌ Anti-Pattern 1: Un-Cached Node Searches in `_process`
```gdscript
# WRONG: Executes scene tree search every single frame (High CPU bottleneck)
func _process(_delta: float) -> void:
	get_node("../UI/Label").text = str(score)
	$Player/AnimationPlayer.play("idle")

# RIGHT: Use @onready caching or exported node paths
@onready private var score_label: Label = $"../UI/Label"
@onready private var anim_player: AnimationPlayer = $Player/AnimationPlayer

func _process(_delta: float) -> void:
	score_label.text = str(score)
```

### ❌ Anti-Pattern 2: Memory Leaks via `remove_child()` Without `queue_free()`
```gdscript
# WRONG: Removing node from scene tree does NOT delete it from memory!
func remove_enemy(enemy: Node) -> void:
	remove_child(enemy) # Node remains orphaned in RAM!

# RIGHT: Explicitly queue node for memory freeing
func remove_enemy(enemy: Node) -> void:
	remove_child(enemy)
	enemy.queue_free()
```

### ❌ Anti-Pattern 3: Over-relying on Singletons / Autoloads for Model State
Avoid using Autoload singletons as monolithic global variable dumps. Store game configuration data in `Resource` objects and inject them into components to preserve unit testability and scene isolation.
---
