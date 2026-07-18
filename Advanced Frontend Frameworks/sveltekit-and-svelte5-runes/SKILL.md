---
name: sveltekit-and-svelte5-runes
description: Complete architecture patterns, state management with Svelte 5 Runes ($state, $derived, $effect, $props), SvelteKit SSR/streaming pipelines, form actions, and production anti-patterns.
---

# SvelteKit & Svelte 5 Runes Architecture Guide

## Core Architectural Principles

### 1. Svelte 5 Runes Paradigm
- **Fine-Grained Signals**: Svelte 5 replaces stores (`writable`, `readable`) and compiler-magic `$:` declarations with deep reactive primitives (Runes).
- **Primitives**:
  - `$state(initial)`: Deeply reactive state definition. Use `$state.raw(initial)` for non-reactive large structures (e.g., WebGL objects, large immutable arrays).
  - `$derived(expression)`: Pure, memoized computational projections. Use `$derived.by(() => { ... })` for complex multi-statement computations.
  - `$effect(() => { ... })`: Side-effect execution (DOM mutation, external sync). Must remain free of state mutations to prevent feedback loops.
  - `$props()`: Component property declaration with TS interface support and default assignments.
  - `$bindable()`: Explicit opt-in two-way data binding for props.
- **Class-Based Reactive Stores**: Encapsulate domain logic inside standard ES classes utilizing `$state` and `$derived` properties, completely eliminating legacy store boilerplate.

### 2. SvelteKit Data Flow & SSR Isolation
- **Universal vs Server Load**:
  - Use `+page.server.ts` for database access, secret keys, or direct server APIs.
  - Use `+page.ts` for universal client/server fetching or rendering logic.
- **Streaming Async Data**: Return non-awaited promises in `+page.server.ts` to stream slow data dependencies using SvelteKit's built-in streaming support.
- **Form Actions & Progressive Enhancement**: Always leverage SvelteKit Form Actions with `use:enhance` to ensure forms work seamlessly with or without JavaScript enabled.

---

## Production Code Examples

### Example 1: Svelte 5 Class-Based Reactive State Store
*Location: `src/lib/stores/cart.svelte.ts`*

```typescript
export interface CartItem {
  id: string
  name: string
  price: number
  quantity: number
}

export class ShoppingCartStore {
  // Deeply reactive state array
  items = $state<CartItem[]>([])
  discountCode = $state<string | null>(null)
  discountPercent = $state<number>(0)

  // Derived memoized values
  itemCount = $derived(this.items.reduce((total, item) => total + item.quantity, 0))
  
  subtotal = $derived(
    this.items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  tax = $derived.by(() => {
    const taxableAmount = Math.max(0, this.subtotal * (1 - this.discountPercent))
    return taxableAmount * 0.08 // 8% sales tax
  })

  total = $derived(Math.max(0, this.subtotal * (1 - this.discountPercent)) + this.tax)

  addItem(newItem: Omit<CartItem, 'quantity'>) {
    const existing = this.items.find(i => i.id === newItem.id)
    if (existing) {
      existing.quantity += 1
    } else {
      this.items.push({ ...newItem, quantity: 1 })
    }
  }

  removeItem(id: string) {
    this.items = this.items.filter(i => i.id !== id)
  }

  updateQuantity(id: string, quantity: number) {
    const item = this.items.find(i => i.id === id)
    if (item) {
      if (quantity <= 0) {
        this.removeItem(id)
      } else {
        item.quantity = quantity
      }
    }
  }

  applyDiscount(code: string, percent: number) {
    this.discountCode = code
    this.discountPercent = percent / 100
  }

  clear() {
    this.items = []
    this.discountCode = null
    this.discountPercent = 0
  }
}

// Global or scoped instantiations
export const cartStore = new ShoppingCartStore()
```

### Example 2: SvelteKit Streaming Load Function & Page Component
*Location: `src/routes/dashboard/+page.server.ts`*

```typescript
import type { PageServerLoad } from './$types'
import { error } from '@sveltejs/kit'

async function fetchFastMetrics(userId: string) {
  // Simulating fast DB query (50ms)
  return { userStatus: 'active', notificationsCount: 4 }
}

async function fetchSlowAnalytics(userId: string) {
  // Simulating heavy analytical query (1500ms)
  await new Promise((resolve) => setTimeout(resolve, 1500))
  return {
    monthlyRevenue: 14250.0,
    activeSubscriptions: 342,
    chartData: [10, 25, 45, 80, 120]
  }
}

export const load: PageServerLoad = async ({ locals, parent }) => {
  const session = await locals.getSession()
  if (!session?.user) {
    throw error(401, 'Unauthorized access to dashboard metrics')
  }

  // Await fast critical data for immediate initial SSR HTML response
  const fastMetrics = await fetchFastMetrics(session.user.id)

  // DO NOT await slow analytical data — return promised stream
  const slowAnalyticsPromise = fetchSlowAnalytics(session.user.id)

  return {
    user: session.user,
    fastMetrics,
    // Streamed promise payload
    streamed: {
      analytics: slowAnalyticsPromise
    }
  }
}
```

