---
name: tauri-rust-and-frontend-desktop
description: Architectural patterns, security IPC, performance optimization, native integration, and production best practices for building cross-platform desktop applications using Tauri (v2) and Rust with modern web frontends (React, Svelte, Vue). Use when designing, building, or optimizing Tauri desktop apps.
---

# Tauri, Rust & Frontend Desktop Application Development

## Overview & Architecture

Tauri bridges modern web UI technology with high-performance native system capabilities implemented in Rust. Unlike Electron, Tauri uses the OS native web view renderer (WebKit on macOS/Linux, WebView2 on Windows) and offloads core app logic, background execution, system integrations, and security enforcement to a lightweight Rust process.

```
+-----------------------------------------------------------------------+
|                         Frontend Layer                                |
|           React / Svelte / Vue / Solid / HTML5 + TS                   |
|  - Renders UI via Native WebView (WebView2 / WebKit)                 |
|  - Calls backend APIs via `@tauri-apps/api/core` invoke()             |
+-----------------------------------------------------------------------+
                                 |  IPC (Serialized JSON / Binary)
                                 v
+-----------------------------------------------------------------------+
|                          Rust Core Layer                              |
|  - Command Handlers (`#[tauri::command]`)                             |
|  - Thread Pool / Async Execution (`tokio` runtime)                    |
|  - State Management (`tauri::State<T>`)                               |
|  - Native OS Capabilities, File I/O, SQLite, Hardware Security IPC   |
+-----------------------------------------------------------------------+
```

### Core Architectural Principles
1. **Decoupled Business Logic**: High-throughput calculations, filesystem modifications, cryptographic routines, and persistent storage MUST live in Rust.
2. **Lean Frontend**: Frontend handles state rendering, UI micro-interactions, and visual layout. Avoid heavy computing or large payload caching in JS memory.
3. **Strict Capability Isolation**: Every native capability (filesystem access, shell execution, dialogs, HTTP requests) is disabled by default and governed by Tauri v2 granular capabilities and permissions ACLs.

---

## Security & IPC Best Practices

### 1. Tauri v2 Security & Capability Model
In Tauri v2, permissions are explicitly granted in `src-tauri/capabilities/default.json` or custom target capabilities:

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default capabilities for production build",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "fs:allow-read-text-file",
    "fs:allow-write-text-file",
    {
      "identifier": "fs:scope",
      "allow": ["$APP_DATA/**", "$DOCUMENT/**"]
    },
    "dialog:allow-open",
    "dialog:allow-save"
  ]
}
```

### 2. Type-Safe IPC with Custom Commands & Error Handling

Never expose raw shell commands or unrestricted file access to the frontend. Expose domain-specific, strongly typed commands.

#### Rust Backend (`src-tauri/src/commands.rs`):
```rust
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri::{State, AppHandle};
use thiserror::Error;

#[derive(Debug, Error, Serialize, Deserialize)]
pub enum AppError {
    #[error("IO Error: {0}")]
    Io(String),
    #[error("Validation Error: {0}")]
    Validation(String),
    #[error("Unauthorized access to resource")]
    Unauthorized,
}

#[derive(Debug, Deserialize)]
pub struct ProcessDataPayload {
    pub item_id: String,
    pub quantity: u32,
}

#[derive(Debug, Serialize)]
pub struct ProcessResult {
    pub status: String,
    pub processed_count: u32,
}

pub struct AppState {
    pub db_connection_count: Mutex<u32>,
}

#[tauri::command]
pub async fn process_secure_data(
    payload: ProcessDataPayload,
    state: State<'_, AppState>,
    _app: AppHandle,
) -> Result<ProcessResult, AppError> {
    if payload.quantity == 0 {
        return Err(AppError::Validation("Quantity must be greater than 0".into()));
    }

    let mut count = state.db_connection_count.lock().map_err(|e| AppError::Io(e.to_string()))?;
    *count += 1;

    // Simulate async compute / I/O work without blocking main thread
    tokio::time::sleep(std::time::Duration::from_millis(50)).await;

    Ok(ProcessResult {
        status: "SUCCESS".into(),
        processed_count: payload.quantity,
    })
}
```

