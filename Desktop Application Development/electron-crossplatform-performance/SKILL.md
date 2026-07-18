---
name: electron-crossplatform-performance
description: Production architecture, multi-process IPC security, V8 memory management, native node modules, window lifecycle optimization, and cross-platform desktop execution using Electron. Use when building, hardening, or tuning performance for enterprise Electron apps across Windows, macOS, and Linux.
---

# Electron Cross-Platform Performance & Architecture

## Process Architecture & Isolation

Electron applications operate across distinct processes isolated by Chromium sandboxing. Enterprise applications must maintain strict process boundaries:

```
+-------------------------------------------------------------------------+
|                              Main Process                               |
|  - Node.js Environment (Full System Privilege)                          |
|  - Manages Application Lifecycle & Native Menus / Tray                  |
|  - Controls BrowserWindow instances & Native APIs                       |
+-------------------------------------------------------------------------+
       |                                              |
       | IPC (ContextBridge)                          | UtilityProcess API
       v                                              v
+-----------------------------+         +---------------------------------+
|     Renderer Process        |         |        Utility Process          |
|  - Chromium Web Engine      |         |  - Background Node.js Work      |
|  - Isolated DOM Rendering   |         |  - Non-blocking CPU tasks       |
|  - `nodeIntegration: false` |         |  - Heavy Data Ingestion         |
|  - `contextIsolation: true` |         +---------------------------------+
+-----------------------------+
```

---

## Security Hardening & Safe IPC Design

### 1. Mandatory Secure BrowserWindow Configurations
Enforce strict security flags on all `BrowserWindow` instances:

```typescript
// main/windowFactory.ts
import { BrowserWindow, app } from 'electron';
import * as path from 'path';

export function createSecureWindow(): BrowserWindow {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    show: false, // Prevent white flashing during load
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,       // Enforce IPC bridge separation
      nodeIntegration: false,        // Disable node access in renderer
      nodeIntegrationInWorker: false,
      sandbox: true,                 // Enable Chromium Renderer Sandbox
      webSecurity: true,             // Enforce Same-Origin Policy
      allowRunningInsecureContent: false,
    },
  });

  win.once('ready-to-show', () => {
    win.show();
  });

  // Enforce Navigation Restraints
  win.webContents.on('will-navigate', (event, url) => {
    const parsedUrl = new URL(url);
    if (parsedUrl.origin !== 'https://app.yourdomain.com' && !url.startsWith('file://')) {
      event.preventDefault();
      console.warn(`Blocked unauthorized navigation to: ${url}`);
    }
  });

  // Prevent New Windows / Popups
  win.webContents.setWindowOpenHandler(({ url }) => {
    // Open external URLs in default system browser securely
    if (url.startsWith('https:')) {
      require('electron').shell.openExternal(url);
    }
    return { action: 'deny' };
  });

  return win;
}
```

### 2. Type-Safe ContextBridge IPC Layer

#### Preload Script (`preload/index.ts`):
```typescript
import { contextBridge, ipcRenderer } from 'electron';

export interface DesktopAPI {
  fetchSystemStats: () => Promise<{ cpuLoad: number; memoryFreeMB: number }>;
  onUpdateStatus: (callback: (status: string) => void) => () => void;
}

const api: DesktopAPI = {
  fetchSystemStats: () => ipcRenderer.invoke('system:get-stats'),
  onUpdateStatus: (callback) => {
    const handler = (_event: unknown, status: string) => callback(status);
    ipcRenderer.on('app:update-status', handler);
    // Return cleanup function to prevent memory leaks
    return () => ipcRenderer.removeListener('app:update-status', handler);
  },
};

contextBridge.exposeInMainWorld('desktopAPI', api);
```

