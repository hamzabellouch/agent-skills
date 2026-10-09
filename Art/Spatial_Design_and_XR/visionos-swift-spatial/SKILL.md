---
name: visionos-swift-spatial
metadata:
  category: Spatial Computing AR and VR
description: Architecting native spatial computing applications for visionOS using Swift, SwiftUI, RealityKit, and ARKit. Use when developing 3D Windows, Volumes, Immersive Spaces, RealityView components, Spatial Audio, ShaderGraph Materials, and Hand/Eye tracking interaction models.
compatibility: visionOS 1.0+, Xcode 15.0+, Swift 5.9+, RealityKit, ARKit
---

# visionOS & Swift Spatial Computing Guidelines

This skill provides architectural guidance, SwiftUI spatial container paradigms, RealityKit 3D rendering patterns, ARKit hand/plane tracking models, and performance standards for building native visionOS applications on Apple Vision Pro.

---

## 1. visionOS Spatial App Architecture

visionOS divides spatial user interfaces into three distinct presentation containers:

```
+-------------------------------------------------------------------------+
|                              Shared Space                               |
|                                                                         |
|   +-----------------------+                    +--------------------+   |
|   |       2D Window       |                    |     3D Volume      |   |
|   |  (SwiftUI Standard)   |                    | (Bounded Reality)  |   |
|   +-----------------------+                    +--------------------+   |
+-------------------------------------------------------------------------+
                                     |
                         (User Enters Full Space)
                                     v
+-------------------------------------------------------------------------+
|                             Full Space                                  |
|                                                                         |
|   +-----------------------------------------------------------------+   |
|   |                        ImmersiveSpace                           |   |
|   |          (Unbounded 3D World / Full Pass-through / VR)          |   |
|   +-----------------------------------------------------------------+   |
+-------------------------------------------------------------------------+
```

1. **Window**: Standard 2D or semi-3D SwiftUI plane residing within the user's Shared Space alongside other applications.
2. **Volume**: Bounded 3D bounding box container displaying 3D RealityKit content alongside windows in Shared Space.
3. **Immersive Space**: Exclusive environment (Mixed, Progressive, or Full) granting total access to surrounding spatial coordinates and ARKit tracking feeds.

---

## 2. SwiftUI & RealityKit Integration (`RealityView`)

### 2.1 Implementing a 3D RealityView inside a SwiftUI Window/Volume

```swift
import SwiftUI
import RealityKit
import RealityKitContent

struct SpatialProductViewer: View {
    @State private var modelEntity: Entity?
    @State private var isRotating = false
    
    var body: some View {
        VStack {
            Text("Interactive Spatial Model")
                .font(.extraLargeTitle)
                .padding()
            
            RealityView { content in
                // 1. Load 3D Asset asynchronously from Bundle
                if let entity = try? await Entity(named: "SpatialGlobe", in: realityKitContentBundle) {
                    entity.position = [0, 0, 0] // Centered in Volume
                    entity.scale = [0.5, 0.5, 0.5]
                    
                    // Enable Spatial Collisions & Hover Effects
                    entity.components.set(CollisionComponent(shapes: [.generateSphere(radius: 0.25)]))
                    entity.components.set(InputTargetComponent())
                    entity.components.set(HoverEffectComponent())
                    
                    content.add(entity)
                    self.modelEntity = entity
                }
            } update: { content in
                // Dynamic state updates
                if let entity = modelEntity {
                    if isRotating {
                        let rotation = Transform(pitch: 0, yaw: .pi / 4, roll: 0)
                        entity.transform.matrix = matrix_multiply(entity.transform.matrix, rotation.matrix)
                    }
                }
            }
            .gesture(
                TapGesture()
                    .targetedToAnyEntity()
                    .onEnded { value in
                        // Hand Pinch / Eye Look interaction trigger
                        isRotating.toggle()
                    }
            )
            .gesture(
                DragGesture()
                    .targetedToAnyEntity()
                    .onChanged { value in
                        guard let entity = self.modelEntity else { return }
                        let translation = value.convert(value.translation3D, from: .local, to: .scene)
                        entity.position += SIMD3<Float>(Float(translation.x), Float(translation.y), Float(translation.z))
                    }
            )
        }
    }
}
```

