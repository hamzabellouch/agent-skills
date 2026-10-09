---
name: ios-swiftui-architecture-and-state
description: Production-grade iOS SwiftUI architecture, state management (@Observable, @State, @Binding, @Environment), Modern Swift Concurrency (async/await, Actors, Task Groups), NavigationStack routing, and Clean Architecture implementation patterns. Use when designing, building, or refactoring iOS apps in SwiftUI.
---

# SwiftUI Architecture & State Management

A comprehensive guide for building scalable, high-performance, and testable iOS applications using SwiftUI, Swift 5.9+ `@Observable`, Modern Swift Concurrency, and Clean Architecture principles.

---

## 1. Core State Management Rules (Swift 5.9+ / Observation Framework)

Swift 5.9 introduced the `@Observable` macro, replacing `ObservableObject`, `@Published`, `@StateObject`, and `@ObservedObject`.

### Property Wrapper Selection Matrix

| Tool | Scope / Use Case | Ownership / Lifetime |
| :--- | :--- | :--- |
| `@State` | Local view-private value types or `@Observable` object instantiation | View owns the lifecycle |
| `@Binding` | Two-way binding passed from parent to child | Parent owns the value; child mutates |
| `@Environment` | Dependency injection & shared environment values | System or ancestor view owns |
| `@Observable` | Reference type domain models & ViewModels | Managed via `@State` or `@Environment` |
| `let` / `var` | Read-only properties or local computed properties | Dependent on parent view initialization |

### Rules for State Management
1. **Never use `ObservableObject` in new Swift 5.9+ code.** Prefer `@Observable final class MyViewModel`.
2. **Instantiate `@Observable` view models in views using `@State`**:
   ```swift
   struct FeedView: View {
       @State private var viewModel = FeedViewModel()
       var body: some View { ... }
   }
   ```
3. **Pass down `@Observable` classes as non-wrapped properties or environment objects**:
   ```swift
   // Shared via Environment
   FeedDetailView()
       .environment(viewModel)

   // Received in Subview
   struct FeedDetailView: View {
       @Environment(FeedViewModel.self) private var viewModel
   }
   ```

---

## 2. SwiftUI Clean Architecture

The recommended architecture separates responsibilities into **Presentation (Views + ViewModels)**, **Domain (Use Cases + Entities)**, and **Data (Repositories + Data Sources)**.

```
   ┌────────────────────────────────────────────────────────┐
   │                    Presentation Layer                   │
   │  ┌──────────────────────┐    ┌──────────────────────┐  │
   │  │    SwiftUI View      │───>│      ViewModel       │  │
   │  └──────────────────────┘    └──────────────────────┘  │
   └─────────────────────────────│──────────────────────────┘
                                 │ Depends on abstraction
   ┌─────────────────────────────▼──────────────────────────┐
   │                      Domain Layer                       │
   │  ┌──────────────────────┐    ┌──────────────────────┐  │
   │  │      Use Case        │───>│ Repository Interface │  │
   │  └──────────────────────┘    └──────────────────────┘  │
   └─────────────────────────────▲──────────────────────────┘
                                 │ Implements
   ┌─────────────────────────────│──────────────────────────┐
   │                       Data Layer                        │
   │  ┌──────────────────────────────────────────────────┐  │
   │  │           Repository Implementation              │  │
   │  └──────────────────────────────────────────────────┘  │
   │           │                               │            │
   │  ┌────────▼─────────┐             ┌───────▼─────────┐  │
   │  │  Remote Service  │             │   Local Database│  │
   │  │  (URLSession)    │             │   (SwiftData)   │  │
   │  └──────────────────┘             └─────────────────┘  │
   └────────────────────────────────────────────────────────┘
```

### Complete Code Implementation Example

#### Domain Layer: Model & Repository Protocol
```swift
import Foundation

struct Article: Identifiable, Hashable, Sendable {
    let id: UUID
    let title: String
    let summary: String
    let publishedAt: Date
}

protocol ArticleRepository: Sendable {
    func fetchArticles() async throws -> [Article]
    func markAsFavorite(id: UUID) async throws
}
```

#### Data Layer: Remote Data Source & Repository Implementation
```swift
actor ArticleRemoteDataSource {
    private let urlSession: URLSession

    init(urlSession: URLSession = .shared) {
        self.urlSession = urlSession
    }

    func fetchArticlesDTO() async throws -> [ArticleDTO] {
        let url = URL(string: "https://api.example.com/v1/articles")!
        let (data, response) = try await urlSession.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }

        return try JSONDecoder().decode([ArticleDTO].self, from: data)
    }
}

struct ArticleDTO: Decodable {
    let id: UUID
    let title: String
    let body: String
    let createdAt: Date

    func toDomain() -> Article {
        Article(id: id, title: title, summary: body, publishedAt: createdAt)
    }
}

final class DefaultArticleRepository: ArticleRepository {
    private let remoteDataSource: ArticleRemoteDataSource

    init(remoteDataSource: ArticleRemoteDataSource = ArticleRemoteDataSource()) {
        self.remoteDataSource = remoteDataSource
    }

    func fetchArticles() async throws -> [Article] {
        let dtos = try await remoteDataSource.fetchArticlesDTO()
        return dtos.map { $0.toDomain() }
    }

    func markAsFavorite(id: UUID) async throws {
        // Local or remote update
    }
}
```

