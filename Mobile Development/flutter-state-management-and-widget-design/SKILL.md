---
name: flutter-state-management-and-widget-design
description: Production-grade Flutter state management (Riverpod 2.x, BLoC/Cubit), widget tree optimization, immutable state modeling, declarative routing (GoRouter), clean architecture, and custom rendering performance patterns. Use when architecting or building scalable Flutter applications.
---

# Flutter State Management & Widget Design

A comprehensive guide for building scalable, high-performance, and maintainable Flutter applications using Riverpod 2.x, BLoC/Cubit, GoRouter, and performance-first widget tree architecture.

---

## 1. State Management Architecture: Riverpod 2.x vs BLoC

### Standard Decision Matrix

| Metric / Requirement | Riverpod 2.x (Notifier / AsyncNotifier) | BLoC / Cubit |
| :--- | :--- | :--- |
| **Compile-time Safety** | Highest (No `ProviderNotFoundException`) | High (Depends on BuildContext hierarchy) |
| **Testability** | Easy override via `ProviderContainer` | Easy via `bloc_test` |
| **Dependency Injection** | Built-in via Provider composition | Requires `RepositoryProvider` / `get_it` |
| **Learning Curve** | Moderate | Moderate-High (Event/State boilerplate) |
| **Use Case Recommendation** | Modern greenfield Flutter apps | Corporate/Enterprise apps with strict event logging |

---

## 2. Riverpod 2.x Production Pattern (AsyncNotifier)

Always use `@riverpod` code generation or `AsyncNotifierProvider` for async state to handle `AsyncValue` (`data`, `loading`, `error`) cleanly.

### Immutable State & Controller Implementation

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

// --- Domain Model ---
class UserProfile {
  final String id;
  final String name;
  final String email;

  const UserProfile({
    required this.id,
    required this.name,
    required this.email,
  });

  UserProfile copyWith({String? name, String? email}) {
    return UserProfile(
      id: id,
      name: name ?? this.name,
      email: email ?? this.email,
    );
  }
}

// --- Repository Interface ---
abstract class UserRepository {
  Future<UserProfile> fetchProfile(String userId);
  Future<void> updateName(String userId, String newName);
}

// --- Repository Provider ---
final userRepositoryProvider = Provider<UserRepository>((ref) {
  throw UnimplementedError('Override in ProviderScope');
});

// --- AsyncNotifier Controller ---
final userProfileControllerProvider =
    AsyncNotifierProvider.family<UserProfileController, UserProfile, String>(
  UserProfileController.new,
);

class UserProfileController extends FamilyAsyncNotifier<UserProfile, String> {
  @override
  Future<UserProfile> build(String arg) async {
    final repository = ref.watch(userRepositoryProvider);
    return repository.fetchProfile(arg);
  }

  Future<void> updateName(String newName) async {
    final repository = ref.read(userRepositoryProvider);
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await repository.updateName(arg, newName);
      final current = state.valueOrNull ?? await repository.fetchProfile(arg);
      return current.copyWith(name: newName);
    });
  }
}
```

---

## 3. Widget Tree Optimization Guidelines

### Rule 1: Use `const` Constructors Everywhere
`const` widgets avoid unnecessary element updates and skip re-building when parent widgets re-render.

### Rule 2: Rebuild Granularly with `select`
Do not watch an entire state object if you only need a single field.

```dart
// ❌ BAD: Rebuilds every time ANY field in UserProfile changes
class UserHeader extends ConsumerWidget {
  final String userId;
  const UserHeader({super.key, required this.userId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncProfile = ref.watch(userProfileControllerProvider(userId));
    return Text(asyncProfile.valueOrNull?.name ?? '');
  }
}

// ✅ GOOD: Rebuilds ONLY when 'name' specifically changes
class UserHeaderOptimized extends ConsumerWidget {
  final String userId;
  const UserHeaderOptimized({super.key, required this.userId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final name = ref.watch(
      userProfileControllerProvider(userId).select((asyncVal) => asyncVal.valueOrNull?.name),
    );
    return Text(name ?? '');
  }
}
```

### Rule 3: Isolate Heavy Animations with `RepaintBoundary`
Wrap isolated, high-frequency animated subtrees in `RepaintBoundary` to prevent rasterizing the whole screen on every tick.

```dart
Widget build(BuildContext context) {
  return Scaffold(
    body: Stack(
      children: [
        const StaticBackgroundView(),
        RepaintBoundary(
          child: CustomParticleAnimation(),
        ),
      ],
    ),
  );
}
```

---

## 4. Declarative Routing with GoRouter

Implement type-safe, declarative routes with authentication guards.

```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final authStateProvider = StateProvider<bool>((ref) => false);

final routerProvider = Provider<GoRouter>((ref) {
  final isAuthenticated = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/home',
    redirect: (context, state) {
      final loggingIn = state.matchedLocation == '/login';
      if (!isAuthenticated && !loggingIn) return '/login';
      if (isAuthenticated && loggingIn) return '/home';
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const HomeScreen(),
        routes: [
          GoRoute(
            path: 'details/:id',
            builder: (context, state) {
              final id = state.pathParameters['id']!;
              return DetailsScreen(id: id);
            },
          ),
        ],
      ),
    ],
  );
});
```

---

## 5. Critical Anti-Patterns & Pitfalls

### ❌ Anti-Pattern 1: Using `BuildContext` Across Async Gaps
**Bad:**
```dart
void onSubmit(BuildContext context) async {
  await fetchData();
  Navigator.of(context).pop(); // Dangerous! Context may no longer be mounted.
}
```
**Good:**
```dart
void onSubmit(BuildContext context) async {
  await fetchData();
  if (!context.mounted) return;
  Navigator.of(context).pop();
}
```

### ❌ Anti-Pattern 2: Instantiating Controllers Inside `build()`
**Bad:**
```dart
Widget build(BuildContext context) {
  final controller = AnimationController(vsync: this, duration: ...); // Memory leak! Re-created on rebuild!
  return ...
}
```
**Good:** Initialize long-lived controllers in `initState()` / disposal in `dispose()`, or use `flutter_hooks` (`useAnimationController`).

### ❌ Anti-Pattern 3: Over-nesting Layout Widgets
Avoid deep nesting of `Container`, `Padding`, and `SizedBox`. Prefer explicit single-pass layout widgets (`Padding`, `Gap`, `Flex`, `CustomScrollView` with `SliverList`).

---

## 6. Unit & Widget Testing Patterns

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';

void main() {
  testWidgets('UserHeader displays name from controller', (tester) async {
    final mockRepository = MockUserRepository();
    when(mockRepository.fetchProfile('123')).thenAnswer(
      (_) async => const UserProfile(id: '123', name: 'Alice', email: 'alice@test.com'),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          userRepositoryProvider.overrideWithValue(mockRepository),
        ],
        child: const MaterialApp(
          home: UserHeaderOptimized(userId: '123'),
        ),
      ),
    );

    // Initial state (loading)
    expect(find.byType(Text), findsOneWidget);

    // Settle async notifier
    await tester.pumpAndSettle();

    expect(find.text('Alice'), findsOneWidget);
  });
}
```
