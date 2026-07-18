---
name: react-native-expo-performance-and-native-modules
description: Production-grade React Native & Expo architecture, high-performance UI (JSI, Reanimated 3, FlashList, Skia), Expo Modules API (C++ / Swift / Kotlin native modules), Fabric architecture, and JavaScript thread optimization. Use when building or optimizing performance-critical React Native and Expo applications.
---

# React Native & Expo Performance & Native Modules

A comprehensive guide for building high-performance, native-speed React Native applications using Expo, modern New Architecture (Fabric & TurboModules), JSI, Reanimated 3, FlashList, and custom Expo Native Modules (Swift/Kotlin/C++).

---

## 1. Modern React Native Architecture Overview

### Bridge Architecture (Legacy) vs New Architecture (Fabric + TurboModules)

```
   ┌─────────────────────────────────────────────────────────────┐
   │                  New Architecture (JSI)                     │
   │                                                             │
   │   ┌──────────────────┐           ┌──────────────────┐       │
   │   │ JavaScript Engine│<=========>│   C++ Host Object│       │
   │   │  (Hermes / V8)   │   Direct  │      (JSI)       │       │
   │   └──────────────────┘  Memory   └──────────────────┘       │
   │            │                    ▲          │                │
   │            │ Fabric Layout      │ Direct   │ Shared         │
   │            ▼ Direct Calls       │ Invok.   ▼ Reference      │
   │   ┌──────────────────┐          │┌──────────────────┐       │
   │   │ Component Views  │──────────┘│   Native Modules │       │
   │   │ (C++ Render Tree)│           │  (Swift / Kotlin)│       │
   │   └──────────────────┘           └──────────────────┘       │
   └─────────────────────────────────────────────────────────────┘
```

### Core Architectural Rules
1. **Enable Hermes Engine & New Architecture**: Always set `"newArchEnabled": true` in `app.json`.
2. **Synchronous C++ / Native Calls via JSI**: Avoid asynchronous JS-to-Native bridge serializations for high-frequency operations (sensors, audio processing, cryptography, animations).
3. **Keep the JS Thread Free (60/120 FPS target)**: Offload layout animations to the UI Thread via Reanimated 3 worklets.

---

## 2. High-Performance UI Optimization

### List Optimization: `FlashList` over `FlatList`

`@shopify/flash-list` recycles views instead of unmounting/remounting them, dramatically reducing JS thread lag during fast scrolling.

```tsx
import React, { useCallback } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { FlashList, ListRenderItem } from '@shopify/flash-list';

interface Message {
  id: string;
  sender: string;
  content: string;
  timestamp: string;
}

interface ChatListProps {
  messages: Message[];
}

const MessageItem = React.memo(({ item }: { item: Message }) => {
  return (
    <View style={styles.card}>
      <Text style={styles.sender}>{item.sender}</Text>
      <Text style={styles.content}>{item.content}</Text>
      <Text style={styles.timestamp}>{item.timestamp}</Text>
    </View>
  );
});

export const ChatList: React.FC<ChatListProps> = ({ messages }) => {
  const renderItem: ListRenderItem<Message> = useCallback(
    ({ item }) => <MessageItem item={item} />,
    []
  );

  return (
    <View style={styles.container}>
      <FlashList
        data={messages}
        renderItem={renderItem}
        estimatedItemSize={72}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' },
  card: { padding: 16, borderBottomWidth: 1, borderBottomColor: '#1e293b' },
  sender: { fontWeight: '600', color: '#38bdf8', marginBottom: 4 },
  content: { color: '#f8fafc', fontSize: 15 },
  timestamp: { color: '#64748b', fontSize: 11, marginTop: 4 },
});
```

### UI Thread Gesture Animations with Reanimated 3

Run gesture calculations directly on the Native UI thread using worklets.

