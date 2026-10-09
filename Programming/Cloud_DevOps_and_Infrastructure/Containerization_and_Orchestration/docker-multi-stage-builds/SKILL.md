---
name: docker-multi-stage-builds
metadata:
  category: Containerization and Orchestration
description: Master production Docker multi-stage builds, container image layer caching, security hardening, non-root user execution, distroless images, and minimal footprint optimizations. Trigger when building Dockerfiles, optimizing image size, or hardening container runtime security.
compatibility: Docker Engine 20.10+, BuildKit, Docker Compose v2+
---

# Docker Multi-Stage Builds & Optimization Skill Guide

This skill defines production standards for authoring secure, minimal-footprint, highly cached multi-stage `Dockerfile` definitions.

---

## 1. Multi-Stage Build Architecture

Multi-stage builds separate compilation environments (which contain full SDKs and build tools) from final production runtime containers (which contain only compiled artifacts and runtime dependencies).

```text
+-------------------------------------------------------------+
| Stage 1: Build & Dependencies (golang:1.22-alpine / node:20) |
| - Full toolchain, build tools, package managers              |
| - Compiles binary / bundle                                  |
+-------------------------------------------------------------+
                              |
                     Copy Artifacts Only
                              v
+-------------------------------------------------------------+
| Stage 2: Production Runtime (gcr.io/distroless or alpine)   |
| - No shell, no package manager, non-root system user       |
| - Minimal image size (<30MB)                                |
+-------------------------------------------------------------+
```

---

## 2. Production Multi-Stage Dockerfile Patterns

### A. Node.js / Next.js Production Dockerfile

```dockerfile
# Syntax directive required for modern BuildKit cache features
# syntax=docker/dockerfile:1.6

# -------------------------------------------------------------
# Base Stage: Shared node environment
# -------------------------------------------------------------
FROM node:20-alpine AS base
WORKDIR /app
RUN apk add --no-libc-compat

# -------------------------------------------------------------
# Stage 1: Install Dependencies with Layer Caching
# -------------------------------------------------------------
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production

# -------------------------------------------------------------
# Stage 2: Build Application
# -------------------------------------------------------------
FROM base AS builder
WORKDIR /app
COPY package.json package-lock.json ./
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NODE_ENV=production
RUN --mount=type=cache,target=/root/.npm \
    npm run build

# -------------------------------------------------------------
# Stage 3: Minimal Production Runtime
# -------------------------------------------------------------
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Create dedicated non-root user and group
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built application assets with ownership settings
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
```

### B. Go Microservice Distroless Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.6

# -------------------------------------------------------------
# Stage 1: Build Go Binary
# -------------------------------------------------------------
FROM golang:1.22-alpine AS builder
WORKDIR /src

# Download modules with BuildKit cache
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

COPY . .

# Compile static binary disabling cgo and strip symbols (-s -w)
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-s -w" -o /bin/server ./cmd/server

# -------------------------------------------------------------
# Stage 2: Distroless Minimal Security Runtime
# -------------------------------------------------------------
FROM gcr.io/distroless/static-debian12:nonroot AS runner
WORKDIR /

COPY --from=builder --chown=nonroot:nonroot /bin/server /server

USER nonroot:nonroot
EXPOSE 8080

ENTRYPOINT ["/server"]
```

---

## 3. Image Optimization & Layer Ordering Rules

1. **Order from Least to Most Frequently Changed**:
   - Install system dependencies first (`apt-get`, `apk`).
   - Copy lock files second (`package-lock.json`, `go.sum`).
   - Copy application source code last (`COPY . .`).
2. **Utilize BuildKit Cache Mounts**:
   - Package manager caches (`/root/.npm`, `/var/cache/apt`) are retained across builds without bloating final image layers.
3. **Combine Shell Instructions**:
   - Combine update, install, and clean steps in a single `RUN` layer to prevent cached package lists in layers.

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

---

## 4. Security Hardening & Image Inspection Commands

```bash
# Enable BuildKit CLI support
export DOCKER_BUILDKIT=1

# Build image with inline build cache support
docker buildx build \
  --build-arg NODE_ENV=production \
  --cache-to type=inline \
  --tag my-app:2.1.0 \
  .

# Scan image for vulnerabilities using Trivy
trivy image --severity HIGH,CRITICAL my-app:2.1.0

# Inspect image layer composition and size breakdown
docker history my-app:2.1.0
```

---

## 5. Anti-Patterns & Best Practices

| Anti-Pattern | Security / Performance Risk | Production Best Practice |
| :--- | :--- | :--- |
| **Running containers as default `root` user** | Container escape vulnerabilities compromise host kernel privilege. | Enforce `USER nonroot` or explicit UID (`USER 10001`). |
| **Including SDK tools in final stage** | Increases attack surface and image size (500MB+ vs 20MB). | Copy static binaries/bundles into distroless or minimal alpine base. |
| **`COPY . .` before `npm install` or `go mod download`** | Invalidates layer cache on any file change, forcing re-download of modules. | Copy dependency manifests (`package.json`, `go.mod`) prior to copying code. |
| **Omitting `.dockerignore` file** | Secrets, `.git`, `node_modules`, and local logs are baked into build context. | Always create a `.dockerignore` excluding `.git`, `node_modules`, `.env`. |