#### Main Process IPC Handler (`main/ipcHandlers.ts`):
```typescript
import { ipcMain } from 'electron';
import * as os from 'os';

export function registerIpcHandlers() {
  ipcMain.handle('system:get-stats', async (event) => {
    // Validate sender frame identity
    if (!event.senderFrame.url.startsWith('file://') && !event.senderFrame.url.startsWith('http://localhost')) {
      throw new Error('Unauthorized IPC invocation');
    }

    const freeMem = os.freemem() / (1024 * 1024);
    const loadAvg = os.loadavg()[0];

    return {
      cpuLoad: Math.round(loadAvg * 100) / 100,
      memoryFreeMB: Math.round(freeMem),
    };
  });
}
```

---

## Memory Management & Performance Tuning

### 1. Offloading Heavy Computation to `utilityProcess`
Never execute CPU-intensive tasks (PDF parsing, compression, cryptography) in the main process or renderer thread.

```typescript
// main/utilityManager.ts
import { utilityProcess, MessageChannelMain } from 'electron';
import * as path from 'path';

export function runBackgroundJob(taskData: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const child = utilityProcess.fork(path.join(__dirname, 'workerTask.js'));

    child.on('spawn', () => {
      child.postMessage({ type: 'START_TASK', payload: taskData });
    });

    child.on('message', (message: any) => {
      if (message.type === 'SUCCESS') {
        resolve(message.result);
        child.kill();
      } else if (message.type === 'ERROR') {
        reject(new Error(message.error));
        child.kill();
      }
    });

    child.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker exited with code ${code}`));
    });
  });
}
```

### 2. V8 Garbage Collection & Memory Leak Prevention
- **Avoid Global Listeners**: Always unregister `ipcRenderer.on` listeners when React/Vue components unmount.
- **Window Dereferencing**: Always set window reference variables to `null` on window close to allow GC.

```typescript
let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = createSecureWindow();
  mainWindow.on('closed', () => {
    mainWindow = null; // Essential for V8 memory cleanup
  });
}
```

### 3. Chromium Command Line Performance Flags
Configure optimized runtime parameters before app initialization:

```typescript
// main/index.ts
import { app } from 'electron';

// Hardware acceleration tuning
app.commandLine.appendSwitch('enable-gpu-rasterization');
app.commandLine.appendSwitch('enable-zero-copy');

// V8 Memory limits for resource-constrained clients
app.commandLine.appendSwitch('js-flags', '--max-old-space-size=4096');

// Disable unneeded features to save startup time
app.commandLine.appendSwitch('disable-breakpad'); // If custom crash reporter is used
```

---

## Cross-Platform OS Customization

| Feature | Windows | macOS | Linux |
| :--- | :--- | :--- | :--- |
| **Window Frame** | Windows Mica / Acrylic API | Vibrancy / Title Bar Overlay | Standard GTK decorations / Frameless |
| **App Updates** | NSIS / Squirrel.Windows | `autoUpdater` with Signed DMG/Zip | AppImage / DEB / Snap |
| **Shortcuts** | `Ctrl+Shift+X` | `Cmd+Shift+X` | `Ctrl+Shift+X` |
| **Tray / Dock** | System Tray notification icons | Dock badge & context menu | AppIndicator / StatusIcon |

---

## Common Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Impact | Architectural Fix |
| :--- | :--- | :--- |
| **`remote` Module Usage** | Severe performance degradation & critical remote code execution vector | Use explicit `ipcMain.handle` / `ipcRenderer.invoke` |
| **Sync IPC (`sendSync`)** | Freezes Chromium renderer event loop, causing visual stutter | Use asynchronous `invoke` / `handle` promise patterns |
| **Synchronous Node File System Calls in Renderer** | Unresponsive UI render thread | Delegate file operations to Main/Utility processes asynchronously |
| **Orphaned IPC Event Listeners** | Memory leak holding DOM elements in V8 heap | Return and invoke unbind functions on component destroy |
| **Missing Content Security Policy (CSP)** | Susceptible to XSS leading to native system compromise | Serve strict CSP headers: `default-src 'self'; script-src 'self'` |