*Location: `src/routes/dashboard/+page.svelte`*

```svelte
<script lang="ts">
  import type { PageData } from './$types'

  // Component props in Svelte 5 using $props rune
  let { data }: { data: PageData } = $props()

  // Destructure reactive references
  let fastMetrics = $derived(data.fastMetrics)
</script>

<div class="dashboard">
  <h1>Welcome, {data.user.name}</h1>

  <!-- Instant SSR Content -->
  <section class="summary-cards">
    <div class="card">Status: {fastMetrics.userStatus}</div>
    <div class="card">Unread Notifications: {fastMetrics.notificationsCount}</div>
  </section>

  <!-- Streamed Content with Promise Resolution -->
  <section class="analytics-section">
    <h2>Analytics Overview</h2>

    {#await data.streamed.analytics}
      <div class="loading-skeleton">
        <p>Loading deep analytics metrics...</p>
      </div>
    {:then analytics}
      <div class="analytics-content">
        <p>Monthly Revenue: ${analytics.monthlyRevenue.toLocaleString()}</p>
        <p>Active Subscriptions: {analytics.activeSubscriptions}</p>
      </div>
    {:catch err}
      <div class="error-box">
        <p>Failed to load analytics: {err.message}</p>
      </div>
    {/await}
  </section>
</div>
```

### Example 3: Progressive Form Action with Action Directive
*Location: `src/routes/contact/+page.server.ts`*

```typescript
import { fail, type Actions } from '@sveltejs/kit'

export const actions: Actions = {
  submitForm: async ({ request }) => {
    const formData = await request.formData()
    const email = formData.get('email')?.toString()
    const message = formData.get('message')?.toString()

    if (!email || !email.includes('@')) {
      return fail(400, { email, message, error: 'Invalid email address' })
    }

    if (!message || message.length < 10) {
      return fail(400, { email, message, error: 'Message must be at least 10 characters long' })
    }

    // Process submission...
    return { success: true, messageId: 'msg_98127391' }
  }
}
```

*Location: `src/routes/contact/+page.svelte`*

```svelte
<script lang="ts">
  import { enhance } from '$app/forms'
  import type { ActionData } from './$types'

  let { form }: { form: ActionData } = $props()

  let isSubmitting = $state(false)
</script>

<form
  method="POST"
  action="?/submitForm"
  use:enhance={() => {
    isSubmitting = true
    return async ({ update }) => {
      isSubmitting = false
      await update()
    }
  }}
>
  <label>
    Email Address:
    <input type="email" name="email" value={form?.email ?? ''} required />
  </label>

  <label>
    Your Message:
    <textarea name="message" required>{form?.message ?? ''}</textarea>
  </label>

  {#if form?.error}
    <p class="error-msg">{form.error}</p>
  {/if}

  {#if form?.success}
    <p class="success-msg">Message sent successfully! Ref: {form.messageId}</p>
  {/if}

  <button type="submit" disabled={isSubmitting}>
    {isSubmitting ? 'Sending...' : 'Send Message'}
  </button>
</form>
```

---

## Anti-Patterns & Common Pitfalls

### ❌ Anti-Pattern 1: Mutating Derived State or Using `$effect` for Computed Values
```svelte
<script lang="ts">
  let count = $state(0)
  let double = $state(0)

  // BAD: Synchronizing derived state using $effect creates extra render ticks & bugs
  $effect(() => {
    double = count * 2
  })

  // GOOD: Use $derived primitive for computational projections
  let doubleDerived = $derived(count * 2)
</script>
```

### ❌ Anti-Pattern 2: Top-Level Request State Leaks in SvelteKit SSR
```typescript
// BAD: Module-scoped state variable in +page.server.ts or server module
// Location: src/lib/server/userState.ts
export let currentUser: User | null = null // SHARED ACROSS REQUESTS IN NODE.JS SSR MEMORY!

export const load = async ({ locals }) => {
  currentUser = locals.user // BUG: Request A overwrites Request B's user!
}

// GOOD: Keep request-bound data strictly inside event locals or pass via return values
export const load = async ({ locals }) => {
  return { user: locals.user }
}
```

### ❌ Anti-Pattern 3: Mixing Legacy Svelte 4 Store Syntax with Runes Mode
```svelte
<script lang="ts">
  import { writable } from 'svelte/store'
  
  // AVOID: Mixing old writable store with Svelte 5 runes creates unnecessary complexity
  const countStore = writable(0)

  // GOOD: Native Svelte 5 $state
  let count = $state(0)
</script>
```
