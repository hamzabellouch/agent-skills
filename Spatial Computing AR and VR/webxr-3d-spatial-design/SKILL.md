---
name: webxr-3d-spatial-design
metadata:
  category: Spatial Computing AR and VR
description: Technical guidelines for building immersive WebXR, Three.js, and WebGPU 3D spatial experiences. Use when implementing WebXR session management (VR/AR/inline), controller/hand tracking inputs, spatial audio, 3D UI raycasting, GLTF loading optimization, or WebGL shader performance.
compatibility: WebXR Device API, Three.js r150+, WebGPU / WebGL2, Chrome/Quest/Vision Pro browsers
---

# WebXR & 3D Spatial Design Production Guidelines

This skill covers architecture, frame loop synchronization, input handling (tracked controllers, hand tracking, raycasting), spatial audio integration, and performance optimization for WebXR and Three.js applications across VR headsets and AR pass-through devices.

---

## 1. WebXR Lifecycle & Session Management

### 1.1 Session Initialization (Immersive VR vs Immersive AR)

```javascript
import * as THREE from 'three';
import { VRButton } from 'three/addons/webxr/VRButton.js';
import { ARButton } from 'three/addons/webxr/ARButton.js';

class SpatialApp {
  constructor() {
    this.container = document.createElement('div');
    document.body.appendChild(this.container);

    // 1. Scene & Camera Setup
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(
      50, 
      window.innerWidth / window.innerHeight, 
      0.1, 
      20
    );
    this.camera.position.set(0, 1.6, 0); // 1.6m height standard human eye level

    // 2. Renderer with WebXR enabled
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.xr.enabled = true;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.container.appendChild(this.renderer.domElement);

    this.initButtons();
    this.initLighting();
  }

  initButtons() {
    // Add VR entry button to DOM
    document.body.appendChild(VRButton.createButton(this.renderer));
  }

  initLighting() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(2, 4, 2);
    dirLight.castShadow = true;
    this.scene.add(dirLight);
  }

  // 3. WebXR-compliant Render Loop (Do NOT use requestAnimationFrame directly)
  start() {
    this.renderer.setAnimationLoop((timestamp, frame) => {
      this.update(timestamp, frame);
      this.renderer.render(this.scene, this.camera);
    });
  }

  update(timestamp, frame) {
    // Frame delta handling
    if (frame) {
      const session = frame.session;
      // Process XR input sources / reference space poses
    }
  }
}
```

---

## 2. Spatial Controller & Hand Tracking Inputs

### 2.1 Raycasting & Interactivity setup

```javascript
import { XRControllerModelFactory } from 'three/addons/webxr/XRControllerModelFactory.js';

export function setupControllers(renderer, scene) {
  const controllerModelFactory = new XRControllerModelFactory();
  const controllers = [];

  for (let i = 0; i < 2; i++) {
    const controller = renderer.xr.getController(i);
    scene.add(controller);

    // Laser pointer visualization
    const geometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(0, 0, -5)
    ]);
    const material = new THREE.LineBasicMaterial({ color: 0x00ffcc, linewidth: 2 });
    const rayLine = new THREE.Line(geometry, material);
    controller.add(rayLine);

    // Controller Grip model (3D representation)
    const grip = renderer.xr.getControllerGrip(i);
    grip.add(controllerModelFactory.createControllerModel(grip));
    scene.add(grip);

    controllers.push({ controller, grip });
  }

  return controllers;
}
```

### 2.2 Spatial Raycasting Interaction

```javascript
const raycaster = new THREE.Raycaster();
const tempMatrix = new THREE.Matrix4();

export function checkIntersections(controller, interactableObjects) {
  tempMatrix.identity().extractRotation(controller.matrixWorld);

  raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
  raycaster.ray.direction.set(0, 0, -1).applyMatrix4(tempMatrix);

  const intersects = raycaster.intersectObjects(interactableObjects, false);

  if (intersects.length > 0) {
    const hitObject = intersects[0].object;
    hitObject.material.color.setHex(0xff0055); // Highlight hit target
    return intersects[0];
  }
  return null;
}
```

---

## 3. Spatial Audio Integration

WebXR experiences demand head-tracked spatial audio using the Web Audio API PositionalAudio:

```javascript
export function attachSpatialAudio(camera, object, soundFileUrl) {
  // Create audio listener attached to camera (HMD position)
  const listener = new THREE.AudioListener();
  camera.add(listener);

  // Create positional audio source attached to 3D object in space
  const sound = new THREE.PositionalAudio(listener);
  const audioLoader = new THREE.AudioLoader();

  audioLoader.load(soundFileUrl, (buffer) => {
    sound.setBuffer(buffer);
    sound.setRefDistance(1);       // Distance where volume starts reducing
    sound.setMaxDistance(10);      // Max audible distance
    sound.setRolloffFactor(1.5);   // Natural attenuation curve
    sound.setLoop(true);
    sound.play();
  });

  object.add(sound);
}
```

---

## 4. Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Consequence | Correct Pattern |
|---|---|---|---|
| Calling `window.requestAnimationFrame()` in WebXR | Critical | Motion sickness, frame stutter, XR freeze | Use `renderer.setAnimationLoop(callback)` |
| High Polygon Models (>100k tris/scene on mobile VR) | Critical | Drops below 72/90/120 Hz, causes nausea | Low-poly assets, Draco compressed GLTF, LOD meshes |
| Unbounded Dynamic Shadows | High | Heavy GPU fill-rate degradation | Use baked lightmaps or single directional shadow caster |
| Fixed 2D UI elements in screen space | High | Visual depth mismatch, eye strain | Position UI elements as 3D world-space panels (1.5-2m distance) |
| Hardcoded rendering dimensions | Medium | Blurry projection on high-res HMDs | Rely on `renderer.xr.getFoveation()` and native WebXR framebuffer scale |

---

## 5. Performance Targets & Asset Pipeline

### Target Framerates
- **Meta Quest 2/3 / Pro**: Minimum **72 FPS** (Target 90 FPS)
- **Apple Vision Pro (Safari WebXR)**: **90 FPS / 96 FPS**
- **PCVR (SteamVR/Oculus Link)**: **90 FPS - 120 FPS**

### Optimization Pipeline
1. **DRACO & KHR_mesh_quantization**: Compress `.gltf`/`.glb` meshes using `gltf-pipeline`.
2. **Basis Universal Textures (`KHR_texture_basisu`)**: Transcode GPU textures at runtime directly to ASTC/BC7/ETC2.
3. **Fixed Foveated Rendering**: Enable WebXR foveation to reduce shading cost near lens periphery:
   ```javascript
   renderer.xr.setFoveation(1.0); // 0.0 (off) to 1.0 (max foveation)
   ```

---

## 6. Verification Checklist

- [ ] **Frame Rate Stability**: Test with Quest Developer Hub or Chrome WebXR DevTools to ensure zero dropped frames.
- [ ] **Pass-through Blending**: Verify transparency setup when running in `immersive-ar` mode.
- [ ] **Reference Space**: Confirm correct reference space (`local-floor` or `bounded-floor`) to match floor level.
