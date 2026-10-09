---
name: vue3-and-nuxt3-architecture
description: Production-grade architecture patterns, state management, SSR strategies, performance optimization, and anti-patterns for Vue 3 (Composition API) and Nuxt 3 applications.
---

# Vue 3 & Nuxt 3 Enterprise Architecture Guide

## Core Architectural Principles

### 1. Composition API & Composables Design
- **Single Responsibility**: Each composable should manage one specific domain concept or side-effect (e.g., `useAuth`, `useInfiniteScroll`, `useWebNotification`).
- **Explicit Return Types & Reactivity**: Prefer returning an explicit object of `ShallowRef`, `Ref`, or `Readonly<Ref>` to preserve reactivity encapsulation.
- **Context Injection**: Use `provide`/`inject` with Symbol keys for scope-level dependency injection (e.g., module configuration, UI themes, scoped dynamic state).
- **Vue 3.5+ Reactive Props Destructuring**: Take advantage of native destructuring for `defineProps()` without losing reactivity, utilizing default value assignment natively.

### 2. Nuxt 3 Full-Stack & Rendering Strategies
- **Hybrid Rendering & Route Rules**: Assign rendering modes strategically in `nuxt.config.ts` (`ssr: true`, `swr`, `static`, `prerender`) based on page freshness and SEO requirements.
- **Nitro Engine & Server Routes**: Enforce strict validation on `server/api/` and `server/routes/` using Zod or H3 built-in helpers (`readValidatedBody`, `getValidatedQuery`).
- **Payload Extraction & Hydration**: Avoid passing non-serializable objects (DOM nodes, class instances, circular references) in `useAsyncData` or `useState`.

### 3. State Management with Pinia & Nuxt `useState`
- **Setup Stores over Option Stores**: Standardize on Setup Store syntax (`defineStore('id', () => { ... })`) for improved Composition API synergy and TypeScript inference.
- **SSR State Isolation**: Avoid top-level global variables outside of functions in server routes or composables to prevent multi-tenant cross-request data leaks.
- **SSR Hydration Boundaries**: Mark client-only states appropriately, using `onMounted` or `<ClientOnly>` wrappers when referencing browser APIs like `window`, `localStorage`, or Web APIs.

---

## Production Code Examples

### Example 1: Type-Safe Dynamic Composable with Auto Cleanup
*Location: `composables/useWebSocketStream.ts`*

```typescript
import { ref, onUnmounted, shallowRef, type Ref } from 'vue'

export interface WebSocketStreamOptions<T> {
  url: string
  reconnectInterval?: number
  maxRetries?: number
  transform?: (raw: unknown) => T
}

export interface WebSocketStreamReturn<T> {
  data: Ref<T | null>
  error: Ref<Error | null>
  isConnected: Ref<boolean>
  send: (payload: unknown) => void
  close: () => void
}

export function useWebSocketStream<T = unknown>(
  options: WebSocketStreamOptions<T>
): WebSocketStreamReturn<T> {
  const { url, reconnectInterval = 3000, maxRetries = 5, transform } = options

  const data = shallowRef<T | null>(null) as Ref<T | null>
  const error = ref<Error | null>(null)
  const isConnected = ref<boolean>(false)

  let socket: WebSocket | null = null
  let retryCount = 0
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  const connect = () => {
    if (import.meta.server) return // Prevent SSR execution

    try {
      socket = new WebSocket(url)

      socket.onopen = () => {
        isConnected.value = true
        error.value = null
        retryCount = 0
      }

      socket.onmessage = (event: MessageEvent) => {
        try {
          const parsed = JSON.parse(event.data)
          data.value = transform ? transform(parsed) : (parsed as T)
        } catch (e) {
          error.value = e instanceof Error ? e : new Error('Failed to parse WebSocket message')
        }
      }

      socket.onerror = (event: Event) => {
        error.value = new Error(`WebSocket error observed: ${JSON.stringify(event)}`)
      }

      socket.onclose = () => {
        isConnected.value = false
        if (retryCount < maxRetries) {
          retryCount++
          reconnectTimer = setTimeout(connect, reconnectInterval)
        }
      }
    } catch (e) {
      error.value = e instanceof Error ? e : new Error('WebSocket connection initialization failed')
    }
  }

  const send = (payload: unknown) => {
    if (socket && isConnected.value) {
      socket.send(typeof payload === 'string' ? payload : JSON.stringify(payload))
    } else {
      console.warn('[useWebSocketStream] Attempted to send payload while disconnected.')
    }
  }

  const close = () => {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (socket) {
      socket.onclose = null // Prevent reconnect loop
      socket.close()
    }
    isConnected.value = false
  }

  connect()

  // Ensure leak-free disposal when hosting component unmounts
  onUnmounted(() => {
    close()
  })

  return {
    data,
    error,
    isConnected,
    send,
    close
  }
}
```

