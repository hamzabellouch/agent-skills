---
name: webgl-and-threejs-3d-experiences
description: Production WebGL & Three.js 3D experience architecture, custom GLSL shaders, memory management & GPU disposal pipelines, instanced rendering, performance optimization, and anti-patterns.
---

# WebGL & Three.js 3D Experiences Architecture Guide

## Core Architectural Principles

### 1. Scene Graph Architecture & Render Lifecycle
- **Unified Engine Class Pattern**: Enforce OOP or functional composition encapsulating `WebGLRenderer`, `Scene`, `PerspectiveCamera`, and RAF loop into a self-contained renderer manager.
- **Render Loop Delta Capping**: Always cap `clock.getDelta()` (e.g., `Math.min(delta, 0.1)`) to avoid physics explosion/teleportation during window unfocus or frame drops.
- **Pixel Ratio Guardrails**: Cap `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))` to prevent mobile GPUs from rendering native 4K/8K viewports at unusable framerates.

### 2. GPU Memory Management & Resource Lifecycle
- **Explicit Garbage Collection**: JavaScript GC does not manage VRAM allocated to WebGL buffers, textures, geometries, or render targets.
- **Disposal Traversal**: Recursively traverse scenes and call `.dispose()` on geometries, materials, textures, and render targets upon component unmount or scene switching.
- **Resource Pooling & Material Sharing**: Instantiation of geometries and materials must happen outside animation loops. Share materials across meshes wherever possible.

### 3. High-Performance WebGL Techniques
- **InstancedMesh**: Use `InstancedMesh` for rendering thousands of repetitive objects (particles, trees, debris) using single draw calls.
- **BVH (Bounding Volume Hierarchy)**: Integrate `three-mesh-bvh` for sub-millisecond raycasting against high-poly meshes instead of brute-force triangle intersection checks.
- **Compressed Assets**: Standardize on KTX2/Basis for textures and DRACO/Meshopt compression for GLTF/GLB models.

---

## Production Code Examples

### Example 1: Full Production Three.js Engine Lifecycle with Automatic GPU Disposal
*Location: `src/3d/Engine.ts`*

```typescript
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

export class Engine {
  private container: HTMLElement
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera
  private renderer: THREE.WebGLRenderer
  private controls: OrbitControls
  private clock: THREE.Clock
  private animationFrameId: number | null = null
  private isDisposed = false

  constructor(container: HTMLElement) {
    this.container = container

    // 1. Scene Initialization
    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color('#0a0a0c')

    // 2. Camera Setup
    const aspect = container.clientWidth / container.clientHeight
    this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000)
    this.camera.position.set(0, 5, 10)

    // 3. WebGL Renderer Setup with Pixel Ratio Capping
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: false,
      powerPreference: 'high-performance'
    })
    this.renderer.setSize(container.clientWidth, container.clientHeight)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.shadowMap.enabled = true
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
    this.renderer.outputColorSpace = THREE.SRGBColorSpace

    container.appendChild(this.renderer.domElement)

    // 4. Controls & Time Tracking
    this.controls = new OrbitControls(this.camera, this.renderer.domElement)
    this.controls.enableDamping = true
    this.controls.dampingFactor = 0.05

    this.clock = new THREE.Clock()

    // 5. Setup Listeners & Start Loop
    window.addEventListener('resize', this.onResize)
    this.start()
  }

  private onResize = () => {
    if (this.isDisposed) return
    const width = this.container.clientWidth
    const height = this.container.clientHeight

    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()

    this.renderer.setSize(width, height)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  }

  private start() {
    const tick = () => {
      if (this.isDisposed) return

      // Delta capping to prevent un-focused window physics explosions
      const delta = Math.min(this.clock.getDelta(), 0.1)

      this.controls.update()
      this.renderer.render(this.scene, this.camera)

      this.animationFrameId = requestAnimationFrame(tick)
    }

    tick()
  }

  public getScene(): THREE.Scene {
    return this.scene
  }

  // Comprehensive GPU Memory Cleanup Pipeline
  public dispose() {
    this.isDisposed = true

    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId)
    }

    window.removeEventListener('resize', this.onResize)
    this.controls.dispose()

    // Recursive traversal and disposal of all geometries, materials, and textures
    this.scene.traverse((object: THREE.Object3D) => {
      if (!(object instanceof THREE.Mesh)) return

      // Dispose geometry
      object.geometry.dispose()

      // Dispose material(s)
      if (Array.isArray(object.material)) {
        object.material.forEach((mat) => this.disposeMaterial(mat))
      } else if (object.material) {
        this.disposeMaterial(object.material)
      }
    })

    this.renderer.dispose()
    if (this.renderer.domElement && this.renderer.domElement.parentElement) {
      this.renderer.domElement.parentElement.removeChild(this.renderer.domElement)
    }
  }

  private disposeMaterial(material: THREE.Material) {
    material.dispose()

    // Dispose all potential texture maps on the material
    for (const key of Object.keys(material)) {
      const value = (material as any)[key]
      if (value && value instanceof THREE.Texture) {
        value.dispose()
      }
    }
  }
}
```

### Example 2: High-Performance `InstancedMesh` Particle Grid
*Location: `src/3d/InstancedGrid.ts`*