```tsx
import React from 'react';
import { StyleSheet, View } from 'react-native';
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
} from 'react-native-reanimated';

export const SwipeableCard: React.FC = () => {
  const translateX = useSharedValue(0);
  const isPressed = useSharedValue(false);

  const panGesture = Gesture.Pan()
    .onBegin(() => {
      'worklet';
      isPressed.value = true;
    })
    .onChange((event) => {
      'worklet';
      translateX.value = event.translationX;
    })
    .onFinalize(() => {
      'worklet';
      isPressed.value = false;
      translateX.value = withSpring(0, { damping: 15 });
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { scale: withTiming(isPressed.value ? 1.05 : 1) },
    ],
    backgroundColor: isPressed.value ? '#3b82f6' : '#1d4ed8',
  }));

  return (
    <GestureHandlerRootView style={styles.container}>
      <GestureDetector gesture={panGesture}>
        <Animated.View style={[styles.card, animatedStyle]} />
      </GestureDetector>
    </GestureHandlerRootView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  card: { width: 300, height: 180, borderRadius: 16, elevation: 5 },
});
```

---

## 3. Custom Expo Native Modules API (Swift & TypeScript)

Expo Modules API provides a modern, Swift/Kotlin-first framework for building TurboModules without touch-points to raw C++ header glue.

### Swift Implementation (`ios/HapticEngineModule.swift`)

```swift
import ExpoModulesCore
import UIKit

public class HapticEngineModule: Module {
  public func definition() -> ModuleDefinition {
    Name("HapticEngine")

    // Synchronous function call (JSI binding)
    Function("triggerImpact") { (style: String) -> Void in
      DispatchQueue.main.async {
        let feedbackStyle: UIImpactFeedbackGenerator.FeedbackStyle
        switch style {
        case "light": feedbackStyle = .light
        case "medium": feedbackStyle = .medium
        case "heavy": feedbackStyle = .heavy
        default: feedbackStyle = .medium
        }
        let generator = UIImpactFeedbackGenerator(style: feedbackStyle)
        generator.prepare()
        generator.impactOccurred()
      }
    }

    // Async function returning a Promise
    AsyncFunction("getBatteryLevel") { () -> Float in
      UIDevice.current.isBatteryMonitoringEnabled = true
      return UIDevice.current.batteryLevel
    }
  }
}
```

### TypeScript Definition & API Wrapper (`src/NativeHapticEngine.ts`)

```typescript
import { requireNativeModule } from 'expo-modules-core';

interface HapticEngineNative {
  triggerImpact(style: 'light' | 'medium' | 'heavy'): void;
  getBatteryLevel(): Promise<number>;
}

const NativeModule = requireNativeModule<HapticEngineNative>('HapticEngine');

export const HapticEngine = {
  triggerImpact(style: 'light' | 'medium' | 'heavy' = 'medium'): void {
    NativeModule.triggerImpact(style);
  },
  async getBatteryLevel(): Promise<number> {
    return await NativeModule.getBatteryLevel();
  },
};
```

---

## 4. Critical Anti-Patterns & JS Thread Bottlenecks

### ❌ Anti-Pattern 1: Passing Inline Objects or Arrow Functions into List Items
**Bad:**
```tsx
<FlatList
  data={data}
  renderItem={({ item }) => (
    <ItemCard item={item} onPress={() => handlePress(item.id)} style={{ margin: 10 }} />
  )}
/>
```
**Good:** Use stable callbacks (`useCallback`) and memoized inline styles or `StyleSheet.create`.

### ❌ Anti-Pattern 2: Animating UI Properties on JS Thread via Standard `Animated`
**Bad:**
```typescript
Animated.timing(this.state.fadeAnim, {
  toValue: 1,
  duration: 1000,
  useNativeDriver: false, // Executes frame ticks on JS thread!
}).start();
```
**Good:** Always set `useNativeDriver: true` for legacy `Animated`, or standardise on `react-native-reanimated 3`.

### ❌ Anti-Pattern 3: Large JSON Payload Serialization over the Bridge
Passing megabyte-sized JSON strings over the bridge stalls both threads.
**Good:** Use binary ArrayBuffers / TypedArrays via JSI, SQLite (e.g. `op-sqlite`), or direct C++ native memory buffers.

---

## 5. Performance Diagnostics Checklist

1. **Monitor Frame Rates**: Use `react-native-performance` and Expo Dev Tools to track JS FPS vs UI FPS.
2. **Hermes Profiling**: Capture CPU profiles via Chrome DevTools (`chrome://inspect`) to pinpoint slow JS functions.
3. **Memory Leaks**: Use Xcode Instruments (Leaks / Allocations) and Android Studio Profiler to check un-freed C++ JSI host objects or unremoved event listeners.