#### Frontend Consumer (`src/api/desktopBridge.ts`):
```typescript
import { invoke } from '@tauri-apps/api/core';

export interface ProcessPayload {
  item_id: string;
  quantity: number;
}

export interface ProcessResult {
  status: string;
  processed_count: number;
}

export async function submitDataProcessing(payload: ProcessPayload): Promise<ProcessResult> {
  try {
    const result = await invoke<ProcessResult>('process_secure_data', { payload });
    return result;
  } catch (error) {
    console.error('Tauri IPC Error:', error);
    throw error;
  }
}
```

---

## Performance Optimizations & Resource Management

### 1. Async Non-Blocking Main Thread
Never block the Tauri main window thread. Use `async fn` for commands and delegate blocking tasks to `tokio::task::spawn_blocking`.

```rust
#[tauri::command]
pub async fn heavy_computation(data: Vec<u8>) -> Result<Vec<u8>, String> {
    tokio::task::spawn_blocking(move || {
        // High-CPU tasks: Image processing, compression, cryptography
        compress_bytes(&data)
    })
    .await
    .map_err(|e| e.to_string())?
}
```

### 2. Zero-Copy & High-Volume Binary Data Streaming
Avoid JSON serializing large arrays over IPC. Use channel events or binary arrays (`Vec<u8>` -> `Uint8Array`).

```rust
use tauri::ipc::Response;

#[tauri::command]
pub fn fetch_large_binary_chunk() -> Response {
    let raw_bytes: Vec<u8> = vec![0u8; 10_000_000]; // 10MB binary
    Response::new(raw_bytes)
}
```

### 3. Frontend Bundle Footprint Minimization
- Enforce dynamic imports / code-splitting for routes and heavy widgets.
- Leverage native font stacks or minimal SVGs over web font bundles.
- Use `vite-plugin-singlefile` or optimized asset bundling to reduce I/O overhead on app launch.

---

## Common Anti-Patterns & Pitfalls

| Anti-Pattern | Risk / Problem | Recommended Pattern |
| :--- | :--- | :--- |
| **Global Shell Invocation** (`shell:allow-execute`) | Arbitrary command execution vulnerabilities | Wrap shell tasks inside custom Rust commands with strict input sanitization |
| **Sync I/O in Main Thread** | Freezes UI window, fails OS responsiveness checks | Use `async` commands & `tokio::fs` or `spawn_blocking` |
| **Storing Secrets in Frontend JS** | Inspectable via WebView WebTools in dev / unpacked builds | Secure secrets in OS Keyring via `keyring-rs` in Rust core |
| **Passing Large Datasets as Plain JSON** | High memory allocation & CPU overhead in JSON parse/serialize | Use binary responses or byte buffers |
| **Unbounded Event Listeners** | Memory leaks in frontend and backend event bus | Unsubscribe (`unlisten()`) on UI component unmount |

---

## Production Setup & Configuration Reference

### `src-tauri/Cargo.toml`
```toml
[package]
name = "tauri-app"
version = "0.1.0"
edition = "2021"

[build-dependencies]
tauri-build = { version = "2.0.0", features = [] }

[dependencies]
tauri = { version = "2.0.0", features = ["tray-icon"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1", features = ["full"] }
thiserror = "1.0"
```

### Main Entrypoint (`src-tauri/src/main.rs`)
```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;

use commands::{process_secure_data, AppState};
use std::sync::Mutex;

fn main() {
    tauri::Builder::default()
        .manage(AppState {
            db_connection_count: Mutex::new(0),
        })
        .invoke_handler(tauri::generate_handler![process_secure_data])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```