#### Presentation Layer: ViewModel & View
```swift
import SwiftUI

@Observable
@MainActor
final class FeedViewModel {
    enum ViewState: Equatable {
        case idle
        case loading
        case loaded([Article])
        case error(String)
    }

    private(set) var state: ViewState = .idle
    private let repository: ArticleRepository

    init(repository: ArticleRepository) {
        self.repository = repository
    }

    func loadArticles() async {
        state = .loading
        do {
            let articles = try await repository.fetchArticles()
            state = .loaded(articles)
        } catch {
            state = .error(error.localizedDescription)
        }
    }
}

struct FeedView: View {
    @State private var viewModel: FeedViewModel

    init(repository: ArticleRepository = DefaultArticleRepository()) {
        _viewModel = State(wrappedValue: FeedViewModel(repository: repository))
    }

    var body: some View {
        NavigationStack {
            Group {
                switch viewModel.state {
                case .idle, .loading:
                    ProgressView("Loading feed...")
                case .loaded(let articles):
                    List(articles) { article in
                        NavigationLink(value: article) {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(article.title)
                                    .font(.headline)
                                Text(article.summary)
                                    .font(.subheadline)
                                    .foregroundStyle(.secondary)
                            }
                        }
                    }
                case .error(let message):
                    ContentUnavailableView("Failed to Load", systemImage: "wifi.exclamationmark", description: Text(message))
                }
            }
            .navigationTitle("Articles")
            .navigationDestination(for: Article.self) { article in
                ArticleDetailView(article: article)
            }
            .task {
                await viewModel.loadArticles()
            }
        }
    }
}

struct ArticleDetailView: View {
    let article: Article

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(article.title)
                    .font(.largeTitle.bold())
                Text(article.publishedAt.formatted())
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(article.summary)
                    .font(.body)
            }
            .padding()
        }
        .navigationTitle("Details")
        .navigationBarTitleDisplayMode(.inline)
    }
}
```

---

## 3. NavigationStack & Type-Safe Decoupled Routing

Never couple views directly via `NavigationLink(destination: NextView())`. Use value-based navigation with custom routes.

```swift
enum AppRoute: Hashable {
    case articleDetail(Article)
    case userProfile(userId: UUID)
    case settings
}

@Observable
final class Router {
    var path = NavigationPath()

    func navigate(to route: AppRoute) {
        path.append(route)
    }

    func pop() {
        if !path.isEmpty {
            path.removeLast()
        }
    }

    func popToRoot() {
        path.removeLast(path.count)
    }
}

struct RootView: View {
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            HomeContentView()
                .navigationDestination(for: AppRoute.self) { route in
                    switch route {
                    case .articleDetail(let article):
                        ArticleDetailView(article: article)
                    case .userProfile(let userId):
                        UserProfileView(userId: userId)
                    case .settings:
                        SettingsView()
                    }
                }
        }
        .environment(router)
    }
}
```

---

## 4. Anti-Patterns & Performance Pitfalls

### ❌ Anti-Pattern 1: Performing heavy computation or side effects in `body`
**Bad:**
```swift
var body: some View {
    let filteredList = items.filter { $0.isValid } // Re-computed on every frame render!
    List(filteredList) { ... }
}
```
**Good:** Perform filtering in ViewModel or memoize state using computed properties on `@Observable` ViewModel.

### ❌ Anti-Pattern 2: Captured self retain cycles in `.task` or async closures
**Bad:**
```swift
.task {
    self.viewModel.startPolling() // Retain risk if not properly cancelled
}
```
**Good:** `.task` modifier automatically handles task cancellation when the view disappears. Ensure ViewModel tasks respect `Task.isCancelled`.

### ❌ Anti-Pattern 3: Over-using `@StateObject` / `@ObservedObject` with Swift 5.9+
Mixing `ObservableObject` and `@Observable` causes redundant UI redraws and invalidates observation tracking. Standardize the codebase on `@Observable`.

---

## 5. Testing Patterns

```swift
import XCTest
@testable import MyApp

@MainActor
final class FeedViewModelTests: XCTestCase {
    func test_loadArticles_success_setsLoadedState() async {
        // Arrange
        let mockArticles = [Article(id: UUID(), title: "Test", summary: "Body", publishedAt: Date())]
        let mockRepository = MockArticleRepository(result: .success(mockArticles))
        let sut = FeedViewModel(repository: mockRepository)

        // Act
        await sut.loadArticles()

        // Assert
        XCTAssertEqual(sut.state, .loaded(mockArticles))
    }
}

final class MockArticleRepository: ArticleRepository, @unchecked Sendable {
    let result: Result<[Article], Error>

    init(result: Result<[Article], Error>) {
        self.result = result
    }

    func fetchArticles() async throws -> [Article] {
        try result.get()
    }

    func markAsFavorite(id: UUID) async throws {}
}
```