```typescript
import * as THREE from 'three'

export function createInstancedGrid(gridSize: number = 50): THREE.InstancedMesh {
  const count = gridSize * gridSize
  const geometry = new THREE.BoxGeometry(0.8, 0.8, 0.8)
  const material = new THREE.MeshStandardMaterial({
    color: new THREE.Color('#3a86ff'),
    roughness: 0.2,
    metalness: 0.8
  })

  const instancedMesh = new THREE.InstancedMesh(geometry, material, count)
  instancedMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage) // Matrix updates every frame

  const dummy = new THREE.Object3D()
  let index = 0

  const halfGrid = gridSize / 2
  for (let x = 0; x < gridSize; x++) {
    for (let z = 0; z < gridSize; z++) {
      dummy.position.set(x - halfGrid, 0, z - halfGrid)
      dummy.updateMatrix()
      instancedMesh.setMatrixAt(index++, dummy.matrix)
    }
  }

  instancedMesh.instanceMatrix.needsUpdate = true
  return instancedMesh
}

// Render-loop height wave animator for InstancedMesh
export function animateInstancedGrid(
  instancedMesh: THREE.InstancedMesh,
  gridSize: number,
  time: number
) {
  const dummy = new THREE.Object3D()
  const matrix = new THREE.Matrix4()
  const position = new THREE.Vector3()
  let index = 0

  for (let x = 0; x < gridSize; x++) {
    for (let z = 0; z < gridSize; z++) {
      instancedMesh.getMatrixAt(index, matrix)
      position.setFromMatrixPosition(matrix)

      // Calculate dynamic wave height offset using sine/cosine harmonics
      const dist = Math.sqrt(position.x * position.x + position.z * position.z)
      const y = Math.sin(dist * 0.5 - time * 3) * 0.8

      dummy.position.set(position.x, y, position.z)
      dummy.updateMatrix()
      instancedMesh.setMatrixAt(index++, dummy.matrix)
    }
  }

  instancedMesh.instanceMatrix.needsUpdate = true
}
```

### Example 3: Custom GLSL Animated Vertex Displacement Shader
*Location: `src/3d/shaders/WaveShader.ts`*

```typescript
import * as THREE from 'three'

const vertexShader = /* glsl */ `
  uniform float uTime;
  uniform float uWaveSpeed;
  uniform float uWaveFrequency;
  uniform float uWaveElevation;

  varying vec2 vUv;
  varying float vElevation;

  void main() {
    vUv = uv;

    vec4 modelPosition = modelMatrix * vec4(position, 1.0);

    float elevation = sin(modelPosition.x * uWaveFrequency + uTime * uWaveSpeed) *
                      cos(modelPosition.z * uWaveFrequency + uTime * uWaveSpeed) *
                      uWaveElevation;

    modelPosition.y += elevation;
    vElevation = elevation;

    vec4 viewPosition = viewMatrix * modelPosition;
    vec4 projectedPosition = projectionMatrix * viewPosition;

    gl_Position = projectedPosition;
  }
`

const fragmentShader = /* glsl */ `
  uniform vec3 uDepthColor;
  uniform vec3 uSurfaceColor;
  uniform float uColorOffset;
  uniform float uColorMultiplier;

  varying vec2 vUv;
  varying float vElevation;

  void main() {
    float mixStrength = (vElevation + uColorOffset) * uColorMultiplier;
    vec3 color = mix(uDepthColor, uSurfaceColor, clamp(mixStrength, 0.0, 1.0));

    gl_FragColor = vec4(color, 1.0);
  }
`

export function createWaveMaterial(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uWaveSpeed: { value: 2.0 },
      uWaveFrequency: { value: 1.5 },
      uWaveElevation: { value: 0.5 },
      uDepthColor: { value: new THREE.Color('#001219') },
      uSurfaceColor: { value: new THREE.Color('#0a9396') },
      uColorOffset: { value: 0.2 },
      uColorMultiplier: { value: 1.5 }
    },
    wireframe: false
  })
}
```

---

## Anti-Patterns & Common Pitfalls

### ❌ Anti-Pattern 1: Allocating Geometries or Materials Inside the Render Loop
```typescript
// BAD: Allocating WebGL objects every frame spikes CPU garbage collection & causes VRAM leaks!
function tick() {
  const geometry = new THREE.SphereGeometry(1, 32, 32) // BUG: 60 objects created per second!
  const mesh = new THREE.Mesh(geometry, sharedMaterial)
  scene.add(mesh)

  renderer.render(scene, camera)
  requestAnimationFrame(tick)
}

// GOOD: Allocate once and reuse references or use InstancedMesh
const sphereGeometry = new THREE.SphereGeometry(1, 32, 32)
```

### ❌ Anti-Pattern 2: Uncapped Pixel Ratio on High DPI Mobile Displays
```typescript
// BAD: Rendering 4K native canvas on mobile device GPUs destroys FPS
renderer.setPixelRatio(window.devicePixelRatio) // Device ratio could be 3.5 or 4!

// GOOD: Cap device pixel ratio at maximum of 2
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
```

### ❌ Anti-Pattern 3: Removing Meshes from Scene without Calling `dispose()`
```typescript
// BAD: Removing mesh from scene graph leaves WebGL geometry/texture memory allocated on GPU
scene.remove(mesh) // GPU VRAM memory is STILL allocated!

// GOOD: Remove AND call dispose() on geometries & materials
scene.remove(mesh)
mesh.geometry.dispose()
if (Array.isArray(mesh.material)) {
  mesh.material.forEach((m) => m.dispose())
} else {
  mesh.material.dispose()
}
```

### ❌ Anti-Pattern 4: Uncapped `clock.getDelta()` on Frame Lag or Tab Unfocus
```typescript
// BAD: Switching browser tabs makes delta huge (e.g. 5 seconds), breaking animation/physics calculation
const delta = clock.getDelta()
mesh.position.x += delta * 10 // Object teleports out of view!

// GOOD: Clamp delta calculation
const delta = Math.min(clock.getDelta(), 0.1)
mesh.position.x += delta * 10
```