### Example 2: Nuxt 3 Nitro Server Route with Zod Validation & Rate Limiting
*Location: `server/api/v1/products.post.ts`*

```typescript
import { z } from 'zod'

const CreateProductSchema = z.object({
  title: z.string().min(3).max(100),
  price: z.number().positive(),
  category: z.enum(['electronics', 'apparel', 'books']),
  sku: z.string().regex(/^[A-Z]{3}-\d{4}$/),
  tags: z.array(z.string()).default([])
})

export type CreateProductInput = z.infer<typeof CreateProductSchema>

export default defineEventHandler(async (event) => {
  // Validate request body against schema
  const result = await readValidatedBody(event, (body) => CreateProductSchema.safeParse(body))

  if (!result.success) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Bad Request',
      data: result.error.format()
    })
  }

  const productData = result.data
  const config = useRuntimeConfig(event)

  try {
    // Perform downstream API call or DB interaction using runtimeConfig
    const response = await $fetch<{ id: string; createdAt: string }>(`${config.apiSecretUrl}/products`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${config.apiSecretKey}`
      },
      body: productData
    })

    setResponseStatus(event, 201)
    return {
      success: true,
      data: {
        id: response.id,
        ...productData,
        createdAt: response.createdAt
      }
    }
  } catch (err: any) {
    throw createError({
      statusCode: err.statusCode || 500,
      statusMessage: err.statusMessage || 'Internal Server Error'
    })
  }
})
```

### Example 3: SSR-Safe Pinia Setup Store with Async Hydration
*Location: `stores/useUserSessionStore.ts`*

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface UserProfile {
  id: string
  email: string
  roles: string[]
}

export const useUserSessionStore = defineStore('userSession', () => {
  const user = ref<UserProfile | null>(null)
  const token = ref<string | null>(null)
  const isHydrated = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.roles.includes('ADMIN') ?? false)

  function setUser(newUser: UserProfile | null) {
    user.value = newUser
  }

  function setToken(newToken: string | null) {
    token.value = newToken
  }

  async function fetchCurrentUser() {
    if (!token.value) return

    try {
      const data = await useRequestFetch()<UserProfile>('/api/v1/auth/me')
      user.value = data
    } catch (e) {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    if (import.meta.client) {
      const authCookie = useCookie('auth_token')
      authCookie.value = null
    }
  }

  return {
    user,
    token,
    isHydrated,
    isAuthenticated,
    isAdmin,
    setUser,
    setToken,
    fetchCurrentUser,
    logout
  }
})
```

---

## Anti-Patterns & Common Pitfalls

### ❌ Anti-Pattern 1: Destructuring Props without Reactivity Preservation
```typescript
// BAD: Destructuring props directly breaks reactivity
const { title, count } = defineProps<{ title: string; count: number }>()
// Changing 'title' or 'count' from parent won't trigger re-evaluations here!

// GOOD (Vue 3.5+ Reactive Props Destructure):
const { title, count = 0 } = defineProps<{ title: string; count?: number }>()

// GOOD (Vue <3.5):
const props = defineProps<{ title: string; count: number }>()
const titleRef = toRef(props, 'title')
```

### ❌ Anti-Pattern 2: Global State Leakage Across SSR Requests
```typescript
// BAD: Declaring mutable state outside composable/store factory function scope
const sharedState = ref({ user: null }) // SHARED ACROSS ALL SSR REQUESTS! User A can see User B's data!

export function useBadState() {
  return sharedState
}

// GOOD: Use Nuxt's useState or Pinia store
export function useGoodState() {
  return useState('unique-user-state-key', () => ({ user: null }))
}
```

### ❌ Anti-Pattern 3: Calling Composables Inside Event Handlers or Async Tasks
```typescript
// BAD: Calling composables after await or inside nested functions breaks Vue lifecycle tracking
async function handleClick() {
  await fetchData()
  const route = useRoute() // ERROR: Current instance lost after await!
}

// GOOD: Instantiate composables at top level of <script setup>
const route = useRoute()
async function handleClick() {
  await fetchData()
  console.log(route.path)
}
```

### ❌ Anti-Pattern 4: Direct Mutation of Props
```typescript
// BAD: Mutating props directly
const props = defineProps<{ modelValue: string }>()
function updateText(val: string) {
  props.modelValue = val // Vue warning! Direct prop mutation is forbidden.
}

// GOOD: Emit update event or use defineModel() (Vue 3.4+)
const modelValue = defineModel<string>()
function updateText(val: string) {
  modelValue.value = val
}
```
