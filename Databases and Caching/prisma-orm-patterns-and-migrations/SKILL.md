---
name: prisma-orm-patterns-and-migrations
description: Best practices for Prisma ORM schema design, high-performance query optimization, preventing N+1 problems, zero-downtime database migrations, connection pooling, and multi-tenant data modeling. Use when building Node.js/TypeScript applications with Prisma.
---

# Prisma ORM Patterns & Migrations Architecture Guide

Production reference for building scalable Node.js and TypeScript applications using Prisma ORM, optimizing database access, executing zero-downtime migrations, and managing connections.

---

## 1. Schema Modeling & Relationship Patterns

### 1.1 Explicit Many-to-Many vs. Implicit Many-to-Many
* **Implicit**: Prisma manages join table automatically. Use when join table needs no additional metadata.
* **Explicit**: User defines join table model. Use when storing timestamps or custom payload on relation records (e.g., `role`, `assignedAt`).

```prisma
// Explicit Many-to-Many with Relation Attributes
model User {
  id        String         @id @default(uuid())
  email     String         @unique
  memberships UserOrganization[]
}

model Organization {
  id        String         @id @default(uuid())
  name      String
  members   UserOrganization[]
}

model UserOrganization {
  userId         String
  organizationId String
  role           String       @default("MEMBER")
  assignedAt     DateTime     @default(now())

  user         User         @relation(fields: [userId], references: [id], onDelete: Cascade)
  organization Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)

  @@id([userId, organizationId])
  @@index([organizationId])
}
```

### 1.2 Referential Actions & Performance Indexing
* Always explicitly define foreign key indexes using `@@index([foreignKeyField])` to optimize join performance and cascading updates/deletes.
* Set appropriate `onDelete` actions (`Cascade`, `SetNull`, `Restrict`, `NoAction`).

---

## 2. Query Optimization & Preventing N+1 Problems

### 2.1 Fine-Grained Projection (`select` vs `include`)
Avoid blind `include` queries that fetch all fields from related tables. Use explicit `select` payloads to reduce payload over-fetching.

```typescript
// ❌ ANTI-PATTERN: Over-fetching full nested objects
const posts = await prisma.post.findMany({
  include: { author: true, comments: true }
});

// ✅ PRODUCTION PATTERN: Explicit field selection
const posts = await prisma.post.findMany({
  select: {
    id: true,
    title: true,
    author: {
      select: {
        id: true,
        name: true
      }
    },
    _count: {
      select: { comments: true }
    }
  }
});
```

### 2.2 Efficient Pagination: Cursor-Based vs. Offset
* **Offset Pagination** (`skip`/`take`): Degrades linearly ($O(N)$) as page depth increases.
* **Cursor-Based Pagination** (`cursor`/`take`): Constant-time lookup ($O(1)$) utilizing indexed fields.

```typescript
async function getPaginatedPosts(cursorId?: string, pageSize = 20) {
  return await prisma.post.findMany({
    take: pageSize + 1, // Fetch +1 to determine hasNextPage
    ...(cursorId && {
      skip: 1, // Skip the cursor document itself
      cursor: { id: cursorId }
    }),
    orderBy: { createdAt: 'desc' }
  });
}
```

---

## 3. Zero-Downtime Migration Workflows

### 3.1 Migration Commands Environment Split

```bash
# Local Development: Generates SQL migration & updates local database
npx prisma migrate dev --name add_user_status

# Production CI/CD Pipeline: Executes pending unapplied migrations safely
npx prisma migrate deploy
```

### 3.2 The Expand-Contract (Parallel Adoption) Pattern
To rename or delete a database column without breaking live application instances during rolling deployments:

```
Step 1 (Expand):    Add new field 'fullName' alongside old 'name' field in schema.
Step 2 (App Code):  Write to both 'name' and 'fullName'; read from 'fullName' with fallback to 'name'.
Step 3 (Backfill):  Run asynchronous background task populating 'fullName' for legacy records.
Step 4 (Contract):  Remove 'name' references from code and drop column in subsequent Prisma migration.
```

---

## 4. Connection Pooling & Client Instantiation

### 4.1 Prisma Client Singleton (Node.js / Next.js)
Prevent multiple client instantiation in serverless or hot-reloading development environments:

```typescript
import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error']
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
```

### 4.2 PgBouncer / Prisma Accelerate Integration
Append `?pgbouncer=true` & `connection_limit=X` parameters to `DATABASE_URL` when utilizing external transaction connection poolers.

---

## 5. Client Extensions & Multi-Tenancy

Utilize Prisma `$extends` to enforce global tenant isolation filters across queries automatically.

```typescript
import { PrismaClient } from '@prisma/client';

export function getTenantPrismaClient(tenantId: string) {
  const baseClient = new PrismaClient();

  return baseClient.$extends({
    query: {
      $allModels: {
        async $allOperations({ model, operation, args, query }) {
          if (['findMany', 'findFirst', 'count', 'updateMany', 'deleteMany'].includes(operation)) {
            args.where = { ...args.where, tenantId };
          }
          return query(args);
        }
      }
    }
  });
}
```

---

## 6. Anti-Patterns & Common Pitfalls

* ❌ **Using `prisma db push` in Production**: Can drop columns and data silently without tracking migration history.
* ❌ **Unindexed Foreign Key Queries**: Leads to database table scans during joins and relation filters.
* ❌ **Long-Running Interactive Transactions**: Holding `$transaction(async (tx) => ...)` open over HTTP requests leads to connection timeouts and pool starvation.
* ❌ **Inefficient Native Queries (`$queryRaw`)**: Using untyped `$queryRawUnsafe` with raw string concatenation opens SQL Injection vulnerabilities. Always use parameterized `$queryRaw` tagged templates.