---

## 3. Immersive Spaces & ARKit Tracking

### 3.1 Managing Immersive Space Lifecycle in App Structure

```swift
import SwiftUI

@main
struct SpatialApp: App {
    @State private var currentImmersionStyle: ImmersionStyle = .mixed

    var body: some Scene {
        // 1. Main Window Scene
        WindowGroup {
            ContentView()
        }
        .windowStyle(.automatic)

        // 2. 3D Bounded Volume Scene
        WindowGroup(id: "ProductVolume") {
            SpatialProductViewer()
        }
        .windowStyle(.volumetric)
        .defaultSize(width: 0.6, height: 0.6, depth: 0.6, units: .meters)

        // 3. Unbounded Immersive Space
        ImmersiveSpace(id: "FullEnvironment") {
            ImmersiveView()
        }
        .immersionStyle(selection: $currentImmersionStyle, in: .mixed, .progressive, .full)
    }
}
```

### 3.2 Hand Tracking with ARKit (`HandTrackingProvider`)

```swift
import ARKit
import RealityKit

@Observable
final class HandTrackingManager {
    private let session = ARKitSession()
    private let handTracking = HandTrackingProvider()
    
    func startTracking() async {
        guard HandTrackingProvider.isSupported else { return }
        
        do {
            try await session.run([handTracking])
            for await update in handTracking.anchorUpdates {
                let handAnchor = update.anchor
                guard handAnchor.isTracked else { continue }
                
                // Track Index Finger Tip position
                if let skeleton = handAnchor.handSkeleton,
                   let indexTip = skeleton.joint(.indexFingerTipFromJoint) {
                    let transform = handAnchor.originFromAnchorTransform * indexTip.anchorFromJointTransform
                    let position = SIMD3<Float>(transform.columns.3.x, transform.columns.3.y, transform.columns.3.z)
                    
                    // Process spatial finger gesture position
                    processIndexTipPosition(position, chirality: handAnchor.chirality)
                }
            }
        } catch {
            print("ARKit Hand Tracking Session Failed: \(error.localizedDescription)")
        }
    }
    
    private func processIndexTipPosition(_ position: SIMD3<Float>, chirality: GestureChirality) {
        // Spatial intersection or UI feedback logic
    }
}
```

---

## 4. Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Consequence | Correct Pattern |
|---|---|---|---|
| Requesting Hand Tracking data in Shared Space | Critical | App crash or denied permission | Hand tracking APIs require active `ImmersiveSpace` |
| Overriding Eye Tracking / Pinch without SwiftUI gestures | High | Non-standard UX, user frustration | Use native SwiftUI gestures (`TapGesture().targetedToAnyEntity()`) |
| Unbounded Volumetric Scene Dimensions | High | Volume clips UI or interferes with user space | Set explicit `.defaultSize(width:height:depth:units:.meters)` |
| Missing Spatial Audio Component on 3D Audio Entities | Medium | Sound flatly stereo-rendered | Attach `SpatialAudioComponent` & configure `AudioListenerComponent` |
| Blocking Main Thread with Heavy Asset Loading | Critical | Frame drop, visionOS system compositor crash | Load USDZ / Reality assets asynchronously via `Entity(named:in:) async` |

---

## 5. Spatial UX & Ergonomics Guidelines

1. **Comfort Zone**: Place interactive content between **1.0 meter and 2.5 meters** from the user's head position.
2. **Field of View Padding**: Avoid placing primary interactive windows near peripheral vertical boundaries.
3. **Hover Effects**: Always attach `HoverEffectComponent()` to interactive 3D entities so visionOS subtle eye-gaze highlights register correctly.
4. **Pass-through Legibility**: Ensure 3D text and UI panels utilize visionOS native Glass Material background translucency (`.background(.ultraThinMaterial)`).

---

## 6. Verification & Xcode Simulator Testing

- [ ] **Interaction Check**: Test Eye Look + Pinch tap trigger using Xcode visionOS Simulator pointer controls.
- [ ] **Volumetric Clipping**: Verify 3D mesh fits within assigned volume bounds without edge slicing.
- [ ] **Memory & Thermals**: Profile with Xcode Instruments (RealityKit Frame Rate & Thermal State).
